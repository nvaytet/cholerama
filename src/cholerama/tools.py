# SPDX-License-Identifier: BSD-3-Clause

from typing import Union

import matplotlib.colors as mcolors
import numpy as np
from matplotlib import colormaps

from . import config


def make_color(c: Union[int, str]) -> str:
    tab20 = colormaps["tab20"]
    color_list = [tab20(i * 2) for i in range(10)] + [
        tab20(i * 2 + 1) for i in range(10)
    ]
    if isinstance(c, int):
        c = color_list[c % len(color_list)]
    return mcolors.to_hex(c)


def make_starting_positions(nplayers) -> list:
    bound = max(config.pattern_size)
    x = np.random.randint(bound, config.nx - bound, size=nplayers)
    y = np.random.randint(bound, config.ny - bound, size=nplayers)
    return list(zip(x, y))
