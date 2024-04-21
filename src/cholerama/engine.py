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
    ):
        if seed is not None:
            np.random.seed(seed)

        self.nx = config.nx
        self.ny = config.ny
        self.start_time = None
        self._test = test
        self.asteroids = []
        self.safe = safe
        self.exiting = False

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
        neighbors = board[yinds, xinds]
        neighbor_count = np.clip(neighbors, 0, 1).sum(axis=0)
        birth_values = np.nan_to_num(
            np.nanmedian(np.where(neighbors == 0, np.nan, neighbors), axis=0),
            copy=False,
        ).astype(int)

        alive_mask = board > 0
        alive_neighbor_count = np.where(alive_mask, neighbor_count, 0)
        # Apply rules
        out = np.where(
            (alive_neighbor_count == 2) | (alive_neighbor_count == 3), board, 0
        )
        birth_mask = ~alive_mask & (neighbor_count == 3)
        # out[birth_mask] = 1
        out = np.where(birth_mask, birth_values, out)
        return out

    def shutdown(self):
        self.update_scoreboard()
        write_times({team: p.trip_time for team, p in self.players.items()})
        self.buffers["all_shutdown"][self.pid] = True

    def update(self):

        clock_time = time.time()
        t = clock_time - self.start_time
        dt = clock_time - self.previous_clock_time

        if dt > self.update_interval:
            dt = dt * config.seconds_to_hours

            if (clock_time - self.last_time_update) > config.time_update_interval:
                self.update_scoreboard()
                self.last_time_update = clock_time

            if (
                clock_time - self.last_forecast_update
            ) > config.weather_update_interval:
                self.forecast = self.weather.get_forecast(t)
                self.last_forecast_update = clock_time

            self.call_player_bots(t=t * config.seconds_to_hours, dt=dt)
            self.move_players(self.weather, t=t, dt=dt)
            self.weather.update_wind_tracers(t=np.array([t]), dt=dt)

            if len(self.players_not_arrived) == 0:
                self.buffers["all_arrived"][self.pid] = True
                self.update_scoreboard()

            self.previous_clock_time = clock_time

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

    def run(self, start_time: float):
        self.initialize_time(start_time)
        while not self.buffers["game_flow"][1]:
            self.update()
        self.shutdown()
