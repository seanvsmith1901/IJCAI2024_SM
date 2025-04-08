import json

from PyQt6.QtWidgets import QPushButton, QWidget


class SubmitButton(QPushButton):
    def submit(self, round_state, connection_manager):
        connection_manager.send_message("SUBMIT_JHG", round_state.client_id, round_state.round_number, round_state.get_allocations_list())
        # client_socket.send(round_state.state_to_JSON())

    def __init__(self):
        super().__init__()
        self.setText('Submit')
