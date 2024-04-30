# SPDX-License-Identifier: BSD-3-Clause

import glob

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def load(file=None):
    if file is None:
        file = glob.glob("results-*.npz")[-1]
    board, history = np.load(file).values()
    return {"board": board, "history": history}


def plot(board, player_data, show=True):
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))
    cmap = mcolors.ListedColormap(
        ["black"] + [p["color"] for p in player_data.values()]
    )
    ax[0].imshow(board, cmap=cmap, interpolation="none", origin="lower")
    ax[0].axis("off")
    ax[0].set_title("Final state")

    for name, data in player_data.items():
        ax[1].plot(data["history"], label=name, color=data["color"])
    ax[1].set_title("Number of cells")
    ax[1].set_xlabel("Iterations")
    ax[1].set_ylabel("Number of cells")
    ax[1].grid()
    ax[1].legend()
    plt.tight_layout()
    if show:
        plt.show()
    return fig, ax
