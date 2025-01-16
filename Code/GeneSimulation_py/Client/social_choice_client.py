import json
import sys
import socket

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextLine
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit

def start_client():
    global client_ID
    # host = '192.168.30.17'  # The server's IP address
    host = '127.0.0.1'  # your local host address cause you're working from home.
    port = 12345  # The port number to connect to
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))
    # Send data to the server

    app = QApplication(sys.argv)
    window = MainWindow(client_socket)
    window.show()
    app.exec()

class MainWindow(QMainWindow):
    def __init__(self, client_socket):
        super().__init__()

        # Event handlers
        def vote_button_clicked():
            print(client_socket)
            message = {"NEW_INPUT": "new_input"}
            client_socket.send(json.dumps(message).encode())


        # Set up widgets
        self.setWindowTitle("My App")

        self.voteLabel = QLabel()
        self.voteLabel.setText("Vote for president! (or whatever we're voting for)")
        self.voteBox = QLineEdit(self)

        self.voteButton = QPushButton("Vote")
        self.voteButton.clicked.connect(vote_button_clicked)

        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.voteLabel)
        layout.addWidget(self.voteBox)
        layout.addWidget(self.voteButton)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

start_client()


