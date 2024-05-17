# SPDX-License-Identifier: BSD-3-Clause

# import my_bot
import germ_bot

import cholerama

bots = {
    name: germ_bot
    for name in [
        "Cholera",
        "Typhoid",
        "Dysentery",
        "Ecoli",
        "Tetanus",
        "Pneumonia",
    ]
}

# bots[my_bot.AUTHOR] = my_bot

cholerama.headless(
    bots=bots,  # List of bots to use
    iterations=4000,  # Number of iterations to run
    show_results=False,  # Display plot of results at the end
)
