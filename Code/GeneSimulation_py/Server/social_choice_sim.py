import copy
import math
from collections import Counter

import numpy as np

from options_creation import generate_two_plus_one_groups_options_best_of_three
from Bots.Pareto import ParetoBot
from Bots.Greedy import GreedyBot
from Bots.gameTheory import gameTheoryBot
from Bots.Random import RandomBot
from Node import Node

NUM_CAUSES = 3


class Social_Choice_Sim:
    def __init__(self, total_players, num_humans, type_bot):
        self.total_players = total_players
        self.num_humans = num_humans
        self.num_bots = total_players - num_humans
        self.type_bot = type_bot
        self.players = self.create_players()
        self.cpp = 3
        self.rad = 5  # hardcoded just work with me here
        self.causes = self.create_cause_nodes()
        self.current_options_matrix = {}
        self.player_nodes = []
        self.all_votes = {}
        self.organized_distance_dict = [] # set it to an empty dict for now
        self.default_greedy = [] # len = num players, contains the current cuase that they are voting for.
        self.bots = self.create_bots()
        self.current_votes = [] # we need to add support for if anyone else has cast a vote. Right now it doesn't reall matter
        self.probabilities = []
        self.options_matrix = None


    def create_bots(self):
        bots_array = []
        for i in range(self.num_bots): # this is where we can add more bots.
            if self.type_bot == 1:  # pareto optimal bots for now
                bots_array.append(ParetoBot(i))
            if self.type_bot == 2:
                bots_array.append(GreedyBot(i))
            if self.type_bot == 3:
                bots_array.append(gameTheoryBot(i))
            if self.type_bot == 4:
                bots_array.append(RandomBot(i))

        return bots_array


    def create_players(self):
        players = {}
        for i in range(self.total_players):
            players[str(i)] = 0
        return players


    def set_chromosome(self, chromosomes):
        if len(chromosomes) != len(self.bots):
            print("WRONG WRONG WRONG")
        else:
            for i in range(len(self.bots)):
                self.bots[i].set_chromosome(chromosomes[i])


    def apply_vote(self, winning_vote):
        for i in range(self.total_players):
            self.players[str(i)] += self.options_matrix[i][int(winning_vote)]


    def create_options_matrix(self, groups):
        self.options_matrix = generate_two_plus_one_groups_options_best_of_three(groups)
        return self.options_matrix # because why not


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


    def get_probabilities(self):
        return self.probabilities


    def get_votes(self): # generic get votes for all bot types. Not optimized for a single chromosome
        bot_votes = {}
        self.all_combinations = [] # used for the current implementation of the GT bot.

        for i, bot in enumerate(self.bots):
            if bot.type == "GT":
                if not self.all_combinations:
                    self.all_combinations = bot.generate_all_possibilities(self.current_options_matrix)
                bot_votes[i] = bot.get_vote(self.all_combinations, self.current_options_matrix)
            else: # only generate the probability matrix if we need it, fetcher is expensive.
                bot_votes[i] = bot.get_vote([], self.current_options_matrix)

        return bot_votes


    def get_votes_single_chromosome(self): # if we want to visualize/test a single chromosome, use this one.
        if self.bots[0].type != "GT":
            print("Hey thats wrong, try again ")
            return
        bot_votes = {}
        self.all_combinations = [] # used for the current implementation of the GT bot.

        for i, bot in enumerate(self.bots):
            if bot.type == "GT":
                if not self.all_combinations:
                    self.probabilities = bot.generate_probabilities(self.current_options_matrix)
                bot_votes[i] = bot.get_vote_optimized_single(self.probabilities, self.current_options_matrix)

        return bot_votes


    def return_win(self, all_votes):
        results = []
        total_votes = all_votes
        winning_vote_count = Counter(total_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(total_votes.values()).most_common(1)[0][0]
        if not (winning_vote_count > len(total_votes) // 2):
            winning_vote = -1

        if winning_vote != -1: # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                results.append(self.current_options_matrix[i][winning_vote])
        else:
            for i in range(len(total_votes)):
                results.append(0)

        return winning_vote, results


    ###--- NODE CREATION FOR FRONT END. NOT USEFUL FOR GENETIC STUFF. ---###


    def create_cause_nodes(self):
        displacement = (2 * math.pi) / NUM_CAUSES # need an additional "0" cause.
        causes = []
        for i in range(NUM_CAUSES): #3 is the number of causes
            new_x = math.cos(displacement * i) * self.rad
            new_y = math.sin(displacement * i) * self.rad
            causes.append(Node(new_x, new_y, "CAUSE", "Cause " + str(i+1)))
        return causes


    def create_player_nodes(self):
        normalized_current_options_matrix = self.current_options_matrix

        player_nodes = []
        for i in range(self.total_players): # i is the player index
            if i == 1:
                pass
            player_index = i
            current_x = 0 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
            current_y = 0
            curr_negatives = []
            for cause_index in range(NUM_CAUSES):  # completely populate this fetcher first.
                # keep track of negatives
                if (self.options_matrix[i][cause_index]) < 0:
                    curr_negatives.append(1)
                else:
                    curr_negatives.append(0)

            for cause_index in range(NUM_CAUSES):
                # create the new positions (onyl use teh abs so the flips scale correctly.
                position_x, position_y = (self.causes[cause_index].get_x()), self.causes[
                    cause_index].get_y()  # get the strength based on where they are
                position_x = ((position_x * abs(normalized_current_options_matrix[i][cause_index])) / (
                            2 * self.rad))  # normalize it to the circle
                position_y = ((position_y * abs(normalized_current_options_matrix[i][cause_index])) / (
                            2 * self.rad))  # normalize it to the circle

                current_x += position_x
                current_y += position_y

            # so this should sum everything up.
            # lets make a novel edge case and test it from there.

            if sum(curr_negatives) == 0: # if there are no negatives.
                pass # do nothing, we are in the right spot.

            if sum(curr_negatives) == 1: # flip over unaffected line
                dots_of_interest = []
                for i, value in enumerate(curr_negatives):
                    if value == 0:
                        dots_of_interest.append(i) # need the index, might have to do a range thing.
                point_1_x, point_1_y = round(self.causes[dots_of_interest[0]].get_x(), 2), round(self.causes[dots_of_interest[0]].get_y(), 2)
                point_2_x, point_2_y = round(self.causes[dots_of_interest[1]].get_x(), 2), round(self.causes[dots_of_interest[1]].get_y(), 2)
                current_x, current_y = self.flip_point_over_line(current_x, current_y, point_1_x, point_1_y, point_2_x, point_2_y)

            if sum(curr_negatives) == 2: # flip over unaffectd point
                pass
                dot_of_interest = [i for i, value in enumerate(curr_negatives) if value == 0][0]

                point_x, point_y = self.causes[dot_of_interest].get_x(), self.causes[dot_of_interest].get_y()
                current_x, current_y = self.flip_point(current_x, current_y, point_x, point_y)

            if sum(curr_negatives) == 3: # flip over origin.
                current_x, current_y = self.flip_point(current_x, current_y, 0, 0) # we just flip over teh origin.

            player_nodes.append(Node(current_x, current_y, "PLAYER", "Player " + str(player_index+1)))
        return player_nodes


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


    def normalize_current_options_matrix(self):
        print("This si the current options matrix \n", self.current_options_matrix)
        new_options = copy.deepcopy(self.current_options_matrix)
        for i, row in enumerate(new_options):
            new_sum = sum(abs(value) for value in row)
            if new_sum != 0:
                for j in range(len(row)):
                    new_options[i][j] /= new_sum
        return new_options


    def start_round(self, groups):
        # options may change, but the causes themselves don't, so we can generate them in init functionality.
        self.current_options_matrix = self.create_options_matrix(groups)
        self.player_nodes = self.create_player_nodes()


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


    def add_votes(self, round, votes):
        # We have to put them all somewhere and here works as good as anywhere else. Not sure if we will need it.
        self.all_votes[round] = votes


    def compile_nodes(self):
        player_nodes = self.get_player_nodes()
        causes = self.get_causes()
        all_nodes = causes + player_nodes
        return all_nodes


    def get_bot_votes(self, current_options_matrix):
        votes = {}
        for i, player in enumerate(self.players):
            if player.getType() != "Human":
                votes[str(i)] = player.getVote(current_options_matrix, i)
        return votes