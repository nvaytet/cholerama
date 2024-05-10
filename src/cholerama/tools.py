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


def make_starting_positions(n, rng) -> list:
    # Possible starting row and column as tuples
    inds = [
        (j, i) for j in range(config.npatches[0]) for i in range(config.npatches[1])
    ]
    choices = rng.choice(range(len(inds)), size=n, replace=False)
    return [inds[i] for i in choices]
