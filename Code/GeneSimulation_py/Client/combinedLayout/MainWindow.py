from functools import partial

import numpy as np
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QWidget
from RoundState import RoundState
from ServerListener import ServerListener
from matplotlib.figure import Figure

from combinedLayout.JhgPanel import JhgPanel


from combinedLayout.SCHistoryGrid import SCHistoryGrid

from .MainDocks import CornerContainer
from .SCCausesGraph import SCCausesGraph
from .ui_functions.SC_functions import *
from .ui_functions.JHG_functions import *

from .ui_functions.tornado_graph import update_tornado_graph


class MainWindow(QMainWindow):
    def __init__(self, connection_manager, num_players, client_id, num_cycles):
        super().__init__()
        # This window is very dependent on things happening in the correct order.
        # If you mess with it, you might break a lot of things.
        # It has been broken up into blocks below to try to mitigate that

    #1# Block one: Sets up the round_state and client socket. Must be the first thing done
        self.tornado_ax = None
        self.tornado_canvas = None
        self.SC_cause_graph = SCCausesGraph(num_cycles)
        self.player_labels = {}
        self.jhg_buttons = []
        self.round_state = RoundState(client_id, num_players, self.jhg_buttons)
        self.connection_manager = connection_manager
        self.num_cycles = num_cycles
    #/1#

    #2# Block two: Creates the elements that will be passed to the server listener for dynamic updating. Must happen before the server listener is created
        self.setWindowTitle(f"Junior High Game: Player {int(self.round_state.client_id) + 1}")

        # Dynamically updated elements
        self.token_label = QLabel()
        self.jhg_popularity_graph = pg.PlotWidget()
        self.jhg_popularity_graph.setXRange(0, 2)
        self.jhg_popularity_graph.setYRange(0, 120)
        self.jhg_popularity_graph.getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(100)]])
        self.jhg_popularity_graph.setBackground("#282828ff")
        view_box = self.jhg_popularity_graph.getViewBox()
        view_box.setLimits(xMin=0, xMax=2, yMin=0, yMax=120)
        self.jhg_network = pg.PlotWidget()
        self.jhg_network.setBackground("#282828ff")
        tabs = QTabWidget()

        # Initialize the social choice panel. This includes defining several variables that will be initialized in SC_functions
        self.tornado_fig = Figure(figsize=(5, 4), dpi=100)
        self.tornado_y = np.arange(self.round_state.num_players)
        self.tornado_ax = self.tornado_fig.add_subplot(111)

        # The QLabels used to display the utility values of each choice in the social choice game
        self.utility_qlabels = []
        self.SC_voting_grid = QTabWidget()
        self.cause_table = QWidget()

        # Header for JHG tab
        self.headerLayout = QHBoxLayout()
        self.round_counter = QLabel("Round 1")
        self.round_counter_font = QFont()
        self.round_counter_font.setPointSize(20)
        self.round_counter.setFont(self.round_counter_font)
        self.headerLayout.addWidget(self.round_counter)
    #/2#

    #3# Block three: Sets up the server listener, which depends on blocks 1&2.
        # Server Listener setup
        self.ServerListener = ServerListener(self, connection_manager, self.round_state, self.round_counter, self.token_label,
                                             self.jhg_popularity_graph, tabs, self.utility_qlabels)
        self.ServerListener_thread = QThread()
        self.ServerListener.moveToThread(self.ServerListener_thread)

        self.set_up_signals()

        self.ServerListener_thread.start()
    #/3#

    #4# Block four: Lays out the client. Dependent on blocks 1&2
        self.JHG_panel = QWidget()
        self.JHG_panel.setMinimumWidth(400)
        self.JHG_panel.setLayout( JhgPanel(self.round_state, connection_manager, self.token_label,
                                           self.jhg_popularity_graph, self.jhg_network, self.jhg_buttons))
        self.JHG_panel.setObjectName("JHG_Panel")
        self.JHG_panel.setProperty("min-height", 80 + 40*self.round_state.num_players)

        self.SC_panel = QTabWidget()
        self.SC_panel.setObjectName("SC_Panel")
        self.SC_panel.setProperty("min-height", 200 + 20*self.round_state.num_players)
        self.SC_panel.setLayout(QVBoxLayout())

        plots_panel = QTabWidget()
        plots_panel.tabBar().setExpanding(True)
        plots_panel.addTab(self.jhg_popularity_graph, "Popularity over time")
        plots_panel.addTab(self.jhg_network, "Network graph")

        create_sc_ui_elements(self)
        self.SC_cause_graph.init_sc_nodes_graph(self.round_state)

        graphs_layout = QVBoxLayout()

        sc_graph_tabs = QTabWidget()
        sc_graph_tabs.addTab(self.SC_cause_graph, "Causes Graph")
        sc_graph_tabs.addTab(self.tornado_canvas, "Effect of past votes")

        graphs_layout.addWidget(sc_graph_tabs)

        self.sc_history_grid = SCHistoryGrid(self.round_state.num_players, self.round_state.client_id, "Voted for", self.SC_cause_graph)
        self.SC_panel.addTab(self.sc_history_grid, "History")
        self.SC_panel.currentChanged.connect(self.SC_tab_changed)

        self.setWindowTitle("JHG: Round 1")
        self.setCentralWidget(CornerContainer(self.JHG_panel, plots_panel, self.SC_panel, sc_graph_tabs))
    #/4#


### --- Setting up pyqt signals --- ###


    def set_up_signals(self):
        # pyqt signal hook-ups
        self.ServerListener.update_jhg_round_signal.connect(partial(update_jhg_ui_elements, self))
        self.ServerListener.update_sc_round_signal.connect(partial(SC_round_init, self))
        self.ServerListener.disable_sc_buttons_signal.connect(partial(disable_sc_buttons, self))
        self.ServerListener.update_sc_utilities_labels_signal.connect(self.update_sc_utilities_labels)
        self.ServerListener.update_tornado_graph_signal.connect(self.update_tornado_graph)
        self.ServerListener.jhg_over_signal.connect(partial(jhg_over, self))
        self.ServerListener.enable_jhg_buttons_signal.connect(partial(enable_jhg_buttons, self))
        self.ServerListener.update_sc_votes_signal.connect(self.update_sc_votes)
        self.ServerListener.update_sc_nodes_graph_signal.connect(self.update_sc_nodes_graph)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)

    def update_sc_votes(self, votes, cycle, is_last_cycle):
        self.round_state.sc_cycle = cycle
        self.SC_cause_graph.update_arrows(votes, True)
        self.SC_voting_grid.current_vote = -1
        self.SC_voting_grid.select_button(None)  # Clears the selection from the SC voting buttons

        if not is_last_cycle:
            self.SC_voting_grid.submit_button.setText("Submit")

    def update_sc_utilities_labels(self, round_num, new_utilities, winning_vote, last_round_votes, last_round_utilities):
        update_sc_utilities_labels(self, round_num, new_utilities, winning_vote, last_round_votes, last_round_utilities)

    def update_tornado_graph(self, tornado_ax, positive_vote_effects, negative_vote_effects):
        update_tornado_graph(self, tornado_ax, positive_vote_effects, negative_vote_effects)

    def update_sc_nodes_graph(self, winning_vote):
        self.SC_cause_graph.update_sc_nodes_graph(self.round_state.sc_round_num, winning_vote)
        self.SC_cause_graph.update_arrows(self.round_state.current_votes)
        self.round_state.current_votes = {i: -1 for i in range(self.round_state.num_players)}

    def SC_tab_changed(self, index):
        tab_changed(self, index)