from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QTabWidget

from combinedLayout.colors import COLORS


class SCGrid(QTabWidget):
    def __init__(self, num_players, client_id, col_2_header_text, col_2_vals, utility_mat):
        super().__init__()
        header_text_list = ["Player", col_2_header_text] + [f"Cause #{i + 1}" for i in range(3)] # 3 is the number of causes

        self.id = int(client_id)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        def centered_label(text):
            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return label

        self.header_labels = [centered_label(header_text) for header_text in header_text_list]
        self.player_labels = [centered_label(f"{i + 1}") for i in range(num_players)]
        self.col_2_labels = [centered_label(str(val)) for val in col_2_vals]
        self.cause_utility_labels = [[centered_label(str(utility)) for utility in utility_mat[i]] for i in
                                     range(num_players)]

        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        # Add the header
        for col, label in enumerate(self.header_labels):
            self.grid.addWidget(label, 0, col)

        # Add the Player numbers to identify each row
        for row, label in enumerate(self.player_labels):
            if row == self.id:
                label.setText(f"You ({row + 1})")
            label.setStyleSheet("color: " + COLORS[row])
            self.grid.addWidget(label, row + 1, 0)

        # Add a label to display whatever it is that is being displayed in column 2 (utility over time, past vote, etc.)
        for row, label in enumerate(self.col_2_labels):
            self.grid.addWidget(label, row + 1, 1)

        # Add the labels for the utility per player
        for row, row_labels in enumerate(self.cause_utility_labels):
            for col, label in enumerate(row_labels):
                self.grid.addWidget(label, row + 1, col + 2)


    def update_grid(self, col_2_vals, utility_mat, round_num):
        self.update_col_2(col_2_vals)
        self.update_utilities(utility_mat)


    def update_col_2(self, col_2_vals):
        if type(col_2_vals) == dict:
            col_2_vals = [value for key, value in sorted(col_2_vals.items())]
        for i, label in enumerate(self.col_2_labels):
            label.setText(str(col_2_vals[i]))


    def update_utilities(self, utility_mat):
        for row, row_labels in enumerate(self.cause_utility_labels):
            for col, widget in enumerate(row_labels):
                row_labels[col].setText(str(utility_mat[row][col]))