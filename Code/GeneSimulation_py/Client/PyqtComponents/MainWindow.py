import json
import time
from functools import partial
from collections import Counter
import pyqtgraph as pg
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as plt
plt.use("QtAgg")
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QPushButton
from .JhgTab import JhgTab
from RoundState import RoundState
from ServerListener import ServerListener
from .Arrow import Arrow

#          l. blue,   red,       orange,    yellow,    pink,      purple,    black,     teal,      l. green,  d. green,   d. blue,  gray
# COLORS = ["#1e88e4", "#e41e1e", "#f5a115", "#f3e708", "#e919d3", "#a00fb9", "#000000", "#1fedbd", "#82e31e", "#417a06", "#1e437e", "#9b9ea4"]
COLORS = ["#FF9191", "#D15C5E", "#965875", "#FFF49F", "#B1907D", "#FFAFD8", "#C9ADE9", "#fdbf6f"]

class MainWindow(QMainWindow):
    SC_vote = pyqtSignal()

    def __init__(self, client_socket, num_players, num_causes, id):
        super().__init__()
        # self.setStyleSheet("background-color: #FF171717;")
        self.setStyleSheet("color: #FFEBEBEB; background-color: #FF171717;")
        # This window is very dependent on things happening in the correct order.
        # If you mess with it, you might break a lot of things.
        # It has been broken up into blocks below to try to mitigate that

    #1# Block one: Sets up the round_state and client socket. Must be the first thing done
        self.tornado_ax = None
        self.tornado_canvas = None
        self.graph_canvas = None
        self.player_labels = {}
        self.cause_labels = {}
        self.jhg_buttons = []
        self.round_state = RoundState(id, num_players, num_causes, self.jhg_buttons)
    #/1#

    #2# Block two: Creates the elements that will be passed to the server listener for dynamic updating. Must happen before the server listener is created
        self.client_socket = client_socket

        self.setWindowTitle(f"Junior High Game: Player {int(self.round_state.client_id) + 1}")

        # keep track of the current vote
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
    #/2#

    #3# Block three: Sets up the server listener, which depends on blocks 1&2.
        # Server Listener setup
        self.ServerListener = ServerListener(self, client_socket, self.round_state, round_counter, self.token_label, self.jhg_plot, tabs, self.utility_qlabels)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)

        # pyqt signal hook-ups
        self.ServerListener.update_jhg_round_signal.connect(self.update_jhg_labels)
        self.ServerListener.update_sc_round_signal.connect(self.update_sc_labels)
        self.ServerListener.disable_sc_buttons_signal.connect(self.disable_sc_buttons)
        self.ServerListener.enable_sc_buttons_signal.connect(self.enable_sc_buttons)
        self.ServerListener.disable_jhg_buttons_signal.connect(self.disable_jhg_buttons)
        self.ServerListener.enable_jhg_buttons_signal.connect(self.enable_jhg_buttons)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)


        self.ServerListener_thread.start()
    #/3#

    #4# Block four: Finishes setting up the client, especially the JHG and SC tabs. Dependent on blocks 1&2
        self.create_sc_labels()
        # JHG tab setup
        jhg_tab = JhgTab(self.round_state, client_socket, self.token_label, self.jhg_plot, self.jhg_buttons)
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
    #/4#



        self.nodes_dict = {}
        self.arrows = {}

    def update_jhg_labels(self):
        for i in range(self.round_state.num_players):
            # If players[i] is the client, show tokens kept. Else, show the received and sent tokens for that player
            if i == int(self.round_state.client_id):
                self.round_state.players[i].kept_number_label.setText(str(int(self.round_state.received[i])))
            else:
                self.round_state.players[i].received_label.setText(str(int(self.round_state.received[i])))
                self.round_state.players[i].sent_label.setText(str(int(self.round_state.sent[i])))

            self.round_state.allocations[i] = 0
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

        # Clear the previous table layout and set up a fresh one
        self.cause_table_layout = QGridLayout()
        self.utility_qlabels.clear()

        # Add the player id column
        self.cause_table_layout.addWidget(QLabel("Player"), 0, 0)
        self.cause_table_layout.addWidget(QLabel("Utility"), 0, 1)
        self.cause_table_layout.setColumnStretch(0, 1)

        self.player_labels = {}
        self.cause_labels = {}

        for player in self.round_state.players:
            player_id = str(player.id + 1)
            player_label = QLabel(player_id)

            if str(int(self.round_state.client_id) + 1) == str(player_id):
                player_label.setText(f"{player_id} You :)")
            else:
                player_label.setText(f"{player_id}")

            player_label.setStyleSheet("color: " + COLORS[player.id])

            self.player_labels[player_id] = player_label
            utilities_label = player.utility_label

            self.cause_table_layout.addWidget(player_label, int(player_id), 0)
            self.cause_table_layout.addWidget(utilities_label, int(player_id), 1)

        self.sc_buttons = []
        # For each cause
        for i in range(self.round_state.num_causes):
            cause_label = QLabel(f"Cause #{i+1}")
            self.cause_table_layout.addWidget(cause_label, 0, i + 2)
            self.cause_table_layout.setColumnStretch(i + 1, 1)
            self.cause_labels[i] = cause_label

            row = []
            for j in range(self.round_state.num_players):
                row.append(QLabel("0"))
                self.cause_table_layout.addWidget(row[j], j + 1, i + 2)
            self.utility_qlabels.append(row)

            vote_button = QPushButton("Vote")
            vote_button.setEnabled(False)
            self.sc_buttons.append(vote_button)
            vote_button.clicked.connect(partial(self.sc_vote, i))
            button_layout = QHBoxLayout()
            button_layout.addWidget(vote_button)
            button_layout.addStretch(1)
            self.cause_table_layout.addLayout(button_layout, self.round_state.num_players + 2, i + 2)

        # Create a single "Submit" button below the causes and vote buttons
        submit_button = QPushButton("Submit")
        submit_button.setEnabled(False)
        submit_button.clicked.connect(self.sc_submit)
        self.sc_buttons.append(submit_button)
        submit_layout = QHBoxLayout()
        submit_layout.addWidget(submit_button)
        submit_layout.addStretch(1)

        # Add submit button layout at the bottom left of the vote buttons
        self.cause_table_layout.addLayout(submit_layout, self.round_state.num_players + 2, 0, 1,
                                          self.round_state.num_causes)


        # Now add the graph to the layout
        graphs_layout = QVBoxLayout()
        self.graph_canvas = self.create_nodes_graph()  # Call the create_graph method
        self.tornado_canvas = self.create_tornado_graph()

        sc_graph_tabs = QTabWidget()
        sc_graph_tabs.addTab(self.graph_canvas, "Nodes Graph")
        sc_graph_tabs.addTab(self.tornado_canvas, "Effect of past votes")
        graphs_layout.addWidget(sc_graph_tabs)

        self.social_choice_tab.layout().addLayout(graphs_layout)
        # Set the layout for the cause table in the social choice tab
        self.social_choice_tab.layout().addLayout(self.cause_table_layout)

    def update_sc_labels(self):
        for i in range(self.round_state.num_causes):
            for j in range(self.round_state.num_players):
                self.utility_qlabels[i][j].setText(str(self.round_state.utilities[j][i]))
        self.update_nodes_graph()

    def update_utilities_labels(self, new_utilities):
        for i in range(self.round_state.num_players):
            self.round_state.players[i].utility_label.setText(str(new_utilities[str(i)]))

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


        self.nodes_ax.annotate(
            text,
            (x_val, y_val),
            textcoords="offset points",
            xytext=(0, 3),
            ha='center',
            fontsize=9,
            color=color,
            weight='bold',
        )

        self.nodes_canvas.draw()
        time.sleep(1) # show it red for 3 seconds


    def create_nodes_graph(self):
        self.nodes_fig = Figure(figsize=(5, 4), dpi=100)
        self.nodes_ax = self.nodes_fig.add_subplot(111)
        self.nodes_x = np.linspace(0, 10, 100)
        self.nodes_y = np.sin(self.nodes_x)
        self.nodes_ax.plot(self.nodes_x, self.nodes_y)
        self.nodes_canvas = FigureCanvas(self.nodes_fig)
        self.nodes_type = []
        self.nodes_text = []

        self.nodes_fig.patch.set_facecolor("#282828ff")
        self.nodes_ax.set_facecolor("#282828ff")
        self.nodes_ax.tick_params(colors="#EBEBEB")
        self.nodes_ax.tick_params(colors="#EBEBEB")
        for spine in self.nodes_ax.spines.values():
            spine.set_color("#EBEBEB")
        return self.nodes_canvas

    def create_tornado_graph(self):
        self.tornado_fig = Figure(figsize=(5, 4), dpi=100)
        self.tornado_y = np.arange(self.round_state.num_players)
        self.tornado_ax = self.tornado_fig.add_subplot(111)

        self.tornado_ax.barh(self.tornado_y, [0 for _ in range(self.round_state.num_players)], color='red', label='Decrease Impact')
        self.tornado_ax.barh(self.tornado_y, [0 for _ in range(self.round_state.num_players)], color='green', label='Increase Impact')

        self.tornado_fig.patch.set_facecolor("#282828ff")
        self.tornado_ax.set_facecolor("#282828ff")
        self.tornado_ax.tick_params(colors="#EBEBEB")
        self.tornado_ax.tick_params(colors="#EBEBEB")
        for spine in self.tornado_ax.spines.values():
            spine.set_color("#EBEBEB")

        return FigureCanvas(self.tornado_fig)

    def update_tornado_graph(self, positive_vote_effects, negative_vote_effects):
        self.tornado_ax.cla()  # Clear the axes

        num_players = self.round_state.num_players
        y_positions = np.arange(num_players)[::-1]  # Reverse order so Player 1 is on top

        # Initialize stacking positions
        left_neg = np.zeros(num_players)  # For negative impacts
        left_pos = np.zeros(num_players)  # For positive impacts

        max_extent = 0  # To determine symmetric x-axis limits

        for i in range(num_players):
            # player_index = num_players - 1 - i  # Reverse player order
            positive_votes = [positive_vote_effects[j][i] for j in range(num_players)]
            negative_votes = [negative_vote_effects[j][i] for j in range(num_players)]

            # Plot negative votes (extending left from zero)
            for j, negative_vote in enumerate(negative_votes):
                if negative_vote != 0:
                    self.tornado_ax.barh(y_positions[i], negative_vote, left=left_neg[i], color=COLORS[j])
                    left_neg[i] += negative_vote  # Update stacking position

            # Plot positive votes (extending right from zero)
            for j, positive_vote in enumerate(positive_votes):
                if positive_vote != 0:
                    self.tornado_ax.barh(y_positions[i], positive_vote, left=left_pos[i], color=COLORS[j])
                    left_pos[i] += positive_vote  # Update stacking position

            # Update max extent for symmetric x-axis
            max_extent = max(max_extent, abs(left_neg[i]), abs(left_pos[i]))

        # Set symmetric x-axis limits
        self.tornado_ax.set_xlim(-max_extent, max_extent)

        # Set labels and title
        self.tornado_ax.set_yticklabels([])
        for i, y_pos in enumerate(y_positions):
            self.tornado_ax.text(-max_extent * 1.05, y_pos, f"Player {i + 1}",
                                 va='center', ha='right', fontsize=10, color=COLORS[i])

        self.tornado_ax.axvline(0, color='#EBEBEB', linewidth=2, linestyle='-')
        self.tornado_ax.figure.canvas.draw_idle()  # Redraw the figure

    def update_nodes_graph(self, winning_vote=None):
        radius = 5 # I just happen to know this, no clue if we need to make this adjustable based on server input.

        if winning_vote != None:
            if winning_vote == -1:
                print("NO ONE WON! NO RED.")
            else:
                print("WE HAVE A WINNING VOTE! ITS ", winning_vote)
                winning_vote += 1
        else:
            self.arrows.clear()

        self.nodes_ax.clear()
        for arrow in self.arrows:
            arrow.draw(self.nodes_ax) # Redraw the arrows if there are any. If there is a winning vote, we erase them.

        self.nodes_x = []
        self.nodes_y = []
        self.nodes_type = []
        self.nodes_text = []
        for node in self.round_state.nodes:
            mini_dict = {"x_pos": float(node["x_pos"]), "y_pos": float(node["y_pos"])}

            self.nodes_dict[node["text"]] = mini_dict

            self.nodes_x.append(float(node["x_pos"]))
            self.nodes_y.append(float(node["y_pos"]))
            self.nodes_type.append(node["type"])
            self.nodes_text.append(node["text"])


        colors = []

        for i, (x_val, y_val) in enumerate(zip(self.nodes_x, self.nodes_y)):
            text = self.nodes_text[i]
            if text.startswith("Player"):
                split_string = text.split()
                text = split_string[1]
                color = COLORS[int(split_string[1]) - 1]
            elif text == "Cause " + str(winning_vote):
                color = "#e41e1e"  # red haha.
            else:
                color = "#EBEBEB"
            self.nodes_ax.annotate(
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

        self.nodes_ax.scatter(self.nodes_x, self.nodes_y, marker='o', c=colors)



        # Clear the axis spines (the square border)
        self.nodes_ax.spines['top'].set_color('none')
        self.nodes_ax.spines['right'].set_color('none')
        self.nodes_ax.spines['left'].set_color('none')
        self.nodes_ax.spines['bottom'].set_color('none')

        self.nodes_ax.set_xticks([])  # Remove x-axis ticks
        self.nodes_ax.set_yticks([])  # Remove y-axis ticks
        self.nodes_ax.set_xticklabels([])  # Optionally remove x-axis labels
        self.nodes_ax.set_yticklabels([])  # Optionally remove y-axis labels

        self.nodes_ax.set_aspect('equal', adjustable='box')

        self.nodes_canvas.draw()

    def update_win(self, winning_vote):
        for i in range(len(self.cause_labels)):
            if winning_vote == i:
                new_string = "WE WON!"
            else:
                new_string = "Cause #" + str(i+1) + " (" + str(winning_vote+1) + ")"
            self.cause_labels[i].setText(new_string)


    def update_potential_sc_votes(self, potential_votes):
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
                    new_text = str(int(player_id) + 1) + " You :) " + "(" + str(vote) + ")"
                else:
                    new_text = str(int(player_id) + 1) + " (" + str(vote) + ")"
                player_label.setText(new_text)
        total_votes = Counter(potential_votes.values()).most_common(len(self.cause_labels)) # take the second element of the tuple or something

        for i in range(len(self.cause_labels)):
            new_string = "Cause #" + str(i+1) + " (0)"
            self.cause_labels[i].setText(new_string)

        for i in range(len(total_votes)):
            new_string = "Cause #" + str(total_votes[i][0]+1) + " (" + str(total_votes[i][1]) + ")"
            self.cause_labels[int(total_votes[i][0])].setText(new_string)

        self.update_arrows(potential_votes)


    def update_arrows(self, potential_votes):
        # checks for existing arrows, and removes them.
        if potential_votes: # only run this if there are actual potential votes.
            for arrow in self.arrows: # if there is anything in there.
                arrow.remove()

            self.arrows = [] # clean the arrows array.
            for key in potential_votes:
                player_name = "Player " + str(int(key)+1)
                start_x = self.nodes_dict[player_name]["x_pos"]
                start_y = self.nodes_dict[player_name]["y_pos"]
                cause_name = "Cause " + str(int(potential_votes[key])+1)
                end_x = self.nodes_dict[cause_name]["x_pos"]
                end_y = self.nodes_dict[cause_name]["y_pos"]

                new_arrow = Arrow((start_x, start_y), (end_x, end_y), color=COLORS[int(key)])
                self.arrows.append(new_arrow)

            for arrow in self.arrows:
                arrow.draw(self.nodes_ax)

            self.nodes_canvas.draw()

    def disable_sc_buttons(self):
        for button in self.sc_buttons:
            button.setEnabled(False)

    def enable_sc_buttons(self):
        for button in self.sc_buttons:
            button.setEnabled(True)

        for i in range(len(self.player_labels)):
            if i == int(self.round_state.client_id):
                self.player_labels[str(i + 1)].setText(f"{i + 1} You :)")
            else:
                self.player_labels[str(i + 1)].setText(f"{i + 1}")

    def disable_jhg_buttons(self):
        for button in self.jhg_buttons:
            button.setEnabled(False)

    def enable_jhg_buttons(self):
        for button in self.jhg_buttons:
            button.setEnabled(True)
