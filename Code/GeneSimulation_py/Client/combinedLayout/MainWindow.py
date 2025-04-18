from functools import partial

import numpy as np
from PyQt6.QtCore import QThread, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QWidget, QGridLayout, QSplitter
from RoundState import RoundState
from ServerListener import ServerListener
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from combinedLayout.JhgPanel import JhgPanel


from combinedLayout.SCHistoryGrid import SCHistoryGrid
from .ui_functions.SC_functions import *
from .ui_functions.JHG_functions import *

from .ui_functions.tornado_graph import update_tornado_graph


class MainWindow(QMainWindow):
    def __init__(self, connection_manager, num_players, client_id):
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
        self.round_state = RoundState(client_id, num_players, self.jhg_buttons)
        self.connection_manager = connection_manager
    #/1#

    #2# Block two: Creates the elements that will be passed to the server listener for dynamic updating. Must happen before the server listener is created
        self.setWindowTitle(f"Junior High Game: Player {int(self.round_state.client_id) + 1}")

        # keep track of the current vote
        self.current_vote = -1

        # Dynamically updated elements
        self.token_label = QLabel()
        self.jhg_popularity_graph = pg.PlotWidget()
        self.jhg_popularity_graph.setXRange(0, 2)
        self.jhg_popularity_graph.setYRange(0, 120)
        self.jhg_popularity_graph.getAxis('bottom').setTicks(
            [[(i, str(i)) for i in range(100)]])
        view_box = self.jhg_popularity_graph.getViewBox()
        view_box.setLimits(xMin=0, xMax=2, yMin=0, yMax=120)
        self.jhg_network = pg.PlotWidget()
        tabs = QTabWidget()

        # Initialize the social choice panel. This includes defining several variables that will be initialized in SC_functions
        self.nodes_fig = Figure(figsize=(5, 4), dpi=100)
        self.nodes_ax = self.nodes_fig.add_subplot(111)
        self.nodes_canvas = FigureCanvas(self.nodes_fig)
        self.tornado_fig = Figure(figsize=(5, 4), dpi=100)
        self.tornado_y = np.arange(self.round_state.num_players)
        self.tornado_ax = self.tornado_fig.add_subplot(111)

        # The QLabels used to display the utility values of each choice in the social choice game
        self.utility_qlabels = []
        self.SC_voting_grid = QGridLayout()
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
        self.panel_grid = QGridLayout()
        # self.side_by_side_layout = QHBoxLayout()

        self.JHG_panel = QWidget()
        self.JHG_panel.setLayout(JhgPanel(self.round_state, connection_manager, self.token_label, self.jhg_popularity_graph, self.jhg_network, self.jhg_buttons))
        self.sc_history_grid = QWidget()
        self.sc_history_grid.setLayout(SCHistoryGrid(self.round_state.num_players,
                                                     self.round_state.client_id, "Voted for"))
        self.JHG_panel.setObjectName("JHG_Panel")
        self.JHG_panel.setStyleSheet("#JHG_Panel {border: 2px solid #FFFDD0; border-radius: 5px; }")
        self.SC_panel = QWidget()
        self.SC_panel.setObjectName("SC_Panel")
        self.SC_panel.setLayout(QVBoxLayout())

        create_sc_ui_elements(self)

        self.JHG_top_SC_bottom_splitter = QSplitter(Qt.Orientation.Vertical) # Top level splitter to divide the JHG and SCG
        self.SC_splitter = QSplitter(Qt.Orientation.Horizontal) # Sub splitter to horizontally divide the SC pane
        self.SC_splitter.addWidget(self.SC_panel)
        self.SC_splitter.addWidget(self.sc_history_grid)
        self.JHG_top_SC_bottom_splitter.addWidget(self.JHG_panel)
        self.JHG_top_SC_bottom_splitter.addWidget(self.SC_splitter)

        self.panel_grid.addWidget(self.JHG_top_SC_bottom_splitter)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.panel_grid)
        self.setCentralWidget(self.central_widget)

        self.nodes_dict = {}
        self.arrows = {}


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
        self.ServerListener.update_potential_sc_votes_signal.connect(self.update_potential_sc_votes)
        self.ServerListener.update_sc_nodes_graph_signal.connect(self.update_sc_nodes_graph)
        self.ServerListener.update_win_signal.connect(self.update_win)
        self.ServerListener_thread.started.connect(self.ServerListener.start_listening)

    def update_potential_sc_votes(self, potential_votes):
        update_potential_sc_votes(self, potential_votes)

    def update_sc_utilities_labels(self, new_utilities, winning_vote, last_round_votes, last_round_utilities):
        update_sc_utilities_labels(self, new_utilities, winning_vote, last_round_votes, last_round_utilities)

    def update_tornado_graph(self, tornado_ax, positive_vote_effects, negative_vote_effects):
        update_tornado_graph(self, tornado_ax, positive_vote_effects, negative_vote_effects)

    def update_sc_nodes_graph(self, winning_vote):
        update_sc_nodes_graph(self, winning_vote)

    def update_win(self, winning_vote):
        update_win(self, winning_vote)