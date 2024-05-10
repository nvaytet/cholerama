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
from .tools import make_color, array_from_shared_mem


class Engine:
    def __init__(
        self,
        bots: dict,
        players: dict,
        iterations: int,
        safe: bool,
        test: bool,
        buffers,
    ):
        self.niter = 0
        self.bots = bots
        self.players = players
        self.buffers = {
            key: array_from_shared_mem(*value) for key, value in buffers.items()
        }

        self.board_old = self.buffers["board_old"]
        self.board_new = self.buffers["board_new"]
        self.player_histories = self.buffers["player_histories"]
        self.player_tokens = self.buffers["player_tokens"]
        self.game_flow = self.buffers["game_flow"]
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

    def run(self):
        while self.niter < self.iterations and not self.game_flow[1]:
            if self.game_flow[0]:
                self.niter += 1
                self.update(self.niter)
        print(f"Reached {self.niter} iterations.")
        histories = {
            name: self.player_histories[i] for i, name in enumerate(self.players)
        }
        finalize_scores(histories, test=self._test)
        self.game_flow[1] = True
