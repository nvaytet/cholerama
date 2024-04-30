# SPDX-License-Identifier: BSD-3-Clause


from .config import config
from .engine import Engine
from .graphics import GraphicalEngine
from .helpers import Positions
from .plot import load, plot


def play(plot_results, **kwargs):
    eng = GraphicalEngine(show_results=False, plot_results=plot_results, **kwargs)
    return eng.run()


def headless(plot_results, **kwargs):
    eng = Engine(show_results=plot_results, plot_results=True, **kwargs)
    return eng.run()


__all__ = ["play", "headless", "config", "load", "plot", "Positions"]
