import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True)
def evolve_board(
    old: np.ndarray,
    new: np.ndarray,
    xoff: np.ndarray,
    yoff: np.ndarray,
    neighbors: np.ndarray,
    buffer: np.ndarray,
    nx: int,
    ny: int,
):

    # xoff = np.array([-1, 0, 1, -1, 1, -1, 0, 1])
    # yoff = np.array([-1, -1, -1, 0, 0, 1, 1, 1])
    # neighbors = np.zeros(8, dtype=int)
    # ny, nx = old.shape

    for j in prange(ny):
        for i in range(nx):
            # # Get the indices of the neighbors
            # yinds = (j + yoff) % ny
            # xinds = (i + xoff) % nx

            # Get the values of the neighbors
            # neighbors = old[yinds, xinds]
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
            # neighbor_count = np.where(neighbors > 0, 1, 0).sum()

            # Apply rules
            if (old[j, i] > 0) and ((neighbor_count == 2) or (neighbor_count == 3)):
                new[j, i] = old[j, i]
            elif (old[j, i] == 0) and (neighbor_count == 3):
                # new[j, i] = np.sort(neighbors)[7]
                # new[j, i] = 1
                if buffer[0] == buffer[1]:
                    new[j, i] = buffer[0]
                elif buffer[0] == buffer[2]:
                    new[j, i] = buffer[0]
                else:
                    new[j, i] = buffer[1]
            else:
                new[j, i] = 0

    # neighbors = self.board[self.yinds, self.xinds]
    # neighbor_count = np.where(neighbors > 0, 1, 0).sum(axis=0)
    # # neighbor_count = np.clip(neighbors, 0, 1).sum(axis=0)

    # alive_mask = self.board > 0
    # alive_neighbor_count = np.where(alive_mask, neighbor_count, 0)

    # # # Apply rules
    # # new = np.where(
    # #     (alive_neighbor_count == 2) | (alive_neighbor_count == 3), self.board, 0
    # # )

    # # birth_mask = ~alive_mask & (neighbor_count == 3)
    # # # # Birth happens always when we have 3 neighbors. When sorted, the most common
    # # # # value will always be in position 7 (=-2).
    # # birth_values = np.sort(neighbors, axis=0)[-2]
    # # self.board = np.where(birth_mask, birth_values, new)

    # # Apply rules
    # self.board = np.where(
    #     (alive_neighbor_count == 2) | (alive_neighbor_count == 3), self.board, 0
    # )

    # birth_mask = ~alive_mask & (neighbor_count == 3)
    # # Birth happens always when we have 3 neighbors. When sorted, the most common
    # # value will always be in position 7 (=-2).
    # birth_inds = np.where(birth_mask)
    # birth_values = np.sort(neighbors[:, birth_inds[0], birth_inds[1]], axis=0)[-2]
    # self.board[birth_inds[0], birth_inds[1]] = birth_values
