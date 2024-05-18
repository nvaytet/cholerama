# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image


def find_empty_regions(
    board: np.ndarray, size: Union[int, Tuple[int, int]], skip: int = 4
) -> np.ndarray:
    """
    Find all empty regions of a given size in the board.

    Parameters:
    ----------
    board : numpy array
        The current state of the board.
    size : int or tuple
        The size of the region to search for.
    skip : int
        The step size for the sliding window. The larger the faster, but less accurate.

    Returns:
    -------
    numpy array
        The [y, x] indices of the bottom-left corner of each empty patch.
    """
    if isinstance(size, int):
        size = (size, size)
    view = sliding_window_view(board, size)[::skip, ::skip, ...]
    return np.argwhere(view.sum((2, 3)) == 0) * skip


def image_to_array(image_path: str) -> np.ndarray:
    """
    Convert an image to a numpy array. White color means 0.

    Parameters:
    ----------
    image_path : str
        The path to the image.

    Returns:
    -------
    numpy array
        The image as a numpy array.
    """
    im = Image.open(image_path).convert("RGB")
    a = np.array(im)
    s = (a - 255).sum(axis=-1)
    return np.clip(s, 0, 1)


@dataclass
class Positions:
    x: np.ndarray
    y: np.ndarray

    def __post_init__(self):
        if len(self.x) != len(self.y):
            raise ValueError("x and y must have the same length.")

    def __len__(self):
        return len(self.x)


def read_rle(fpath: str) -> Positions:
    with open(fpath) as f:
        lines = [line for line in f.readlines() if not line.startswith('#')]
    xs = []
    ys = []
    digits_next_repeat = ''
    x = 0
    y = 0
    # Skip one line containing bounding box
    for line in lines[1:]:
        for c in line:
            if c in '0123456789':
                digits_next_repeat += c
                continue
            if c in 'bo$':
                repeat = (
                    1 if digits_next_repeat == ''
                    else int(digits_next_repeat)
                )
                if c == 'b':
                    x += repeat 
                elif c == 'o':
                    for _ in range(repeat):
                        xs.append(x)
                        ys.append(y)
                        x += 1
                elif c == '$':
                    y += repeat
                    x = 0
                digits_next_repeat = ''
            if c == '!':
                return Positions(
                    x=np.array(xs, dtype='int'),
                    y=np.array(ys, dtype='int')
                )
    raise ValueError(f'{fpath} is not a well formatted rle file')
