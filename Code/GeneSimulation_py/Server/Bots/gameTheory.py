import numpy as np

class gameTheoryBot:
    def __init__(self, self_id):
        self.self_id = self_id

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, current_options_matrix):
        options = {}
        current_best = 0
        # rewrite this
        options[self.self_id] = {}
        for cause in range(-1, len(current_options_matrix[0])): # iterates from -1 to num_causes
            new_array = [None] * len(current_options_matrix)
            new_array[self.self_id] = cause
            options[self.self_id][cause] = new_array




        return current_best