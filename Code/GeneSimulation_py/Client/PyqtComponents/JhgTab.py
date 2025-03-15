from PyQt6.QtWidgets import QHBoxLayout, QTabWidget

from .JhgPanel import JhgPanel

class JhgTab(QHBoxLayout):
    def __init__(self, round_state, client_socket, token_counter, jhg_popularity_plot, jhg_network_graph, jhg_buttons):
        super().__init__()

        # Where token allocation happens
        jhg_voting_panel = JhgPanel(round_state, client_socket, token_counter, jhg_buttons)

        # Where the graphs are
        plots_panel = QTabWidget()

        plots_panel.addTab(jhg_popularity_plot, "Popularity over time")
        plots_panel.addTab(jhg_network_graph, "Network graph")

        self.addLayout(jhg_voting_panel)
        self.addWidget(plots_panel)