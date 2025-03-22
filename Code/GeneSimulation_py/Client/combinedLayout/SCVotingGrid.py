from functools import partial

from PyQt6.QtWidgets import QPushButton

from SCGrid import SCGrid


class SCVotingGrid(SCGrid):
    def __init__(self, num_players, num_causes, graphs_layout, main_window):
        col_2_vals = [0 for _ in range(num_players)]
        utility_mat = [[0 for _ in range(num_causes)] for _ in range(num_players)]
        super().__init__(num_players, num_causes, "Utility", col_2_vals, utility_mat)

        self.insertLayout(0, graphs_layout)
        self.vote_buttons = [QPushButton("Vote") for _ in range(num_causes)]

        from ui_functions.SC_functions import sc_vote, sc_submit
        submit_button = QPushButton("Submit")
        submit_button.setEnabled(False)
        submit_button.clicked.connect(partial(sc_submit, main_window))
        self.grid.addWidget(submit_button, num_players + 2, 0)


        for col in range(num_causes):
            button = self.vote_buttons[col]
            button.setEnabled(False)
            button.clicked.connect(partial(sc_vote, main_window, col))
            self.grid.addWidget(self.vote_buttons[col], num_players + 2, col + 2)

        self.buttons = self.vote_buttons
        self.buttons.append(submit_button)

