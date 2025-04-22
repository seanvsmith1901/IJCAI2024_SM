import pyqtgraph as pg

from .jhg_network_graph import update_jhg_network_graph
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
        # pen = pg.mkPen(COLORS[i])
        update_jhg_popularity_graph(main_window.round_state, main_window.jhg_popularity_graph)
        # main_window.jhg_popularity_graph.plot(main_window.round_state.players[i].popularity_over_time, pen=pen)


def update_jhg_popularity_graph(round_state, jhg_popularity_graph):
    max_popularity = 0
    for i in range(len(round_state.players)):
        pen = pg.mkPen(COLORS[i])
        jhg_popularity_graph.plot(round_state.players[i].popularity_over_time, pen=pen)
        if max(round_state.players[i].popularity_over_time) > max_popularity:
            max_popularity = max(round_state.players[i].popularity_over_time)

    view_box = jhg_popularity_graph.getViewBox()
    view_box.setLimits(xMin=0, xMax =round_state.jhg_round_num + 1, yMin=0, yMax=max_popularity + 10)

    jhg_popularity_graph.setXRange(0, round_state.jhg_round_num + 1, padding=0)
    jhg_popularity_graph.setYRange(0, max_popularity + 10, padding=0)



def jhg_over(main_window):
    for button in main_window.jhg_buttons:
        button.setEnabled(False)

    update_jhg_network_graph(main_window)

    # Enable the SC buttons
    for button in main_window.SC_voting_grid.buttons:
        if button.objectName() != "clear_button":
            button.setEnabled(True)

    main_window.SC_panel.setStyleSheet("#SC_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: none; }")


def enable_jhg_buttons(main_window):
    main_window.JHG_panel.setStyleSheet("#JHG_Panel { border: 2px solid #FFFDD0; border-radius: 5px; }")
    main_window.SC_panel.setStyleSheet("#SC_Panel { border: none; }")
    for button in main_window.jhg_buttons:
        if button.objectName() == "JHGSubmitButton":
            button.setText("Submit")
        button.setEnabled(True)

    main_window.setWindowTitle(f"JHG: Round {main_window.round_state.jhg_round_num + 1}")
