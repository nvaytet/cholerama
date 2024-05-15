# SPDX-License-Identifier: BSD-3-Clause


from .config import config
from .engine import Engine, setup

# from .graphics import GraphicalEngine
from .helpers import Positions
from .main import play
from .plot import load, plot


# def play(**kwargs):
#     eng = GraphicalEngine(**kwargs)
#     return eng.run()


def headless(*, bots, iterations, seed=None, show_results=False, **kwargs):
    buffers, players, dict_of_bots = setup(bots=bots, iterations=iterations, seed=seed)
    eng = Engine(
        bots=dict_of_bots,
        players=players,
        iterations=iterations,
        buffers=buffers,
        **kwargs,
    )
    return eng.run(show_results)


__all__ = ["play", "headless", "config", "load", "plot", "Positions"]
