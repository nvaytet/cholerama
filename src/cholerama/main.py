# SPDX-License-Identifier: BSD-3-Clause

import time
from multiprocessing import Process
from multiprocessing.managers import SharedMemoryManager


import numpy as np


from . import config
from .engine import Engine
from .graphics import Graphics

# from .map import MapData
from .player import Player
from .tools import array_from_shared_mem


# class Clock:
#     def __init__(self):
#         self._start_time = None

#     @property
#     def start_time(self):
#         if self._start_time is None:
#             self._start_time = time.time()
#         return self._start_time


# clock = Clock()


def spawn_graphics(*args):
    graphics = Graphics(*args)
    graphics.run()


def spawn_engine(*args):
    engine = Engine(*args)
    engine.run()


def play(bots, iterations, seed=None, start=None, safe=False, ncores=8, test=True):

    # self.iterations = iterations
    # self._test = test
    # self.safe = safe
    # self._show_results = show_results
    # self.token_interval = max(1, iterations // config.additional_tokens)
    n_sub_processes = max(ncores - 1, 1)
    rounds_played = 0 if test else read_round()

    board_old = np.zeros((config.ny, config.nx), dtype=int)
    board_new = board_old.copy()

    starting_positions = make_starting_positions(len(bots))

    if isinstance(bots, dict):
        dict_of_bots = {
            name: bot.Bot(number=i + 1, name=name, x=pos[0], y=pos[1])
            for i, ((name, bot), pos) in enumerate(
                zip(bots.items(), starting_positions)
            )
        }
    else:
        dict_of_bots = {
            bot.AUTHOR: bot.Bot(number=i + 1, name=bot.AUTHOR, x=pos[0], y=pos[1])
            for i, (bot, pos) in enumerate(zip(bots, starting_positions))
        }

    # starting_positions = make_starting_positions(len(self.bots))

    groups = np.array_split(list(bots.keys()), n_sub_processes)

    # Split the board along the x dimension into n_sub_processes
    board_ind_start = np.linspace(0, config.nx, n_sub_processes + 1, dtype=int)
    player_histories = np.zeros((len(bots), iterations + 1), dtype=int)

    buffer_mapping = {
        "board_old": board_old,
        "board_new": board_new,
    }

    with SharedMemoryManager() as smm:

        buffers = {}
        for key, arr in buffer_mapping.items():
            mem = smm.SharedMemory(size=arr.nbytes)
            arr_shared = array_from_shared_mem(mem, arr.dtype, arr.shape)
            arr_shared[...] = arr
            buffers[key] = (mem, arr.dtype, arr.shape)

        graphics = Process(
            target=spawn_graphics,
            args=(
                players,
                high_contrast,
                {
                    key: buffers[key]
                    for key in (
                        "tracer_positions",
                        "player_positions",
                        "game_flow",
                        "player_status",
                        "all_arrived",
                        "all_shutdown",
                    )
                },
            ),
        )

        engines = []
        bot_index_begin = 0
        for i, group in enumerate(groups):
            engines.append(
                Process(
                    target=spawn_engine,
                    args=(
                        i,
                        seed,
                        {name: bots[name] for name in group},
                        {name: players[name] for name in group},
                        bot_index_begin,
                        buffers,
                        safe,
                        world_map,
                    ),
                )
            )
            bot_index_begin += len(group)

        graphics.start()
        for engine in engines:
            engine.start()
        graphics.join()
        for engine in engines:
            engine.join()
