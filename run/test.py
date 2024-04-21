# SPDX-License-Identifier: BSD-3-Clause

import glob
import importlib

import cholerama

bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

cholerama.play(
    bots=bots,  # List of bots to use
    test=True,  # Set to True to run in test mode
    fps=10,  # Frames per second
)
