# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Config:
    nx: int = 500
    ny: int = 400
    pattern_size: Tuple[int] = (18, 36)
    max_name_length: int = 30
    tokens_per_game: int = 500


config = Config()
