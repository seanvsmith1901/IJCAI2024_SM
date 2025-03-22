import json
from functools import partial
from collections import Counter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QTabWidget, QGridLayout, QPushButton

from .tornado_graph import create_tornado_graph
from .sc_nodes_graph import update_sc_nodes_graph, create_sc_nodes_graph
from combinedLayout.Arrow import Arrow
from combinedLayout.SCVotingGrid import SCVotingGrid
from combinedLayout.colors import COLORS


def create_sc_ui_elements(main_window):
    # main_window.utility_qlabels.clear()

    # # Clear the previous table layout and set up a fresh one
    # main_window.cause_table_layout = QGridLayout()
    # main_window.utility_qlabels.clear()
    #
    # # Add the player id column
    # main_window.cause_table_layout.addWidget(QLabel("Player"), 0, 0)
    # main_window.cause_table_layout.addWidget(QLabel("Utility"), 0, 1)
    # main_window.cause_table_layout.setColumnStretch(0, 1)
    #
    # main_window.player_labels = {}
    # main_window.cause_labels = {}
    #
    # # Add a row for each player to display their name and accumulated utility
    # for player in main_window.round_state.players:
    #     player_id = str(player.id + 1)
    #     player_label = QLabel(player_id)
    #
    #     if str(int(main_window.round_state.client_id) + 1) == str(player_id):
    #         player_label.setText(f"{player_id} You :)")
    #     else:
    #         player_label.setText(f"{player_id}")
    #
    #     player_label.setStyleSheet("color: " + COLORS[player.id])
    #
    #     main_window.player_labels[player_id] = player_label
    #     utilities_label = player.utility_label
    #
    #     main_window.cause_table_layout.addWidget(player_label, int(player_id), 0)
    #     main_window.cause_table_layout.addWidget(utilities_label, int(player_id), 1)
    #
    # main_window.sc_buttons = []
    # # For each cause, create a header in the table
    # for i in range(main_window.round_state.num_causes):
    #     cause_label = QLabel(f"Cause #{i + 1}")
    #     main_window.cause_table_layout.addWidget(cause_label, 0, i + 2)
    #     main_window.cause_table_layout.setColumnStretch(i + 1, 1)
    #     main_window.cause_labels[i] = cause_label
    #
    #     # Add a label to display the utility of the cause for each player for each cause
    #     row = []
    #     for j in range(main_window.round_state.num_players):
    #         row.append(QLabel("0"))
    #         main_window.cause_table_layout.addWidget(row[j], j + 1, i + 2)
    #     main_window.utility_qlabels.append(row)
    #
    #     vote_button = QPushButton("Vote")
    #     vote_button.setEnabled(False)
    #     main_window.sc_buttons.append(vote_button)
    #     vote_button.clicked.connect(partial(sc_vote, main_window, i))
    #     button_layout = QHBoxLayout()
    #     button_layout.addWidget(vote_button)
    #     button_layout.addStretch(1)
    #     main_window.cause_table_layout.addLayout(button_layout, main_window.round_state.num_players + 2, i + 2)
    #
    # # Create a single "Submit" button below the causes and vote buttons
    # submit_button = QPushButton("Submit")
    # submit_button.setEnabled(False)
    # submit_button.clicked.connect(partial(sc_submit, main_window))
    # main_window.sc_buttons.append(submit_button)
    # submit_layout = QHBoxLayout()
    # submit_layout.addWidget(submit_button)
    # submit_layout.addStretch(1)
    #
    # # Add submit button layout at the bottom left of the vote buttons
    # main_window.cause_table_layout.addLayout(submit_layout, main_window.round_state.num_players + 2, 0, 1,
    #                                          main_window.round_state.num_causes)



    graphs_layout = QVBoxLayout()
    main_window.graph_canvas = create_sc_nodes_graph(main_window)
    main_window.tornado_canvas = create_tornado_graph(main_window, main_window.tornado_fig, main_window.tornado_ax, main_window.tornado_y)

    sc_graph_tabs = QTabWidget()
    sc_graph_tabs.addTab(main_window.graph_canvas, "Causes Graph")
    sc_graph_tabs.addTab(main_window.tornado_canvas, "Effect of past votes")

    graphs_layout.addWidget(sc_graph_tabs)

    main_window.SC_voting_grid = SCVotingGrid(main_window.round_state.num_players, main_window.round_state.num_causes, graphs_layout, main_window)
    main_window.SC_voting_grid.update_grid([1 for _ in range(main_window.round_state.num_players)], [[1 for _ in range(3)] for _ in range(main_window.round_state.num_players)])

    # main_window.SC_panel.layout().addLayout(graphs_layout)
    main_window.SC_panel.layout().addLayout(main_window.SC_voting_grid)


def update_sc_ui_elements(main_window):
    main_window.SC_panel.setStyleSheet("#SC_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: none; }")
    main_window.SC_voting_grid.update_utilities(main_window.round_state.utilities)
    update_sc_nodes_graph(main_window)


def update_sc_utilities_labels(main_window, new_utilities, winning_vote):
    if winning_vote != -1:
        main_window.SC_voting_grid.update_col_2(new_utilities)


def update_win(main_window, winning_vote):
    for i in range(len(main_window.cause_labels)):
        if winning_vote == i:
            new_string = "WE WON!"
        else:
            new_string = "Cause #" + str(i + 1) + " (" + str(winning_vote + 1) + ")"
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
            if str(int(main_window.round_state.client_id) + 1) == str(int(player_id) + 1):
                new_text = str(int(player_id) + 1) + " You :) " + "(" + str(vote) + ")"
            else:
                new_text = str(int(player_id) + 1) + " (" + str(vote) + ")"
            player_label.setText(new_text)
    total_votes = Counter(potential_votes.values()).most_common(
        len(main_window.cause_labels))  # take the second element of the tuple or something

    for i in range(len(main_window.cause_labels)):
        new_string = "Cause #" + str(i + 1) + " (0)"
        main_window.cause_labels[i].setText(new_string)

    for i in range(len(total_votes)):
        new_string = "Cause #" + str(total_votes[i][0] + 1) + " (" + str(total_votes[i][1]) + ")"
        main_window.cause_labels[int(total_votes[i][0])].setText(new_string)

    update_arrows(main_window, potential_votes)


def update_arrows(main_window, potential_votes):
    # checks for existing arrows, and removes them.
    if potential_votes:  # only run this if there are actual potential votes.
        for arrow in main_window.arrows:  # if there is anything in there.
            arrow.remove()

        main_window.arrows = []  # clean the arrows array.
        for key in potential_votes:
            player_name = "Player " + str(int(key) + 1)
            start_x = main_window.nodes_dict[player_name]["x_pos"]
            start_y = main_window.nodes_dict[player_name]["y_pos"]
            cause_name = "Cause " + str(int(potential_votes[key]) + 1)
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
        "FINAL_VOTE": main_window.current_vote,
    }
    main_window.client_socket.send(json.dumps(message).encode())


def sc_display_winning_vote(main_window, winning_vote):
    x_val = -1
    y_val = -1
    text = ""
    color = "#e41e1e"
    for node in main_window.round_state.nodes:
        if node["text"] == "Cause " + str(int(winning_vote) + 1):
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


def disable_sc_buttons(main_window):
    for button in main_window.SC_voting_grid.buttons:
        button.setEnabled(False)


def enable_sc_buttons(main_window):
    for button in main_window.SC_voting_grid.buttons:
        button.setEnabled(True)

    # for i in range(len(main_window.player_labels)):
    #     if i == int(main_window.round_state.client_id):
    #         main_window.player_labels[str(i + 1)].setText(f"{i + 1} You :)")
    #     else:
    #         main_window.player_labels[str(i + 1)].setText(f"{i + 1}")
