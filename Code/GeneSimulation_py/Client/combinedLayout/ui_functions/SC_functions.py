from PyQt6.QtWidgets import QVBoxLayout, QTabWidget

from .tornado_graph import create_tornado_graph
from combinedLayout.SCVotingGrid import SCVotingGrid


def create_sc_ui_elements(main_window):
    client_id = main_window.round_state.client_id
    graphs_layout = QVBoxLayout()
    main_window.tornado_canvas = create_tornado_graph(main_window, main_window.tornado_fig, main_window.tornado_ax, main_window.tornado_y)

    sc_graph_tabs = QTabWidget()
    sc_graph_tabs.addTab(main_window.SC_cause_graph, "Causes Graph")
    sc_graph_tabs.addTab(main_window.tornado_canvas, "Effect of past votes")

    graphs_layout.addWidget(sc_graph_tabs)

    # Set up the SC history panel
    main_window.SC_voting_grid = SCVotingGrid(main_window.round_state.num_players, client_id, graphs_layout, main_window)
    main_window.SC_voting_grid.update_grid([0 for _ in range(main_window.round_state.num_players)], [[0 for _ in range(3)] for _ in range(main_window.round_state.num_players)], 0)

    main_window.SC_panel.setMinimumWidth(400)
    main_window.SC_panel.addTab(main_window.SC_voting_grid, "Current Round")


def SC_round_init(main_window):
    # Update sc ui elements
    main_window.SC_panel.setStyleSheet("#SC_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: none; }")
    main_window.SC_voting_grid.update_utilities(main_window.round_state.utilities)
    main_window.SC_cause_graph.update_sc_nodes_graph(main_window.round_state.round_number)

    # Enable the SC buttons
    for button in main_window.SC_voting_grid.buttons:
        if button.objectName() != "clear_button":
            button.setEnabled(True)


def update_sc_utilities_labels(main_window, new_utilities, winning_vote, last_round_votes, last_round_utilities):
    history_grid = main_window.sc_history_grid
    history_grid.update_sc_history(main_window.round_state.round_number, last_round_votes, last_round_utilities)
    history_grid.change_round(main_window.round_state.round_number)

    if winning_vote != -1:
        main_window.SC_voting_grid.update_col_2(new_utilities)


def sc_vote(main_window, vote):
    main_window.current_vote = vote
    main_window.connection_manager.send_message("POTENTIAL_SC_VOTE", main_window.round_state.client_id, vote)


def sc_submit(main_window, voting_grid):
    voting_grid.select_button(None) # Clears the selection from the SC voting buttons
    main_window.connection_manager.send_message("SUBMIT_SC", main_window.round_state.client_id, main_window.current_vote)


def disable_sc_buttons(main_window):
    for button in main_window.SC_voting_grid.buttons:
        button.setEnabled(False)
    main_window.current_vote = -1


def get_winning_vote(votes):
    vote_counts = {"1": 0, "2": 0, "3": 0}
    for vote in votes:
        if vote != -1:
            vote_counts[str(vote)] += 1
    winning_vote = int(max(vote_counts, key=vote_counts.get))

    if vote_counts[str(winning_vote)] <= len(votes) // 2:
        winning_vote = 0

    winning_vote -= 1  # Winning vote is one indexed, so it needs to be converted to 0 index

    return winning_vote