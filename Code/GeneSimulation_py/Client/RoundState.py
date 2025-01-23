from Player import Player


class RoundState:
    tokens = 22
    allocations = [0 for i in range(11)]
    players = []

    def __init__(self):
        self.client_player = Player(10)

        for i in range(10):
            self.players.append(Player(i))
        self.players.append(self.client_player)