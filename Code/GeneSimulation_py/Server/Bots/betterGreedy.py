import copy
from collections import Counter
import numpy as np

class betterGreedy:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "BG"
        self.chromosome = None
        self.risk_adversity = "MAX"
        # so RISK adversity is MAX (1) and High (0). It's not implemented yet.

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, big_boy_list, current_options_matrix):

        self_id = self.self_id
        mutable_matrix = [[max(val + 1, 0) for val in [0] + row] for row in current_options_matrix]

        # Normalize each row
        for row in mutable_matrix:
            total = sum(row)
            if total > 0:
                for i in range(len(row)):
                    row[i] /= total

        # Sum each column
        num_cols = len(mutable_matrix[0])
        col_sums = [sum(mutable_matrix[row][col] for row in range(len(mutable_matrix))) for col in range(num_cols)]

        # Normalize column sums
        col_total = sum(col_sums)
        col_probs = [val / col_total for val in col_sums]

        # Compute our new row
        our_row = current_options_matrix[self_id]
        new_row = [0]  # offset column 0
        risk_aversion = self.chromosome[0]
        for i, val in enumerate(our_row):
            if val > 0:
                #new_row.append(col_probs[i + 1] * val)
                new_prob = col_probs[i + 1] ** risk_aversion
                new_row.append(new_prob * val)

            else:
                new_row.append(0)


        # Return index of max value, correcting for offset
        return new_row.index(max(new_row)) - 1

















