# SPDX-License-Identifier: BSD-3-Clause

from typing import Union, Tuple

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image


def find_empty_patches(
    board: np.ndarray, patch_size: Union[int, Tuple[int, int]], skip: int = 8
) -> np.ndarray:
    """
    Find all empty patches of a given size in the board.

    Parameters:
    ----------
    board : numpy array
        The current state of the board.
    patch_size : int or tuple
        The size of the patch to search for.
    skip : int
        The step size for the sliding window. The larger the faster, but less accurate.

    Returns:
    -------
    numpy array
        The [y, x] indices of the bottom-left corner of each empty patch.
    """
    # valid = board == 0
    if isinstance(patch_size, int):
        patch_size = (patch_size, patch_size)
    # return np.argwhere(sliding_window_view(valid, patch_size).all(axis=(-2, -1)))
    view = sliding_window_view(board, patch_size)[::skip, ::skip, ...]
    # yy, xx = np.where(view.sum((2, 3)) == 0)
    # yy*skip, xx*skip
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
