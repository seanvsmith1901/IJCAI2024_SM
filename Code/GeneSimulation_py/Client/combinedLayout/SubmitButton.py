import json

from PyQt6.QtWidgets import QPushButton, QWidget


class SubmitButton(QPushButton):
    def submit(self, round_state, client_socket):
        client_socket.send(json.dumps(round_state.state_to_JSON()).encode())

    def __init__(self):
        super().__init__()
        self.setText('Submit')
