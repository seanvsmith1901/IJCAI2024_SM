import json
import time
from functools import partial
from collections import Counter
import pyqtgraph as pg
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib

# matplotlib.use('Qt5Agg')
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QPushButton
from .Arrow import Arrow

COLORS = ["#FF9191", "#D15C5E", "#965875", "#FFF49F", "#B1907D", "#FFAFD8", "#C9ADE9", "#fdbf6f"]

def create_sc_ui_elements(main_window):
    main_window.utility_qlabels.clear()

    # Create the QWidget for the social choice tab if not already created
    if not main_window.social_choice_tab.layout():
        main_window.social_choice_tab.setLayout(QVBoxLayout())

    # Clear the previous table layout and set up a fresh one
    main_window.cause_table_layout = QGridLayout()
    main_window.utility_qlabels.clear()

    # Add the player id column
    main_window.cause_table_layout.addWidget(QLabel("Player"), 0, 0)
    main_window.cause_table_layout.addWidget(QLabel("Utility"), 0, 1)
    main_window.cause_table_layout.setColumnStretch(0, 1)

    main_window.player_labels = {}
    main_window.cause_labels = {}

    for player in main_window.round_state.players:
        player_id = str(player.id + 1)
        player_label = QLabel(player_id)

        if str(int(main_window.round_state.client_id) + 1) == str(player_id):
            player_label.setText(f"{player_id} You :)")
        else:
            player_label.setText(f"{player_id}")

        player_label.setStyleSheet("color: " + COLORS[player.id])

        main_window.player_labels[player_id] = player_label
        utilities_label = player.utility_label

        main_window.cause_table_layout.addWidget(player_label, int(player_id), 0)
        main_window.cause_table_layout.addWidget(utilities_label, int(player_id), 1)

    main_window.sc_buttons = []
    # For each cause
    for i in range(main_window.round_state.num_causes):
        cause_label = QLabel(f"Cause #{i + 1}")
        main_window.cause_table_layout.addWidget(cause_label, 0, i + 2)
        main_window.cause_table_layout.setColumnStretch(i + 1, 1)
        main_window.cause_labels[i] = cause_label

        row = []
        for j in range(main_window.round_state.num_players):
            row.append(QLabel("0"))
            main_window.cause_table_layout.addWidget(row[j], j + 1, i + 2)
        main_window.utility_qlabels.append(row)

        vote_button = QPushButton("Vote")
        vote_button.setEnabled(False)
        main_window.sc_buttons.append(vote_button)
        vote_button.clicked.connect(partial(sc_vote, main_window, i))
        button_layout = QHBoxLayout()
        button_layout.addWidget(vote_button)
        button_layout.addStretch(1)
        main_window.cause_table_layout.addLayout(button_layout, main_window.round_state.num_players + 2, i + 2)

    # Create a single "Submit" button below the causes and vote buttons
    submit_button = QPushButton("Submit")
    submit_button.setEnabled(False)
    submit_button.clicked.connect(partial(sc_submit, main_window))
    main_window.sc_buttons.append(submit_button)
    submit_layout = QHBoxLayout()
    submit_layout.addWidget(submit_button)
    submit_layout.addStretch(1)

    # Add submit button layout at the bottom left of the vote buttons
    main_window.cause_table_layout.addLayout(submit_layout, main_window.round_state.num_players + 2, 0, 1, main_window.round_state.num_causes)

    graphs_layout = QVBoxLayout()
    main_window.graph_canvas = create_sc_nodes_graph(main_window)
    main_window.tornado_canvas = create_sc_tornado_graph(main_window)

    sc_graph_tabs = QTabWidget()
    sc_graph_tabs.addTab(main_window.graph_canvas, "Causes Graph")
    sc_graph_tabs.addTab(main_window.tornado_canvas, "Effect of past votes")

    graphs_layout.addWidget(sc_graph_tabs)

    main_window.SC_panel.layout().addLayout(graphs_layout)
    main_window.SC_panel.layout().addLayout(main_window.cause_table_layout)

    
def update_sc_ui_elements(main_window):
    for i in range(main_window.round_state.num_causes):
        for j in range(main_window.round_state.num_players):
            main_window.utility_qlabels[i][j].setText(str(main_window.round_state.utilities[j][i]))
    update_sc_nodes_graph(main_window)

def create_sc_nodes_graph(main_window):
    # # main_window.nodes_fig = Figure(figsize=(5, 4), dpi=100)
    # main_window.nodes_ax = main_window.nodes_fig.add_subplot(111)
    # main_window.nodes_x = np.linspace(0, 10, 100)
    # main_window.nodes_y = np.sin(main_window.nodes_x)
    # main_window.nodes_ax.plot(main_window.nodes_x, main_window.nodes_y)
    # main_window.nodes_canvas = FigureCanvas(main_window.nodes_fig)
    main_window.nodes_canvas.show()
    main_window.nodes_type = []
    main_window.nodes_text = []

    main_window.nodes_fig.patch.set_facecolor("#282828ff")
    main_window.nodes_ax.set_facecolor("#282828ff")
    main_window.nodes_ax.tick_params(color="#EBEBEB")
    main_window.nodes_ax.tick_params(color="#EBEBEB")
    for spine in main_window.nodes_ax.spines.values():
        spine.set_color("#EBEBEB")
    return main_window.nodes_canvas

def update_sc_utilities_labels(main_window, new_utilities, winning_vote):
    if winning_vote != -1:
        for i in range(main_window.round_state.num_players):
            main_window.round_state.players[i].utility_label.setText(str(new_utilities[str(i)]))

def update_sc_nodes_graph(main_window, winning_vote=None):
    radius = 5 # I just happen to know this, no clue if we need to make this adjustable based on server input.

    if winning_vote != None:
        if winning_vote == -1:
            print("NO ONE WON! NO RED.")
        else:
            print("WE HAVE A WINNING VOTE! ITS ", winning_vote)
            winning_vote += 1
    else:
        main_window.arrows.clear()

    main_window.nodes_ax.clear()
    for arrow in main_window.arrows:
        arrow.draw(main_window.nodes_ax) # Redraw the arrows if there are any. If there is a winning vote, we erase them.

    main_window.nodes_x = []
    main_window.nodes_y = []
    main_window.nodes_type = []
    main_window.nodes_text = []
    for node in main_window.round_state.nodes:
        mini_dict = {"x_pos": float(node["x_pos"]), "y_pos": float(node["y_pos"])}

        main_window.nodes_dict[node["text"]] = mini_dict

        main_window.nodes_x.append(float(node["x_pos"]))
        main_window.nodes_y.append(float(node["y_pos"]))
        main_window.nodes_type.append(node["type"])
        main_window.nodes_text.append(node["text"])


    colors = []

    for i, (x_val, y_val) in enumerate(zip(main_window.nodes_x, main_window.nodes_y)):
        text = main_window.nodes_text[i]
        if text.startswith("Player"):
            split_string = text.split()
            text = split_string[1]
            color = COLORS[int(split_string[1]) - 1]
        elif text == "Cause " + str(winning_vote):
            color = "#e41e1e"  # red haha.
        else:
            color = "#EBEBEB"
        main_window.nodes_ax.annotate(
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

    main_window.nodes_ax.scatter(main_window.nodes_x, main_window.nodes_y, marker='o', c=colors)

    # Clear the axis spines (the square border)
    main_window.nodes_ax.spines['top'].set_color('none')
    main_window.nodes_ax.spines['right'].set_color('none')
    main_window.nodes_ax.spines['left'].set_color('none')
    main_window.nodes_ax.spines['bottom'].set_color('none')

    main_window.nodes_ax.set_xticks([])  # Remove x-axis ticks
    main_window.nodes_ax.set_yticks([])  # Remove y-axis ticks
    main_window.nodes_ax.set_xticklabels([])  # Optionally remove x-axis labels
    main_window.nodes_ax.set_yticklabels([])  # Optionally remove y-axis labels

    main_window.nodes_ax.set_aspect('equal', adjustable='box')

    main_window.nodes_canvas.draw()

def create_sc_tornado_graph(main_window):
    # main_window.tornado_fig = Figure(figsize=(5, 4), dpi=100)
    # main_window.tornado_y = np.arange(main_window.round_state.num_players)
    # main_window.tornado_ax = main_window.tornado_fig.add_subplot(111)

    main_window.tornado_ax.barh(main_window.tornado_y, [0 for _ in range(main_window.round_state.num_players)], color='red', label='Decrease Impact')
    main_window.tornado_ax.barh(main_window.tornado_y, [0 for _ in range(main_window.round_state.num_players)], color='green', label='Increase Impact')

    main_window.tornado_fig.patch.set_facecolor("#282828ff")
    main_window.tornado_ax.set_facecolor("#282828ff")
    main_window.tornado_ax.tick_params(color="#EBEBEB")
    main_window.tornado_ax.tick_params(color="#EBEBEB")
    for spine in main_window.tornado_ax.spines.values():
        spine.set_color("#EBEBEB")

    return FigureCanvas(main_window.tornado_fig)

def update_sc_tornado_graph(main_window, positive_vote_effects, negative_vote_effects):
    main_window.tornado_ax.cla()  # Clear the axes

    num_players = main_window.round_state.num_players
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
                main_window.tornado_ax.barh(y_positions[i], negative_vote, left=left_neg[i], color=COLORS[j])
                left_neg[i] += negative_vote  # Update stacking position

        # Plot positive votes (extending right from zero)
        for j, positive_vote in enumerate(positive_votes):
            if positive_vote != 0:
                main_window.tornado_ax.barh(y_positions[i], positive_vote, left=left_pos[i], color=COLORS[j])
                left_pos[i] += positive_vote  # Update stacking position

        # Update max extent for symmetric x-axis
        max_extent = max(max_extent, abs(left_neg[i]), abs(left_pos[i]))

    # Set symmetric x-axis limits
    main_window.tornado_ax.set_xlim(-max_extent, max_extent)

    # Set labels and title
    main_window.tornado_ax.set_yticklabels([])
    for i, y_pos in enumerate(y_positions):
        main_window.tornado_ax.text(-max_extent * 1.05, y_pos, f"Player {i + 1}",
                             va='center', ha='right', fontsize=10, color=COLORS[i])

    main_window.tornado_ax.axvline(0, color='#EBEBEB', linewidth=2, linestyle='-')
    main_window.tornado_ax.figure.canvas.draw_idle()  # Redraw the figure

def update_win(main_window, winning_vote):
    for i in range(len(main_window.cause_labels)):
        if winning_vote == i:
            new_string = "WE WON!"
        else:
            new_string = "Cause #" + str(i+1) + " (" + str(winning_vote+1) + ")"
        main_window.cause_labels[i].setText(new_string)

def update_potential_sc_votes(main_window, potential_votes):
    for i in range(len(main_window.player_labels)):
        player_label = main_window.player_labels.get(str(int(i) + 1))
        if str(int(main_window.round_state.client_id) + 1) == str(int(i) + 1):
            new_text = str(int(i) + 1) + " You :) "
        else:
            new_text = str(int(i) + 1)
        player_label.setText(new_text)

    for player_id, vote in potential_votes.items():
        player_label = main_window.player_labels.get(str(int(player_id) + 1))  # Adjust ID for zero-indexed list
        if player_label:
            if str(int(main_window.round_state.client_id) + 1) == str(int(player_id)+1):
                new_text = str(int(player_id) + 1) + " You :) " + "(" + str(vote) + ")"
            else:
                new_text = str(int(player_id) + 1) + " (" + str(vote) + ")"
            player_label.setText(new_text)
    total_votes = Counter(potential_votes.values()).most_common(len(main_window.cause_labels)) # take the second element of the tuple or something

    for i in range(len(main_window.cause_labels)):
        new_string = "Cause #" + str(i+1) + " (0)"
        main_window.cause_labels[i].setText(new_string)

    for i in range(len(total_votes)):
        new_string = "Cause #" + str(total_votes[i][0]+1) + " (" + str(total_votes[i][1]) + ")"
        main_window.cause_labels[int(total_votes[i][0])].setText(new_string)

    update_arrows(main_window, potential_votes)

def update_arrows(main_window, potential_votes):
    # checks for existing arrows, and removes them.
    if potential_votes: # only run this if there are actual potential votes.
        for arrow in main_window.arrows: # if there is anything in there.
            arrow.remove()

        main_window.arrows = [] # clean the arrows array.
        for key in potential_votes:
            player_name = "Player " + str(int(key)+1)
            start_x = main_window.nodes_dict[player_name]["x_pos"]
            start_y = main_window.nodes_dict[player_name]["y_pos"]
            cause_name = "Cause " + str(int(potential_votes[key])+1)
            end_x = main_window.nodes_dict[cause_name]["x_pos"]
            end_y = main_window.nodes_dict[cause_name]["y_pos"]

            new_arrow = Arrow((start_x, start_y), (end_x, end_y), color=COLORS[int(key)])
            main_window.arrows.append(new_arrow)

        for arrow in main_window.arrows:
            arrow.draw(main_window.nodes_ax)

        main_window.nodes_canvas.draw()

def sc_vote(main_window, vote):
    message = {
        "CLIENT_ID": main_window.round_state.client_id,
        "POTENTIAL_VOTE": vote,
    }
    main_window.current_vote = vote
    main_window.client_socket.send(json.dumps(message).encode())

def sc_submit(main_window):
    message = {
        "CLIENT_ID": main_window.round_state.client_id,
        "FINAL_VOTE" : main_window.current_vote,
    }
    main_window.client_socket.send(json.dumps(message).encode())

def sc_display_winning_vote(main_window, winning_vote):
    x_val = -1
    y_val = -1
    text = ""
    color = "#e41e1e"
    for node in main_window.round_state.nodes:
        if node["text"] == "Cause " + str(int(winning_vote)+1):
            x_val = node["x_pos"]
            y_val = node["y_pos"]
            text = node["text"]


    main_window.nodes_ax.annotate(
        text,
        (x_val, y_val),
        textcoords="offset points",
        xytext=(0, 3),
        ha='center',
        fontsize=9,
        color=color,
        weight='bold',
    )

    main_window.nodes_canvas.draw()
    time.sleep(1) # show it red for 3 seconds

def disable_sc_buttons(main_window):
    for button in main_window.sc_buttons:
        button.setEnabled(False)

def enable_sc_buttons(main_window):
    for button in main_window.sc_buttons:
        button.setEnabled(True)

    for i in range(len(main_window.player_labels)):
        if i == int(main_window.round_state.client_id):
            main_window.player_labels[str(i + 1)].setText(f"{i + 1} You :)")
        else:
            main_window.player_labels[str(i + 1)].setText(f"{i + 1}")