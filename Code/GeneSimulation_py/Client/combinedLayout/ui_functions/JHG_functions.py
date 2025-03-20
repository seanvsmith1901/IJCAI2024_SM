import pyqtgraph as pg
from ..colors import COLORS


def update_jhg_ui_elements(main_window):
    for i in range(main_window.round_state.num_players):
        # If players[i] is the client, show tokens kept. Else, show the received and sent tokens for that player
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
        pen = pg.mkPen(COLORS[i])
        main_window.jhg_plot.plot(main_window.round_state.players[i].popularity_over_time, pen=pen)


def disable_jhg_buttons(main_window):
    for button in main_window.jhg_buttons:
        button.setEnabled(False)


def enable_jhg_buttons(main_window):
    for button in main_window.jhg_buttons:
        button.setEnabled(True)
