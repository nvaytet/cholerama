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
    iterations=5000,  # Number of iterations to run
    fps=30,  # Frames per second
    plot_results=True,  # Save a figure of the results
    test=False,  # Not a test
)
