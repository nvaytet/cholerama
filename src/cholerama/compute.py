# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
from numba import njit, prange


@njit(boundscheck=False, cache=True, fastmath=True, parallel=True)
def evolve_board(
    old: np.ndarray,
    new: np.ndarray,
    xoff: np.ndarray,
    yoff: np.ndarray,
    cell_counts: np.ndarray,
    nx: int,
    ny: int,
):
    for j in prange(ny):
        neighbors = np.zeros(8, dtype="int32")
        buffer = np.zeros(3, dtype="int32")
        for i in range(nx):
            # Get the values of the neighbors
            neighbor_count = 0
            for k in range(8):
                xind = (i + xoff[k]) % nx
                yind = (j + yoff[k]) % ny
                n = old[yind, xind]
                neighbors[k] = n
                if n > 0:
                    if neighbor_count < 3:
                        buffer[neighbor_count] = n
                    neighbor_count += 1

            # Apply rules
            if (old[j, i] > 0) and ((neighbor_count == 2) or (neighbor_count == 3)):
                new[j, i] = old[j, i]
            elif (old[j, i] == 0) and (neighbor_count == 3):
                if buffer[0] == buffer[1]:
                    new[j, i] = buffer[0]
                elif buffer[0] == buffer[2]:
                    new[j, i] = buffer[0]
                else:
                    new[j, i] = buffer[1]
            else:
                new[j, i] = 0

    # Update cell counts
    cell_counts[...] = np.bincount(new.ravel())[1:]
