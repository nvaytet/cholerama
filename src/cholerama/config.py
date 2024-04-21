# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    nx: int = 400
    ny: int = 400
    fps: int = 30
    iterations: int = 100
    pattern_size: int = 14


config = Config()
