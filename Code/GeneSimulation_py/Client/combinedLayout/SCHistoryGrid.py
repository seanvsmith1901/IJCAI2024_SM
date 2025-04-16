from PyQt6.QtWidgets import QHBoxLayout, QLabel, QComboBox

from .SCGrid import SCGrid


class SCHistoryGrid(SCGrid):
    def __init__(self, num_players, player_id, col_2_header_text):
        self.sc_history = {}
        col_2_vals = [0 for _ in range(num_players)]
        utility_mat = [[0 for _ in range(3)] for _ in range(num_players)]
        super().__init__(num_players, player_id, col_2_header_text, col_2_vals, utility_mat)

        self.round_drop_down = QComboBox()
        self.round_drop_down.currentIndexChanged.connect(self.change_round)

        self.selector_layout = QHBoxLayout()
        self.selector_layout.addWidget(QLabel("Round to view"))
        self.selector_layout.addWidget(self.round_drop_down)

        self.layout.insertLayout(0, self.selector_layout)

    def change_round(self, index):
        round_key = str(index + 1)
        if round_key in self.sc_history:
            self.update_grid(self.sc_history[round_key]["votes"], self.sc_history[round_key]["utilities"])


    def update_sc_history(self, round, votes, utilities):
        self.round_drop_down.addItem(f"Round {round}")
        self.sc_history[str(round)] = {"votes": votes, "utilities": utilities}

        self.round_drop_down.repaint()
        self.round_drop_down.setCurrentIndex(round - 1)


    def update_grid(self, votes, utilities):
        super().update_grid(votes, utilities)

        # Find the winning vote, if it exists
        vote_counts = {"1": 0, "2": 0, "3": 0}
        for vote in votes:
            if vote != -1:
                vote_counts[str(vote)] += 1
        winning_vote = int(max(vote_counts, key=vote_counts.get))

        # Ensures that the most popular vote has a majority (> 50%)
        if vote_counts[str(winning_vote)] <= len(votes) // 2:
            winning_vote = 0

        # if winning_vote != 0:
        winning_vote -= 1 # Winning vote is one indexed, so it needs to be converted to 0 index
        # Loop through the labels for each player
        for row_idx, row in enumerate(self.cause_utility_labels):
            # Access each label in the row
            for cause_idx, label in enumerate(row):
                # If this label coincides with the winning vote, color it based off of the utility for the current player
                if cause_idx == winning_vote:
                    if utilities[row_idx][winning_vote] > 0:
                        label.setStyleSheet("color: green;")
                    elif utilities[row_idx][winning_vote] < 0:
                        label.setStyleSheet("color: red;")
                    else:
                        label.setStyleSheet("color: white;")
                else:
                    label.setStyleSheet("color: white;")

        for i, label in enumerate(self.header_labels):
            label.setStyleSheet("color: white;")
            if winning_vote != -1:
                if i - 2 == winning_vote: # There are two columns before the utility labels start, so you need to subtract 2
                    label.setStyleSheet("color: green;")