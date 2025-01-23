from PyQt6.QtWidgets import QLabel


class Player:
    received_from_player = 0
    sent_to_player = 0
    popularity = 100

    def __init__(self, id):
        self.id = id

        self.id_label = QLabel(str(self.id + 1))
        self.popularity_label = QLabel(str(self.popularity))
        self.sent_label = QLabel(str(self.received_from_player))
        self.received_label = QLabel(str(self.sent_to_player))