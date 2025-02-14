import json
import time
from functools import partial
from collections import Counter

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

#          l. blue,   red,       orange,    yellow,    pink,      purple,    black,     teal,      l. green,  d. green,   d. blue,  gray
COLORS = ["#1e88e4", "#e41e1e", "#f5a115", "#f3e708", "#e919d3", "#a00fb9", "#000000", "#1fedbd", "#82e31e", "#417a06", "#1e437e", "#9b9ea4"]


class MainWindow(QMainWindow):
    SC_vote = pyqtSignal()

    def __init__(self, client_socket):
        self.round_state = RoundState()
        self.client_socket = client_socket
        super().__init__()

        # keep track of current vote
        self.current_vote = None

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

        #JHG tab setup
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
        tabs.setTabEnabled(0, False)

        self.nodes_dict = {}

    def update_jhg_labels(self):
        for i in range(self.round_state.num_players):
            self.round_state.allocations[i] = 0
            self.round_state.players[i].received_label.setText(str(int(self.round_state.received[i])))
            self.round_state.players[i].sent_label.setText(str(int(self.round_state.sent[i])))
            self.round_state.players[i].popularity_label.setText(str(round(self.round_state.message["POPULARITY"][i])))
            self.round_state.players[i].popularity_over_time.append(self.round_state.message["POPULARITY"][i])
            self.round_state.players[i].allocation_box.setText("0")
            pen = pg.mkPen(COLORS[i])
            self.jhg_plot.plot(self.round_state.players[i].popularity_over_time, pen=pen)

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

        self.player_labels = {}
        self.cause_labels = {}

        for i in range(self.round_state.num_players):
            player_id = str(i + 1)
            player_label = QLabel(player_id)

            if str(int(self.round_state.client_id) + 1) == str(player_id):
                player_label.setText(f"{player_id} You :)")
            else:
                player_label.setText(f"{player_id}")

            player_label.setStyleSheet("color: " + COLORS[i]) # no clue if that will work.

            self.player_labels[player_id] = player_label

            self.cause_table_layout.addWidget(player_label, int(player_id), 0)

        # For each cause
        for i in range(self.round_state.num_causes):
            cause_label = QLabel(f"Cause #{i+1}")
            self.cause_table_layout.addWidget(cause_label, 0, i + 1)
            self.cause_table_layout.setColumnStretch(i + 1, 1)
            self.cause_labels[i] = cause_label

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

        # Create a single "Submit" button below the causes and vote buttons
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.sc_submit)
        submit_layout = QHBoxLayout()
        submit_layout.addWidget(submit_button)
        submit_layout.addStretch(1)

        # Add submit button layout at the bottom left of the vote buttons
        self.cause_table_layout.addLayout(submit_layout, self.round_state.num_players + 2, 0, 1,
                                          self.round_state.num_causes)


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
            "POTENTIAL_VOTE": vote,
        }
        self.current_vote = vote
        self.client_socket.send(json.dumps(message).encode())

    def sc_submit(self):
        message = {
            "CLIENT_ID": self.round_state.client_id,
            "FINAL_VOTE" : self.current_vote,
        }
        self.client_socket.send(json.dumps(message).encode())

    def sc_display_winning_vote(self, winning_vote):
        x_val = -1
        y_val = -1
        text = ""
        color = "#e41e1e"
        for node in self.round_state.nodes:
            if node["text"] == "Cause " + str(int(winning_vote)+1):
                x_val = node["x_pos"]
                y_val = node["y_pos"]
                text = node["text"]


        self.ax.annotate(
            text,
            (x_val, y_val),
            textcoords="offset points",
            xytext=(0, 3),
            ha='center',
            fontsize=9,
            color=color,
            weight='bold',
        )

        self.canvas.draw()
        time.sleep(1) # show it red for 3 seconds


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

    def update_graph(self, winning_vote=None):
        radius = 5 # I just happen to know this, no clue if we need to make this adjusatable based on server input.
        if winning_vote:
            winning_vote += 1

        self.ax.clear()
        self.x = []
        self.y = []
        self.type = []
        self.text = []
        for node in self.round_state.nodes:
            mini_dict = {}
            mini_dict["x_pos"] = float(node["x_pos"])
            mini_dict["y_pos"] = float(node["y_pos"])

            self.nodes_dict[node["text"]] = mini_dict
            self.x.append(float(node["x_pos"]))
            self.y.append(float(node["y_pos"]))
            self.type.append(node["type"])
            self.text.append(node["text"])


        colors = []


        for i, (x_val, y_val) in enumerate(zip(self.x, self.y)):
            text = self.text[i]
            if text.startswith("Player"):
                split_string = text.split()
                text = split_string[1]
                color = COLORS[int(split_string[1])-1]
            elif text == "Cause " + str(winning_vote):
                color = "#e41e1e"
            else:
                color = "black"
            self.ax.annotate(
                text,
                (x_val, y_val),
                textcoords="offset points",
                xytext=(0, 3),
                ha='center',
                fontsize=9,
                color=color,
                weight='bold',
            )
            colors.append(color)

        self.ax.scatter(self.x, self.y, marker='o', c=colors)



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

        # circle = Circle((0, 0), radius, color='black', fill=False, lw=2)  # Use Circle from patches
        # self.ax.add_patch(circle)

        self.canvas.draw()



    def update_win(self, winning_vote):

        for i in range(len(self.cause_labels)):
            if winning_vote == i:
                new_string = "WE WON!"
            else:
                new_string = "Cause #" + str(i+1) + " (" + str(winning_vote+1) + ")"
            self.cause_labels[i].setText(new_string)


    def update_votes(self, potential_votes):
        for i in range(len(self.player_labels)):
            player_label = self.player_labels.get(str(int(i) + 1))
            if str(int(self.round_state.client_id) + 1) == str(int(i) + 1):
                new_text = str(int(i) + 1) + " You :) "
            else:
                new_text = str(int(i) + 1)
            player_label.setText(new_text)


        for player_id, vote in potential_votes.items():
            player_label = self.player_labels.get(str(int(player_id) + 1))  # Adjust ID for zero-indexed list
            if player_label:
                if str(int(self.round_state.client_id) + 1) == str(int(player_id)+1):
                    new_text = str(int(player_id) + 1) + " You :) " + "(" + str(vote+1) + ")"
                else:
                    new_text = str(int(player_id) + 1) + " (" + str(vote+1) + ")"
                player_label.setText(new_text)
        total_votes = Counter(potential_votes.values()).most_common(len(self.cause_labels)) # take the second element of the tuple or something

        for i in range(len(self.cause_labels)):
            new_string = "Cause #" + str(i+1) + " (0)"
            self.cause_labels[i].setText(new_string)

        for i in range(len(total_votes)):
            print("this is the tuple ", total_votes[i])
            new_string = "Cause #" + str(total_votes[i][0]+1) + " (" + str(total_votes[i][1]) + ")"
            self.cause_labels[int(total_votes[i][0])].setText(new_string)




