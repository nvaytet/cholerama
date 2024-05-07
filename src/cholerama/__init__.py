# SPDX-License-Identifier: BSD-3-Clause


from .config import config
from .engine import Engine

# from .graphics import GraphicalEngine
from .helpers import Positions
from .main import play
from .plot import load, plot


# def play(**kwargs):
#     eng = GraphicalEngine(**kwargs)
#     return eng.run()


def headless(**kwargs):
    eng = Engine(**kwargs)
    return eng.run()


__all__ = ["play", "headless", "config", "load", "plot", "Positions"]
