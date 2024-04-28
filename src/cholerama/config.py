# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Config:
    nx: int = 700
    ny: int = 600
    pattern_size: Tuple[int] = (36, 36)
    max_name_length: int = 30
    initial_tokens: int = 100
    additional_tokens: int = 200


config = Config()
