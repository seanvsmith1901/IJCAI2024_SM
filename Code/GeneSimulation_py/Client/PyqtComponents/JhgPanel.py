from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget

from .SubmitButton import SubmitButton


class JhgPanel(QVBoxLayout):
    def __init__(self, round_state, client_socket):
        super().__init__()
        # footer
        footer = QHBoxLayout()
        submitButton = SubmitButton()
        submitButton.clicked.connect(lambda: submitButton.submit(round_state, client_socket))
        footer.addWidget(submitButton)
        self.token_label = QLabel("Tokens: " + str(round_state.tokens))
        footer.addWidget(self.token_label)

        # Each of the following blocks of code creates a column to display a particular type of data per player.
        # Each column loops through the players and adds the respective element from the associated player class.

        # ID column - Displays the id + 1 (for human readability) of each player
        player_id_column = QVBoxLayout()
        player_id_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        player_id_column.addWidget(QLabel("Player"))
        for i in range(0, 11):
            player_id_column.addWidget(round_state.players[i].id_label)

        # Popularity column - Displays the popularity of the player at the start of the current round
        popularity_column = QVBoxLayout()
        popularity_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        popularity_column.addWidget(QLabel("Popularity"))
        for i in range(0, 11):
            popularity_column.addWidget(round_state.players[i].popularity_label)

        # Sent column - Displays the number of tokens that the client player sent to the associated player the last round
        sent_column = QVBoxLayout()
        sent_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        sent_column.addWidget(QLabel("Sent"))
        for i in range(0, 11):
            sent_column.addWidget(round_state.players[i].sent_label)

        # Received column - Displays the number of tokens that the client player received from the associated player the last round
        received_column = QVBoxLayout()
        received_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        received_column.addWidget(QLabel("Received"))
        for i in range(0, 11):
            received_column.addWidget(round_state.players[i].received_label)

        # Allocations column - Shows the number of tokens that the client player has allocated to the associated player,
        # as well as buttons to change that value
        allocations_column = QVBoxLayout()
        allocations_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        allocations_column.addWidget(QLabel("Allocations"))
        for i in range(0, 11):
            print(f"CID: {round_state.client_id} i: {i} type: {int(round_state.client_id)}")
            allocations_row = QHBoxLayout()
            if i == int(round_state.client_id):
                allocations_row.addWidget(QLabel("You :)"))
                print("Ya boi")
            else:
                allocations_row.addWidget(round_state.players[i].minus_button, 2)
                allocations_row.addWidget(round_state.players[i].allocation_box, .5)
                allocations_row.addWidget(round_state.players[i].plus_button, 2)

                # Connect the functions that update counters to the plus and minus buttons
                round_state.players[i].minus_button.update.connect(
                    partial(round_state.players[i].update_allocation_minus, round_state, self.token_label, i))
                round_state.players[i].plus_button.update.connect(
                    partial(round_state.players[i].update_allocation_plus, round_state, self.token_label, i))

            allocations_column.addLayout(allocations_row)

        # Used to group the various columns and display them next to each other (as columns)
        column_layout = QHBoxLayout()

        column_layout.addLayout(player_id_column)
        column_layout.addLayout(popularity_column)
        column_layout.addLayout(sent_column)
        column_layout.addLayout(received_column)
        column_layout.addLayout(allocations_column)

        self.addLayout(column_layout)
        self.addLayout(footer)