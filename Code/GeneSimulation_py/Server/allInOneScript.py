import copy
import math
import random
from collections import Counter

import numpy as np

from Code.GeneSimulation_py.Server.Bots.Pareto import ParetoBot
from Code.GeneSimulation_py.Server.Bots.Greedy import GreedyBot
from Code.GeneSimulation_py.Server.Bots.gameTheory import gameTheoryBot
from Code.GeneSimulation_py.Server.Bots.Random import RandomBot
from Code.GeneSimulation_py.Server.Node import Node

class Social_Choice_Sim:
    def __init__(self, total_players, num_causes, num_humans, type_bot):
        self.total_players = total_players
        self.num_humans = num_humans
        self.num_bots = total_players - num_humans
        self.type_bot = type_bot
        self.players = self.create_players()
        self.cpp = 3
        self.rad = 5  # hardcoded just work with me here
        self.num_causes = num_causes
        self.causes = self.create_cause_nodes(num_causes)
        self.current_options_matrix = {}
        self.player_nodes = []
        self.all_votes = {}
        self.organized_distance_dict = [] # set it to an empty dict for now
        self.default_greedy = [] # len = num players, contains the current cuase that they are voting for.
        self.bots = self.create_bots()
        self.current_votes = [] # we need to add support for if anyone else has cast a vote. Right now it doesn't reall matter
        self.probabilities = []

    def create_bots(self):
        bots_array = []
        for i in range(self.num_bots): # this is where we can add more bots.
            if self.type_bot == 1:  # pareto optimal bots for now
                bots_array.append(ParetoBot(i))
            if self.type_bot == 2:
                bots_array.append(GreedyBot(i))
            if self.type_bot == 3:
                bots_array.append(gameTheoryBot(i))
            if self.type_bot == 4:
                bots_array.append(RandomBot(i))

        return bots_array

    def create_players(self):
        players = {}
        for i in range(self.num_humans):
            players[str(i)] = 0
        return players

    def set_chromosome(self, chromosomes):
        if len(chromosomes) != len(self.bots):
            print("WRONG WRONG WRONG")
        else:
            for i in range(len(self.bots)):
                self.bots[i].set_chromosome(chromosomes[i])

    def apply_vote(self, winning_vote):
        for i in range(self.total_players):
            self.players[str(i)] += self.options_matrix[i][int(winning_vote)]

    def create_options_matrix(self):
        self.options_matrix = [[random.randint(-10, 10) for _ in range(self.num_causes)] for _ in range(self.total_players)]
        return self.options_matrix # because why not

    def get_causes(self):
        return self.causes

    def get_current_options_matrix(self):
        return self.current_options_matrix

    def get_player_nodes(self):
        return self.player_nodes

    def get_nodes(self):
        return self.player_nodes + self.causes

    def get_player_utility(self):
        return self.players

    def start_round(self):
        # options may change, but the causes themselves don't, so we can generate them in init functionality.
        self.current_options_matrix = self.create_options_matrix()
        # self.player_nodes = self.create_player_nodes() # TODO: UNCOMMENT THIS LINE
        # YOU ARE GOING TO NEED TO GET THE BOT VOTES FROM THE JHG OBJECT - WE USE THOSE BOTS AGAIN.

    def get_probabilities(self):
        return self.probabilities

    def get_votes(self): # generic get votes for all bot types. Not optimized for a single chromosome
        bot_votes = {}
        self.all_combinations = [] # used for the current implementation of the GT bot.

        for i, bot in enumerate(self.bots):
            if bot.type == "GT":
                if not self.all_combinations:
                    self.all_combinations = bot.generate_all_possibilities(self.current_options_matrix)
                bot_votes[i] = bot.get_vote(self.all_combinations, self.current_options_matrix)
            else: # only generate the probability matrix if we need it, fetcher is expensive.
                bot_votes[i] = bot.get_vote([], self.current_options_matrix)

        return bot_votes

    def get_votes_single_chromosome(self): # if we want to visualize/test a single chromosome, use this one.
        bot_votes = {}
        self.probabilities = [] # used for the current implementation of the GT bot.

        for i, bot in enumerate(self.bots):
            if bot.type == "GT":
                if not self.probabilities:
                    self.probabilities = bot.generate_probabilities(self.current_options_matrix)
                bot_votes[i] = bot.get_vote_optimized_single(self.probabilities, self.current_options_matrix)
            else: # only generate the probability matrix if we need it, fetcher is expensive.
                bot_votes[i] = bot.get_vote([], self.current_options_matrix)

        return bot_votes


    def return_win(self, all_votes):
        results = []
        total_votes = all_votes
        winning_vote_count = Counter(total_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(total_votes.values()).most_common(1)[0][0]
        if not (winning_vote_count > len(total_votes) // 2):
            winning_vote = -1

        if winning_vote != -1: # if its -1, then nothing happend. NOT the last entry in the fetcher. that was a big bug that flew under the radar.
            for i in range(len(total_votes)):
                results.append(self.current_options_matrix[i][winning_vote])
        else:
            for i in range(len(total_votes)):
                results.append(0)

        return winning_vote, results



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

class Chromosome:
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness = 0

    def set_fitness(self, fitness):
        self.fitness = fitness

    def add_fitness(self, new_fitness):
        self.fitness += new_fitness

    def reset_fitness(self):
        self.fitness = 0

    # Override __getitem__ to allow direct access to chromosome list
    def __getitem__(self, index):
        return self.chromosome[index]

    # Override __eq__
    def __eq__(self, other):
        return isinstance(other, Chromosome) and self.chromosome == other.chromosome

    def __hash__(self):
        return hash(tuple(self.chromosome))


import random
import time

from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
from Code.GeneSimulation_py.Server.Bots.chromosome import Chromosome
import os
import csv
import statistics
from Code.GeneSimulation_py.Server.Bots.genetic_logger import Logger


def initalize_population(pop_size, num_genes, lower_bound, upper_bound):
    population = []
    for _ in range(pop_size): # how many we want to create
        chromosome = [random.uniform(lower_bound, upper_bound) for _ in range(num_genes-1)]
        chromosome.append(random.randint(0, 1))
        population.append(Chromosome(chromosome))
    return population

def tournament_selection(population, k=5, num_parents=11):
    selected = []
    for _ in range(num_parents):
        tournament = random.sample(population, k)
        winner = max(tournament, key=lambda c: c.fitness)
        selected.append(winner)
    return selected

def sort_by_fitness(population):
    return sorted(population, key=lambda chromosome: chromosome.fitness, reverse=True) # highest fitness first

def apply_eliteness(sorted_chromosomes, num_to_keep):
    return sorted_chromosomes[:num_to_keep]


def mutate(chromosome, mutation_rate=0.05):
    new_chrom = []
    for gene in chromosome[:-1]:  # float genes
        if random.random() < mutation_rate:
            new_chrom.append(random.uniform(0, 1))  # resample in same range
        else:
            new_chrom.append(gene)

    # Last gene is binary (0 or 1), flip it with mutation_rate
    if random.random() < mutation_rate:
        new_chrom.append(1 - chromosome[-1])
    else:
        new_chrom.append(chromosome[-1])

    return new_chrom

def reproduce(sorted_population, elite_size, population_size):
    new_population = apply_eliteness(sorted_population, elite_size)
    while len(new_population) < population_size:
        parent1 = random.choice(sorted_population[:elite_size]).chromosome
        parent2 = random.choice(sorted_population[:elite_size]).chromosome

        offspring1, offspring2 = one_point_crossover(parent1, parent2)

        offspring1 = mutate(offspring1)
        offspring2 = mutate(offspring2)

        new_population.append(Chromosome(offspring1))
        new_population.append(Chromosome(offspring2))
    return new_population

def one_point_crossover(parent1, parent2):
    crossover_point = random.randint(0, len(parent1) - 1)
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

    return offspring1, offspring2

def save_to_file(genes_to_save, gen_number):
    directory = r"C:\Users\Sean\Documents\GitHub\IJCAI2024_SM\Code\GeneSimulation_py\Server\Bots\chromosomeRepo"
    if not os.path.exists(directory):
        # print(f"Directory {directory} does not exist. Creating it now...")
        os.makedirs(directory)
    file_path = os.path.join(directory, f"generation_{gen_number}.csv")
    try:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            #header = ["Gene Index"] + [f"C[{i}]" for i in range(num_genes)] possible espansion?
            writer.writerow(["Gene Index", "C[0]", "C[1]" ,"C[2]","C[3]","C[4]","C[5]","C[6]","C[7]","C[8]","C[9]","C[10]","C[11]","C[12]","C[13]","C[14]","C[15]","C[16]","C[17]","C[18]","C[19]","C[20]"])  # Header row
            for i, gene in enumerate(genes_to_save):
                writer.writerow([i + 1] + gene.chromosome)  # Keeps proper CSV formatting
        print(f"Successfully saved {file_path}")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

def reset_fitness(population):
    for chromosome in population:
        chromosome.reset_fitness()


import csv
import statistics
import os
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt


class Logger:
    def __init__(self):
        self.fitness_history = []
        self.diversity_history = []
        self.pca_snapshots = []
        self.cooperation_scores = []

    def log_generation(self, population, cooperation_score):
        fitnesses = [c.fitness for c in population]
        avg_fitness = statistics.mean(fitnesses)
        max_fitness = max(fitnesses)
        diversity = compute_diversity(population)

        self.fitness_history.append((avg_fitness, max_fitness, cooperation_score))
        self.diversity_history.append(diversity)

        gene_matrix = np.array([chrom.chromosome for chrom in population])
        pca = PCA(n_components=2)
        projected = pca.fit_transform(gene_matrix)
        self.pca_snapshots.append(projected)


    def save_logs(self, folder="logs"):
        print("Saving it all to a CSV...")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "fitness.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Generation", "Average", "Max", "Coop"])
            for i, (avg, max_) in enumerate(self.fitness_history):
                writer.writerow([i, avg, max_])
        with open(os.path.join(folder, "diversity.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Generation", "Diversity"])
            for i, diversity in enumerate(self.diversity_history):
                writer.writerow([i, diversity])

    def plot_pca_snapshots(self, folder="logs"):
        os.makedirs(folder, exist_ok=True)
        for i, projection in enumerate(self.pca_snapshots):
            plt.figure(figsize=(6, 6))
            plt.scatter(projection[:, 0], projection[:, 1], alpha=0.6)
            plt.title(f"Population PCA (Gen {i})")
            plt.xlabel("PC1")
            plt.ylabel("PC2")
            plt.grid(True)
            plt.savefig(os.path.join(folder, f"pca_gen_{i}.png"))
            plt.close()

def compute_diversity(population):
    gene_matrix = np.array([chrom.chromosome for chrom in population])
    diversity = np.std(gene_matrix, axis=0).mean()
    return diversity


if __name__ == '__main__':
    pop_size = 100 # lets just generate 100 chromosomes
    num_genes = 20 # the total parameters I want to explore. look at gameTheory.py.
    lower_bound = 0
    upper_bound = 1
    num_to_keep = 11 # just becuase, why not.

    logger = Logger()

    start_time = time.time()
    print("starting... ")
    # initalize the sim, and sets up a defualt population
    sim = Social_Choice_Sim(11, 3, 0, 3)  # starts the social choice sim (always use these parameters for now)
    population = initalize_population(pop_size, num_genes, lower_bound, upper_bound)
    fitness_history = []
    diversity_history = []

    ## POPULATION INITIALIZING / START ##
    for generation in range(200): # run 200 generations
        print("Starting on generation ", generation)
        cooperation_score = 0 # starts at 0 for every generation
        chromosomes_used = {} # where the key is the chromosome, and the attribute is all of the fintesses.
        for _ in range(10): # tries 10 trials for chromosome fitness
            selected_population = [random.randint(0, 99) for _ in range(11)]  # 11 random numbers from 1-100
            current_chromosomes = [population[i] for i in selected_population] # sets up the population
            sim.set_chromosome(current_chromosomes) # should set all the chromosomes
            for _ in range(10): # play 10 rounds per set of chromosomes.
                print("starting an individual round ")
                sim.start_round()
                bot_votes = sim.get_votes()
                winning_vote, results = sim.return_win(bot_votes) # is all votes, works here
                if winning_vote != -1: # keep track of how often they cooperate.
                    cooperation_score += 1
                for i, chromosome in enumerate(current_chromosomes):
                    if chromosome not in chromosomes_used:
                        chromosomes_used[chromosome] = []
                    chromosomes_used[chromosome].append(results[i])


        for chromosome in chromosomes_used: # gets the average utility increase for each chromosome.
            chromosome.add_fitness(statistics.mean(chromosomes_used[chromosome]))

        print("chromosomes trained. Selecting the most fit...")
        population = sort_by_fitness(population) # now it shoudl work as anticipated.
        logger.log_generation(population, cooperation_score)

        top_11 = tournament_selection(population, k=5, num_parents=num_to_keep)
        #top_11 = population[:11] # grabs the 11 top ones
        save_to_file(population, generation) # save the actual chromosomes around so I can look for them later. s
        population = reproduce(top_11, num_to_keep, pop_size) # only keep the top 11. no wonder we were struggling.
        for chromosome in population: # reset the fitness so it doesn't accumulate.
            chromosome.reset_fitness()
    logger.save_logs()
    logger.plot_pca_snapshots()
    end_time = time.time()
    print("this was the total training time ", end_time - start_time)








