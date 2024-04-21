# SPDX-License-Identifier: BSD-3-Clause

import numpy as np


from . import config


class Player:
    def __init__(self, name: str, number: int, pattern: np.ndarray):
        self.name = name
        self.number = number
        self.ncells = np.sum(pattern > 0)
        self.cell_history = []

    def update(self, board: np.ndarray):
        self.ncells = np.sum(board == self.number)
        self.cell_history.append(self.ncells)
        print(self.name, self.ncells)

    # @property
    # def coverage(self):
    #     return self.ncells / (config.nx * config.ny)
