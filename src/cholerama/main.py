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
from .scores import read_round
from .tools import array_from_shared_mem, make_starting_positions, make_color


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


def play(bots, iterations, seed=None, fps=None, safe=False, test=True, ncores=8):

    # self.iterations = iterations
    # self._test = test
    # self.safe = safe
    # self._show_results = show_results
    # self.token_interval = max(1, iterations // config.additional_tokens)
    n_sub_processes = max(ncores - 1, 1)
    rounds_played = 0 if test else read_round()

    board_old = np.zeros((config.ny, config.nx), dtype=int)
    board_new = board_old.copy()
    player_histories = np.zeros((len(bots), iterations + 1), dtype=int)

    # Divide the board into as many patches as there are players, and try to make the
    # patches as square as possible

    # # decompose number of players into prime numbers
    # nplayers = len(bots)
    # factors = []
    # for i in range(2, nplayers + 1):
    #     while nplayers % i == 0:
    #         factors.append(i)
    #         nplayers //= i
    # # now group the factors into 2 groups because the board is 2D. Try to make the
    # # groups as close to each other in size as possible, when multiplied together
    # group1 = []
    # group2 = []
    # for f in factors:
    #     if np.prod(group1) < np.prod(group2):
    #         group1.append(f)
    #     else:
    #         group2.append(f)

    # # starting_positions = make_starting_positions(len(bots))
    starting_positions = np.full((len(bots), 2), 100, dtype=int)

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
    players = {}
    # self.player_histories = np.zeros((len(self.bots), self.iterations + 1), dtype=int)
    for i, (bot, pos) in enumerate(zip(dict_of_bots.values(), starting_positions)):
        player = Player(
            name=bot.name,
            number=i + 1,
            pattern=bot.pattern,
            color=make_color(i if bot.color is None else bot.color),
        )
        p = player.pattern
        board_old[pos[1] : pos[1] + p.shape[0], pos[0] : pos[0] + p.shape[1]] = p * (
            i + 1
        )
        players[bot.name] = player
        player_histories[i, 0] = player.ncells

    # # starting_positions = make_starting_positions(len(self.bots))

    groups = np.array_split(list(bots.keys()), n_sub_processes)

    # Split the board along the x dimension into n_sub_processes
    board_ind_start = np.linspace(0, config.ny, n_sub_processes + 1, dtype=int)
    game_flow = np.zeros(n_sub_processes, dtype=bool)  # pause, exit_from_graphics

    print("groups:", groups)
    print("board_ind_start:", board_ind_start)

    buffer_mapping = {
        "board_old": board_old,
        "board_new": board_new,
        "player_histories": player_histories,
        "game_flow": game_flow,
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
                fps,
                test,
                buffers,
            ),
        )

        engines = []
        # bot_index_begin = 0
        for i, group in enumerate(groups):
            engines.append(
                Process(
                    target=spawn_engine,
                    args=(
                        i,
                        board_ind_start[i],
                        board_ind_start[i + 1],
                        {name: bots[name] for name in group},
                        {name: players[name] for name in group},
                        iterations,
                        safe,
                        test,
                        seed,
                        buffers,
                    ),
                )
            )
            # bot_index_begin += len(group)

        graphics.start()
        for engine in engines:
            engine.start()
        graphics.join()
        for engine in engines:
            engine.join()
