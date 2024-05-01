# SPDX-License-Identifier: BSD-3-Clause

import glob

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def load(file=None):
    if file is None:
        file = sorted(glob.glob("results-*.npz"))[-1]
    print("Loading:", file)
    return {
        key: value if value.shape else value[()] for key, value in np.load(file).items()
    }


def plot(*, board, show=True, fname=None, **players):
    plt.ioff()
    fig, ax = plt.subplots(2, 1, figsize=(9, 9))
    colors = {
        name.removesuffix("_color"): c
        for name, c in players.items()
        if name.endswith("_color")
    }
    histories = {
        name.removesuffix("_history"): h
        for name, h in players.items()
        if name.endswith("_history")
    }
    cmap = mcolors.ListedColormap(["black"] + list(colors.values()))
    ax[0].imshow(board, cmap=cmap, interpolation="none", origin="lower")
    ax[0].axis("off")
    ax[0].set_title("Final state")

    for name in colors:
        ax[1].plot(histories[name], label=name, color=colors[name])
    ax[1].set_title("Number of cells")
    ax[1].set_xlabel("Iterations")
    ax[1].set_ylabel("Number of cells")
    ax[1].grid()
    ax[1].legend()
    plt.tight_layout()
    if show:
        plt.show()
    if fname is not None:
        fig.savefig(fname.replace(".npz", ".pdf"))
    return fig, ax
