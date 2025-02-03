import pyqtgraph as pg

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .BodyLayout import BodyLayout
from RoundState import RoundState

from ServerListener import ServerListener


class MainWindow(QMainWindow):
    def __init__(self, client_socket):
        round_state = RoundState()
        super().__init__()

        # This is dynamically updated elsewhere, so it must exist before the SeverListener. It is finally added to
        # a layout in JhgPanel.py
        self.token_label = QLabel()
        jhg_plot = pg.PlotWidget()

        # Header
        headerLayout = QHBoxLayout()
        round_counter = QLabel("Round 1")
        round_counter_font = QFont()
        round_counter_font.setPointSize(20)
        round_counter.setFont(round_counter_font)
        headerLayout.addWidget(round_counter)

        # Listens for incoming data from the server. Must be before the body layout, but after round_counter
        self.ServerListener = ServerListener(self, client_socket, round_state, round_counter, self.token_label, jhg_plot)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)
        self.ServerListener_thread.start()

        # Body
        body_layout = BodyLayout(round_state, client_socket, self.token_label, jhg_plot)

        # Add the other layouts to the master layout
        master_layout = QVBoxLayout()
        master_layout.addLayout(headerLayout)
        master_layout.addLayout(body_layout)

        central_widget = QWidget()
        central_widget.setLayout(master_layout)

        self.setCentralWidget(central_widget)