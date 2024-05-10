# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image


def find_empty_regions(
    board: np.ndarray, size: Union[int, Tuple[int, int]], skip: int = 2
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
