# SPDX-License-Identifier: BSD-3-Clause

import os
import time
from typing import Any, Dict, Optional, List

import matplotlib.colors as mcolors
from matplotlib import colormaps
import numpy as np


from . import config
from .engine import Engine
from .plot import plot
from .scores import read_scores


class Graphics:
    def __init__(self, board, players, player_histories):
        import pyqtgraph as pg

        self.app = pg.mkQApp("Cholerama")
        self.window = pg.GraphicsLayoutWidget()
        self.window.setWindowTitle("Cholerama")
        self.window.setBackground("#1a1a1a")
        self.left_view = self.window.addViewBox(None, col=0)
        self.left_view.setAspectLocked(True)

        nplayers = len(player_histories)

        self.cmap = mcolors.ListedColormap(["black"] + [p.color for p in players])

        # tab20 = colormaps["tab20"]
        # self.cmap = mcolors.ListedColormap(
        #     ["black"] + [f"C{i}" for i in range(nplayers)]
        # )

        self.image = pg.ImageItem(image=self.cmap(board.T))
        self.left_view.addItem(self.image)

        # self.right_view = self.window.addViewBox(1, 2)
        self.right_view = self.window.addPlot(row=None, col=1)
        self.right_view.setMouseEnabled(x=False)
        self.right_view.setLabel("bottom", text="Number of cells")
        self.right_view.setLabel("left", text="Iterations")
        # self.right_view.setAspectLocked(True)

        # self.plot = self.right_view.addPlot(0, 0, 1, 1)
        self.lines = []
        self.xhistory = np.arange(player_histories.shape[1])
        for i in range(nplayers):
            self.lines.append(
                self.right_view.plot(
                    # self.xhistory, player_histories[i], pen=mcolors.to_hex(f"C{i}")
                    player_histories[i],
                    self.xhistory,
                    pen=mcolors.to_hex(f"C{i}"),
                )
            )

        # plotpen = pg.mkPen(color='k', width=2)
        # upperplot.plot(first_time, first_record, pen=plotpen)

        # self.window.ci.layout.setRowStretchFactor(0, 4)
        self.window.ci.layout.setColumnMaximumWidth(1, 300)
        # self.window.ci.layout.setCol

        # self.left_view.setRange(
        #     xRange=[
        #         config.room_image_size,
        #         config.room_image_size * (config.board_size + 1),
        #     ],
        #     yRange=[
        #         config.room_image_size,
        #         config.room_image_size * (config.board_size + 1),
        #     ],
        #     padding=0,
        # )
        # # graph.setXRange(0,5)
        # # graph.setYRange(0,10)

        return

    def update(self, board, histories):

        self.image.setImage(self.cmap(board.T))
        for i, hist in enumerate(histories):
            self.lines[i].setData(hist[:], self.xhistory)


class GraphicalEngine(Engine):

    def __init__(self, *args, fps=15, **kwargs):
        super().__init__(*args, **kwargs)

        self.graphics = Graphics(
            self.board,
            players=self.players.values(),
            player_histories=self.player_histories,
        )
        self.niter = 0
        self.fps = fps
        # print("self.fps", self.fps)

    def update_leaderboard(self, scores, peaks):
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

        # sorted_times = dict(sorted(fastest_times.items(), key=lambda item: item[1]))
        # time_list = list(enumerate(sorted_times.items()))
        # for i, (name, t) in time_list[:3]:
        #     try:
        #         time = str(datetime.timedelta(seconds=int(t)))[2:]
        #     except OverflowError:
        #         time = "None"
        #     self.peak_boxes[i].setText(
        #         f'<div style="color:{self.players[name].color}">&#9632;</div> '
        #         f"{i+1}. {name[:config.max_name_length]}: {time}"
        #     )

    def run(self):

        import pyqtgraph as pg
        from pyqtgraph.Qt import QtCore

        try:
            from PyQt5 import QtWidgets as qw
        except ImportError:
            from PySide2 import QtWidgets as qw

        main_window = qw.QMainWindow()
        main_window.setWindowTitle("Cholerama")
        main_window.setGeometry(0, 0, 1200, 700)

        # Create a central widget to hold the two widgets
        central_widget = qw.QWidget()
        main_window.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = qw.QHBoxLayout(central_widget)

        def _make_separator():
            separator = qw.QFrame()
            separator.setFrameShape(qw.QFrame.HLine)
            separator.setLineWidth(1)
            return separator

        # # Left side turn bar
        # widget0 = QWidget()
        # layout.addWidget(widget0)
        # widget0_layout = QVBoxLayout(widget0)
        # widget0.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # widget0.setMinimumWidth(int(main_window.width() * 0.05))

        # self.player_turns = []
        # for i in range(len(self.buffers["player_turns"])):
        #     img = os.path.join(config.resourcedir, "none.png")
        #     self.player_turns.append(
        #         QLabel(f'0: <img src="{img}" width="32" height="32">')
        #     )
        #     widget0_layout.addWidget(self.player_turns[-1])
        # widget0_layout.addStretch()

        # # Left side player bar
        # widget1 = QWidget()
        # layout.addWidget(widget1)
        # widget1_layout = QVBoxLayout(widget1)
        # widget1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # widget1.setMinimumWidth(int(main_window.width() * 0.1))

        # players = list(self.player_avatars.keys())
        # n = len(players) // 2
        # self.player_status = {}
        # for name in players[:n]:
        #     # self.player_status[name] = QLabel(
        #     #     f'{name}: ' f'<img src="{filename}" width="32" height="32">'
        #     # )
        #     widget = QWidget()
        #     widget_layout = QVBoxLayout(widget)
        #     widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        #     # qim = ImageQt.ImageQt(
        #     #     Image.fromarray(
        #     #         self.buffers['player_images_array'][players.index(name)]
        #     #     ).resize((32, 32))
        #     # )
        #     # pix = QtGui.QPixmap.fromImage(qim)
        #     # header = QLabel(f'{name}:')
        #     # header.setPixmap(pix)

        #     header = QLabel(
        #         f'{name}: <img src="{self.player_avatars[name]}" width="32" height="32">'
        #     )

        #     widget_layout.addWidget(header)
        #     footer = QWidget()
        #     footer_layout = QHBoxLayout(footer)
        #     img_path = os.path.join(config.resourcedir, "none.png")
        #     action1 = QLabel(f'1: <img src="{img_path}" width="32" height="32">')
        #     action2 = QLabel(f'2: <img src="{img_path}" width="32" height="32">')
        #     self.player_status[name] = (action1, action2)
        #     footer_layout.addWidget(action1)
        #     footer_layout.addWidget(action2)
        #     widget_layout.addWidget(footer)

        #     widget1_layout.addWidget(widget)

        #     separator = QFrame()
        #     separator.setFrameShape(QFrame.HLine)
        #     separator.setLineWidth(1)
        #     # separator.setStyleSheet('border: 0px; background-color: #808080;')
        #     widget1_layout.addWidget(separator)

        # # self.time_label = QLabel("Time left:")
        # # widget1_layout.addWidget(self.time_label)
        # # self.tracer_checkbox = QCheckBox("Wind tracers", checked=True)
        # # self.tracer_checkbox.stateChanged.connect(self.graphics.toggle_wind_tracers)
        # # widget1_layout.addWidget(self.tracer_checkbox)

        # widget1_layout.addStretch()
        # self.pause_button = QPushButton("Next")
        # # self.pause_button.setCheckable(True)
        # self.pause_button.clicked.connect(self.toggle_pause)
        # widget1_layout.addWidget(self.pause_button)

        # # Main game window
        # widget5 = QWidget()
        # widget5_layout = QVBoxLayout(widget5)
        # widget5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # widget5_layout.addWidget(self.graphics.window)
        # # self.window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # # self.window.setFixedWidth(int(main_window.width() * 0.65))

        # self.status_bar = QLabel("NOTHING")
        # self.status_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # self.status_bar.setStyleSheet("border: 1px solid #000000;")
        # # Set height of status bar
        # self.status_bar.setFixedHeight(40)
        # # Width of status bar equal to width of window
        # self.status_bar.setFixedWidth(self.window.width())
        # widget5_layout.addWidget(self.status_bar)
        layout.addWidget(self.graphics.window)

        # # Right side player bar
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

        # self.update_leaderboard(
        #     {name: 0 for name in self.players}, {name: 0 for name in self.players}
        # )
        self.update_leaderboard(*read_scores(self.players.keys(), test=self._test))
        self.update_tokenboard()

        #     widget_layout.addWidget(header)
        #     footer = QWidget()
        #     footer_layout = QHBoxLayout(footer)
        #     img_path = os.path.join(config.resourcedir, "none.png")
        #     action1 = QLabel(f'1: <img src="{img_path}" width="32" height="32">')
        #     action2 = QLabel(f'2: <img src="{img_path}" width="32" height="32">')
        #     self.player_status[name] = (action1, action2)
        #     footer_layout.addWidget(action1)
        #     footer_layout.addWidget(action2)
        #     widget_layout.addWidget(footer)

        #     widget2_layout.addWidget(widget)

        #     separator = QFrame()
        #     separator.setFrameShape(QFrame.HLine)
        #     separator.setLineWidth(1)
        #     # separator.setStyleSheet('border: 0px; background-color: #808080;')
        #     widget2_layout.addWidget(separator)

        # widget2_layout.addStretch()

        main_window.show()

        # self.board[2, 2].mask.setOpacity(0.1)
        # self.update2()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000 // self.fps if self.fps is not None else 0)
        # self.timer.start()
        pg.exec()
        # self.shutdown()
        # self.update_leaderboard(*read_scores(self.players.keys(), test=self._test))

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

    # def run(self):
    #     # self.timer = QtCore.QTimer()
    #     # self.timer.timeout.connect(self.update)
    #     # self.timer.setInterval(1000 // self.fps if self.fps is not None else 0)
    #     # self.timer.start()
    #     pg.exec()
