from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton


class SocialChoicePanel(QVBoxLayout):
    def __init__(self):
        super().__init__()
        vote_label = QLabel("Vote")
        vote_box = QLineEdit()
        submit_button = QPushButton("Submit")

        self.addWidget(vote_label)
        self.addWidget(vote_box)
        self.addWidget(submit_button)