from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QGridLayout
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
        for i in range(round_state.num_players):
            player_panel.addWidget(round_state.players[i].id_label, i + 1, 0)         # Player ID
            round_state.players[i].id_label.setStyleSheet(f"color: " + COLORS[i])
            player_panel.addWidget(round_state.players[i].popularity_label, i + 1, 1) # Popularity at the start of this round

            # If the current player is the client, then simply place a QLabel labeling it in the allocations_row
            allocations_row = QGridLayout()
            if i == int(round_state.client_id):
                round_state.players[i].id_label.setText(f"You ({i + 1})")

                player_panel.addWidget(round_state.players[i].kept_text_label, i + 1, 3)
                player_panel.addWidget(round_state.players[i].kept_number_label, i + 1, 4)
            else:
                player_panel.addWidget(round_state.players[i].sent_label, i + 1, 2)  # Tokens client sent to this player last round
                player_panel.addWidget(round_state.players[i].received_label, i + 1, 3)  # Tokens received by the client from this player last round
                allocations_row.addWidget(round_state.players[i].minus_button, 0, 0)
                allocations_row.addWidget(round_state.players[i].allocation_box, 0, 1)
                round_state.players[i].allocation_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
                allocations_row.addWidget(round_state.players[i].plus_button, 0, 2)

                # Connect the functions that update counters to the plus and minus buttons
                round_state.players[i].minus_button.update.connect(
                    partial(round_state.players[i].update_allocation_minus, round_state, token_counter, i))
                round_state.players[i].plus_button.update.connect(
                    partial(round_state.players[i].update_allocation_plus, round_state, token_counter, i))
            player_panel.addLayout(allocations_row, i + 1, 4)

        player_panel.addWidget(submitButton, round_state.num_players + 2, 0, 1, 3)
        player_panel.addWidget(token_counter, round_state.num_players + 2, 3, 1, 3)


        self.addLayout(player_panel)
        # self.addLayout(footer)