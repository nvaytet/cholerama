# SPDX-License-Identifier: BSD-3-Clause

from typing import Dict

import matplotlib.colors as mcolors
import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

try:
    from PyQt5 import QtWidgets as qw
except ImportError:
    from PySide2 import QtWidgets as qw

from . import config
from .engine import Engine
from .player import Player
from .plot import plot
from .scores import read_scores


class Graphics:
    def __init__(
        self,
        board: np.ndarray,
        players: Dict[str, Player],
        player_histories: np.ndarray,
    ):

        self.app = pg.mkQApp("Cholerama")
        self.window = pg.GraphicsLayoutWidget()
        self.window.setWindowTitle("Cholerama")
        self.window.setBackground("#1a1a1a")
        self.left_view = self.window.addViewBox(None, col=0)
        self.left_view.setAspectLocked(True)

        nplayers = len(player_histories)
        self.cmap = mcolors.ListedColormap(["black"] + [p.color for p in players])
        self.image = pg.ImageItem(image=self.cmap(board.T))
        self.left_view.addItem(self.image)

        self.right_view = self.window.addPlot(row=None, col=1)
        self.right_view.setMouseEnabled(x=False)
        self.right_view.setLabel("bottom", text="Number of cells")
        self.right_view.setLabel("left", text="Iterations")
        self.lines = []
        self.xhistory = np.arange(player_histories.shape[1])
        for i in range(nplayers):
            self.lines.append(
                self.right_view.plot(
                    player_histories[i], self.xhistory, pen=mcolors.to_hex(f"C{i}")
                )
            )
        self.window.ci.layout.setColumnMaximumWidth(1, 300)

        return

    def update(self, board: np.ndarray, histories: np.ndarray):
        self.image.setImage(self.cmap(board.T))
        for i, hist in enumerate(histories):
            self.lines[i].setData(hist[:], self.xhistory)


def _make_separator():
    separator = qw.QFrame()
    separator.setFrameShape(qw.QFrame.HLine)
    separator.setLineWidth(1)
    return separator


class GraphicalEngine(Engine):

    def __init__(self, *args, fps: int = 15, **kwargs):
        super().__init__(*args, **kwargs)

        self.graphics = Graphics(
            self.board,
            players=self.players.values(),
            player_histories=self.player_histories,
        )
        self.niter = 0
        self.fps = fps

    def update_leaderboard(self, scores: Dict[str, int], peaks: Dict[str, int]):
        sorted_scores = dict(
            sorted(scores.items(), key=lambda item: item[1], reverse=True)
        )
        for i, (name, score) in enumerate(sorted_scores.items()):
            self.score_boxes[i].setText(
                f'<div style="color:{self.players[name].color}">&#9632;</div> '
                f"{i+1}. {name[:config.max_name_length]}: {score}"
            )
        sorted_peaks = dict(
            sorted(peaks.items(), key=lambda item: item[1], reverse=True)
        )
        for i, name in enumerate(list(sorted_peaks.keys())[:3]):
            self.peak_boxes[i].setText(
                f'<div style="color:{self.players[name].color}">&#9632;</div> '
                f"{i+1}. {name[:config.max_name_length]}: {peaks[name]}"
            )

    def update_tokenboard(self):
        for name, p in self.players.items():
            self.token_boxes[name].setText(
                f'<div style="color:{p.color}">&#9632;</div> '
                f"{name[:config.max_name_length]}: {p.tokens}"
            )

    def run(self):
        main_window = qw.QMainWindow()
        main_window.setWindowTitle("Cholerama")
        main_window.setGeometry(0, 0, 1200, 700)

        # Create a central widget to hold the two widgets
        central_widget = qw.QWidget()
        main_window.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = qw.QHBoxLayout(central_widget)
        layout.addWidget(self.graphics.window)
        widget2 = qw.QWidget()
        layout.addWidget(widget2)
        widget2_layout = qw.QVBoxLayout(widget2)
        widget2.setSizePolicy(qw.QSizePolicy.Fixed, qw.QSizePolicy.Preferred)
        widget2.setMinimumWidth(int(self.graphics.window.width() * 0.08))
        widget2_layout.addWidget(qw.QLabel("<b>Leader board</b>"))

        widget2_layout.addWidget(_make_separator())

        widget2_layout.addWidget(qw.QLabel("<b>Scores:</b>"))
        self.score_boxes = {}
        for i, p in enumerate(self.players.values()):
            self.score_boxes[i] = qw.QLabel(p.name)
            widget2_layout.addWidget(self.score_boxes[i])

        widget2_layout.addWidget(_make_separator())

        widget2_layout.addWidget(qw.QLabel("<b>Peak coverage:</b>"))
        self.peak_boxes = {}
        for i in range(3):
            self.peak_boxes[i] = qw.QLabel(f"{i + 1}.")
            widget2_layout.addWidget(self.peak_boxes[i])

        widget2_layout.addWidget(_make_separator())

        widget2_layout.addWidget(qw.QLabel("<b>Player tokens:</b>"))
        self.token_boxes = {}
        for name, p in self.players.items():
            self.token_boxes[name] = qw.QLabel(p.name)
            widget2_layout.addWidget(self.token_boxes[name])

        widget2_layout.addWidget(_make_separator())

        widget2_layout.addStretch()
        self.play_button = qw.QPushButton("Play")
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.toggle_pause)
        widget2_layout.addWidget(self.play_button)

        self.update_leaderboard(*read_scores(self.players.keys(), test=self._test))
        self.update_tokenboard()

        main_window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000 // self.fps if self.fps is not None else 0)
        pg.exec()

    def toggle_pause(self):
        if self.play_button.isChecked():
            self.timer.start()
            self.play_button.setText("Pause")
        else:
            self.timer.stop()
            self.play_button.setText("Play")

    def show_results(self, fname: str):
        if self.plot_results:
            fig, _ = plot(self.board, self.player_histories, show=False)
            fig.savefig(fname.replace(".npz", ".pdf"))

    def update(self):
        self.niter += 1
        if self.niter > self.iterations:
            self.shutdown()
            self.update_leaderboard(*read_scores(self.players.keys(), test=self._test))
            self.timer.stop()
            return
        super().update(self.niter)
        self.graphics.update(self.board, histories=self.player_histories)
        self.update_tokenboard()
