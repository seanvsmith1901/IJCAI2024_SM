import copy
from collections import Counter
import numpy as np

class gameTheoryBot:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "GT"
        self.chromosome = None
        self.risk_adversity = "MAX"
        # so RISK adversity is MAX (1) and High (0). It's not implemented yet.

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, big_boy_list, current_options_matrix):
        cause_probability = self.get_cause_probability(big_boy_list)
        normalized_cause_probability = copy.copy(cause_probability)
        normalized_cause_probability = [(x / sum(normalized_cause_probability)) for x in normalized_cause_probability]

        self.current_options_matrix = current_options_matrix
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])

        current_rewards = self.think_about_reward(normalized_cause_probability)
        current_vote = self.use_bot_type(current_rewards) # accounts for off by one error.

        return current_vote


    # takes in the current options matrix, returns the probability of each cause passing.
    def generate_probabilities(self, current_options_matrix):
        weights_array = self.chromosome # just name passing
        self.current_options_matrix = current_options_matrix # and setting
        choices_matrix, choice_list = self.create_choices_matrix(current_options_matrix) # figures out which choice each cause is for each player
        probability_matrix = self.create_probability_matrix(choices_matrix, weights_array) # generates the probaility matirx
        # just ot make sure we have everythinbg we need.
        self.num_players = len(current_options_matrix) # sets some stats
        self.num_causes = len(current_options_matrix[0]) # sets other stats
        self.probability_matrix = probability_matrix # ikd if this helps or not but its there

        big_boy_list = list(self.generate_combinations(0, [1] * (self.num_players + 1))) # this is a FERTCHER. generates every possible vote and its probability
        cause_probability = self.get_cause_probability(big_boy_list) # this is also a fetcher. Adds all them up and multiplies them to find the final probabiliyt
        normalized_cause_probability = copy.copy(cause_probability) # we just want to normalize the probabilities so they add to 1
        normalized_cause_probability = [(x / sum(normalized_cause_probability)) for x in normalized_cause_probability] # normalize them
        return normalized_cause_probability # returns that probability

    def get_vote_optimized_single(self, normalized_cause_probability, current_options_matrix):
        self.current_options_matrix = current_options_matrix
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        current_rewards = self.think_about_reward(normalized_cause_probability)
        current_vote = self.use_bot_type(current_rewards)
        return current_vote  # offset for -1 cause we normally start at 0.

    def use_bot_type(self, current_rewards): # cut some stuff out for now, we can add this in later to fine tune risk adversity.
        ra = self.chromosome[19] # last element in the chromosome represents the risk adversity.
        max_tuple = max(current_rewards, key=lambda x: x[1]) # getting the max right off the bat could be helpful.
        max_value, max_chance = max_tuple
        max_index  = current_rewards.index(max_tuple)  # offset for -1 cause we normally start at 0.
        if ra == 1 or ra == 0:
            return current_rewards.index(max_tuple) - 1 # to adjust for 0 and -1 error.
        # if ra == 0: # if they are within 0.9 of eachother and the reward is significantly higher. This hasn't been tested, remove for now.
        #     for index, reward in enumerate(current_rewards):
        #         expected_value, chance = reward # double check this line.
        #         # if there is a higher payoff to be found here
        #         if self.current_options_matrix[self.self_id][index] > (self.current_options_matrix[self.self_id][max_index]) * 1.5:
        #             if (chance / max_chance) > self.chromosome[18]: # margin of error
        #                 return index
        #     return max_index # if there is no better option, return the max

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
        num_causes = 3
        cause_probability = [0 for _ in range(num_causes + 1)]
        total_votes = len(all_possibilities[0]) # just the first element. if its emty something is afoot.
        for possibility in all_possibilities:
            freqs = {}
            max_item = None
            max_count = 0

            # doing this by hand my speed it up
            for item in possibility:
                freqs[item] = freqs.get(item, 0) + 1
                if freqs[item] > max_count:
                    max_count = freqs[item]
                    max_item = item

            if max_count > total_votes // 2:
                cause_probability[int(max_item)] += possibility[-1]
            else:
                cause_probability[0] += possibility[-1] # no majority, 0 is now the most likely yo pass
        return cause_probability

    # start here. This is where all teh magic starts.
    def generate_all_possibilities(self, current_options_matrix):
        # this is the OG one.
        #weights_array = [1, 0.25, 0.10, 0.05, 0, 1, 0.25, 0.125, 0.0, 0.125, 0.0625, 0.003125, 0, 0.50, 0.25, 0.125, 0.0625, 0]
        weights_array = self.chromosome
        self.current_options_matrix = current_options_matrix
        choices_matrix, choice_list = self.create_choices_matrix(current_options_matrix)
        probability_matrix = self.create_probability_matrix(choices_matrix, weights_array)
        # just ot make sure we have everythinbg we need.
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        self.probability_matrix = probability_matrix


        big_boy_list = list(self.generate_combinations(0, [1] * (self.num_players + 1)))
        return big_boy_list

    ## creates the choice of each index, from 2 being the best to -1 being the worst. (2, 1, 0, -1)
    def create_choices_matrix(self, current_options_matrix):
        new_probabilities_matrix = copy.deepcopy(current_options_matrix)
        for i in range(len(current_options_matrix)):
            new_list = new_probabilities_matrix[i]
            new_list.insert(0, 0)
            sorted_list = sorted(new_list)
            index_map = {val: idx - 1 for idx, val in enumerate(sorted_list)}  # Get new indexes
            new_probabilities_matrix[i] = [index_map[val] for val in new_list]  # Replace values with indexes

        choices_array = np.array(new_probabilities_matrix)
        total_sums = choices_array.sum(axis=0)
        new_column_preferences = copy.deepcopy(total_sums.tolist())
        sorted_list = sorted(new_column_preferences)
        index_map = {val: idx - 1 for idx, val in enumerate(sorted_list)}  # Get new indexes
        column_preferences = [index_map[val] for val in new_column_preferences]  # Replace values with indexes
        return new_probabilities_matrix, column_preferences

    def create_probability_matrix(self, choices_matrix, weights_array):
        # weights are an array that holds the 5 possible edge cases
        # first is the null case and the other 4 are for varying cases
        # with the last case being almost worthless to explore so there's no reason
        # i think there are definitely better ways to map this out; having another weight being attributed to the difference in weights, for example
        # but lets start here and get something workign and go from there.

        # Total sum represents the amount of votes that particular option has
        # choice_list represents its magnitude of winning
        # so if total sum is [15, 2, 3, 4] then nothing happening has 15 votes, cause 1 has 2, etc
        # and choice list would then be [2, -1, 0, 1], where cause 1 is the most likely to win
        # I want to combine this idea of winning along with if that yeilds a positive utility to decide votes.
        # should be silly.

        choices_array = np.array(choices_matrix)
        total_sums = choices_array.sum(axis=0)

        probability_matrix = copy.deepcopy(choices_matrix)

        for i in range(len(choices_matrix)):
            for j in range(len(choices_matrix[i])): # iterating through every choice
                if j == 0: # if we are considering the no vote option
                    new_utility = 0 - max(self.current_options_matrix[i]) # consider utility to be what you are missing out on
                    if new_utility > 0: # if the max is negative
                        probability_matrix[i][j] = weights_array[0] # then we will only vote for nothing to happen

                    else:
                        if choices_matrix[i][j] == 2: # should only occur if best option is 0
                            probability_matrix[i][j] = weights_array[1]
                        elif choices_matrix[i][j] == 1:
                            probability_matrix[i][j] = weights_array[2]
                        elif choices_matrix[i][j] == 0:
                            probability_matrix[i][j] = weights_array[3]
                        elif choices_matrix[i][j] == -1:
                            probability_matrix[i][j] = weights_array[4] # literally the worst option. never vote for this.

                else: # note: j = j-1 bc current_options_matrix doesn't consider the 0th option to have a utility. might be worth fixing.
                    if total_sums[j] > 0 and self.current_options_matrix[i][j-1] > 0: # if this is GOOD for them
                        if choices_matrix[i][j] == 2: # most attractive option
                            probability_matrix[i][j] = weights_array[5] # Def what they will vote for.
                        elif choices_matrix[i][j] == 1:
                            probability_matrix[i][j] = weights_array[6] # some prob
                        elif choices_matrix[i][j] == 0:
                            probability_matrix[i][j] = weights_array[7]
                        elif choices_matrix[i][j] == 0:
                            probability_matrix[i][j] = weights_array[8] # no shot.

                    elif total_sums[j] > 0 and self.current_options_matrix[i][j-1] <= 0: # likely but not good for us
                        if choices_matrix[i][j] == 2: # change these numbers around later.
                            probability_matrix[i][j] = weights_array[9]
                        elif choices_matrix[i][j] == 1:
                            probability_matrix[i][j] = weights_array[10]
                        elif choices_matrix[i][j] == 0:
                            probability_matrix[i][j] = weights_array[11]
                        elif choices_matrix[i][j] == -1:
                            probability_matrix[i][j] = weights_array[12]

                    elif total_sums[j] <= 0 and self.current_options_matrix[i][j-1] > 0: # not very likely but good for us
                        if choices_matrix[i][j] == 2:  # change these numbers around later.
                            probability_matrix[i][j] = weights_array[13]
                        elif choices_matrix[i][j] == 1:
                            probability_matrix[i][j] = weights_array[14]
                        elif choices_matrix[i][j] == 0:
                            probability_matrix[i][j] = weights_array[15]
                        elif choices_matrix[i][j] == 0:
                            probability_matrix[i][j] = weights_array[16]

                    elif total_sums[j] <= 0 and self.current_options_matrix[i][j-1] <= 0: # not likely, not good for us.
                        probability_matrix[i][j] = weights_array[17] # there is never a reason to vote for this. this is just straight bad.

        return probability_matrix

    def generate_combinations(self, current_id, current_array):
        if current_id == self.num_players:
            yield tuple(current_array)  # Using tuple instead of copy to save memory
            return

        for cause in range(self.num_causes):
            prob = self.probability_matrix[current_id][cause]
            if prob > 0:
                current_array[current_id] = cause
                current_array[-1] *= prob
                yield from self.generate_combinations(current_id + 1, current_array)
                current_array[-1] /= prob  # Restore probability for next iteration

