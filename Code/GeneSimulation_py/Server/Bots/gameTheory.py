import copy
from collections import Counter

class gameTheoryBot:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "GT"

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, all_possibilities, current_options_matrix):
        self.current_options_matrix = current_options_matrix
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        # so what we currently have is a giant mcfetching list of all of the options and their associated probability.
        # so now we need to create a dict of causes, everytime a cause wins we add that probability to that cause
        # so we can calculate the probability of that cause winning.
        # so thats nuts.
        cause_probability = self.get_cause_probability(all_possibilities)
        normalized_cause_probability = copy.copy(cause_probability)
        normalized_cause_probability = [(x / sum(normalized_cause_probability)) for x in normalized_cause_probability]
        current_rewards = self.think_about_reward(normalized_cause_probability)
        max_tuple = max(current_rewards, key=lambda x: x[1])
        return current_rewards.index(max_tuple) - 1
        # so now we have a couple of options. we can scale based on a few things, such as following current greedy probability
        # or we can make it focused on pure reward. RN lets make it focused on pure reward and go from there.



    def think_about_reward(self, normalized_cause_probability):
        current_options = self.current_options_matrix
        current_rewards = [] # stores a tuple that contains the index and the expected reward.
        for i, value in enumerate(normalized_cause_probability):
            if i == 0:
                expected_reward = 0
            else:
                expected_reward = value * current_options[self.self_id][i-1]

            current_rewards.append((value, expected_reward)) # want it as a tuple
        return current_rewards




    def get_cause_probability(self, all_possibilities):
        cause_probability = [0 for _ in range(self.num_causes + 1)]
        for possibility in all_possibilities:
            counts = Counter(possibility)
            most_common = counts.most_common(1)[0][0]
            cause_probability[int(most_common) + 1] += possibility[-1]
        return cause_probability


    def generate_all_possibilities(self, current_options_matrix):
        self.current_options_matrix = current_options_matrix
        choices_matrix = self.create_choices_matrix(current_options_matrix)
        probability_matrix = self.create_probability_matrix(choices_matrix)
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        self.probability_matrix = probability_matrix
        options = {}
        new_array = [1] * (len(current_options_matrix) + 1)  # n + 1 total values
        big_boy_list = []
        self.add_more_stuff(0, options, new_array, big_boy_list) # recursive function to generate all the fetchers.
        return big_boy_list

    def create_choices_matrix(self, current_options_matrix):
        new_probabilities_matrix = copy.deepcopy(current_options_matrix)
        for i in range(len(current_options_matrix)):
            new_list = new_probabilities_matrix[i]
            new_list.insert(0, 0)
            sorted_list = sorted(new_list)
            index_map = {val: idx - 1 for idx, val in enumerate(sorted_list)}  # Get new indexes
            new_probabilities_matrix[i] = [index_map[val] for val in new_list]  # Replace values with indexes
        return new_probabilities_matrix

    def create_probability_matrix(self, choices_matrix):
        probability_matrix = copy.deepcopy(choices_matrix)
        for i in range(len(choices_matrix)):
            for j in range(len(choices_matrix[i])):
                if choices_matrix[i][j] == -1:
                    probability_matrix[i][j] = 0
                if choices_matrix[i][j] == 0:
                    probability_matrix[i][j] = 0
                if choices_matrix[i][j] == 1:
                    probability_matrix[i][j] = .25
                if choices_matrix[i][j] == 2:
                    probability_matrix[i][j] = .75

        return probability_matrix


    def add_more_stuff(self, current_id, options, current_array, big_boy_list):

        if current_id == self.num_players:
            return

        for cause in range(-1, (self.num_causes)): # for each cause, crate a new array with that vote for that player filled in

            prob = self.probability_matrix[current_id][cause]
            if prob > 0:
                new_array = current_array.copy()
                new_array[current_id] = cause
                new_name = str(current_id) + '_' + str(cause)
                options[new_name] = {}
                new_array[-1] *= prob
                self.add_more_stuff(current_id + 1, options[new_name], new_array, big_boy_list)

                if current_id + 1 == self.num_players:
                    big_boy_list.append(new_array)
                    options[new_name] = new_array


