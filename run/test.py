# SPDX-License-Identifier: BSD-3-Clause


import germ_bot
import puffer_bot

import cholerama

# bots = {
#     name: germ_bot
#     for name in [
#         "Cholera",
#         "Typhoid",
#         "Dysentery",
#         "Ecoli",
#         "Tetanus",
#         "Pneumonia",
#     ]
# }

# # # for name in ["SpaceFiller", "AnotherFiller"]:
# # #     bot = germ_bot.FillerBot(name=name, number=len(bots) + 1)
# # #     bots.append(bot)

# bots.update({name: puffer_bot for name in ["Puff", "Huff"]})

bots = {germ_bot.AUTHOR: germ_bot}

cholerama.play(
    bots=bots,  # List of bots to use
    iterations=2000,  # Number of iterations to run
    seed=None,  # Random seed
    fps=30,  # Frames per second
    # plot_results=True,  # Save a figure of the results
    test=False,
    ncores=8,
)

# cholerama.headless(
#     bots=bots,  # List of bots to use
#     iterations=500,  # Number of iterations to run
#     show_results=False,  # Save a figure of the results
#     nthreads=12,
# )
