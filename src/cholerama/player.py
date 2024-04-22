# SPDX-License-Identifier: BSD-3-Clause

from typing import Union

from PIL import Image
import numpy as np


from . import config


class Player:
    def __init__(
        self, name: str, number: int, color: str, pattern: Union[np.ndarray, str]
    ):
        self.name = name
        self.number = number
        self.score = 0
        self.color = color

        if isinstance(pattern, str):
            im = Image.open(pattern).convert("RGB")
            a = np.array(im)
            s = (a - 255).sum(axis=-1)
            self.pattern = np.clip(s, 0, 1)
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
        # self.history.append(self.ncells)
        # print(self.name, self.ncells)

    # @property
    # def coverage(self):
    #     return self.ncells / (config.nx * config.ny)
