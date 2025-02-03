from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from .JhgPanel import JhgPanel

class BodyLayout(QHBoxLayout):
    def __init__(self, round_state, client_socket, token_counter, jhg_plot):
        super().__init__()

        # Where token allocation happens
        jhg_panel = JhgPanel(round_state, client_socket, token_counter)

        # Where the graphs are
        right_panel = QVBoxLayout()

        right_panel.addWidget(jhg_plot)

        self.addLayout(jhg_panel)
        self.addLayout(right_panel)