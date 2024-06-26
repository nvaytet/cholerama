# SPDX-License-Identifier: BSD-3-Clause

import glob
import importlib

import cholerama

bots = [importlib.import_module(repo) for repo in glob.glob("*_bot")]

cholerama.play(
    bots=bots,  # List of bots to use
    iterations=4000,  # Number of iterations to run
    fps=30,  # Frames per second
    show_results=False,  # Save a figure of the results
    test=False,  # Not a test
    safe=True,  # Safe mode to catch errors
)
