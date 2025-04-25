import time

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
    main_window.SC_panel.addTab(main_window.SC_voting_grid, "Next Round")


# Triggered by SC_INIT
def SC_round_init(main_window):
    # Update sc ui elements
    main_window.SC_voting_grid.update_utilities(main_window.round_state.utilities)
    if main_window.round_state.sc_round_num == 1:
        main_window.SC_cause_graph.update_sc_nodes_graph(main_window.round_state.sc_round_num)


# Triggered by SC_OVER
def update_sc_utilities_labels(main_window, round_num, new_utilities, winning_vote, last_round_votes, last_round_utilities):
    history_grid = main_window.sc_history_grid
    history_grid.update_sc_history(round_num, last_round_votes, last_round_utilities)
    main_window.SC_panel.setCurrentIndex(1)
    main_window.SC_cause_graph.update_arrows(history_grid.sc_history[str(round_num)]["votes"], True)
    main_window.SC_panel.setTabText(1, "Results")
    main_window.SC_panel.setTabText(0, "Next Round")

    if winning_vote != -1:
        main_window.SC_voting_grid.update_col_2(new_utilities)


def tab_changed(main_window, index):
    current_tab = main_window.SC_panel.widget(index)
    cause_graph = main_window.SC_cause_graph
    if current_tab == main_window.SC_voting_grid:
        cause_graph.update_sc_nodes_graph(main_window.round_state.sc_round_num)
        cause_graph.update_arrows(main_window.round_state.current_votes, True)

        if main_window.SC_panel.tabText(1) == "Results":
            main_window.SC_panel.setTabText(1, "History")
    elif current_tab == main_window.sc_history_grid and main_window.sc_history_grid.sc_history:
        sc_history_tab = main_window.sc_history_grid
        selected_round = sc_history_tab.round_drop_down.currentIndex() + 1
        votes = sc_history_tab.sc_history[str(selected_round)]["votes"]
        winning_vote = get_winning_vote(votes)

        cause_graph.update_sc_nodes_graph(selected_round, winning_vote)
        cause_graph.update_arrows(votes)


def sc_vote(main_window, vote):
    main_window.SC_voting_grid.current_vote = vote


def sc_submit(main_window, voting_grid):
    # voting_grid.select_button(None) # Clears the selection from the SC voting buttons
    main_window.connection_manager.send_message("SUBMIT_SC", main_window.round_state.client_id, main_window.SC_voting_grid.current_vote)
    # if main_window.round_state.sc_cycle == main_window.SC_cause_graph.num_cycles:
    #     main_window.round_state.sc_cycle == 1


def disable_sc_buttons(main_window):
    for button in main_window.SC_voting_grid.buttons:
        button.setEnabled(False)
        if button.objectName() == "SCSubmitButton":
            button.setText("Submit Vote")
    main_window.SC_voting_grid.current_vote = -1


def get_winning_vote(votes):
    vote_counts = {"0": 0, "1": 0, "2": 0}
    for vote in votes.values():
        if vote != -1:
            vote_counts[str(vote)] += 1
    winning_vote = int(max(vote_counts, key=vote_counts.get))

    if vote_counts[str(winning_vote)] <= len(votes) // 2:
        winning_vote = 0

    winning_vote -= 1  # Winning vote is one indexed, so it needs to be converted to 0 index

    return winning_vote