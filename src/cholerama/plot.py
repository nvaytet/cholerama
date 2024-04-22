# SPDX-License-Identifier: BSD-3-Clause

import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def load(file=None):
    if file is None:
        file = glob.glob("results-*.npz")[-1]
    board, history = np.load(file).values()
    return {"board": board, "history": history}


def plot(board, history):
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))
    cmap = mcolors.ListedColormap(["black"] + [f"C{i}" for i in range(len(history))])
    ax[0].imshow(board, cmap=cmap, interpolation="none")
    ax[0].axis("off")
    ax[0].set_title("Final state")

    ax[1].plot(history.T)
    ax[1].set_title("Number of cells")
    ax[1].set_xlabel("Iterations")
    ax[1].set_ylabel("Number of cells")
    plt.tight_layout()
    plt.show()
    return fig, ax


def show_results(file=None):
    data = load(file)
    plot(data["board"], data["history"])
