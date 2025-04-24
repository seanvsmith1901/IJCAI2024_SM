import numpy as np

from Player import Player


class RoundState:
    players = []
    client_id = -1 # look at JHG panel for debugging stuff.
    jhg_round_num = 0
    sc_round_num = 0

    # Stuff for jhg
    tokens = 0 # Number of tokens remaining for the current round
    allocations = [] # Represents the tokens that you will send to others
    received = [] # Each position in the list represents the number of tokens received from the player with id _
    sent = []
    popularity_over_time = []


    # Stuff for sc
    options = []
    nodes = {}
    utilities = []

    def __init__(self, id, num_players, jhg_buttons):
        self.num_players = num_players
        self.client_id = id
        self.tokens = 2 * num_players  # Number of tokens remaining for the current round
        self.allocations = [0 for _ in range(num_players)]  # Represents the tokens that you will send to others
        self.received = [0 for _ in range(num_players)] # Each position in the list represents the number of tokens received from the player with id _
        self.sent = [0 for _ in range(num_players)]
        self.popularity_over_time = [100 for _ in range(num_players)]
        self.influence_mat = np.array([[0 for _ in range(num_players)] for _ in range(num_players)])
        self.relationships_mat = np.array([[0 for _ in range(num_players)] for _ in range(num_players)])
        self.current_votes = [-1 for _ in range(num_players)]
        self.sc_cycle = None


        for i in range(num_players):
            self.players.append(Player(i))
            jhg_buttons.append(self.players[-1].minus_button)
            jhg_buttons.append(self.players[-1].plus_button)


    def get_allocations_list(self):
        self.allocations[int(self.client_id)] = self.tokens
        return self.allocations