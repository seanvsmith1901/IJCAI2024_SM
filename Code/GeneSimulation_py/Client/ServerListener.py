import json

from PyQt6.QtCore import QObject


class ServerListener(QObject):
    def __init__(self, main_window, client_socket, round_state, round_counter, token_label, jhg_plot):
        super().__init__()
        self.client_socket = client_socket
        self.round_state = round_state
        self.round_counter = round_counter
        self.main_window = main_window
        self.token_label = token_label
        self.jhg_plot = jhg_plot

    # Once connected to the server, this method is called on a threaded object. Once the thread calls it, it
    # continuously listens for data from the server. This is the entrance point for all functionality based off of
    # receiving data from the server. Kinda a switch board of sorts
    def start_listening(self):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                json_data = json.dumps(json.loads(data.decode()))
                if "ID" in json_data:
                    self.round_state.client_id = json.loads(json_data)["ID"]
                    self.main_window.setWindowTitle(f"Junior High Game: Player {int(self.round_state.client_id) + 1}")
                    self.round_state.num_players = json.loads(json_data)["NUM_PLAYERS"]
                if "ROUND" in json_data:
                    json_data = json.loads(json_data)
                    self.update_round_state(json_data)

    # Prepares the client for the next round by updating self.round_state and the gui
    def update_round_state(self, json_data):
        self.round_state.received = json_data["RECEIVED"]
        self.round_state.sent = json_data["SENT"]
        self.round_state.round_number = int(json_data["ROUND"])

        self.jhg_plot.clear()

        for i in range (11):
            self.round_state.allocations[i] = 0
            self.round_state.tokens = self.round_state.num_players * 2

            self.round_state.players[i].received_label.setText(str(self.round_state.received[i]))
            self.round_state.players[i].sent_label.setText(str(self.round_state.sent[i]))
            self.round_state.players[i].popularity_label.setText(str(round(json_data["POPULARITY"][i])))
            self.round_state.players[i].popularity_over_time.append(json_data["POPULARITY"][i])
            self.round_state.players[i].allocation_box.setText("0")
            self.jhg_plot.plot(self.round_state.players[i].popularity_over_time)
            # print(self.round_state.players[i].popularity_over_time)



        self.round_counter.setText(f'Round {self.round_state.round_number + 1}')
        self.token_label.setText(f"Tokens: {self.round_state.tokens}")