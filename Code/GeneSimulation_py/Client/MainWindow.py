import json

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget

from VoteButton import VoteButton

class Worker(QObject):
    data_received = pyqtSignal(str)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def start_listening(self):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                # This just has to be wrong. Got to be a better way... But I can't find it.
                json_data = json.dumps(json.loads(data.decode()))
                if "RESULT" in json_data:
                    vote_matrix = (json.loads(json_data))["RESULTS"]
                    print(vote_matrix)

class MainWindow(QMainWindow):
    def update_text(self, label):
        label.setText("AHHHHHHHH!")
        print("Ya tu sabes")

    def __init__(self, client_socket):
        super().__init__()


        # Set up widgets
        self.setWindowTitle("My App")

        self.voteLabel = QLabel()
        self.voteLabel.setText("Vote for president! (or whatever we're voting for)")
        self.voteLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voteBox = QLineEdit(self)

        # Clicking this button sends the vote in voteBox to the server
        self.voteButton = VoteButton(client_socket, "Vote", self.voteBox, self.voteLabel)

        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.voteLabel)
        layout.addWidget(self.voteBox)
        layout.addWidget(self.voteButton)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.worker = Worker(client_socket)
        self.worker.data_received.connect(self.update_text)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start_listening)
        self.worker_thread.start()

    # def create_vote_table(self):
    #     self.tableWidget = QTableWidget()