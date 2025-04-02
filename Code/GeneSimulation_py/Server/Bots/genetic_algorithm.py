import random
from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
from collections import Counter


def initalize_population(pop_size, num_genes, lower_bound, upper_bound):
    popualtion = []

    for _ in range(pop_size):
        chromosome = [random.uniform(lower_bound, upper_bound) for _ in range(num_genes)]
        popualtion.append(chromosome)

    return popualtion

def define_fitness(chromosome):
    sim = Social_Choice_Sim(11, 3, 0, 3)  # starts the social choice sim, call it whatever you want
    sim.set_chromosome(chromosome)
    results = {}
    num_rounds = 10
    for i in range(11): # total_players
        results[i] = [] # just throw in all the utilites

    for i in range(num_rounds): # just a ridicuously large number

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.
        bot_votes = sim.get_votes() # where da magic happens

        total_votes = len(bot_votes)
        winning_vote_count = Counter(bot_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(bot_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > total_votes // 2):
            winning_vote = -1

        for i in range(total_votes):
            results[i].append(current_options_matrix[i][winning_vote])

    print("here were the resuts ", results)
        #print("This was the current options matrix \n", current_options_matrix, "\n this were the probabilities \n", probs, " \n these were the actual votes \n", bot_votes, " and here was the winning vote ", winning_vote)
    # Number of rounds (assuming all bots have the same number of rounds)
    num_rounds = len(next(iter(results.values())))  # length of the list of scores for a single bot
    sums_per_round = {}
    for bot in results:
        sums_per_round[bot] = []
        current_sum = 0
        for i, new_sum in enumerate(results[bot]):
            current_sum += new_sum
            sums_per_round[bot].append(current_sum)

    total_sum = 0
    for current_sum in sums_per_round:
        total_sum += sums_per_round[current_sum][-1] # get the latest score

    total_average = total_sum / num_rounds
    random_player = random.randint(0, len(population) - 1)
    random_player_score = sums_per_round[random_player][-1] / num_rounds
    fitness = random_player_score - total_average
    return fitness # how will did a random player do with this algorithm, how much better did they do than everyone else.




if __name__ == '__main__':
    pop_size = 11
    num_genes = 18 # the total parameters I want to explore. look at gameTheory.py.
    lower_bound = 0
    upper_bound = 1

    population = initalize_population(pop_size, num_genes, lower_bound, upper_bound)
    for chromosome in population:
        print("this is how fit a particular chromosome is ", define_fitness(chromosome))

