# this brother doesn't even think, he just votes greedy. haven't implemented him yet though, at least in here. THere is a basic implementation under
# the SOcial choice sim under get vote. just repurpose the code under this umbrella and go from there.
import math


class GreedyBot():
    def __init__(self, self_id):
        self.self_id = self_id

    def get_vote(self, current_options_matrix):
        distance_array = []
        player_array = []
        cause_array = []
        organized_dict = {}
        for player in range(len(current_options_matrix)):
            organized_dict[player] = {}
            for cause in range(len(current_options_matrix[player])):
                organized_dict[player][cause] = 0
                # lets use x1 as player and x2 as cause.
                current_distance = (math.sqrt(((self.causes[cause].get_x() + self.player_nodes[player].get_x()) ** 2) + (self.causes[cause].get_y() + self.player_nodes[player].get_y()) ** 2))
                distance_array.append(current_distance)
                player_array.append(player)




                cause_array.append(cause)
                organized_dict[player][cause] = current_distance
        big_boy_array = list(zip(distance_array, player_array, cause_array))
        sorted_list = sorted(big_boy_array, key=lambda x: x[0])
        self.organized_distance_dict = organized_dict
        self.create_default_greedy()

    def create_default_greedy(self):
        default_greedy = []
        for player in self.organized_distance_dict:  # gets me the keys
            player_dict = self.organized_distance_dict[player]
            min_key = min(player_dict, key=player_dict.get)
            default_greedy.append(min_key)
        self.default_greedy = default_greedy
