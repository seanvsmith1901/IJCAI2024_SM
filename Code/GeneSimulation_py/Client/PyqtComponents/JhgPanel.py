from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QGridLayout

from .SubmitButton import SubmitButton

class JhgPanel(QVBoxLayout):
    def __init__(self, round_state, client_socket, token_counter):
        super().__init__()
        # footer
        footer = QHBoxLayout()
        submitButton = SubmitButton()
        submitButton.clicked.connect(lambda: submitButton.submit(round_state, client_socket))
        footer.addWidget(submitButton)
        token_counter.setText(f"Tokens: {round_state.tokens}")
        footer.addWidget(token_counter)

        # Each of the following blocks of code creates a column to display a particular type of data per player.
        # Each column loops through the players and adds the respective element from the associated player class.
        player_panel = QGridLayout()

        # ID column - Displays the id + 1 (for human readability) of each player
        player_panel.addWidget(QLabel("Player"), 0, 0)
        for i in range(0, 11):
            player_panel.addWidget(round_state.players[i].id_label, i + 1, 0)

        # Popularity column - Displays the popularity of the player at the start of the current round
        player_panel.addWidget(QLabel("Popularity"), 0, 1)
        for i in range(0, 11):
            player_panel.addWidget(round_state.players[i].popularity_label, i + 1, 1)

        # Sent column - Displays the number of tokens that the client player sent to the associated player the last round
        player_panel.addWidget(QLabel("Sent"), 0, 2)
        for i in range(0, 11):
            player_panel.addWidget(round_state.players[i].sent_label, i + 1, 2)

        # Received column - Displays the number of tokens that the client player received from the associated player the last round
        player_panel.addWidget(QLabel("Received"), 0, 3)
        for i in range(0, 11):
            player_panel.addWidget(round_state.players[i].received_label, i + 1, 3)

        # Allocations column - Shows the number of tokens that the client player has allocated to the associated player,
        # as well as buttons to change that value
        player_panel.addWidget(QLabel("Allocations"), 0, 4)
        for i in range(0, 11):
            allocations_row = QHBoxLayout()
            if i == int(round_state.client_id):
                allocations_row.addWidget(QLabel("You :)"))
            else:
                allocations_row.addWidget(round_state.players[i].minus_button, 2)
                allocations_row.addWidget(round_state.players[i].allocation_box, 1)
                allocations_row.addWidget(round_state.players[i].plus_button, 2)

                # Connect the functions that update counters to the plus and minus buttons
                round_state.players[i].minus_button.update.connect(
                    partial(round_state.players[i].update_allocation_minus, round_state, token_counter, i))
                round_state.players[i].plus_button.update.connect(
                    partial(round_state.players[i].update_allocation_plus, round_state, token_counter, i))
            player_panel.addLayout(allocations_row, i + 1, 4)

        self.addLayout(player_panel)
        self.addLayout(footer)