# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F405
import os
import time
from typing import Any, Dict, Optional, List

import matplotlib.colors as mcolors
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

from PIL import Image, ImageQt


try:
    from PyQt5.QtWidgets import (
        QCheckBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QSizePolicy,
        QSlider,
        QVBoxLayout,
        QWidget,
        QPushButton,
    )
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (
        QMainWindow,
        QWidget,
        QLabel,
        QHBoxLayout,
        QVBoxLayout,
        QCheckBox,
        QSizePolicy,
        QSlider,
        QFrame,
        QPushButton,
    )
    from PySide2.QtCore import Qt

# import pyqtgraph.opengl as gl


from . import config


class Graphics:
    def __init__(self, board, nplayers: int):
        # t0 = time.time()
        # print("Composing graphics...", end=" ", flush=True)
        self.app = pg.mkQApp("Cholerama")
        self.window = pg.GraphicsLayoutWidget()
        self.window.setWindowTitle("Cholerama")
        self.view = self.window.addViewBox()
        self.view.setAspectLocked(True)

        self.cmap = mcolors.ListedColormap(
            ["black"] + [f"C{i}" for i in range(nplayers)]
        )

        self.image = pg.ImageItem(image=self.cmap(board))
        self.view.addItem(self.image)

        # self.view.setRange(
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

    def update(self, board):

        self.image.setImage(self.cmap(board))


class GraphicalEngine(Engine):

    def run(self):
        main_window = QMainWindow()
        main_window.setWindowTitle("Room 25")
        main_window.setGeometry(0, 0, 1400, 900)

        # Create a central widget to hold the two widgets
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QHBoxLayout(central_widget)

        # Left side turn bar
        widget0 = QWidget()
        layout.addWidget(widget0)
        widget0_layout = QVBoxLayout(widget0)
        widget0.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget0.setMinimumWidth(int(main_window.width() * 0.05))

        self.player_turns = []
        for i in range(len(self.buffers["player_turns"])):
            img = os.path.join(config.resourcedir, "none.png")
            self.player_turns.append(
                QLabel(f'0: <img src="{img}" width="32" height="32">')
            )
            widget0_layout.addWidget(self.player_turns[-1])
        widget0_layout.addStretch()

        # Left side player bar
        widget1 = QWidget()
        layout.addWidget(widget1)
        widget1_layout = QVBoxLayout(widget1)
        widget1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget1.setMinimumWidth(int(main_window.width() * 0.1))

        players = list(self.player_avatars.keys())
        n = len(players) // 2
        self.player_status = {}
        for name in players[:n]:
            # self.player_status[name] = QLabel(
            #     f'{name}: ' f'<img src="{filename}" width="32" height="32">'
            # )
            widget = QWidget()
            widget_layout = QVBoxLayout(widget)
            widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

            # qim = ImageQt.ImageQt(
            #     Image.fromarray(
            #         self.buffers['player_images_array'][players.index(name)]
            #     ).resize((32, 32))
            # )
            # pix = QtGui.QPixmap.fromImage(qim)
            # header = QLabel(f'{name}:')
            # header.setPixmap(pix)

            header = QLabel(
                f'{name}: <img src="{self.player_avatars[name]}" width="32" height="32">'
            )

            widget_layout.addWidget(header)
            footer = QWidget()
            footer_layout = QHBoxLayout(footer)
            img_path = os.path.join(config.resourcedir, "none.png")
            action1 = QLabel(f'1: <img src="{img_path}" width="32" height="32">')
            action2 = QLabel(f'2: <img src="{img_path}" width="32" height="32">')
            self.player_status[name] = (action1, action2)
            footer_layout.addWidget(action1)
            footer_layout.addWidget(action2)
            widget_layout.addWidget(footer)

            widget1_layout.addWidget(widget)

            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setLineWidth(1)
            # separator.setStyleSheet('border: 0px; background-color: #808080;')
            widget1_layout.addWidget(separator)

        # self.time_label = QLabel("Time left:")
        # widget1_layout.addWidget(self.time_label)
        # self.tracer_checkbox = QCheckBox("Wind tracers", checked=True)
        # self.tracer_checkbox.stateChanged.connect(self.graphics.toggle_wind_tracers)
        # widget1_layout.addWidget(self.tracer_checkbox)

        widget1_layout.addStretch()
        self.pause_button = QPushButton("Next")
        # self.pause_button.setCheckable(True)
        self.pause_button.clicked.connect(self.toggle_pause)
        widget1_layout.addWidget(self.pause_button)

        # Main game window
        widget5 = QWidget()
        widget5_layout = QVBoxLayout(widget5)
        widget5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget5_layout.addWidget(self.window)
        self.window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.window.setFixedWidth(int(main_window.width() * 0.65))

        self.status_bar = QLabel("NOTHING")
        self.status_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.status_bar.setStyleSheet("border: 1px solid #000000;")
        # Set height of status bar
        self.status_bar.setFixedHeight(40)
        # Width of status bar equal to width of window
        self.status_bar.setFixedWidth(self.window.width())
        widget5_layout.addWidget(self.status_bar)
        layout.addWidget(widget5)

        # Right side player bar
        widget2 = QWidget()
        layout.addWidget(widget2)
        widget2_layout = QVBoxLayout(widget2)
        widget2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        widget2.setMinimumWidth(int(main_window.width() * 0.1))

        for name in players[n:]:
            widget = QWidget()
            widget_layout = QVBoxLayout(widget)
            widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            header = QLabel(
                f'{name}: <img src="{self.player_avatars[name]}" width="32" height="32">'
            )
            widget_layout.addWidget(header)
            footer = QWidget()
            footer_layout = QHBoxLayout(footer)
            img_path = os.path.join(config.resourcedir, "none.png")
            action1 = QLabel(f'1: <img src="{img_path}" width="32" height="32">')
            action2 = QLabel(f'2: <img src="{img_path}" width="32" height="32">')
            self.player_status[name] = (action1, action2)
            footer_layout.addWidget(action1)
            footer_layout.addWidget(action2)
            widget_layout.addWidget(footer)

            widget2_layout.addWidget(widget)

            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setLineWidth(1)
            # separator.setStyleSheet('border: 0px; background-color: #808080;')
            widget2_layout.addWidget(separator)

        widget2_layout.addStretch()

        main_window.show()

        # self.board[2, 2].mask.setOpacity(0.1)
        # self.update2()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000 // 15)
        # self.timer.setInterval(5)
        # self.timer.setInterval(0)
        self.timer.start()

        # self.timer2 = QtCore.QTimer()
        # self.timer2.timeout.connect(self.update2)
        # # self.timer.setInterval(1000 // 30)
        # self.timer2.setInterval(50)
        # # self.timer.setInterval(0)
        # self.timer2.start()

        # self.board.rooms[0, 0].mask.setOpacity(0.1)
        # pg.QtGui.QApplication.processEvents()

        pg.exec()

        self.buffers["game_flow"][0] = 0
        self.buffers["game_flow"][1] = 1

    def add_room(self, room):
        self.view.addItem(room.image)
        self.view.addItem(room.mask)
