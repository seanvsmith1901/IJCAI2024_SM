import pyqtgraph as pg

from PyQt6.QtCore import QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .BodyLayout import BodyLayout
from RoundState import RoundState

from ServerListener import ServerListener


class MainWindow(QMainWindow):
    def __init__(self, client_socket):
        self.round_state = RoundState()
        super().__init__()

        # This is dynamically updated elsewhere, so it must exist before the SeverListener. It is finally added to
        # a layout in JhgPanel.py
        self.token_label = QLabel()
        self.jhg_plot = pg.PlotWidget()

        # Header - Even though it's just one element, needs to be placed in a layout to play nice with being added
        headerLayout = QHBoxLayout()
        round_counter = QLabel("Round 1")
        round_counter_font = QFont()
        round_counter_font.setPointSize(20)
        round_counter.setFont(round_counter_font)
        headerLayout.addWidget(round_counter)

        # Listens for incoming data from the server. Must be before the body layout (so that the elements that will be
        # used in JHG_panel exist as they are created when the player objects are created).
        # Note that any elements that you want to dynamically update based on server response need to be passed. This
        # means that all the graph elements need to be created here in MainWindow and then passed to SeverListener
        self.ServerListener = ServerListener(self, client_socket, self.round_state, round_counter, self.token_label, self.jhg_plot)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)

        self.ServerListener.update_round_signal.connect(self.update_labels)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)
        self.ServerListener_thread.start()

        # Body
        body_layout = BodyLayout(self.round_state, client_socket, self.token_label, self.jhg_plot)

        # Add the other layouts to the master layout
        master_layout = QVBoxLayout()
        master_layout.addLayout(headerLayout)
        master_layout.addLayout(body_layout)

        central_widget = QWidget()
        central_widget.setLayout(master_layout)

        self.setCentralWidget(central_widget)

    def update_labels(self):
        for i in range (11):
            self.round_state.allocations[i] = 0

            self.round_state.players[i].received_label.setText(str(int(self.round_state.received[i])))
            self.round_state.players[i].sent_label.setText(str(int(self.round_state.sent[i])))
            self.round_state.players[i].popularity_label.setText(str(round(self.round_state.message["POPULARITY"][i])))
            self.round_state.players[i].popularity_over_time.append(self.round_state.message["POPULARITY"][i])
            self.round_state.players[i].allocation_box.setText("0")
            self.jhg_plot.plot(self.round_state.players[i].popularity_over_time)
