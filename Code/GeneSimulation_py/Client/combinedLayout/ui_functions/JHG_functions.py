import pyqtgraph as pg
from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtGui import QCursor

from .jhg_network_graph import update_jhg_network_graph
from ..colors import COLORS


# Custom ScatterPlotItem that supports tooltips
class HoverScatter(pg.ScatterPlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)


    def hoverEvent(self, event):
        if event.isExit():
            QToolTip.showText(QCursor.pos(), "")
            return
        points = self.pointsAt(event.pos())
        if points:
            point = points[0]
            cursor_pos = QCursor.pos()

            # Create an offset to show the tooltip to the right of the cursor
            offset = QPoint(10, -30)  # Adjust the (10, 0) values as needed for spacing

            # Set the tooltip position
            tooltip_position = cursor_pos + offset

            # Show the tooltip (default system look)
            QToolTip.showText(tooltip_position, str(point.data()))


def update_jhg_ui_elements(main_window):
    for i in range(main_window.round_state.num_players):
        if i == int(main_window.round_state.client_id):
            main_window.round_state.players[i].kept_number_label.setText(str(int(main_window.round_state.received[i])))
        else:
            main_window.round_state.players[i].received_label.setText(str(int(main_window.round_state.received[i])))
            main_window.round_state.players[i].sent_label.setText(str(int(main_window.round_state.sent[i])))

        main_window.round_state.allocations[i] = 0
        main_window.round_state.players[i].popularity_label.setText(
            str(round(main_window.round_state.message["POPULARITY"][i])))
        main_window.round_state.players[i].popularity_over_time.append(main_window.round_state.message["POPULARITY"][i])
        main_window.round_state.players[i].allocation_box.setText("0")

        update_jhg_popularity_graph(main_window.round_state, main_window.jhg_popularity_graph)


def update_jhg_popularity_graph(round_state, jhg_popularity_graph):
    jhg_popularity_graph.clear()
    max_popularity = 0

    for i, player in enumerate(round_state.players):
        color = COLORS[i]
        pen = pg.mkPen(color, width=2)

        x = list(range(len(player.popularity_over_time)))
        y = player.popularity_over_time

        # Main line
        jhg_popularity_graph.plot(x, y, pen=pen)

        # Tooltip spots
        spots = [
            {'pos': (x[j], y[j]), 'data': f"{player.id + 1}", 'brush': pg.mkBrush(color), 'size': 10, 'pen': None}
            for j in range(len(x))
        ]

        scatter = HoverScatter(spots=spots)
        jhg_popularity_graph.addItem(scatter)

        max_popularity = max(max_popularity, max(y))

    view_box = jhg_popularity_graph.getViewBox()
    view_box.setLimits(
        xMin=0,
        xMax=round_state.jhg_round_num + 1,
        yMin=0,
        yMax=max_popularity + 10,
    )

    jhg_popularity_graph.setXRange(0, round_state.jhg_round_num + 1, padding=0)
    jhg_popularity_graph.setYRange(0, max_popularity + 10, padding=0)


def jhg_over(main_window):
    for button in main_window.jhg_buttons:
        button.setEnabled(False)

    update_jhg_network_graph(main_window)

    for button in main_window.SC_voting_grid.buttons:
        if button.objectName() != "clear_button":
            button.setEnabled(True)

    main_window.SC_panel.setCurrentIndex(0)
    main_window.round_state.sc_cycle = 1
    main_window.SC_cause_graph.update_cycle_label(1, True)

    main_window.SC_panel.setStyleSheet("#SC_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: none; }")
    main_window.SC_panel.setTabText(0, "Current Round")


def enable_jhg_buttons(main_window):
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.SC_panel.setStyleSheet("#SC_Panel { border: none; }")
    for button in main_window.jhg_buttons:
        if button.objectName() == "JHGSubmitButton":
            button.setText("Submit")
        button.setEnabled(True)

    main_window.setWindowTitle(f"JHG: Round {main_window.round_state.jhg_round_num + 1}")