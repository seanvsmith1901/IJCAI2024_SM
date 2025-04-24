from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from combinedLayout.allocation_buttons import MinusButton, PlusButton

class Player:
    received_from_player = 0
    sent_to_player = 0
    popularity = 100

    # For SC
    displayed_vote = None


    # Handle updating the sent, received, and tokens remaining fields after the minus button is pressed
    def update_allocation_minus(self, round_state, tokens_label, player):
        # If the client player has decided to steal from the associated player, subtract one from both that player's
        # allocation and the tokens available to the client player
        if round_state.allocations[player] <= 0:
            if round_state.tokens > 0:
                round_state.allocations[player] = round_state.allocations[player] - 1
                round_state.tokens -= 1
        else:
            round_state.allocations[player] = round_state.allocations[player] - 1
            round_state.tokens += 1

        self.allocation_box.setText(str(round_state.allocations[player]))
        tokens_label.setText("Tokens: " + str(round_state.tokens))


    # Handle updating the sent, received, and tokens remaining fields after the plus button is pressed
    def update_allocation_plus(self, round_state, tokens_label, player):
        # If the client player has not decided to steal tokens, then one should be added to the associated player's
        # allocation, and one subtracted from tokens available for the client player
        if round_state.allocations[player] >= 0:
            if round_state.tokens > 0:
                round_state.allocations[player] = round_state.allocations[player] + 1
                round_state.tokens -= 1
        else:
            round_state.allocations[player] = round_state.allocations[player] + 1
            round_state.tokens += 1

        self.allocation_box.setText(str(round_state.allocations[player]))
        tokens_label.setText("Tokens: " + str(round_state.tokens))


    def __init__(self, id):
        self.id = id
        self.popularity_over_time = [self.popularity]

        # PyQt elements that make up the rows of the JHG_panel. Contained in the Player class for ease of access/tying them to the player
        self.id_label = QLabel(str(self.id + 1))
        self.popularity_label = QLabel(str(self.popularity))
        self.sent_label = QLabel(str(self.received_from_player))
        self.received_label = QLabel(str(self.sent_to_player))

        # Center the labels
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.popularity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.received_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.kept_text_label = QLabel("Tokens kept:")
        self.kept_number_label = QLabel("0")
        self.minus_button = MinusButton()
        self.minus_button.setStyleSheet("max-height: 1.2em")
        self.minus_button.setStyleSheet("min-height: 1.2em")
        self.plus_button = PlusButton()
        self.plus_button.setStyleSheet("max-height: 1.2em")
        self.plus_button.setStyleSheet("min-height: 1.2em")
        self.allocation_box = QLabel("0")

        self.minus_button.setMinimumWidth(self.minus_button.fontMetrics().horizontalAdvance("-") + 20)
        self.plus_button.setMinimumWidth(self.plus_button.fontMetrics().horizontalAdvance("+") + 20)

        # Label to display total utilities
        self.utility_label = QLabel("0")