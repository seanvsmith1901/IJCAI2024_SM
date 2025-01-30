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
    def __init__(self, client_socket, round_state, round_counter):
        super().__init__()
        self.client_socket = client_socket
        self.round_state = round_state
        self.round_counter = round_counter

    # Once connected to the server, this method is called on a threaded object. Once the thread calls it, it
    # continuously listens for data from the server. This is the entrance point for all functionality based off of
    # receiving data from the server. Kinda a switch board of sorts
    def start_listening(self,):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                json_data = json.dumps(json.loads(data.decode()))
                if "ID" in json_data:
                    self.round_state.client_id = json.loads(json_data)["ID"]
                if "ROUND" in json_data:
                    json_data = json.loads(json_data)
                    self.update_received_label(json_data)
                    self.update_sent_label(json_data)

                    self.round_state.round_number = int(json_data["ROUND"])
                    self.round_counter.setText(f'Round {int(json_data["ROUND"]) + 1}')

    def update_received_label(self, json_data):
        self.round_state.received = json_data["RECEIVED"]
        for i in range (11):
            self.round_state.players[i].received_label.setText(str(self.round_state.received[i]))

    def update_sent_label(self, json_data):
        self.round_state.sent = json_data["SENT"]
        for i in range (11):
            self.round_state.players[i].sent_label.setText(str(self.round_state.sent[i]))

class MainWindow(QMainWindow):
    def __init__(self, client_socket):
        round_state = RoundState()
        super().__init__()

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

        self.worker = Worker(client_socket, round_state, roundCounter)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start_listening)
        self.worker_thread.start()