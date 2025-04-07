import random
# I literally just want to see what happens when people play randomly. I am expecting a lot of nothing to happen.
# low cooperation score, 0 slope at the end, low covariance as well (especialyl over repeated games)

class RandomBot():
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "R"

    def set_chromosome(self, chromosome): # doesn't actually get used, just for conveience sake
        self.chromosome = chromosome

    def get_vote(self, empty_list, current_options_matrix):
        total_options = len(current_options_matrix[0]) # how many cuases are there
        final_vote = random.randint(0, total_options)
        final_vote -= 1 # off my one error.
        return final_vote
