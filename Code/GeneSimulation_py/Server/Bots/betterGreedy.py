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
        pass

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, big_boy_list, current_options_matrix):
        mutable_current_options_matrix = copy.deepcopy(current_options_matrix)
        for row in mutable_current_options_matrix:
            row.insert(0, 0)

        num_rows = len(mutable_current_options_matrix)
        num_cols = len(mutable_current_options_matrix[0])

        for i in range(num_rows):
            for j in range(num_cols):
                if mutable_current_options_matrix[i][j] < 0:
                    mutable_current_options_matrix[i][j] = 0
                else: # to represent 0 in a way that makes sense.
                    mutable_current_options_matrix[i][j] += 1

        # this then normalizes it.
        for i in range(num_rows):
            total_sum = sum(mutable_current_options_matrix[i])
            for col in range(num_cols):
                if mutable_current_options_matrix[i][col] > 0:
                    mutable_current_options_matrix[i][col] /= total_sum

        # now we sum up the columsn to find which column has the best shot of winning
        total_column_values = []
        for col in range(num_cols):
            current_col_value = 0
            for row in range(num_rows):
                current_col_value += mutable_current_options_matrix[row][col]
            total_column_values.append(current_col_value)

        total_sum = sum(total_column_values)
        total_column_values = [item / total_sum for item in total_column_values]

        our_row = current_options_matrix[self.self_id] # gets us our current row
        new_row = copy.deepcopy(our_row)
        new_row.insert(0, 0)
        for i in range(len(new_row)):
            if i == 0:
                new_row[i] = 0
            else:
                if new_row[i] > 0:
                    new_row[i] = total_column_values[i] * current_options_matrix[self.self_id][i-1] # to get the current utility
                else:
                    new_row[i] = 0
        max_value = max(new_row)
        max_index = new_row.index(max_value)
        return max_index - 1 # off by 1 error.


















