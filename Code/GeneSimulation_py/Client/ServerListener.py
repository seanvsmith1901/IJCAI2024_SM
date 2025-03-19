import json

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from combinedLayout.SC_functions import update_potential_sc_votes, update_sc_nodes_graph, update_win, \
    update_sc_utilities_labels, update_sc_tornado_graph


class ServerListener(QObject):
    update_jhg_round_signal = pyqtSignal()
    update_sc_round_signal = pyqtSignal()
    disable_sc_buttons_signal = pyqtSignal()
    enable_sc_buttons_signal = pyqtSignal()
    enable_jhg_buttons_signal = pyqtSignal()
    disable_jhg_buttons_signal = pyqtSignal()
    update_jhg_network_graph = pyqtSignal()

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
    # continuously listens for data from the server. This is the entrance point for all functionality based on
    # receiving data from the server. Kinda a switch board of sorts
    def start_listening(self):
        while True:
            try:
                # Receive data in chunks
                data = self.client_socket.recv(4096)
                if data:
                    try:
                        # Attempt to decode and load JSON data
                        json_data = json.loads(data.decode())

                        # Check if "ROUND_TYPE" exists in the parsed JSON data
                        if "ROUND_TYPE" in json_data:
                            if json_data["ROUND_TYPE"] == "jhg":
                                self.tabs.setCurrentIndex(0)
                                self.update_jhg_state(json_data)

                            elif json_data["ROUND_TYPE"] == "sc_init":
                                self.tabs.setCurrentIndex(1)
                                self.round_state.options = json_data["OPTIONS"]
                                self.round_state.nodes = json_data["NODES"]
                                self.round_state.utilities = json_data["UTILITIES"]
                                self.round_state.influence_mat = np.array(json_data["INFLUENCE_MAT"])
                                # self.round_state.relationships_mat = np.array(json_data["RELATION_STRENGTH"])
                                self.update_sc_round_signal.emit()
                                self.enable_sc_buttons_signal.emit()
                                self.disable_jhg_buttons_signal.emit()
                                self.update_jhg_network_graph.emit()

                            elif json_data["ROUND_TYPE"] == "sc_vote":
                                # self.main_window.update_potential_sc_votes(json_data["POTENTIAL_VOTES"])
                                update_potential_sc_votes(self.main_window, json_data["POTENTIAL_VOTES"])

                            elif json_data["ROUND_TYPE"] == "sc_over":  # cris-cross!
                                self.disable_sc_buttons_signal.emit()
                                update_sc_nodes_graph(self.main_window, json_data["WINNING_VOTE"])
                                update_win(self.main_window, json_data["WINNING_VOTE"])
                                new_utilities = json.loads(json.dumps(json_data["NEW_UTILITIES"]))
                                update_sc_utilities_labels(self.main_window, new_utilities, json_data["WINNING_VOTE"])
                                update_sc_tornado_graph(self.main_window, json_data["POSITIVE_VOTE_EFFECTS"],
                                                                      json_data["NEGATIVE_VOTE_EFFECTS"])

                            elif json_data["ROUND_TYPE"] == "sc_in_progress":
                                pass

                        # Handle other cases like SWITCH_ROUND
                        elif "SWITCH_ROUND" in json_data:
                            self.tabs.setCurrentIndex(0)
                            self.enable_jhg_buttons_signal.emit()

                    except json.JSONDecodeError:
                        # Handle error in case of malformed JSON or invalid data
                        print("Received invalid JSON data:", data)
                        continue  # Skip this message and continue receiving more

                    except Exception as e:
                        # Handle any other unexpected errors
                        print(f"Error processing message: {e}")
                        continue  # Continue to the next loop iteration

            except Exception as e:
                # Catch general socket or connection errors
                print(f"Error receiving data: {e}")
                break  # Optionally break or continue listening based on your use case



    # Prepares the client for the next round by updating self.round_state and the gui
    def update_jhg_state(self, json_data):
        self.round_state.message = json_data
        if "RECEIVED" in json_data:
            self.round_state.received = json_data["RECEIVED"]
        self.round_state.sent = json_data["SENT"]
        self.round_state.round_number = int(json_data["ROUND"])
        self.round_state.tokens = self.round_state.num_players * 2
        self.round_state.current_popularities = json_data["POPULARITY"]
        self.jhg_plot.clear()

        self.update_jhg_round_signal.emit()

        self.round_counter.setText(f'Round {self.round_state.round_number + 1}')
        self.token_label.setText(f"Tokens: {self.round_state.tokens}")