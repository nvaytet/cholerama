# SPDX-License-Identifier: BSD-3-Clause


from .config import config
from .engine import Engine
from .graphics import GraphicalEngine
from .helpers import Positions
from .plot import load, plot


def play(*args, **kwargs):
    eng = GraphicalEngine(*args, **kwargs)
    eng.run()


def headless(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    eng.run()


__all__ = ["play", "headless", "config", "load", "plot", "Positions"]
