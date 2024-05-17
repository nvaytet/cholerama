# SPDX-License-Identifier: BSD-3-Clause

from typing import Union

import numpy as np

from . import config
from .helpers import Positions, image_to_array


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
        self.patch_bounds = {
            "xmin": patch[1] * patch_size[1],
            "xmax": (patch[1] + 1) * patch_size[1],
            "ymin": patch[0] * patch_size[0],
            "ymax": (patch[0] + 1) * patch_size[0],
        }
        self.ncells = len(self.pattern)
        self.tokens = config.initial_tokens - self.ncells
        self.history = []

    def update(self, ncells: int):
        self.ncells = ncells
