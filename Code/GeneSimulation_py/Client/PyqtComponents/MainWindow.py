import json
from functools import partial

import pyqtgraph as pg

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QStackedLayout, QTabWidget, \
    QGridLayout, QPushButton, QSizePolicy

from .JhgTab import JhgTab
# if this is breaking stuff for you garrett, let me know. The imports always break on my end if I don't do this.
from Code.GeneSimulation_py.Client.RoundState import RoundState

from Code.GeneSimulation_py.Client.ServerListener import ServerListener

from .SocialChoicePanel import SocialChoicePanel


class MainWindow(QMainWindow):
    SC_vote = pyqtSignal()
    def __init__(self, client_socket):
        self.round_state = RoundState()
        self.client_socket = client_socket
        super().__init__()

        # This is dynamically updated elsewhere, so it must exist before the SeverListener. It is finally added to
        # a layout in JhgPanel.py
        self.token_label = QLabel()
        self.jhg_plot = pg.PlotWidget()
        tabs = QTabWidget()

        # The QLabels used to display the utility values of each choice in the social choice game
        self.utility_qlabels = []
        self.cause_table_layout = QGridLayout()
        self.cause_table = QWidget()




        # Header - Even though it's just one element, needs to be placed in a layout to play nice with being added
        headerLayout = QHBoxLayout()
        round_counter = QLabel("Round 1")
        round_counter_font = QFont()
        round_counter_font.setPointSize(20)
        round_counter.setFont(round_counter_font)
        headerLayout.addWidget(round_counter)

        # Listens for incoming data from the server. Must be before the body layout (so that the elements that will be
        # used in JHG_panel exist as they are created when the player objects are created).
        # Note that any elements that you want to dynamically update based on server response need to be passed. This
        # means that all the graph elements need to be created here in MainWindow and then passed to SeverListener
        self.ServerListener = ServerListener(self, client_socket, self.round_state, round_counter, self.token_label, self.jhg_plot, tabs, self.utility_qlabels)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)

        self.ServerListener.update_jhg_round_signal.connect(self.update_jhg_labels)
        self.ServerListener.create_sc_round_signal.connect(self.create_sc_labels)
        self.ServerListener.update_sc_round_signal.connect(self.update_sc_labels)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)
        self.ServerListener_thread.start()

        # Body
        jhg_tab = JhgTab(self.round_state, client_socket, self.token_label, self.jhg_plot)

        # Add the other layouts to the master layout

        JHG_tab = QWidget()
        JHG_layout = QVBoxLayout()
        JHG_layout.addLayout(headerLayout)
        JHG_layout.addLayout(jhg_tab)
        JHG_tab.setLayout(JHG_layout)

        self.social_choice_tab = QWidget()
        # self.social_choice_tab.setLayout(SocialChoicePanel(self.round_state, self))

        tabs.addTab(JHG_tab, "JHG")
        tabs.addTab(self.social_choice_tab, "Social Choice")

        self.setCentralWidget(tabs)

    def update_jhg_labels(self):
        for i in range (11):
            self.round_state.allocations[i] = 0

            self.round_state.players[i].received_label.setText(str(int(self.round_state.received[i])))
            self.round_state.players[i].sent_label.setText(str(int(self.round_state.sent[i])))
            self.round_state.players[i].popularity_label.setText(str(round(self.round_state.message["POPULARITY"][i])))
            self.round_state.players[i].popularity_over_time.append(self.round_state.message["POPULARITY"][i])
            self.round_state.players[i].allocation_box.setText("0")
            self.jhg_plot.plot(self.round_state.players[i].popularity_over_time)

    def create_sc_labels(self):
        self.utility_qlabels.clear()

        # Add the player id column
        self.cause_table_layout.addWidget(QLabel("Player"), 0, 0)
        self.cause_table_layout.setColumnStretch(0, 1)
        for player in self.round_state.players:
            print("this is the client_id ", self.round_state.client_id, " and this is the player player id ", player.id)
            if (str(self.round_state.client_id) == str(player.id)):
                self.cause_table_layout.addWidget(QLabel(str(player.id + 1) + " You :)"), player.id + 1, 0)
            self.cause_table_layout.addWidget(QLabel(str(player.id + 1)), player.id + 1, 0)

        # For each cause
        for i in range(self.round_state.num_causes):
            self.cause_table_layout.addWidget(QLabel("Cause #" + str(i)), 0, i + 1)
            self.cause_table_layout.setColumnStretch(i + 1, 1)
            row = []
            # Create a Qlabel, add it to self.utility_qlabels, and add it to the cause_table_layout
            for j in range(self.round_state.num_players):
                row.append(QLabel("0"))
                self.cause_table_layout.addWidget(row[j], j + 1, i + 1)
            self.utility_qlabels.append(row)

            vote_button = QPushButton("Vote")
            vote_button.clicked.connect(partial(self.sc_vote, i))
            button_layout = QHBoxLayout()
            button_layout.addWidget(vote_button)
            button_layout.addStretch(1)
            self.cause_table_layout.addLayout(button_layout, self.round_state.num_players + 2, i + 1)

        self.social_choice_tab.setLayout(self.cause_table_layout)

    def update_sc_labels(self):
        # For each cause column...
        for i in range(self.round_state.num_causes):
            for j in range(self.round_state.num_players):
                self.utility_qlabels[i][j].setText(str(self.round_state.utilities[j][i]))

    def sc_vote(self, vote):
        message = {
            "CLIENT_ID": self.round_state.client_id,
            "FINAL_VOTE": vote,
        }
        self.client_socket.send(json.dumps(message).encode())
        print("voted")