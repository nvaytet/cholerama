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


def make_starting_positions(n) -> list:
    dmin = 0
    while dmin < (0.15 * (config.nx + config.ny) / 2):
        x = np.random.randint(0, config.nx - config.pattern_size[1], size=n)
        y = np.random.randint(0, config.ny - config.pattern_size[0], size=n)
        if n == 1:
            break
        x1 = np.broadcast_to(x, (n, n))
        x2 = x1.T
        y1 = np.broadcast_to(y, (n, n))
        y2 = y1.T
        dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        dmin = dist[dist > 0].min()
    #     print(dmin)

    # bound = max(config.pattern_size)
    # x = np.random.randint(bound, config.nx - bound, size=nplayers)
    # y = np.random.randint(bound, config.ny - bound, size=nplayers)
    return list(zip(x, y))
