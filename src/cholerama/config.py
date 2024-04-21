# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    nx: int = 512
    ny: int = 512
    fps: int = 30
    iterations: int = 1000


config = Config()
