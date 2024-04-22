# SPDX-License-Identifier: BSD-3-Clause

import datetime
import time
from typing import Any, Dict, Optional

import numpy as np


from . import config
from .player import Player


class Engine:
    def __init__(
        self,
        bots: list,
        iterations: int = 100,
        safe: bool = False,
        test: bool = True,
        seed: Optional[int] = None,
        fps: Optional[int] = 10,
    ):
        if seed is not None:
            np.random.seed(seed)

        self.iterations = iterations
        self._test = test
        self.safe = safe
        self.fps = fps

        self.board = np.zeros((config.ny, config.nx), dtype=int)

        self.bots = {bot.name: bot for bot in bots}
        starting_positions = self.make_starting_positions()
        self.players = {}
        self.player_histories = np.zeros((len(self.bots), self.iterations))
        for i, (bot, pos) in enumerate(zip(self.bots.values(), starting_positions)):
            player = Player(name=bot.name, number=i + 1, pattern=bot.pattern)
            p = player.pattern
            self.board[pos[1] : pos[1] + p.shape[0], pos[0] : pos[0] + p.shape[1]] = (
                p * (i + 1)
            )
            self.players[bot.name] = player
            self.player_histories[i, 0] = player.ncells

        # self.player_histories = np.zeros((len(self.players), config.iterations))

        self.xoff = [-1, 0, 1, -1, 1, -1, 0, 1]
        self.yoff = [-1, -1, -1, 0, 0, 1, 1, 1]
        self.xinds = np.empty((8,) + self.board.shape, dtype=int)
        self.yinds = np.empty_like(self.xinds)

        for i, (xo, yo) in enumerate(zip(self.xoff, self.yoff)):
            g = np.meshgrid(
                (np.arange(config.nx) + xo) % config.nx,
                (np.arange(config.ny) + yo) % config.ny,
                indexing="xy",
            )
            self.xinds[i, ...] = g[0]
            self.yinds[i, ...] = g[1]

    def make_starting_positions(self) -> list:
        bound = max(config.pattern_size)
        x = np.random.randint(bound, config.nx - bound, size=len(self.bots))
        y = np.random.randint(bound, config.ny - bound, size=len(self.bots))
        return list(zip(x, y))

    # def execute_player_bot(self, player, t: float, dt: float):
    #     instructions = None
    #     args = {
    #         "t": t,
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

    # def call_player_bots(self, t: float, dt: float):
    #     for player in [p for p in self.players.values() if not p.arrived]:
    #         if self.safe:
    #             try:
    #                 player.execute_bot_instructions(
    #                     self.execute_player_bot(player=player, t=t, dt=dt)
    #                 )
    #             except:  # noqa
    #                 pass
    #         else:
    #             player.execute_bot_instructions(
    #                 self.execute_player_bot(player=player, t=t, dt=dt)
    #             )

    def evolve_board(self):
        neighbors = self.board[self.yinds, self.xinds]
        neighbor_count = np.clip(neighbors, 0, 1).sum(axis=0)
        # self.board = np.where(neighbor_count > 0, 1, self.board)

        # birth_values = np.nan_to_num(
        #     np.nanmedian(np.where(neighbors == 0, np.nan, neighbors), axis=0),
        #     copy=False,
        # ).astype(int)

        #

        alive_mask = self.board > 0
        alive_neighbor_count = np.where(alive_mask, neighbor_count, 0)
        # Apply rules
        new = np.where(
            (alive_neighbor_count == 2) | (alive_neighbor_count == 3), self.board, 0
        )

        # Birth happens always when we have 3 neighbors. The most common value will
        # always be in position 7.
        birth_mask = ~alive_mask & (neighbor_count == 3)
        birth_values = np.sort(neighbors, axis=0)[-2]
        self.board = np.where(birth_mask, birth_values, new)

    def shutdown(self):
        self.update_scoreboard()
        write_times({team: p.trip_time for team, p in self.players.items()})
        self.buffers["all_shutdown"][self.pid] = True

    def update(self, it: int):
        self.evolve_board()
        for i, player in enumerate(self.players.values()):
            player.update(self.board)
            self.player_histories[i, it] = player.ncells
            # player.ncells = np.sum(self.board == player.number)

    def run(self):
        # self.initialize_time(start_time)
        pause = 1 / self.fps if self.fps is not None else None
        for it in range(self.iterations):
            print(it)
            self.update(it)
            if pause is not None:
                time.sleep(pause)
        self.shutdown()
