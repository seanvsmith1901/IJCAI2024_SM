import json

from PyQt6.QtWidgets import QPushButton


class VoteButton(QPushButton):

    def __init__(self, client_socket, name, inputTextBox, topLabel):
        super().__init__()
        print(client_socket)

        # Event handlers
        def vote_button_clicked():
            message = {"VOTE": inputTextBox.text()}
            client_socket.send(json.dumps(message).encode())
            self.setDisabled(True)
            topLabel.setText("You already voted.")

        self.setText(name)
        self.clicked.connect(vote_button_clicked)
