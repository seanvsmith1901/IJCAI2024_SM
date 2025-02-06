from PyQt6.QtWidgets import QLabel, QGridLayout, QHBoxLayout, QWidget


class SocialChoicePanel(QHBoxLayout):
    # def update_utilities(self):
    #     for player in self.round_state.players:
    #         self.main_window.cause_table_layout.addWidget(QLabel(str(player.id)), player.id + 1, 0)
    #
    #     # For each cause
    #     for i in range(self.round_state.num_causes):
    #
    #         # Set the appropriate QLabel to display the utility of that cause
    #         for j in range(self.round_state.num_players):
    #             self.main_window.utility_qlabels[j][i].setText(self.round_state.utilities[j][i])
    #             self.main_window.cause_table_layout.addWidget(self.main_window.utility_qlabels[i][j], j + 1, i + 1)

    def __init__(self, round_state, main_window):
        self.round_state = round_state
        self.main_window = main_window

        super().__init__()
        # self.utility_qlabels = [[QLabel("hey") for _ in range(self.round_state.num_players)] for _ in range(self.round_state.num_causes)]
        # self.cause_table_layout = QGridLayout()
        # self.cause_table_layout.addWidget(QLabel("Player"), 0, 0)
        # for player in self.round_state.players:
        #     self.cause_table_layout.addWidget(QLabel(str(player.id)), player.id + 1, 0)
        #
        # for i in range(self.round_state.num_causes):
        #     self.cause_table_layout.addWidget(QLabel("Cause #" + str(i)), 0, i + 1)
        #
        #     for j in range(self.round_state.num_players):
        #         self.cause_table_layout.addWidget(utility_qlabels[i][j], j + 1, i + 1)
        #
        # self.cause_table = QWidget()
        # self.cause_table.setLayout(self.cause_table_layout)
        #
        # self.addWidget(self.cause_table)
