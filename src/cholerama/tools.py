# SPDX-License-Identifier: BSD-3-Clause

from multiprocessing.shared_memory import SharedMemory
from typing import Tuple, Union

import matplotlib.colors as mcolors
import numpy as np
from matplotlib import colormaps

from . import config


def array_from_shared_mem(
    shared_mem: SharedMemory,
    shared_data_dtype: np.dtype,
    shared_data_shape: Tuple[int, ...],
) -> np.ndarray:
    arr = np.frombuffer(shared_mem.buf, dtype=shared_data_dtype)
    arr = arr.reshape(shared_data_shape)
    return arr


def make_color(c: Union[int, str]) -> str:
    tab20 = colormaps["tab20"]
    color_list = [tab20(i * 2) for i in range(10)] + [
        tab20(i * 2 + 1) for i in range(10)
    ]
    if isinstance(c, int):
        c = color_list[c % len(color_list)]
    return mcolors.to_hex(c)


def make_starting_positions(n) -> list:
    # possible starting row and column as tuples
    stepx = config.nx // config.npatches[1]
    stepy = config.ny // config.npatches[0]
    inds = [
        (i * stepx, j * stepy)
        for i in range(config.npatches[0])
        for j in range(config.npatches[1])
    ]
    return np.random.choice(inds, size=n, replace=False).tolist()

    # dmin = 0
    # while dmin < (0.15 * (config.nx + config.ny) / 2):
    #     x = np.random.randint(0, config.nx - config.pattern_size[1], size=n)
    #     y = np.random.randint(0, config.ny - config.pattern_size[0], size=n)
    #     if n == 1:
    #         break
    #     x1 = np.broadcast_to(x, (n, n))
    #     x2 = x1.T
    #     y1 = np.broadcast_to(y, (n, n))
    #     y2 = y1.T
    #     dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    #     dmin = dist[dist > 0].min()
    # return list(zip(x, y))
