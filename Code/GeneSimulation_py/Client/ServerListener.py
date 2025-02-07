import json

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QLabel


class ServerListener(QObject):
    update_jhg_round_signal = pyqtSignal()
    update_sc_round_signal = pyqtSignal()
    create_sc_round_signal = pyqtSignal()
    def __init__(self, main_window, client_socket, round_state, round_counter, token_label, jhg_plot, tabs, utility_qlabels):
        super().__init__()
        self.client_socket = client_socket
        self.round_state = round_state
        self.round_counter = round_counter
        self.main_window = main_window
        self.token_label = token_label
        self.jhg_plot = jhg_plot
        self.tabs = tabs
        self.utility_qlabels = utility_qlabels

    # Once connected to the server, this method is called on a threaded object. Once the thread calls it, it
    # continuously listens for data from the server. This is the entrance point for all functionality based off of
    # receiving data from the server. Kinda a switch board of sorts
    def start_listening(self):
        while True:
            data = self.client_socket.recv(4096)
            if data:
                json_data = json.dumps(json.loads(data.decode()))
                # The server sends a packet with "ID" the first time that the client connects. Set up the client based on the passed ID
                if "ID" in json_data:
                    self.round_state.client_id = json.loads(json_data)["ID"]
                    self.main_window.setWindowTitle(f"Junior High Game: Player {int(self.round_state.client_id) + 1}")
                    self.round_state.num_players = json.loads(json_data)["NUM_PLAYERS"]
                    self.round_state.num_causes = json.loads(json_data)["NUM_CAUSES"]
                    self.create_sc_round_signal.emit()
                if "ROUND_TYPE" in json_data:
                    json_data = json.loads(json_data)
                    if json_data["ROUND_TYPE"] == "jhg":
                        self.tabs.setCurrentIndex(0)
                        self.update_jhg_state(json_data)

                    elif json_data["ROUND_TYPE"] == "sc_init":
                        self.tabs.setCurrentIndex(1)
                        self.round_state.options = json_data["OPTIONS"]
                        self.round_state.nodes = json_data["NODES"]
                        self.round_state.utilities = json_data["UTILITIES"]
                        #self.round_state.relations = json_data["RELATION_STRENGTH"]
                        self.update_sc_round_signal.emit()
                    elif json_data["ROUND_TYPE"] == "sc_in_progress":
                        pass



    # Prepares the client for the next round by updating self.round_state and the gui
    def update_jhg_state(self, json_data):
        self.round_state.message = json_data
        self.round_state.received = json_data["RECEIVED"]
        self.round_state.sent = json_data["SENT"]
        self.round_state.round_number = int(json_data["ROUND"])
        self.round_state.tokens = self.round_state.num_players * 2

        self.jhg_plot.clear()

        self.update_jhg_round_signal.emit()

        self.round_counter.setText(f'Round {self.round_state.round_number + 1}')
        self.token_label.setText(f"Tokens: {self.round_state.tokens}")