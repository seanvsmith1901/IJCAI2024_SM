import copy
import math
import random
import numpy as np
from networkx import normalized_cut_size

from options_creation import generate_two_plus_one_groups_options_best_of_three
from Node import Node

class Social_Choice_Sim:
    def __init__(self, num_players, num_causes):
        self.num_players = num_players
        # self.num_humans = num_humans
        # self.num_bots = num_players - num_humans
        # self.type_bot = type_bot
        self.players = self.create_players()
        self.cpp = 3
        self.rad = 5  # hardcoded just work with me here
        self.num_causes = num_causes
        self.causes = self.create_cause_nodes(num_causes)
        self.current_options_matrix = {}
        self.player_nodes = []
        self.all_votes = {}
        self.organized_distance_dict = []  # set it to an empty dict for now
        self.default_greedy = []  # len = num players, contains the current cuase that they are voting for.
        # self.bots = self.create_bots()
        self.current_votes = []  # we need to add support for if anyone else has cast a vote. Right now it doesn't reall matter
        # but like when we add players I want the bots to be able to change thier strategy based on player input. maybe.

    def create_players(self):
        players = {}
        for i in range(self.num_players):
            players[str(i)] = 0
        return players
        # creates a 0 dict for all the players at some list i. I could not do that, but this feels safer.

    def apply_vote(self, winning_vote):
        if winning_vote != -1:
            for i in range(self.num_players):
                self.players[str(i)] += self.options_matrix[i][int(winning_vote)]

    def create_options_matrix(self, groups):
        self.options_matrix = generate_two_plus_one_groups_options_best_of_three(groups)
        return self.options_matrix # because why not
        # self.options_matrix = [[random.randint(-10, 10) for _ in range(self.num_causes)] for _ in range(self.num_players)]

    def create_cause_nodes(self, num_causes):
        displacement = (2 * math.pi) / num_causes # need an additional "0" cause.
        causes = []
        for i in range(num_causes):
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            causes.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i+1)))
        return causes

    def create_player_nodes(self):
        # normalized_current_options_matrix = self.normalize_current_options_matrix()
        normalized_current_options_matrix = self.current_options_matrix

        player_nodes = []
        for i in range(self.num_players):  # i is the player index
            if i == 1:
                pass
            player_index = i
            current_x = 0  # https://www.youtube.com/watch?v=r7l0Rq9E8MY
            current_y = 0
            curr_negatives = []
            for cause_index in range(self.num_causes):  # completely populate this fetcher first.
                # keep track of negatives
                if (self.options_matrix[i][cause_index]) < 0:
                    curr_negatives.append(1)
                else:
                    curr_negatives.append(0)

            for cause_index in range(self.num_causes):
                # create the new positions (onyl use teh abs so the flips scale correctly.
                position_x, position_y = (self.causes[cause_index].get_x()), self.causes[
                    cause_index].get_y()  # get the strength based on where they are
                # take the absolute value of the strength, we will flip it later. maybe.
                # position_x = (position_x * abs(normalized_current_options_matrix[i][cause_index])) # normalize it to the circle
                position_x = ((position_x * abs(normalized_current_options_matrix[i][cause_index])) / (
                            2 * self.rad))  # normalize it to the circle
                # position_y = (position_y * abs(normalized_current_options_matrix[i][cause_index])) # normalize it to the circleposition_x = ((position_x * abs(normalized_current_options_matrix[i][cause_index])) / (2 * self.rad)) # normalize it to the circle
                position_y = ((position_y * abs(normalized_current_options_matrix[i][cause_index])) / (
                            2 * self.rad))  # normalize it to the circle

                current_x += position_x
                current_y += position_y

            # so this should sum everything up.
            # lets make a novel edge case and test it from there.

            if sum(curr_negatives) == 0:  # if there are no negatives.
                pass  # do nothing, we are in the right spot.

            if sum(curr_negatives) == 1:  # flip over unaffected line
                dots_of_interest = []
                for i, value in enumerate(curr_negatives):
                    if value == 0:
                        dots_of_interest.append(i)  # need the index, might have to do a range thing.
                point_1_x, point_1_y = round(self.causes[dots_of_interest[0]].get_x(), 2), round(
                    self.causes[dots_of_interest[0]].get_y(), 2)
                point_2_x, point_2_y = round(self.causes[dots_of_interest[1]].get_x(), 2), round(
                    self.causes[dots_of_interest[1]].get_y(), 2)
                current_x, current_y = self.flip_point_over_line(current_x, current_y, point_1_x, point_1_y, point_2_x,
                                                                 point_2_y)

            if sum(curr_negatives) == 2:  # flip over unaffectd point
                pass
                dot_of_interest = [i for i, value in enumerate(curr_negatives) if value == 0][0]

                point_x, point_y = self.causes[dot_of_interest].get_x(), self.causes[dot_of_interest].get_y()
                current_x, current_y = self.flip_point(current_x, current_y, point_x, point_y)

            if sum(curr_negatives) == 3:  # flip over origin.
                current_x, current_y = self.flip_point(current_x, current_y, 0, 0)  # we just flip over teh origin.

            player_nodes.append(Node(current_x, current_y, "PLAYER", "Player " + str(player_index + 1)))

        return player_nodes

    def flip_point_over_line(self, point_x, point_y, line_point1_x, line_point1_y, line_point2_x, line_point2_y):
        m = self.slope(line_point1_x, line_point1_y, line_point2_x, line_point2_y)
        m_perp = self.perpendicular_slope(m)

        if m == float('inf'):
            x_intersect = line_point1_x
            y_intersect = point_y
        elif m == (0):
            x_intersect = point_x
            y_intersect = line_point1_y
        else:
            x_intersect = (m * line_point1_x - m_perp * point_x - line_point1_y + point_y) / (m - m_perp)
            y_intersect = m * (x_intersect - line_point1_x) + line_point1_y

        x_reflected = 2 * x_intersect - point_x
        y_reflected = 2 * y_intersect - point_y

        return x_reflected, y_reflected

    def slope(self, x1, y1, x2, y2):
        if x2 - x1 == 0:
            return float('inf')
        return (y2 - y1) / (x2 - x1)

    def perpendicular_slope(self, m):
        if m == 0:
            return float('inf')
        if m == float('inf'):
            return 0.0
        else:
            return -1 / m

    # point 1 is the point we want to flip, point 2 is the point we are flipping over
    def flip_point(self, point_1_x, point_1_y, point_2_x, point_2_y):
        reflected_x = 2 * point_2_x - point_1_x
        reflected_y = 2 * point_2_y - point_1_y
        return reflected_x, reflected_y

    def normalize_current_options_matrix(self):
        print("This si the current options matrix \n", self.current_options_matrix)
        new_options = copy.deepcopy(self.current_options_matrix)
        for i, row in enumerate(new_options):
            new_sum = sum(abs(value) for value in row)
            if new_sum != 0:
                for j in range(len(row)):
                    new_options[i][j] /= new_sum

        print("these are the new options before multiplying \n", new_options)

        # for i in range(len(new_options)):
        #     for j in range(len(new_options[i])):
        #         new_options[i][j] *= 2 # make them sum up to 10. IG.

        print("these are the new options \n", new_options)
        return new_options

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

    def start_round(self, groups):
        # options may change, but the causes themselves don't, so we can generate them in init functionality.
        self.current_options_matrix = self.create_options_matrix(groups)
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
        new_matrix = copy.deepcopy(normalized_matrix)

        if normalized_matrix.min() < 0: # if we contain negative values.
            for i, row in enumerate(normalized_matrix):
                for j, element in enumerate(row):
                    if element > 0:
                        element = element / normalized_matrix.max()
                    elif element < 0:
                        element = element / normalized_matrix.min()
                    new_matrix[i][j] = element

        else: # all positive values, so we can normalize this the easy way.
            new_matrix = (normalized_matrix - normalized_matrix.min()) / (normalized_matrix.max() - normalized_matrix.min())

        new_matrix = np.round(new_matrix, decimals=2) # reduce size.
        return new_matrix

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
                elif new_relations[i][j] == 0 and new_relations[j][i] != 0 and new_relations[j][i] > 0:
                    new_value = math.sqrt(new_relations[j][i])
                    relation_strengths[j][i] = new_value
                    relation_strengths[i][j] = new_value
                elif new_relations[i][j] == 0 and new_relations[j][i] != 0 and new_relations[j][i] < 0:
                    new_value = math.sqrt(abs(new_relations[j][i])) # make it positive and then negative again
                    relation_strengths[j][i] = -new_value
                    relation_strengths[i][j] = -new_value
                elif new_relations[j][i] == 0 and new_relations[i][j] != 0 and new_relations [i][j] > 0:
                    new_value = math.sqrt(new_relations[i][j])
                    relation_strengths[i][j] = new_value
                    relation_strengths[j][i] = new_value
                elif new_relations[j][i] == 0 and new_relations[i][j] != 0 and new_relations[i][j] <0:
                    new_value = math.sqrt(abs(new_relations[i][j]))
                    relation_strengths[i][j] = -new_value
                    relation_strengths[j][i] = -new_value
                else:
                    relation_strengths[i][j] = 0
                    relation_strengths[j][i] = 0
        return relation_strengths

    def add_votes(self, round, votes):
        # We have to put them all somewhere and here works as good as anywhere else. Not sure if we will need it.
        self.all_votes[round] = votes

