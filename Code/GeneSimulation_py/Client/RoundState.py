import json

from Player import Player


class RoundState:
    tokens = 22
    allocations = [0 for i in range(11)]
    players = []
    client_id = 10

    def __init__(self):
        self.client_player = Player(10)

        for i in range(10):
            self.players.append(Player(i))
        self.players.append(self.client_player)

    def state_to_JSON(self):
        message = {
            "CLIENT_ID": self.client_id,
            "ALLOCATIONS": self.allocations,
            "ROUND_NUMBER": 1,
        }

        return json.dumps(message)