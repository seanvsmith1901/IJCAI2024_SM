from PyQt6.QtWidgets import QPushButton


class SubmitButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText('Submit')
        self.setObjectName("JHGSubmitButton")


    def submit(self, round_state, connection_manager):
        connection_manager.send_message("SUBMIT_JHG", round_state.client_id, round_state.jhg_round_num, round_state.get_allocations_list())

        self.setText('Resubmit')
