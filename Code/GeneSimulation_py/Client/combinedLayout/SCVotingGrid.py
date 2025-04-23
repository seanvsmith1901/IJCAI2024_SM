from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget

from SCGrid import SCGrid


NUM_CAUSES = 3

class SCVotingGrid(SCGrid):
    def __init__(self, num_players, player_id, graphs_layout, main_window):
        from ui_functions.SC_functions import sc_vote
        self.current_vote = -1
        self.player_id = player_id

        col_2_vals = [0 for _ in range(num_players)]
        utility_mat = [[0 for _ in range(NUM_CAUSES)] for _ in range(num_players)]
        super().__init__(num_players, self.player_id, "Utility", col_2_vals, utility_mat)

        # Set up the clear button
        self.clear_button = QPushButton("Clear Vote")
        self.clear_button.setObjectName("clear_button")
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(partial(sc_vote, main_window, -1))
        self.clear_button.clicked.connect(partial(self.select_button, None))

        # Set up the submit button
        self.submit_button = QPushButton("Submit Vote")
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(partial(self.submit_clicked, main_window, self.submit_button))
        self.submit_button.setObjectName("SCSubmitButton")

        # Add the submit and clear buttons to a layout and set that as the header
        self.header = QHBoxLayout()
        self.header.addWidget(self.submit_button)
        self.header.addWidget(self.clear_button)

        self.layout.insertLayout(0, self.header)

        self.vote_buttons = [QPushButton(f"Cause {i + 1}") for i in range(NUM_CAUSES)]
        for col in range(NUM_CAUSES):
            button = self.vote_buttons[col]
            button.setMinimumWidth(70)
            button.setMaximumWidth(100)
            button.setEnabled(False)

            # Wrap the button in a container widget that expands
            wrapper = QWidget()
            layout = QHBoxLayout(wrapper)
            layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the button
            layout.addWidget(button)

            self.grid.addWidget(wrapper, 0, col + 2)
            self.grid.setColumnStretch(col + 2, 1)  # Still let the column expand

            button.clicked.connect(partial(sc_vote, main_window, col))
            button.clicked.connect(partial(self.select_button, button))

        self.buttons = self.vote_buttons
        self.buttons.append(self.submit_button)
        self.buttons.append(self.clear_button)

    # If None is passed as button, it will clear the vote (used for teh clear vote button and to reset after the round)
    def select_button(self, button):
        button_found = False
        for i, vote_button in enumerate(self.vote_buttons):
            if vote_button == button:
                vote_button.setProperty("btnState", "checked")
                self.current_vote = i
                self.clear_button.setEnabled(True)
                button_found = True
            elif vote_button.objectName() == "SCSubmitButton":
                button_found = True
            else:
                vote_button.setProperty("btnState", "unchecked")

            vote_button.style().unpolish(vote_button)
            vote_button.style().polish(vote_button)
            vote_button.update()

        if not button_found:
            self.current_vote = -1

        if button is None:
            self.clear_button.setEnabled(False)

    def submit_clicked(self, main_window, submit_button):
        from ui_functions.SC_functions import sc_submit
        sc_submit(main_window, self)

        submit_button.setText(f"Resubmit Vote")