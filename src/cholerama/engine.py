# SPDX-License-Identifier: BSD-3-Clause

import datetime
import time
from typing import Any, Dict, Optional

import numpy as np


from . import config


class Engine:
    def __init__(
        self,
        bots: list,
        safe: bool = False,
        test: bool = True,
        seed: Optional[int] = None,
        fps: Optional[int] = 10,
    ):
        if seed is not None:
            np.random.seed(seed)

        self.start_time = None
        self._test = test
        self.asteroids = []
        self.safe = safe
        self.exiting = False
        self.fps = fps

        self.board = np.zeros((config.ny, config.nx), dtype=int)

        pattern2 = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
        # pattern2 = np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
        self.board[50:53, 50:53] = pattern2

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
        birth_values = np.nan_to_num(
            np.nanmedian(np.where(neighbors == 0, np.nan, neighbors), axis=0),
            copy=False,
        ).astype(int)

        alive_mask = self.board > 0
        alive_neighbor_count = np.where(alive_mask, neighbor_count, 0)
        # Apply rules
        new = np.where(
            (alive_neighbor_count == 2) | (alive_neighbor_count == 3), self.board, 0
        )
        birth_mask = ~alive_mask & (neighbor_count == 3)
        # out[birth_mask] = 1
        self.board = np.where(birth_mask, birth_values, new)

    def shutdown(self):
        self.update_scoreboard()
        write_times({team: p.trip_time for team, p in self.players.items()})
        self.buffers["all_shutdown"][self.pid] = True

    def update(self, it: int):
        self.evolve_board()

    def update_scoreboard(self):

        for i, player in enumerate(self.players.values()):
            self.buffers["player_status"][self.bot_index_begin + i, ...] = np.array(
                [
                    get_player_points(player),
                    player.distance_travelled,
                    player.speed,
                    len([ch for ch in player.checkpoints if ch.reached]),
                ],
                dtype=float,
            )

    def run(self):
        # self.initialize_time(start_time)
        pause = 1 / self.fps if self.fps is not None else None
        for it in config.iterations:
            self.update(it)
            if pause is not None:
                time.sleep(pause)
        self.shutdown()
