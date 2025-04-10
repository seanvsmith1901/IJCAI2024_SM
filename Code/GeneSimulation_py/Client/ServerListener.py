from collections import defaultdict

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from combinedLayout.ui_functions.tornado_graph import update_tornado_graph
from combinedLayout.ui_functions.SC_functions import update_potential_sc_votes, update_sc_nodes_graph, update_win, \
    update_sc_utilities_labels


class ServerListener(QObject):
    update_jhg_round_signal = pyqtSignal()
    update_sc_round_signal = pyqtSignal()
    disable_sc_buttons_signal = pyqtSignal()
    enable_sc_buttons_signal = pyqtSignal()
    enable_jhg_buttons_signal = pyqtSignal()
    disable_jhg_buttons_signal = pyqtSignal()
    update_jhg_network_graph = pyqtSignal()


    def __init__(self, main_window, connection_manager, round_state, round_counter, token_label, jhg_popularity_graph, tabs, utility_qlabels):
        super().__init__()
        self.response_functions = defaultdict(lambda: self.unknown_message_type_handler, {
            "JHG_OVER": self.JHG_OVER,
            "SC_INIT": self.SC_INIT,
            "SC_VOTES": self.SC_VOTES,
            "SC_OVER": self.SC_OVER,
        })

        self.connection_manager = connection_manager
        self.round_state = round_state
        self.round_counter = round_counter
        self.main_window = main_window
        self.token_label = token_label
        self.jhg_popularity_graph = jhg_popularity_graph
        self.tabs = tabs
        self.utility_qlabels = utility_qlabels


    # Once connected to the server, this method is called on a threaded object. Once the thread calls it, it
    # continuously listens for data from the server. This is the entrance point for all functionality based on
    # receiving data from the server. Kinda a switch board of sorts
    def start_listening(self):
        while True:
            # Get all of the messages from the server waiting
            messages = self.connection_manager.get_message()
            for message in messages:
                # Run the appropriate function based on the message type
                self.response_functions[message["TYPE"]](message)


    def JHG_OVER(self, message):
        self.tabs.setCurrentIndex(0)
        self.update_jhg_state(message)


    def SC_INIT(self, message):
        self.tabs.setCurrentIndex(1)
        self.round_state.options = message["OPTIONS"]
        self.round_state.nodes = message["NODES"]
        self.round_state.utilities = message["UTILITIES"]
        self.round_state.influence_mat = np.array(message["INFLUENCE_MAT"])

        # TODO: Combine these signals
        self.update_sc_round_signal.emit()
        self.enable_sc_buttons_signal.emit()
        self.disable_jhg_buttons_signal.emit()
        self.update_jhg_network_graph.emit()


    def SC_VOTES(self, message):
        update_potential_sc_votes(self.main_window, message["POTENTIAL_VOTES"])


    def SC_OVER(self, message):
        self.disable_sc_buttons_signal.emit()
        update_sc_nodes_graph(self.main_window, message["WINNING_VOTE"])
        update_win(self.main_window, message["WINNING_VOTE"])
        # new_utilities = json.loads(json.dumps(message["NEW_UTILITIES"]))
        new_utilities = message["NEW_UTILITIES"]
        update_sc_utilities_labels(self.main_window, new_utilities, message["WINNING_VOTE"], message["VOTES"], message["UTILITIES"])
        update_tornado_graph(self.main_window, self.main_window.tornado_ax, message["POSITIVE_VOTE_EFFECTS"],
                                              message["NEGATIVE_VOTE_EFFECTS"])

        # Switch to JHG
        self.tabs.setCurrentIndex(0)
        self.enable_jhg_buttons_signal.emit()


    def unknown_message_type_handler(self, message):
        print(f"[Warning] Unknown message TYPE: {message.get('TYPE')}, message: {message}")


    # Prepares the client for the next round by updating self.round_state and the gui
    def update_jhg_state(self, json_data):
        self.round_state.message = json_data

        self.round_state.received = json_data["RECEIVED"]
        self.round_state.sent = json_data["SENT"]
        self.round_state.round_number = json_data["ROUND"]
        self.round_state.tokens = self.round_state.num_players * 2
        self.round_state.current_popularities = json_data["POPULARITY"]
        self.jhg_popularity_graph.clear()

        self.update_jhg_round_signal.emit()

        self.round_counter.setText(f'Round {self.round_state.round_number + 1}')
        self.token_label.setText(f"Tokens: {self.round_state.tokens}")
