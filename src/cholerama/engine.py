# SPDX-License-Identifier: BSD-3-Clause

import time
from typing import Optional, Tuple, Union

import numpy as np
from numba import set_num_threads

from . import config
from .compute import evolve_board
from .helpers import Positions
from .player import Player
from .plot import plot
from .scores import finalize_scores, read_round
from .tools import make_color, array_from_shared_mem, make_starting_positions


def setup(bots, iterations, seed=None):

    rng = np.random.default_rng(seed)
    nplayers = len(bots)

    board_old = np.zeros((config.ny, config.nx), dtype=int)
    board_new = board_old.copy()
    player_histories = np.zeros((nplayers, iterations + 1), dtype=int)
    player_tokens = np.zeros(nplayers, dtype=int)
    game_flow = np.zeros(2, dtype=bool)  # pause, exit

    starting_patches = make_starting_positions(nplayers, rng)
    patch_size = (config.ny // config.npatches[0], config.nx // config.npatches[1])

    if isinstance(bots, dict):
        dict_of_bots = {
            name: bot.Bot(
                number=i + 1, name=name, patch_location=patch, patch_size=patch_size
            )
            for i, ((name, bot), patch) in enumerate(
                zip(bots.items(), starting_patches)
            )
        }
    else:
        dict_of_bots = {
            bot.AUTHOR: bot.Bot(number=i + 1, name=bot.AUTHOR, patch=patch)
            for i, (bot, patch) in enumerate(zip(bots, starting_patches))
        }

    players = {}
    for i, (bot, patch) in enumerate(zip(dict_of_bots.values(), starting_patches)):
        player = Player(
            name=bot.name,
            number=i + 1,
            pattern=bot.pattern,
            color=make_color(i if bot.color is None else bot.color),
            patch=patch,
        )
        p = player.pattern
        x, y = p.x, p.y
        x = ((np.asarray(x) % config.stepx) + (patch[1] * config.stepx)) % config.nx
        y = ((np.asarray(y) % config.stepy) + (patch[0] * config.stepy)) % config.ny
        board_old[y, x] = player.number
        players[bot.name] = player
        player_histories[i, 0] = player.ncells
        player_tokens[i] = player.tokens

    buffers = {
        "board_old": board_old,
        "board_new": board_new,
        "player_histories": player_histories,
        "player_tokens": player_tokens,
        "game_flow": game_flow,
    }
    return buffers, players, dict_of_bots


class Engine:
    def __init__(
        self,
        bots: dict,
        players: dict,
        iterations: int,
        buffers: dict,
        safe: bool = False,
        test: bool = True,
    ):
        self.bots = bots
        self.players = players
        # self.buffers = {
        #     key: array_from_shared_mem(*value) for key, value in buffers.items()
        # }

        self.board_old = buffers["board_old"]
        self.board_new = buffers["board_new"]
        self.player_histories = buffers["player_histories"]
        self.player_tokens = buffers["player_tokens"]
        self.game_flow = buffers["game_flow"]
        self.cell_counts = np.zeros(len(self.bots), dtype=int)

        self.iterations = iterations
        self._test = test
        self.safe = safe
        self.token_interval = max(1, iterations // config.additional_tokens)

        self.xoff = np.array([-1, 0, 1, -1, 1, -1, 0, 1])
        self.yoff = np.array([-1, -1, -1, 0, 0, 1, 1, 1])
        self.neighbors = np.zeros(8, dtype=int)
        self.neighbor_buffer = np.zeros(3, dtype=int)

        # Pre-compile numba function
        evolve_board(
            self.board_old,
            self.board_new,
            self.xoff,
            self.yoff,
            self.neighbors,
            self.neighbor_buffer,
            self.cell_counts,
            config.nx,
            config.ny,
        )

    def add_player_new_cells(self, player: Player, new_cells: Positions):
        x, y = new_cells.x, new_cells.y
        ntok = len(x)
        ok = True
        if ntok != len(y):
            print(f"Player {player.name}: new cells x and y have different lengths.")
            ok = False
        if ntok > player.tokens:
            print(
                f"Player {player.name}: not enough tokens: needs {ntok}, "
                f"has {player.tokens}."
            )
            ok = False
        x = (
            (np.asarray(x) % config.stepx) + (player.patch[1] * config.stepx)
        ) % config.nx
        y = (
            (np.asarray(y) % config.stepy) + (player.patch[0] * config.stepy)
        ) % config.ny
        if self.board_old[y, x].sum() > 0:
            print(f"Player {player.name}: cannot overwrite alive cells.")
            ok = False
        if ok:
            self.board_old[y, x] = player.number
            player.tokens -= ntok

    def call_player_bots(self, it: int):
        for bot, player in zip(self.bots.values(), self.players.values()):
            if player.ncells == 0:
                continue
            self.board_new.setflags(write=False)
            new_cells = None
            args = {
                "iteration": int(it),
                "board": self.board_new,
                "patch": self.board_new[
                    player.patch_bounds["ymin"] : player.patch_bounds["ymax"],
                    player.patch_bounds["xmin"] : player.patch_bounds["xmax"],
                ],
                "tokens": int(player.tokens),
            }
            if self.safe:
                try:
                    new_cells = bot.iterate(**args)
                except:  # noqa
                    pass
            else:
                new_cells = bot.iterate(**args)
            self.board_new.setflags(write=True)
            if new_cells:
                self.add_player_new_cells(player, new_cells)

    def update(self, it: int):
        if it % self.token_interval == 0:
            for player in [p for p in self.players.values() if p.ncells > 0]:
                player.tokens += 1
        self.call_player_bots(it)
        evolve_board(
            self.board_old,
            self.board_new,
            self.xoff,
            self.yoff,
            self.neighbors,
            self.neighbor_buffer,
            self.cell_counts,
            config.nx,
            config.ny,
        )
        self.board_old[...] = self.board_new[...]
        for i, player in enumerate(self.players.values()):
            player.update(ncells=self.cell_counts[i])
        self.player_histories[:, it] = self.cell_counts
        self.player_tokens[...] = np.array([p.tokens for p in self.players.values()])

    def write_scores(self):
        histories = {
            name: self.player_histories[i] for i, name in enumerate(self.players)
        }
        finalize_scores(histories, test=self._test)

    def write_results(self, show_results: bool = False):
        results = {}
        fname = "results-" + time.strftime("%Y%m%d-%H%M%S") + ".npz"
        results["board"] = self.board_old
        for i, (name, player) in enumerate(self.players.items()):
            results[f"{name}_history"] = self.player_histories[i]
            results[f"{name}_color"] = player.color
        np.savez(fname, **results)
        plot(fname=fname.replace(".npz", ".pdf"), show=show_results, **results)
        return results

    def run(self, show_results: bool = False):
        for it in range(1, self.iterations + 1):
            # print(it)
            self.update(it)
        print(f"Reached {it} iterations.")
        self.write_scores()
        results = self.write_results(show_results)
        return results


class GraphicalEngine(Engine):

    def __init__(
        self,
        bots: dict,
        players: dict,
        iterations: int,
        buffers: dict,
        safe: bool = False,
        test: bool = True,
    ):
        self.niter = 0
        super().__init__(
            bots=bots,
            players=players,
            iterations=iterations,
            safe=safe,
            test=test,
            buffers={
                key: array_from_shared_mem(*value) for key, value in buffers.items()
            },
        )

    def run(self):
        while self.niter < self.iterations and not self.game_flow[1]:
            if self.game_flow[0]:
                self.niter += 1
                self.update(self.niter)
        print(f"Reached {self.niter} iterations.")
        self.write_scores()
        self.game_flow[1] = True
