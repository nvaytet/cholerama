# SPDX-License-Identifier: BSD-3-Clause

import glob
import importlib

import cholerama
import germ_bot

# bots = []
# for repo in glob.glob("*_bot"):
#     module = importlib.import_module(f"{repo}")
#     bots.append(module.Bot())

bots = []
for name in [
    "Cholera",
    "Typhoid",
    "Dysentery",
    "Malaria",
    "Influenza",
    # "Tuberculosis",
    # "YellowFever",
    # "Smallpox",
    # "Measles",
]:
    bot = germ_bot.Bot()
    bot.name = name
    bots.append(bot)

cholerama.play(
    bots=bots,  # List of bots to use
    test=True,  # Set to True to run in test mode
    fps=10,  # Frames per second
)

# cholerama.headless(
#     bots=bots,  # List of bots to use
#     test=True,  # Set to True to run in test mode
#     fps=10,  # Frames per second
# )
