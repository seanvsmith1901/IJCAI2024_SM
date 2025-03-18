import copy

import numpy as np

class gameTheoryBot:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "GT"

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, all_possibilities):
        # dummy code. fill this in better later.
        print("This is what we currently receive under all_possibilities")
        current_best = 0

        return current_best



    def generate_all_possibilities(self, current_options_matrix):
        self.current_options_matrix = current_options_matrix
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        options = {}

        new_array = [None] * (len(current_options_matrix) + 1)  # n + 1 total values

        options, new_name = self.add_more_stuff(0, options, new_array)

        return options

    def add_more_stuff(self, current_id, options, current_array, new_name=None):
        print("here is the player id ", str(current_id), " and the state of the current_array ", str(current_array))

        current_options = {}

        for cause in range(-1, (self.num_causes)): # for each cause, crate a new array with that vote for that player filled in
            new_array = current_array.copy()
            new_array[current_id] = cause
            new_name = str(current_id) + '_' + str(cause)
            current_options[new_name] = new_array

        if current_id == ((self.num_players)): # base case for jakes father in law. populate it first and go from there.
            print("We have hit return with ", current_array, " and ", new_name)
            return current_array, new_name

        current_id += 1 # go to the next player
        for player in range(current_id, self.num_players): # for every other player
            new_names = []
            new_options_list = []
            for new_name in current_options: # this is where those names are suppsoed to get stored.
                new_options = current_options[new_name]
                new_options, _ = self.add_more_stuff(player, options, new_options, new_name) # and call the same function again on the smaller case.
                new_names.append(new_name) # not sure if this will help.
                new_options_list.append(new_options)

            for i, name in enumerate(new_names):
                current_options[name] = new_options_list[i]

        return current_options, new_name



