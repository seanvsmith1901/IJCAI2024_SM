from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit

from VoteButton import VoteButton


class MainWindow(QMainWindow):
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