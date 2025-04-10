from PyQt6.QtWidgets import QWidget, QTabWidget, QHBoxLayout
from .JhgVotingPanel import JhgVotingPanel


class JhgPanel(QHBoxLayout):
    def __init__(self, round_state, connection_manager, token_counter, jhg_popularity_plot, jhg_network_graph, jhg_buttons):
        super().__init__()
        JHG_panel_layout = QHBoxLayout()

        # Where token allocation happens
        jhg_voting_panel = QWidget()  # Create the QWidget that will hold the layout
        voting_layout = JhgVotingPanel(round_state, connection_manager, token_counter, jhg_buttons)  # Create the layout
        jhg_voting_panel.setLayout(voting_layout)  # Set the layout to the QWidget

        # Where the graphs are shown
        plots_panel = QTabWidget()
        plots_panel.addTab(jhg_popularity_plot, "Popularity over time")
        plots_panel.addTab(jhg_network_graph, "Network graph")

        JHG_panel_layout.addWidget(jhg_voting_panel)
        JHG_panel_layout.addWidget(plots_panel)
        self.addLayout(JHG_panel_layout)