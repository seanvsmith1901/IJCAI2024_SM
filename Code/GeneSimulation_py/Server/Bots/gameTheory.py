import copy
from collections import Counter

class gameTheoryBot:
    def __init__(self, self_id):
        self.self_id = self_id
        self.type = "GT"
        # my idea for risk adversity is as follows:
        # MAX: Follows the most likely outcome
        # HIGH: unless the reward is higher for the second most likely outcome and those are fairly close, vote likely
        # MEDIUM-HIGH - looks at first and second, is more willing to go less likely.
        # MEDIUM LOW - looks at first second and third, is willing much more willing to go less likely
        # LOW - Purely expected value based.
        # MIN - pure greedy basically.
        self.risk_adversity = "MAX"

    # here is what teh scturecture is going to look like. store an array, and at that index store the value of what they ahve voted for.
    def get_vote(self, normalized_cause_probability, current_options_matrix):
        self.current_options_matrix = current_options_matrix
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        # so what we currently have is a giant mcfetching list of all of the options and their associated probability.
        # so now we need to create a dict of causes, everytime a cause wins we add that probability to that cause
        # so we can calculate the probability of that cause winning.
        # so thats nuts.

        current_rewards = self.think_about_reward(normalized_cause_probability)
        current_vote = self.use_bot_type(current_rewards)

        #max_tuple = max(current_rewards, key=lambda x: x[1]) # if we want a pure expected value vote.

        return current_vote # offset for -1 cause we normally start at 0.
        # so now we have a couple of options. we can scale based on a few things, such as following current greedy probability
        # or we can make it focused on pure reward. RN lets make it focused on pure reward and go from there.


    def use_bot_type(self, current_rewards): # lets start here for now.
        ra = self.risk_adversity
        max_tuple = max(current_rewards, key=lambda x: x[1]) # getting the max right off the bat could be helpful.
        max_value, max_chance = max_tuple
        max_index  = current_rewards.index(max_tuple)  # offset for -1 cause we normally start at 0.
        if ra == "MAX":
            return current_rewards.index(max_tuple) - 1 # to adjust for 0 and -1 error.
        if ra == "HIGH": # if they are within 0.9 of eachother and the reward is significantly higher.
            for index, reward in enumerate(current_rewards):
                expected_value, chance = reward # double check this line.
                # if there is a higher payoff to be found here
                if self.current_options_matrix[self.self_id][index] > (self.current_options_matrix[self.self_id][max_index]) * 1.5:
                    if (chance / max_chance) > 0.9: # margin of error
                        return index
            return max_index # if there is no better option, return the max





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
        total_votes = len(all_possibilities[0]) # just the first element. if its emty something is afoot.
        for possibility in all_possibilities:
            counts = Counter(possibility)
            winning_vote = counts.most_common(1)[0][0]
            winning_vote_count = counts.most_common(1)[0][1]
            if winning_vote_count > total_votes // 2: # check for majority
                cause_probability[int(winning_vote)] += possibility[-1]
            else:
                cause_probability[0] += possibility[-1] # no majority, 0 is now the most likel yo pass
        return cause_probability

    # start here. This is where all teh magic starts.
    def generate_all_possibilities(self, current_options_matrix):
        self.current_options_matrix = current_options_matrix
        choices_matrix = self.create_choices_matrix(current_options_matrix)
        probability_matrix = self.create_probability_matrix(choices_matrix)
        # just ot make sure we have everythinbg we need.
        self.num_players = len(current_options_matrix)
        self.num_causes = len(current_options_matrix[0])
        self.probability_matrix = probability_matrix
        options = {}
        new_array = [1] * (len(current_options_matrix) + 1)  # n + 1 total values
        big_boy_list = []
        self.add_more_stuff(0, options, new_array, big_boy_list) # recursive function to generate all the fetchers.
        cause_probability = self.get_cause_probability(big_boy_list)


        normalized_cause_probability = copy.copy(cause_probability)
        normalized_cause_probability = [(x / sum(normalized_cause_probability)) for x in normalized_cause_probability]

        return normalized_cause_probability

    ## creates the choice of each index, from 2 being the best to -1 being the worst. (2, 1, 0, -1)
    def create_choices_matrix(self, current_options_matrix):
        new_probabilities_matrix = copy.deepcopy(current_options_matrix)
        for i in range(len(current_options_matrix)):
            new_list = new_probabilities_matrix[i]
            new_list.insert(0, 0)
            sorted_list = sorted(new_list)
            index_map = {val: idx - 1 for idx, val in enumerate(sorted_list)}  # Get new indexes
            new_probabilities_matrix[i] = [index_map[val] for val in new_list]  # Replace values with indexes
        return new_probabilities_matrix

    # reorders the probabilibty matrix to contain probabilities -- 3 or 4th choice get zeroed out, 25% chance to pick second choice.
    # this is where we could afford to do some refining.
    def create_probability_matrix(self, choices_matrix):
        probability_matrix = copy.deepcopy(choices_matrix)

        for i in range(len(choices_matrix)):
            for j in range(len(choices_matrix[i])):
                if j == 0: # considering no vote
                    if choices_matrix[i][j] == 2: # no vote is their most likely option
                        probability_matrix[i][j] = 1 # if their best option is no vote, they aren't going to vote for anything else.
                        continue # keep moving on
                    if choices_matrix[i][j] == 1: #
                        probability_matrix[i][j] = 0.25
                        continue # keep moving on

                if self.current_options_matrix[i][j-1] > 0: # if there is a positive value
                    if choices_matrix[i][j] == -1: # all positive options are now considered.
                        probability_matrix[i][j] = .1
                    if choices_matrix[i][j] == 0:
                        probability_matrix[i][j] = .25
                    if choices_matrix[i][j] == 1:
                        probability_matrix[i][j] = .5
                    if choices_matrix[i][j] == 2:
                        probability_matrix[i][j] = .75
                elif self.current_options_matrix[i][j-1] == 0:
                    if choices_matrix[i][j] == 1 :
                        probability_matrix[i][j] = 0.25
                    if choices_matrix[i][j] == 2:
                        probability_matrix[i][j] = 1 # its this or nothing. nothing else really makes sense.
                else:
                    probability_matrix[i][j] = 0 # if its negative, ain't no way they are voting for it.

        return probability_matrix


    def add_more_stuff(self, current_id, options, current_array, big_boy_list):

        if current_id == self.num_players:
            return

        for cause in range(-1, (self.num_causes)): # for each cause, crate a new array with that vote for that player filled in
            new_cause = cause + 1 # I think this is needed as an adjustment?
            prob = self.probability_matrix[current_id][new_cause]
            if prob > 0:
                new_array = current_array.copy()
                new_array[current_id] = new_cause
                new_name = str(current_id) + '_' + str(new_cause)
                options[new_name] = {}
                new_array[-1] *= prob
                self.add_more_stuff(current_id + 1, options[new_name], new_array, big_boy_list)

                if current_id + 1 == self.num_players:
                    big_boy_list.append(new_array)
                    options[new_name] = new_array


