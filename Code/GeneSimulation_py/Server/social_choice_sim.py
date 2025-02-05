import math
import random
import numpy as np

from Code.GeneSimulation_py.Server.Node import Node

class Social_Choice_Sim:
    def __init__(self, num_players, num_causes):
        self.num_players = num_players
        self.players = self.create_players()
        self.num_options = 3 # we can do more? just to start here.
        self.rad = 5  # hardcoded just work with me here
        self.num_causes = num_causes
        self.causes = self.create_cause_nodes(num_causes)

    def create_players(self):
        players = {}
        for i in range(self.num_players):
            players[str(i)] = 0
        return players
        # creates a 0 dict for all the players at some list i. I could not do that, but this feels safer.

    def apply_vote(self, winning_vote):
        print("this is the index we are currently considering, ", winning_vote)
        for i in range(self.num_players):
            self.players[str(i)] += self.options_matrix[i][int(winning_vote)]
        print("this is what we look like after we have voted ", winning_vote, "\n", self.players)




    def create_options_matrix(self):
        #self.options_matrix = [[10,-10,-10]]
        #return self.options_matrix
        self.options_matrix = [[random.randint(-10, 10) for _ in range(self.num_options)] for _ in range(self.num_players)]
        return self.options_matrix # because why not

    def create_cause_nodes(self, num_causes):
        displacement = (2 * math.pi) / num_causes
        causes = []
        for i in range(num_causes):
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            causes.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i+1)))
        return causes

    def create_player_nodes(self):
        player_nodes = []
        for i in range(self.num_players): # i is the player index
            current_x = 0 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
            current_y = 0
            for cause_index in range(self.num_causes):
                # get the strength of the new vectors
                position_x, position_y = self.causes[cause_index].get_x(), self.causes[cause_index].get_y()
                if self.options_matrix[i][cause_index] >= 0:
                    position_x = (position_x * self.options_matrix[i][cause_index]) / (2.1 * self.rad)
                    position_y = (position_y * self.options_matrix[i][cause_index]) / (2.1 * self.rad)
                else: # ignore negative numbers. too many headaches.
                    position_x = 0
                    position_y = 0

                current_x += position_x
                current_y += position_y

            player_nodes.append(Node(current_x, current_y, "PLAYER", "Player " + str(i+1)))

        return player_nodes

    def get_causes(self):
        return self.causes


def normalize_vector(vector):
    return vector / np.linalg.norm(vector)
