# SPDX-License-Identifier: BSD-3-Clause

import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
import matplotlib.colors as mcolors
from numba import set_num_threads


from . import config
from .compute import evolve_board
from .player import Player
from .plot import plot
from .tools import make_color


class Engine:
    def __init__(
        self,
        bots: list,
        iterations: int = 100,
        safe: bool = False,
        test: bool = True,
        seed: Optional[int] = None,
        plot_results: bool = False,
        # fps: Optional[int] = 10,
    ):
        set_num_threads(14)
        if seed is not None:
            np.random.seed(seed)

        self.iterations = iterations
        self._test = test
        self.safe = safe
        self.plot_results = plot_results
        self.token_interval = max(1, iterations // config.tokens_per_game)
        print("self.token_interval", self.token_interval)
        # self.fps = fps

        self.board = np.zeros((config.ny, config.nx), dtype=int)
        self.new_board = self.board.copy()

        self.bots = {bot.name: bot for bot in bots}
        starting_positions = self.make_starting_positions()
        self.players = {}
        self.player_histories = np.zeros((len(self.bots), self.iterations + 1))
        for i, (bot, pos) in enumerate(zip(self.bots.values(), starting_positions)):
            player = Player(
                name=bot.name,
                number=i + 1,
                pattern=bot.pattern,
                color=make_color(i if bot.color is None else bot.color),
            )
            p = player.pattern
            self.board[pos[1] : pos[1] + p.shape[0], pos[0] : pos[0] + p.shape[1]] = (
                p * (i + 1)
            )
            self.players[bot.name] = player
            self.player_histories[i, 0] = player.ncells

        # self.player_histories = np.zeros((len(self.players), config.iterations))

        self.xoff = np.array([-1, 0, 1, -1, 1, -1, 0, 1])
        self.yoff = np.array([-1, -1, -1, 0, 0, 1, 1, 1])
        self.neighbors = np.zeros(8, dtype=int)
        self.xinds = np.empty((8,) + self.board.shape, dtype=int)
        self.yinds = np.empty_like(self.xinds)
        self.neighbor_buffer = np.zeros(3, dtype=int)

        for i, (xo, yo) in enumerate(zip(self.xoff, self.yoff)):
            g = np.meshgrid(
                (np.arange(config.nx) + xo) % config.nx,
                (np.arange(config.ny) + yo) % config.ny,
                indexing="xy",
            )
            self.xinds[i, ...] = g[0]
            self.yinds[i, ...] = g[1]

        # Pre-compile numba function
        evolve_board(
            self.board,
            self.new_board,
            self.xoff,
            self.yoff,
            self.neighbors,
            self.neighbor_buffer,
            config.nx,
            config.ny,
        )

    def make_starting_positions(self) -> list:
        bound = max(config.pattern_size)
        x = np.random.randint(bound, config.nx - bound, size=len(self.bots))
        y = np.random.randint(bound, config.ny - bound, size=len(self.bots))
        return list(zip(x, y))

    # def execute_player_bot(self, player, t: float, dt: float):
    #     instructions = None
    #     args = {
    #         "iteration": t,
    #         "dt": dt,
    #         "longitude": player.longitude,
    #         "latitude": player.latitude,
    #         "heading": player.heading,
    #         "speed": player.speed,
    #         "vector": player.get_vector(),
    #         "forecast": self.forecast,
    #         "map": self.map_proxy,
    #     }
    #     if self.safe:
    #         try:
    #             instructions = self.bots[player.team].run(**args)
    #         except:  # noqa
    #             pass
    #     else:
    #         instructions = self.bots[player.team].run(**args)
    #     return instructions

    def add_player_new_cells(
        self, player: Player, new_cells: Tuple[np.ndarray, np.ndarray]
    ):
        x, y = new_cells
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
        x = np.asarray(x) % config.nx
        y = np.asarray(y) % config.ny
        if self.board[y, x].sum() > 0:
            print(f"Player {player.name}: cannot overwrite alive cells.")
            ok = False
        if ok:
            self.board[y, x] = player.number
            player.tokens -= ntok

    def call_player_bots(self, it: int):
        # TODO: Roll the order of players for each round
        for name, player in ((n, p) for n, p in self.players.items() if p.ncells > 0):
            self.board.setflags(write=False)
            new_cells = None
            args = {
                "iteration": int(it),
                "board": self.board,
                "tokens": int(player.tokens),
            }
            if self.safe:
                try:
                    new_cells = self.bots[name].run(**args)
                except:  # noqa
                    pass
            else:
                new_cells = self.bots[name].run(**args)
            self.board.setflags(write=True)
            if new_cells:
                self.add_player_new_cells(player, new_cells)

    def evolve_board(self):
        neighbors = self.board[self.yinds, self.xinds]
        neighbor_count = np.where(neighbors > 0, 1, 0).sum(axis=0)
        # neighbor_count = np.clip(neighbors, 0, 1).sum(axis=0)

        alive_mask = self.board > 0
        alive_neighbor_count = np.where(alive_mask, neighbor_count, 0)

        # # Apply rules
        # new = np.where(
        #     (alive_neighbor_count == 2) | (alive_neighbor_count == 3), self.board, 0
        # )

        # birth_mask = ~alive_mask & (neighbor_count == 3)
        # # # Birth happens always when we have 3 neighbors. When sorted, the most common
        # # # value will always be in position 7 (=-2).
        # birth_values = np.sort(neighbors, axis=0)[-2]
        # self.board = np.where(birth_mask, birth_values, new)

        # Apply rules
        self.board = np.where(
            (alive_neighbor_count == 2) | (alive_neighbor_count == 3), self.board, 0
        )

        birth_mask = ~alive_mask & (neighbor_count == 3)
        # Birth happens always when we have 3 neighbors. When sorted, the most common
        # value will always be in position 7 (=-2).
        birth_inds = np.where(birth_mask)
        birth_values = np.sort(neighbors[:, birth_inds[0], birth_inds[1]], axis=0)[-2]
        self.board[birth_inds[0], birth_inds[1]] = birth_values

    def show_results(self, fname: str):
        if self.plot_results:
            fig, _ = plot(self.board, self.player_histories)
            fig.savefig(fname)

    def shutdown(self):
        fname = "results-" + time.strftime("%Y%m%d-%H%M%S") + ".npz"
        np.savez(fname, board=self.board, history=self.player_histories)
        self.show_results(fname.replace(".npz", ".pdf"))
        # if self.plot_results:
        #     fig, _ = plot(self.board, self.player_histories)
        #     fig.savefig(fname.replace(".npz", ".pdf"))

    def update(self, it: int):
        if it % self.token_interval == 0:
            for player in self.players.values():
                player.tokens += 1
        self.call_player_bots(it)
        # self.evolve_board()
        evolve_board(
            self.board,
            self.new_board,
            self.xoff,
            self.yoff,
            self.neighbors,
            self.neighbor_buffer,
            config.nx,
            config.ny,
        )
        self.board, self.new_board = self.new_board, self.board
        for i, player in enumerate(self.players.values()):
            player.update(self.board)
            self.player_histories[i, it] = player.ncells
            # player.ncells = np.sum(self.board == player.number)

    def run(self):
        # self.initialize_time(start_time)
        for it in range(1, self.iterations + 1):
            self.update(it)
        print(f"Reached {it} iterations.")
        self.shutdown()
