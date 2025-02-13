import json

from Player import Player


class RoundState:
    players = []
    client_id = -1 # look at JHG panel for debugging stuff.
    round_number = 0

    # Stuff for jhg
    tokens = 22 # Number of tokens remaining for the current round
    allocations = [0 for _ in range(11)] # Represents the tokens that you will send to others
    received = [0 for _ in range(11)] # Each position in the list represents the number of tokens received from the player with id _
    sent = [0 for _ in range(11)]
    popularity_over_time = [100 for _ in range(11)]


    # Stuff for sc
    options = []
    nodes = []
    utilities = []

    def __init__(self, id, num_players, num_causes):
        self.num_players = num_players
        self.client_id = id
        self.num_causes = num_causes

        for i in range(num_players):
            self.players.append(Player(i))

    def state_to_JSON(self):
        self.allocations[int(self.client_id)] = self.tokens
        message = {
            "CLIENT_ID": self.client_id,
            "ALLOCATIONS": self.allocations,
            "ROUND_NUMBER": self.round_number,
        }

        return json.dumps(message)