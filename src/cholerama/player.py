# SPDX-License-Identifier: BSD-3-Clause

from typing import Union

import numpy as np

from . import config
from .helpers import image_to_array


class Player:
    def __init__(
        self, name: str, number: int, color: str, pattern: Union[np.ndarray, str]
    ):
        self.name = name
        self.number = number
        self.color = color
        self.tokens = 0
        self.peak = 0

        if isinstance(pattern, str):
            self.pattern = image_to_array(pattern)
        else:
            self.pattern = np.asarray(pattern)

        if any(np.array(self.pattern.shape) > np.array(config.pattern_size)):
            raise ValueError(
                f"Pattern must be contained in size {config.pattern_size}. "
                f"Got {self.pattern.shape}."
            )

        self.ncells = np.sum(self.pattern > 0)
        self.history = []

    def update(self, board: np.ndarray):
        self.ncells = np.sum(board == self.number)
