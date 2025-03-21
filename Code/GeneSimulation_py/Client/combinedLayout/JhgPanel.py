from PyQt6.QtWidgets import QWidget, QTabWidget, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QPainter, QColor

from .JhgVotingPanel import JhgVotingPanel


class JhgPanel(QHBoxLayout):
    def __init__(self, round_state, client_socket, token_counter, jhg_popularity_plot, jhg_network_graph, jhg_buttons):
        super().__init__()
        JHG_panel_layout = QHBoxLayout()

        # Where token allocation happens
        jhg_voting_panel = QWidget()  # Create the QWidget that will hold the layout
        voting_layout = JhgVotingPanel(round_state, client_socket, token_counter, jhg_buttons)  # Create the layout
        jhg_voting_panel.setLayout(voting_layout)  # Set the layout to the QWidget

        # Where the graphs are shown
        plots_panel = QTabWidget()
        plots_panel.addTab(jhg_popularity_plot, "Popularity over time")
        plots_panel.addTab(jhg_network_graph, "Network graph")

        JHG_panel_layout.addWidget(jhg_voting_panel)
        JHG_panel_layout.addWidget(plots_panel)
        self.addLayout(JHG_panel_layout)

    def paintEvent(self, event):
        # Create a QPainter to paint custom graphics
        painter = QPainter(self)

        # Set custom drawing properties (e.g., background color)
        # painter.setBrush(QColor(255, 255, 0))  # Yellow background
        painter.setPen(QColor(255, 0, 0))  # Red border
        painter.drawRect(self.rect())  # Draw the border of the widget

        # Finish painting and clean up
        painter.end()