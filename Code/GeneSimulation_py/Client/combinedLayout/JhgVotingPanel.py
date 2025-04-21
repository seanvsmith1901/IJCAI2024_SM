from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QFrame, QWidget
from .SubmitButton import SubmitButton

from .colors import COLORS


class JhgVotingPanel(QVBoxLayout):
    def __init__(self, round_state, connection_manager, token_counter, jhg_buttons):
        super().__init__()
        while round_state.client_id == -1: # tripping over its own shoelaces.
            pass
        # footer
        # Needs to go through the SubmitButton class so that the signal and socket works correctly
        submitButton = SubmitButton()
        jhg_buttons.append(submitButton)
        submitButton.clicked.connect(lambda: submitButton.submit(round_state, connection_manager))
        token_counter.setText(f"Tokens: {round_state.tokens}")

        # Each of the following blocks of code creates a column to display a particular type of data per player.
        # Each column loops through the players and adds the respective element from the associated player class.
        player_panel = QGridLayout()

        # Headers for the table
        player_panel.addWidget(QLabel("Player"), 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        player_panel.addWidget(QLabel("Popularity"), 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        player_panel.addWidget(QLabel("Sent"), 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        player_panel.addWidget(QLabel("Received"), 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        player_panel.addWidget(QLabel("Allocations"), 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)

        # Creates a row in the gui for each player to display the popularity, tokens sent to, and tokens received from
        # that player the last round. Also adds the elements to allow for token allocations
        row_index = 1
        for i in range(round_state.num_players):
            if i == int(round_state.client_id):
                # --- Line above ---
                spacer_above = QFrame()
                spacer_above.setStyleSheet("background-color: #3a414a; margin-bottom: -20px")
                spacer_above.setFrameShape(QFrame.Shape.HLine)
                spacer_above.setFrameShadow(QFrame.Shadow.Sunken)
                player_panel.addWidget(spacer_above, row_index, 0, 1, player_panel.columnCount())
                row_index += 1

                # --- Client row ---
                round_state.players[i].id_label.setText(f"You ({i + 1})")
                player_panel.addWidget(round_state.players[i].id_label, row_index, 0)
                round_state.players[i].id_label.setStyleSheet(f"color: " + COLORS[i])
                player_panel.addWidget(round_state.players[i].popularity_label, row_index, 1)
                player_panel.addWidget(round_state.players[i].kept_text_label, row_index, 3)
                player_panel.addWidget(round_state.players[i].kept_number_label, row_index, 4)

                round_state.players[i].id_label.setFixedHeight(30)

                row_index += 1  # move past client row

                # --- Line below ---
                spacer_below = QFrame()
                spacer_below.setStyleSheet("background-color: #3a414a;")
                spacer_below.setFrameShape(QFrame.Shape.HLine)
                spacer_below.setFrameShadow(QFrame.Shadow.Sunken)
                player_panel.addWidget(spacer_below, row_index, 0, 1, player_panel.columnCount())
            else:
                # everyone else
                player_panel.addWidget(round_state.players[i].id_label, row_index, 0)
                round_state.players[i].id_label.setStyleSheet(f"color: " + COLORS[i])
                player_panel.addWidget(round_state.players[i].popularity_label, row_index, 1)
                player_panel.addWidget(round_state.players[i].sent_label, row_index, 2)
                player_panel.addWidget(round_state.players[i].received_label, row_index, 3)

                allocations_row = QGridLayout()
                allocations_row.addWidget(round_state.players[i].minus_button, 0, 0)
                allocations_row.addWidget(round_state.players[i].allocation_box, 0, 1)
                round_state.players[i].allocation_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
                allocations_row.addWidget(round_state.players[i].plus_button, 0, 2)

                round_state.players[i].minus_button.update.connect(
                    partial(round_state.players[i].update_allocation_minus, round_state, token_counter, i))
                round_state.players[i].plus_button.update.connect(
                    partial(round_state.players[i].update_allocation_plus, round_state, token_counter, i))

                player_panel.addLayout(allocations_row, row_index, 4)

            row_index += 1

        # round_state.num_players + 4 accounts for the header and the spacer lines.
        player_panel.addWidget(submitButton, round_state.num_players + 4, 0, 1, 3)
        player_panel.addWidget(token_counter, round_state.num_players + 4, 3, 1, 3)


        self.addLayout(player_panel)
        # self.addLayout(footer)