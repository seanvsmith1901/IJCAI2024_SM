import math
import random
import numpy as np

from Node import Node

class Social_Choice_Sim:
    def __init__(self, num_players, num_causes):
        self.num_players = num_players
        self.players = self.create_players()
        self.cpp = 3
        self.rad = 5  # hardcoded just work with me here
        self.num_causes = num_causes
        self.causes = self.create_cause_nodes(num_causes)
        self.current_options_matrix = {}
        self.player_nodes = []
        self.all_votes = {}

    def create_players(self):
        players = {}
        for i in range(self.num_players):
            players[str(i)] = 0
        return players
        # creates a 0 dict for all the players at some list i. I could not do that, but this feels safer.

    def apply_vote(self, winning_vote):
        for i in range(self.num_players):
            self.players[str(i)] += self.options_matrix[i][int(winning_vote)]

    def create_options_matrix(self):
        #self.options_matrix = [[10,-10,-10]]
        #return self.options_matrix
        self.options_matrix = [[random.randint(-10, 10) for _ in range(self.num_causes)] for _ in range(self.num_players)]
        return self.options_matrix # because why not

    def create_cause_nodes(self, num_causes):
        displacement = (2 * math.pi) / num_causes # need an additional "0" cause.
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
                position_x = (position_x * self.options_matrix[i][cause_index]) / (2 * self.rad)
                position_y = (position_y * self.options_matrix[i][cause_index]) / (2 * self.rad)

                current_x += position_x
                current_y += position_y

            player_nodes.append(Node(current_x, current_y, "PLAYER", "Player " + str(i+1)))

        return player_nodes

    def get_causes(self):
        return self.causes

    def get_current_options_matrix(self):
        return self.current_options_matrix

    def get_player_nodes(self):
        return self.player_nodes

    def get_nodes(self):
        return self.player_nodes + self.causes

    def get_player_utility(self):
        return self.players

    def start_round(self):
        # options may change, but the causes themselves don't, so we can generate them in init functionality.
        self.current_options_matrix = self.create_options_matrix()
        self.player_nodes = self.create_player_nodes()
        # YOU ARE GOING TO NEED TO GET THE BOT VOTES FROM THE JHG OBJECT - WE USE THOSE BOTS AGAIN.

    # takes in the influence matrix, and then spits out the 3 strongest calculated relations for every player.
    def calculate_relation_strength(self, new_relations):
        cpp = self.cpp # how many closest personal promises each player has or something.
        # this is where I had to decide how I wanted to gauge the strength of relations
        new_values = self.apply_heuristic(new_relations)
        # specialized bc of negative values and possible stealing.
        normalized_values = self.normalize(new_values)
        # goes through the normalized heuristic, finds the cpp strongest, and makes them into a serializable dictionary we can send across.
        return_values = self.make_dict(normalized_values, cpp)
        return_values = self.make_native_type(return_values)
        return return_values

    def make_native_type(self, return_values):
        new_dict = {}
        for key, inner_dict in return_values.items():
            new_key = key.item() if isinstance(key, np.integer) else key
            new_inner_dict = {}
            for item, value in inner_dict.items():
                new_inner_dict[item] = value.item if isinstance(value, np.generic) else value
            new_dict[new_key] = new_inner_dict
        return new_dict


    def make_dict(self, normalized_values, cpp):
        return_values = {}
        for i in range(len(normalized_values)): # its square so it doesn't really matter
            row = np.array(normalized_values[i]) # I think that works?
            indices = np.argsort(np.abs(row))[-cpp:]
            extreme_values = row[indices]
            return_values[i] = {}
            dict_pop = {}
            for idx, value in zip(indices, extreme_values):
                dict_pop[idx] = value
            return_values[i] = dict_pop
        return return_values


    def normalize(self, new_values):
        normalized_matrix = np.array(new_values)
        if normalized_matrix.min() < 0: # for negative values - likely doesn't work.
            for element in normalized_matrix.flat: # literally no freaking clue if this works.
                if element > 0:
                    normalized_matrix[element] = element / (normalized_matrix.max())
                elif element < 0:
                    normalized_matrix[element] = element / (normalized_matrix.min())
                # otherwise its 0 and we don't have to do anything.

        else: # all positive values, so we can normalize this the easy way.
            normalized_matrix = (normalized_matrix - normalized_matrix.min()) / (normalized_matrix.max() - normalized_matrix.min())

        normalized_matrix = np.round(normalized_matrix, decimals=2) # reduce size.
        return normalized_matrix

    def apply_heuristic(self, new_relations):
        # I GOT IT FINALLY! This line structure has been messing with me for a while now.
        relation_strengths = [[0] * self.num_players for _ in range(self.num_players)]
        for i in range(len(new_relations)):
            for j in range(len(new_relations)):
                if i == j: # This way we don't consider self-relations - just remove them from the matrix.
                    new_relations[i][j] = 0
                if new_relations[i][j] != 0 and new_relations[j][i] != 0:
                    new_value = (new_relations[i][j] + new_relations[j][i]) / 2
                    relation_strengths[i][j] = new_value
                    relation_strengths[j][i] = new_value
                elif new_relations[i][j] == 0 and new_relations[j][i] != 0:
                    print(new_relations[j][i])
                    new_value = math.sqrt(new_relations[j][i])
                    relation_strengths[j][i] = new_value
                    relation_strengths[i][j] = new_value
                elif new_relations[j][i] == 0 and new_relations[i][j] != 0:
                    new_value = math.sqrt(new_relations[i][j])
                    relation_strengths[i][j] = new_value
                    relation_strengths[j][i] = new_value
                else:
                    relation_strengths[i][j] = 0
                    relation_strengths[j][i] = 0
        return relation_strengths

    def add_votes(self, round, votes):
        # We have to put them all somewhere and here works as good as anywhere else. Not sure if we will need it.
        self.all_votes[round] = votes

    def get_votes(self):
        # aight so what we need to do here
        pass
        # we first need to assemble what likelehood we have of everyone switching.
        # how can we model this? I don't really know.
        # see I want a probablility of switches and then just evaluate some of them
        # i might have to do more trig.
        # or I could evalute the distance from each node given the nodes, evalutae that distance, put it in a 2d array
        # then convert that into something I can use.
        # sure why note
        distance_array = [[0 for cause in self.num_causes] for player in self.num_players]
        for player in range(len(self.options_matrix)):
            for cause in range(len(self.options_matrix[player])):
                dist = [player] - current_cause_node

        # pull out the most likely ones, put it in a format we can use
        # from there, evalute all possible


        # this is the portion I don't understand - not sure the best way to brute force it without just blowing up my computer haha.
        # like I understand that some swaps are more likely than others but like
        # I don't understand how I should force swaps to be considered
        # we should do this even if there is a majority, just to check to see if there is a better nash equilibrium that is somewhat likely
        # i am NOT sure how to evalute how likely a swap is, likely using a multiplicaiton of distance
        # but given that, I am not sure how high that needs to be in order to conisder siwtching
        # obviously if we are at a favorible nash equilibrium, is it even worth considering a swap?
        # idk. THose are questions for future sean bc this project might get hairy.
        # could be mad fun though, I am looking forward to it.
        # for swap in swaps (ordered from most likely to least likely, likely with a max limiter)
            # if w/ swap there is a majority
                # save swap as a nash equilibria


