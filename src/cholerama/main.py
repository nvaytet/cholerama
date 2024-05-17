# SPDX-License-Identifier: BSD-3-Clause

import time
from multiprocessing import Process
from multiprocessing.managers import SharedMemoryManager

import numpy as np

from .engine import GraphicalEngine, setup
from .graphics import Graphics
from .plot import plot
from .tools import array_from_shared_mem


def spawn_graphics(*args):
    graphics = Graphics(*args)
    graphics.run()


def spawn_engine(*args):
    engine = GraphicalEngine(*args)
    engine.run()


def play(
    bots, iterations, seed=None, fps=None, safe=False, test=True, show_results=False
):
    buffers, players, dict_of_bots = setup(bots=bots, iterations=iterations, seed=seed)
    results = {"board": buffers["board_old"]}
    results.update(
        {
            f"{name}_history": buffers["player_histories"][i]
            for i, name in enumerate(players)
        }
    )
    results.update({f"{name}_color": player.color for name, player in players.items()})

    shared_arrays = {}
    with SharedMemoryManager() as smm:
        shared_buffers = {}
        for key, arr in buffers.items():
            mem = smm.SharedMemory(size=arr.nbytes)
            shared_arrays[key] = array_from_shared_mem(mem, arr.dtype, arr.shape)
            shared_arrays[key][...] = arr
            shared_buffers[key] = (mem, arr.dtype, arr.shape)

        graphics = Process(
            target=spawn_graphics,
            args=(
                players,
                30,
                test,
                shared_buffers,
            ),
        )

        engine = Process(
            target=spawn_engine,
            args=(
                dict_of_bots,
                players,
                iterations,
                shared_buffers,
                fps,
                safe,
                test,
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
