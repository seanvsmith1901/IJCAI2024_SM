from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget


class JhgPanel(QVBoxLayout):
    def update_allocation_plus(self, round_state, tokens_label, box, player):
        if round_state.allocations[player] >= 0:
            if round_state.tokens > 0:
                round_state.allocations[player] = round_state.allocations[player] + 1
                round_state.tokens -= 1
        else:
            round_state.allocations[player] = round_state.allocations[player] + 1
            round_state.tokens += 1

        box.setText(str(round_state.allocations[player]))
        tokens_label.setText("Tokens: " + str(round_state.tokens))


    def update_allocation_minus(self, round_state, tokens_label, box, player):
        if round_state.allocations[player] <= 0:
            if round_state.tokens > 0:
                round_state.allocations[player] = round_state.allocations[player] - 1
                round_state.tokens -= 1
        else:
            round_state.allocations[player] = round_state.allocations[player] - 1
            round_state.tokens += 1

        box.setText(str(round_state.allocations[player]))
        tokens_label.setText("Tokens: " + str(round_state.tokens))

    def __init__(self, round_state):
        super().__init__()
        # footer
        footer = QHBoxLayout()
        submitButton = QPushButton("Submit")
        footer.addWidget(submitButton)
        self.token_label = QLabel("Tokens: " + str(round_state.tokens))
        footer.addWidget(self.token_label)

        # Columns
        player_id_column = QVBoxLayout()
        player_id_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        player_id_column.addWidget(QLabel("Player"))
        for i in range(0, 11):
            player_id_column.addWidget(round_state.players[i].id_label)

        popularity_column = QVBoxLayout()
        popularity_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        popularity_column.addWidget(QLabel("Popularity"))
        for i in range(0, 11):
            popularity_column.addWidget(round_state.players[i].popularity_label)

        sent_column = QVBoxLayout()
        sent_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        sent_column.addWidget(QLabel("Sent"))
        for i in range(0, 11):
            sent_column.addWidget(round_state.players[i].sent_label)

        received_column = QVBoxLayout()
        received_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        received_column.addWidget(QLabel("Received"))
        for i in range(0, 11):
            received_column.addWidget(round_state.players[i].received_label)

        allocations_column = QVBoxLayout()
        allocations_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        allocations_column.addWidget(QLabel("Allocations"))
        for i in range(0, 11):
            allocations_row = QHBoxLayout()

            allocation_box = QLabel("0")
            minus_button = QPushButton("-")
            minus_button.clicked.connect(partial(self.update_allocation_minus, round_state, self.token_label, allocation_box, i))
            plus_button = QPushButton("+")
            plus_button.clicked.connect(partial(self.update_allocation_plus, round_state, self.token_label, allocation_box, i))

            # Set size policy for buttons to only size to content
            minus_button.setFixedWidth(minus_button.fontMetrics().horizontalAdvance("-") + 20)
            plus_button.setFixedWidth(plus_button.fontMetrics().horizontalAdvance("+") + 20)

            allocations_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            # allocation_box.setFixedWidth(30)

            allocations_row.addWidget(minus_button)
            allocations_row.addWidget(allocation_box)
            allocations_row.addWidget(plus_button)

            allocations_column.addLayout(allocations_row)

        column_layout = QHBoxLayout()

        column_layout.addLayout(player_id_column)
        column_layout.addLayout(popularity_column)
        column_layout.addLayout(sent_column)
        column_layout.addLayout(received_column)
        column_layout.addLayout(allocations_column)

        self.addLayout(column_layout)
        self.addLayout(footer)