# SPDX-License-Identifier: BSD-3-Clause


import germ_bot

import cholerama

bots = []
for name in [
    "Cholera",
    "Typhoid",
    "Dysentery",
    "Malaria",
    "Influenza",
    "Tuberculosis",
]:
    bot = germ_bot.Bot()
    bot.name = name
    bots.append(bot)

# for name in ["SpaceFiller", "AnotherFiller"]:
#     bot = germ_bot.FillerBot()
#     bot.name = name
#     bots.append(bot)

for name in ["Puff", "Huff"]:
    bot = germ_bot.PufferBot()
    bot.name = name
    bots.append(bot)

cholerama.play(
    bots=bots,  # List of bots to use
    iterations=5000,  # Number of iterations to run
    fps=None,  # Frames per second
    plot_results=True,  # Save a figure of the results
    test=False,
)

# cholerama.headless(
#     bots=bots,  # List of bots to use
#     iterations=1000,  # Number of iterations to run
#     plot_results=False,  # Save a figure of the results
#     nthreads=8,
# )
