import json

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from .BodyLayout import BodyLayout
from RoundState import RoundState


class Worker(QObject):
    data_received = pyqtSignal(str)

    def __init__(self, client_socket, round_state):
        super().__init__()
        self.client_socket = client_socket
        self.round_state = round_state

    def start_listening(self):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                json_data = json.dumps(json.loads(data.decode()))
                if "ID" in json_data:
                    print(json.loads(json_data)["ID"])
                    self.round_state.client_id = json.loads(json_data)["ID"]
                if "RESULT" in json_data:
                    print("result")

class MainWindow(QMainWindow):
    def __init__(self, client_socket):
        round_state = RoundState()
        super().__init__()

        self.worker = Worker(client_socket, round_state)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start_listening)
        self.worker_thread.start()

        self.setWindowTitle("Junior High Game")

        # Header
        headerLayout = QHBoxLayout()
        roundCounter = QLabel("Round 1")
        roundCounterFont = QFont()
        roundCounterFont.setPointSize(20)
        roundCounter.setFont(roundCounterFont)
        headerLayout.addWidget(roundCounter)

        # Body
        body_layout = BodyLayout(round_state, client_socket)

        # Add the other layouts to the master layout
        master_layout = QVBoxLayout()
        master_layout.addLayout(headerLayout)
        master_layout.addLayout(body_layout)

        central_widget = QWidget()
        central_widget.setLayout(master_layout)

        self.setCentralWidget(central_widget)