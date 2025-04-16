from collections import Counter
from PyQt6.QtWidgets import QVBoxLayout, QTabWidget

from .tornado_graph import create_tornado_graph
from .sc_nodes_graph import update_sc_nodes_graph, create_sc_nodes_graph
from combinedLayout.Arrow import Arrow
from combinedLayout.SCVotingGrid import SCVotingGrid
from combinedLayout.colors import COLORS

from combinedLayout.SCHistoryGrid import SCHistoryGrid


def create_sc_ui_elements(main_window):
    client_id = main_window.round_state.client_id
    graphs_layout = QVBoxLayout()
    main_window.graph_canvas = create_sc_nodes_graph(main_window)
    main_window.tornado_canvas = create_tornado_graph(main_window, main_window.tornado_fig, main_window.tornado_ax, main_window.tornado_y)

    sc_graph_tabs = QTabWidget()
    sc_graph_tabs.addTab(main_window.graph_canvas, "Causes Graph")
    sc_graph_tabs.addTab(main_window.tornado_canvas, "Effect of past votes")

    graphs_layout.addWidget(sc_graph_tabs)

    # Set up the SC history panel
    main_window.SC_voting_grid = SCVotingGrid(main_window.round_state.num_players, client_id, graphs_layout, main_window)
    main_window.SC_voting_grid.update_grid([0 for _ in range(main_window.round_state.num_players)], [[0 for _ in range(3)] for _ in range(main_window.round_state.num_players)])

    main_window.SC_panel.setMinimumWidth(400)
    main_window.SC_panel.addTab(main_window.SC_voting_grid, "Current Round")


def SC_round_init(main_window):
    # Update sc ui elements
    main_window.SC_panel.setStyleSheet("#SC_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: none; }")
    main_window.SC_voting_grid.update_utilities(main_window.round_state.utilities)
    update_sc_nodes_graph(main_window)

    # Enable the SC buttons
    for button in main_window.SC_voting_grid.buttons:
        button.setEnabled(True)


def update_sc_utilities_labels(main_window, new_utilities, winning_vote, last_round_votes, last_round_utilities):
    history_grid = main_window.sc_history_grid
    history_grid.update_sc_history(main_window.round_state.round_number, last_round_votes, last_round_utilities)
    history_grid.change_round(main_window.round_state.round_number)

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
            if int(potential_votes[key]) != -1:
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
    main_window.current_vote = vote
    main_window.connection_manager.send_message("POTENTIAL_SC_VOTE", main_window.round_state.client_id, vote)


def sc_submit(main_window, voting_grid):
    voting_grid.select_button(None) # Clears the selection from the SC voting buttons
    main_window.connection_manager.send_message("SUBMIT_SC", main_window.round_state.client_id, main_window.current_vote)


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
    main_window.current_vote = -1
