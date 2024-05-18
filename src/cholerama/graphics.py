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
from .engine import GraphicalEngine
from .player import Player
from .scores import read_scores
from .tools import array_from_shared_mem


def _make_separator():
    separator = qw.QFrame()
    separator.setFrameShape(qw.QFrame.HLine)
    separator.setLineWidth(1)
    return separator


class Graphics:
    def __init__(
        self,
        # players: Dict[str, Player],
        # fps: int,
        # test: bool,
        # buffers,
        dict_of_bots,
        players,
        iterations,
        buffers,
        fps,
        safe,
        test,
    ):
        self.players = players
        self.buffers = {
            key: array_from_shared_mem(*value) for key, value in buffers.items()
        }
        self.fps = fps
        self._test = test
        self.player_histories = self.buffers["player_histories"]
        self.board = self.buffers["board_old"]

        self.app = pg.mkQApp("Cholerama")
        self.window = pg.GraphicsLayoutWidget()
        self.window.setWindowTitle("Cholerama")
        self.window.setBackground("#1a1a1a")
        self.left_view = self.window.addViewBox(None, col=0)
        self.left_view.setAspectLocked(True)

        self.cmap = mcolors.ListedColormap(
            ["black"] + [p.color for p in self.players.values()]
        )
        self.image = pg.ImageItem(image=self.cmap(self.board.T))
        self.left_view.addItem(self.image)

        self.outlines = []
        lw = 5
        for i, p in enumerate(self.players.values()):
            x1 = p.patch[1] * config.stepx + lw / 2
            x2 = (p.patch[1] + 1) * config.stepx - lw / 2
            y1 = p.patch[0] * config.stepy + lw / 2
            y2 = (p.patch[0] + 1) * config.stepy - lw / 2
            outl_x = np.array([x1, x2, x2, x1, x1])
            outl_y = np.array([y1, y1, y2, y2, y1])
            self.outlines.append(
                pg.PlotCurveItem(
                    outl_x,
                    outl_y,
                    pen=pg.mkPen(mcolors.to_hex(p.color), width=lw),
                )
            )
            self.left_view.addItem(self.outlines[-1])

        self.right_view = self.window.addPlot(row=None, col=1)
        self.right_view.setMouseEnabled(x=False)
        self.right_view.setLabel("bottom", text="Number of cells")
        self.right_view.setLabel("left", text="Iterations")
        self.lines = []
        self.xhistory = np.arange(self.player_histories.shape[1])
        for i, p in enumerate(self.players.values()):
            self.lines.append(
                self.right_view.plot(
                    self.player_histories[i], self.xhistory, pen=mcolors.to_hex(p.color)
                )
            )
        self.window.ci.layout.setColumnMaximumWidth(1, 300)
        self.niter = 0

        self.engine = GraphicalEngine(
            dict_of_bots,
            players,
            iterations,
            buffers,
            fps,
            safe,
            test,
        )

        # dict_of_bots,
        # players,
        # iterations,

    def update(self):
        self.niter += 1
        self.engine.update(self.niter)
        self.image.setImage(self.cmap(self.board.T))
        for i, hist in enumerate(self.player_histories):
            self.lines[i].setData(hist[:], self.xhistory)
        self.update_tokenboard()
        if self.niter == self.engine.iterations:
            print(f"Reached {self.niter} iterations.")
            self.engine.write_scores()
            self.buffers["game_flow"][1] = True
        if self.buffers["game_flow"][1]:
            self.update_leaderboard(read_scores(self.players.keys(), test=self._test))
            self.timer.stop()

    def update_leaderboard(self, scores: dict):
        names = list(scores["0"].keys())
        sum_scores = {
            name: sum([v[name]["score"] for v in scores.values()]) for name in names
        }
        max_peaks = {
            name: max([v[name]["peak"] for v in scores.values()]) for name in names
        }
        sorted_scores = dict(
            sorted(sum_scores.items(), key=lambda item: item[1], reverse=True)
        )
        for i, (name, score) in enumerate(sorted_scores.items()):
            self.score_boxes[i].setText(
                f'<div style="color:{self.players[name].color}">&#9632;</div> '
                f"{i+1}. {name[:config.max_name_length]}: {score}"
            )
        sorted_peaks = dict(
            sorted(max_peaks.items(), key=lambda item: item[1], reverse=True)
        )
        for i, name in enumerate(list(sorted_peaks.keys())[:3]):
            self.peak_boxes[i].setText(
                f'<div style="color:{self.players[name].color}">&#9632;</div> '
                f"{i+1}. {name[:config.max_name_length]}: {sorted_peaks[name]}"
            )

    def update_tokenboard(self):
        for i, (name, p) in enumerate(self.players.items()):
            self.token_boxes[name].setText(
                f'<div style="color:{p.color}">&#9632;</div> '
                f"{name[:config.max_name_length]}: {self.buffers['player_tokens'][i]}"
            )

    def run(self):
        main_window = qw.QMainWindow()
        main_window.setWindowTitle("Cholerama")
        main_window.setGeometry(0, 0, 1280, 800)

        # Create a central widget to hold the two widgets
        central_widget = qw.QWidget()
        main_window.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = qw.QHBoxLayout(central_widget)
        layout.addWidget(self.window)
        widget2 = qw.QWidget()
        layout.addWidget(widget2)
        widget2_layout = qw.QVBoxLayout(widget2)
        widget2.setSizePolicy(qw.QSizePolicy.Fixed, qw.QSizePolicy.Preferred)
        widget2.setMinimumWidth(int(self.window.width() * 0.08))
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

        self.update_leaderboard(read_scores(self.players.keys(), test=self._test))
        self.update_tokenboard()

        main_window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000 // self.fps if self.fps is not None else 0)
        self.timer.start()
        pg.exec()
        self.buffers["game_flow"][1] = True

    def toggle_pause(self):
        if self.play_button.isChecked():
            for outline in self.outlines:
                outline.setVisible(False)
            self.buffers["game_flow"][0] = True
            self.play_button.setText("Pause")
        else:
            self.buffers["game_flow"][0] = False
            self.play_button.setText("Play")
