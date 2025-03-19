from PyQt6.QtWidgets import QWidget, QTabWidget, QHBoxLayout

from .JhgVotingPanel import JhgVotingPanel


class JhgPanel(QWidget):
    def __init__(self, round_state, client_socket, token_counter, jhg_popularity_plot, jhg_network_graph, jhg_buttons):
        super().__init__()
        JHG_panel_layout = QHBoxLayout()

        # Where token allocation happens
        # jhg_voting_panel = JhgVotingPanel(round_state, client_socket, token_counter, jhg_buttons)
        jhg_voting_panel = QWidget()
        jhg_voting_panel.setLayout(JhgVotingPanel(round_state, client_socket, token_counter, jhg_buttons))
        # Where the graphs are shown
        plots_panel = QTabWidget()


        plots_panel.addTab(jhg_popularity_plot, "Popularity over time")
        plots_panel.addTab(jhg_network_graph, "Network graph")

        JHG_panel_layout.addWidget(jhg_voting_panel)
        JHG_panel_layout.addWidget(plots_panel)
        self.setLayout(JHG_panel_layout)