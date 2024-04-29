# SPDX-License-Identifier: BSD-3-Clause

import time
from typing import Optional, Tuple, Union

import numpy as np
from numba import set_num_threads

from . import config
from .compute import evolve_board
from .player import Player
from .plot import plot
from .scores import finalize_scores, read_round
from .tools import make_color, make_starting_positions


class Engine:
    def __init__(
        self,
        bots: Union[dict, list],
        iterations: int = 100,
        safe: bool = False,
        test: bool = True,
        seed: Optional[int] = None,
        plot_results: bool = False,
        nthreads: Optional[int] = None,
    ):
        if nthreads is not None:
            set_num_threads(nthreads)
        if seed is not None:
            np.random.seed(seed)

        self.iterations = iterations
        self._test = test
        self.safe = safe
        self.plot_results = plot_results
        self.token_interval = max(1, iterations // config.additional_tokens)
        self.rounds_played = 0 if self._test else read_round()

        self.board = np.zeros((config.ny, config.nx), dtype=int)
        self.new_board = self.board.copy()

        starting_positions = make_starting_positions(len(bots))

        if isinstance(bots, dict):
            self.bots = {
                name: bot.Bot(number=i + 1, name=name, x=pos[0], y=pos[1])
                for i, ((name, bot), pos) in enumerate(
                    zip(bots.items(), starting_positions)
                )
            }
        else:
            self.bots = {
                bot.AUTHOR: bot.Bot(number=i + 1, name=bot.AUTHOR, x=pos[0], y=pos[1])
                for i, (bot, pos) in enumerate(zip(bots, starting_positions))
            }

        starting_positions = make_starting_positions(len(self.bots))
        self.players = {}
        self.player_histories = np.zeros(
            (len(self.bots), self.iterations + 1), dtype=int
        )
        for i, (bot, pos) in enumerate(zip(self.bots.values(), starting_positions)):
            player = Player(
                name=bot.name,
                number=i + 1,
                pattern=bot.pattern,
                color=make_color(i if bot.color is None else bot.color),
            )
            p = player.pattern
            if any(np.array(p.shape) > np.array(config.pattern_size)):
                raise ValueError(
                    f"Player {bot.name}: pattern size {p.shape} not allowed."
                )
            psum = np.sum(p)
            if psum > config.initial_tokens:
                raise ValueError(
                    f"Player {bot.name}: pattern has more than "
                    f"{config.initial_tokens} tokens."
                )
            player.tokens -= psum
            self.board[pos[1] : pos[1] + p.shape[0], pos[0] : pos[0] + p.shape[1]] = (
                p * (i + 1)
            )
            self.players[bot.name] = player
            self.player_histories[i, 0] = player.ncells

        self.bot_call_order = np.roll(
            list(self.players.keys()), self.rounds_played % len(self.players)
        )

        self.xoff = np.array([-1, 0, 1, -1, 1, -1, 0, 1])
        self.yoff = np.array([-1, -1, -1, 0, 0, 1, 1, 1])
        self.neighbors = np.zeros(8, dtype=int)
        self.neighbor_buffer = np.zeros(3, dtype=int)

        # Pre-compile numba function
        evolve_board(
            self.board,
            self.new_board,
            self.xoff,
            self.yoff,
            self.neighbors,
            self.neighbor_buffer,
            config.nx,
            config.ny,
        )

    def add_player_new_cells(
        self, player: Player, new_cells: Tuple[np.ndarray, np.ndarray]
    ):
        x, y = new_cells
        ntok = len(x)
        ok = True
        if ntok != len(y):
            print(f"Player {player.name}: new cells x and y have different lengths.")
            ok = False
        if ntok > player.tokens:
            print(
                f"Player {player.name}: not enough tokens: needs {ntok}, "
                f"has {player.tokens}."
            )
            ok = False
        x = np.asarray(x) % config.nx
        y = np.asarray(y) % config.ny
        if self.board[y, x].sum() > 0:
            print(f"Player {player.name}: cannot overwrite alive cells.")
            ok = False
        if ok:
            self.board[y, x] = player.number
            player.tokens -= ntok

    def call_player_bots(self, it: int):
        # TODO: Roll the order of players for each round
        # players = list(self.players.values())
        for name in self.bot_call_order:
            # for name, player in ((n, p) for n, p in self.players.items() if p.ncells > 0):
            player = self.players[name]
            if player.ncells == 0:
                continue
            self.board.setflags(write=False)
            new_cells = None
            args = {
                "iteration": int(it),
                "board": self.board,
                "tokens": int(player.tokens),
            }
            if self.safe:
                try:
                    new_cells = self.bots[name].run(**args)
                except:  # noqa
                    pass
            else:
                new_cells = self.bots[name].run(**args)
            self.board.setflags(write=True)
            if new_cells:
                self.add_player_new_cells(player, new_cells)

    def show_results(self, fname: str):
        if self.plot_results:
            fig, _ = plot(self.board, self.player_histories)
            fig.savefig(fname)

    def shutdown(self):
        for i, player in enumerate(self.players.values()):
            player.peak = self.player_histories[i].max()
        finalize_scores(self.players, test=self._test)
        fname = "results-" + time.strftime("%Y%m%d-%H%M%S") + ".npz"
        np.savez(fname, board=self.board, history=self.player_histories)
        self.show_results(fname.replace(".npz", ".pdf"))

    def update(self, it: int):
        if it % self.token_interval == 0:
            for player in [p for p in self.players.values() if p.ncells > 0]:
                player.tokens += 1
        self.call_player_bots(it)
        evolve_board(
            self.board,
            self.new_board,
            self.xoff,
            self.yoff,
            self.neighbors,
            self.neighbor_buffer,
            config.nx,
            config.ny,
        )
        self.board, self.new_board = self.new_board, self.board
        for i, player in enumerate(self.players.values()):
            player.update(self.board)
            self.player_histories[i, it] = player.ncells

    def run(self):
        for it in range(1, self.iterations + 1):
            self.update(it)
        print(f"Reached {it} iterations.")
        self.shutdown()
