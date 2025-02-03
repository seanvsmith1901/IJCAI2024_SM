from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
import pyqtgraph as pg

from .JhgPanel import JhgPanel
from .SocialChoicePanel import SocialChoicePanel


# from .SocialChoicePanel import SocialChoicePanel


class BodyLayout(QHBoxLayout):
    def __init__(self, round_state, client_socket, token_counter, jhg_plot):
        super().__init__()

        jhg_panel = JhgPanel(round_state, client_socket, token_counter)
        right_panel = QVBoxLayout()

        right_panel.addWidget(jhg_plot)

        self.addLayout(jhg_panel)
        self.addLayout(right_panel)

        # divider_line = QFrame()
        # divider_line.setFrameShape(QtWidgets.QFrame.VLine)
        # divider_line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # self.addLayout(jhg_panel)
        # self.addLayout(social_choice_panel)

        # self.addWidget(divider_line)
        # jhg_panel = JhgPanel()
        # # social_choice_panel = JhgPanel()
        #
        # # divider_line = QFrame()
        # # divider_line.setFrameShape(QtWidgets.QFrame.VLine)
        # # divider_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        #
        #
        # body_layout.addWidget(jhg_panel)
        # body_layout.addWidget(divider_line)
        # body_layout.addWidget(social_choice_panel)