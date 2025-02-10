import json
from functools import partial

import pyqtgraph as pg

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QStackedLayout, QTabWidget, \
    QGridLayout, QPushButton, QSizePolicy

import pyqtgraph as pg
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as plt
plt.use("QtAgg")

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QStackedLayout, QTabWidget, \
    QGridLayout, QPushButton, QSizePolicy

from matplotlib.patches import Circle  # Import Circle from matplotlib.patches

from .JhgTab import JhgTab

# Sean's imports
# from Code.GeneSimulation_py.Client.RoundState import RoundState
#
# from Code.GeneSimulation_py.Client.ServerListener import ServerListener

# Garrett's imports
from RoundState import RoundState

from ServerListener import ServerListener

from .SocialChoicePanel import SocialChoicePanel


class MainWindow(QMainWindow):
    SC_vote = pyqtSignal()

    def __init__(self, client_socket):
        self.round_state = RoundState()
        self.client_socket = client_socket
        super().__init__()

        # Dynamically updated elements
        self.token_label = QLabel()
        self.jhg_plot = pg.PlotWidget()
        tabs = QTabWidget()

        # Initialize the social choice tab
        self.social_choice_tab = QWidget()

        # The QLabels used to display the utility values of each choice in the social choice game
        self.utility_qlabels = []
        self.cause_table_layout = QGridLayout()
        self.cause_table = QWidget()

        # Header for JHG tab
        headerLayout = QHBoxLayout()
        round_counter = QLabel("Round 1")
        round_counter_font = QFont()
        round_counter_font.setPointSize(20)
        round_counter.setFont(round_counter_font)
        headerLayout.addWidget(round_counter)

        # Server Listener setup
        self.ServerListener = ServerListener(self, client_socket, self.round_state, round_counter, self.token_label, self.jhg_plot, tabs, self.utility_qlabels)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)

        self.ServerListener.update_jhg_round_signal.connect(self.update_jhg_labels)
        self.ServerListener.create_sc_round_signal.connect(self.create_sc_labels)
        self.ServerListener.update_sc_round_signal.connect(self.update_sc_labels)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)
        self.ServerListener_thread.start()

        # JHG tab setup
        jhg_tab = JhgTab(self.round_state, client_socket, self.token_label, self.jhg_plot)
        JHG_tab = QWidget()
        JHG_layout = QVBoxLayout()
        JHG_layout.addLayout(headerLayout)
        JHG_layout.addLayout(jhg_tab)
        JHG_tab.setLayout(JHG_layout)

        # Add tabs to QTabWidget
        tabs.addTab(JHG_tab, "JHG")
        tabs.addTab(self.social_choice_tab, "Social Choice")

        # Set the central widget to the tabs widget
        self.setCentralWidget(tabs)

    def update_jhg_labels(self):
        for i in range(11):
            self.round_state.allocations[i] = 0
            self.round_state.players[i].received_label.setText(str(int(self.round_state.received[i])))
            self.round_state.players[i].sent_label.setText(str(int(self.round_state.sent[i])))
            self.round_state.players[i].popularity_label.setText(str(round(self.round_state.message["POPULARITY"][i])))
            self.round_state.players[i].popularity_over_time.append(self.round_state.message["POPULARITY"][i])
            self.round_state.players[i].allocation_box.setText("0")
            self.jhg_plot.plot(self.round_state.players[i].popularity_over_time)

    def create_sc_labels(self):
        self.utility_qlabels.clear()

        # Create the QWidget for the social choice tab if not already created
        if not self.social_choice_tab.layout():
            self.social_choice_tab.setLayout(QVBoxLayout())

        # Clear the previous table layout and setup a fresh one
        self.cause_table_layout = QGridLayout()
        self.utility_qlabels.clear()

        # Add the player id column
        self.cause_table_layout.addWidget(QLabel("Player"), 0, 0)
        self.cause_table_layout.setColumnStretch(0, 1)

        for player in self.round_state.players:
            if str(self.round_state.client_id) == str(player.id):
                self.cause_table_layout.addWidget(QLabel(f"{player.id + 1} You :)"), player.id + 1, 0)
            self.cause_table_layout.addWidget(QLabel(str(player.id + 1)), player.id + 1, 0)

        # For each cause
        for i in range(self.round_state.num_causes):
            self.cause_table_layout.addWidget(QLabel(f"Cause #{i}"), 0, i + 1)
            self.cause_table_layout.setColumnStretch(i + 1, 1)
            row = []
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

        # Now add the graph to the layout
        graph_layout = QVBoxLayout()  # Create a new layout for the graph
        self.graph_canvas = self.create_graph()  # Call the create_graph method
        graph_layout.addWidget(self.graph_canvas)  # Add the graph widget to the layout

        # Add the graph layout to the social choice tab
        self.social_choice_tab.layout().addLayout(graph_layout)  # Add graph to the social choice tab layout

        # Set the layout for the cause table in the social choice tab
        self.social_choice_tab.layout().addLayout(self.cause_table_layout)

    def update_sc_labels(self):
        for i in range(self.round_state.num_causes):
            for j in range(self.round_state.num_players):
                self.utility_qlabels[i][j].setText(str(self.round_state.utilities[j][i]))
        self.update_graph()

    def sc_vote(self, vote):
        message = {
            "CLIENT_ID": self.round_state.client_id,
            "FINAL_VOTE": vote,
        }
        self.client_socket.send(json.dumps(message).encode())

    def create_graph(self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.x = np.linspace(0, 10, 100)
        self.y = np.sin(self.x)
        self.ax.plot(self.x, self.y)
        self.canvas = FigureCanvas(self.fig)
        self.type = []
        self.text = []
        return self.canvas

    def update_graph(self):
        radius = 5 # I just happen to know this, no clue if we need to make this adjusatable based on server input.

        self.ax.clear()
        self.x = []
        self.y = []
        self.type = []
        self.text = []
        for node in self.round_state.nodes:
            self.x.append(float(node["x_pos"]))
            self.y.append(float(node["y_pos"]))
            self.type.append(node["type"])
            self.text.append(node["text"])

        self.ax.scatter(self.x, self.y, marker='o')

        for i, (x_val, y_val) in enumerate(zip(self.x, self.y)):
            text = self.text[i]
            if text.startswith("Player"):
                text = text[-1]
            self.ax.annotate(
                text,
                (x_val, y_val),
                textcoords="offset points",
                xytext=(0, 3),
                ha='center',
                fontsize=9,
                color='black',
                weight='bold',
            )



        # Clear the axis spines (the square border)
        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['left'].set_color('none')
        self.ax.spines['bottom'].set_color('none')

        self.ax.set_xticks([])  # Remove x-axis ticks
        self.ax.set_yticks([])  # Remove y-axis ticks
        self.ax.set_xticklabels([])  # Optionally remove x-axis labels
        self.ax.set_yticklabels([])  # Optionally remove y-axis labels

        self.ax.set_aspect('equal', adjustable='box')

        circle = Circle((0, 0), radius, color='black', fill=False, lw=2)  # Use Circle from patches
        self.ax.add_patch(circle)

        self.canvas.draw()