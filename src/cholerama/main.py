# SPDX-License-Identifier: BSD-3-Clause

import time
from multiprocessing import Process
from multiprocessing.managers import SharedMemoryManager


import numpy as np


from . import config
from .engine import Engine
from .graphics import Graphics

from .player import Player
from .plot import plot
from .tools import array_from_shared_mem, make_starting_positions, make_color


def spawn_graphics(*args):
    graphics = Graphics(*args)
    graphics.run()


def spawn_engine(*args):
    engine = Engine(*args)
    engine.run()


def play(
    bots, iterations, seed=None, fps=None, safe=False, test=True, show_results=False
):

    rng = np.random.default_rng(seed)

    board_old = np.zeros((config.ny, config.nx), dtype=int)
    board_new = board_old.copy()
    player_histories = np.zeros((len(bots), iterations + 1), dtype=int)
    player_tokens = np.zeros(len(bots), dtype=int)

    starting_patches = make_starting_positions(len(bots), rng)
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

    game_flow = np.zeros(2, dtype=bool)  # pause, exit
    buffer_mapping = {
        "board_old": board_old,
        "board_new": board_new,
        "player_histories": player_histories,
        "player_tokens": player_tokens,
        "game_flow": game_flow,
    }

    results = {"board": board_old}
    results.update(
        {f"{name}_history": player_histories[i] for i, name in enumerate(players)}
    )
    results.update({f"{name}_color": player.color for name, player in players.items()})

    shared_arrays = {}

    with SharedMemoryManager() as smm:

        buffers = {}
        for key, arr in buffer_mapping.items():
            mem = smm.SharedMemory(size=arr.nbytes)
            shared_arrays[key] = array_from_shared_mem(mem, arr.dtype, arr.shape)
            shared_arrays[key][...] = arr
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

        engine = Process(
            target=spawn_engine,
            args=(
                dict_of_bots,
                players,
                iterations,
                safe,
                test,
                buffers,
            ),
        )

        graphics.start()
        engine.start()
        graphics.join()
        engine.join()

        fname = "results-" + time.strftime("%Y%m%d-%H%M%S") + ".npz"
        results["board"][...] = shared_arrays["board_old"][...]
        for i, name in enumerate(players):
            results[f"{name}_history"][...] = shared_arrays["player_histories"][i][...]

    np.savez(fname, **results)
    plot(fname=fname.replace(".npz", ".pdf"), show=show_results, **results)
    return results
