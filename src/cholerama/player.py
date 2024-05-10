# SPDX-License-Identifier: BSD-3-Clause

from typing import Union

import numpy as np

from . import config
from .helpers import image_to_array, Positions


class Player:
    def __init__(
        self, name: str, number: int, color: str, pattern: Union[np.ndarray, str], patch
    ):
        self.name = name
        self.number = number
        self.color = color
        self.peak = 0
        self.patch = patch

        self.pattern = pattern
        if isinstance(self.pattern, str):
            array = image_to_array(self.pattern)
            xy = np.where(array > 0)
            self.pattern = Positions(x=xy[1], y=xy[0])
        if not isinstance(self.pattern, Positions):
            raise ValueError("Pattern must be an instance of Positions.")

        if len(self.pattern) > config.initial_tokens:
            raise ValueError(
                f"Too many tokens used in pattern by Player {self.name}: "
                f"{len(self.pattern)} > {config.initial_tokens}."
            )

        patch_size = (config.nx // config.npatches[1], config.ny // config.npatches[0])
        if (
            (self.pattern.x.min() < 0)
            or (self.pattern.x.max() >= patch_size[1])
            or (self.pattern.y.min() < 0)
            or (self.pattern.y.max() >= patch_size[0])
        ):
            raise ValueError(
                f"Pattern indices must be positive and contained in size {patch_size}. "
            )

        # if any(np.array(self.pattern.shape) > np.array(config.pattern_size)):
        #     raise ValueError(
        #         f"Pattern must be contained in size {config.pattern_size}. "
        #         f"Got {self.pattern.shape}."
        #     )

        self.ncells = len(self.pattern)
        # if psum > config.initial_tokens:
        #     raise ValueError(
        #         f"Player {self.name}: pattern has more than "
        #         f"{config.initial_tokens} tokens."
        #     )

        self.tokens = config.initial_tokens - self.ncells
        # self.ncells = np.sum(self.pattern > 0)
        self.history = []

    # def update(self, board: np.ndarray):
    #     self.ncells = np.sum(board == self.number)
    def update(self, ncells: int):
        self.ncells = ncells
