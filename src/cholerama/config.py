# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Config:
    nx: int = 500
    ny: int = 400
    pattern_size: Tuple[int] = (18, 36)


config = Config()
