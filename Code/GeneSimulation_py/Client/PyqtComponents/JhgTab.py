from PyQt6.QtWidgets import QHBoxLayout, QStackedLayout

from .JhgPanel import JhgPanel

class JhgTab(QHBoxLayout):
    def __init__(self, round_state, client_socket, token_counter, jhg_popularity_plot):
        super().__init__()

        # Where token allocation happens
        jhg_voting_panel = JhgPanel(round_state, client_socket, token_counter)

        # Where the graphs are
        plots_panel = QStackedLayout()

        plots_panel.addWidget(jhg_popularity_plot)

        self.addLayout(jhg_voting_panel)
        self.addLayout(plots_panel)