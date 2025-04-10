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


if __name__ == '__main__':
    pop_size = 100 # lets just generate 100 chromosomes
    num_genes = 20 # the total parameters I want to explore. look at gameTheory.py.
    lower_bound = 0
    upper_bound = 1
    num_to_keep = 11 # just becuase, why not.

    logger = Logger()

    start_time = time.time()
    # initalize the sim, and sets up a defualt population
    sim = Social_Choice_Sim(11, 3, 0, 3)  # starts the social choice sim (always use these parameters for now)
    population = initalize_population(pop_size, num_genes, lower_bound, upper_bound)
    fitness_history = []
    diversity_history = []

    ## POPULATION INITIALIZING / START ##
    for generation in range(200): # run 200 generations
        cooperation_score = 0 # starts at 0 for every generation
        chromosomes_used = {} # where the key is the chromosome, and the attribute is all of the fintesses.
        for i in range(10): # tries 10 trials for chromosome fitness
            selected_population = [random.randint(0, 99) for _ in range(11)]  # 11 random numbers from 1-100
            current_chromosomes = [population[i] for i in selected_population] # sets up the population
            sim.set_chromosome(current_chromosomes) # should set all the chromosomes
            for i in range(10): # play 10 rounds per set of chromosomes.
                sim.start_round()
                bot_votes = sim.get_votes()
                winning_vote, results = sim.return_win(bot_votes) # is all votes, works here
                if winning_vote != -1: # keep track of how often they cooperate.
                    cooperation_score += 1
                for i, chromosome in enumerate(current_chromosomes):
                    if chromosome not in chromosomes_used:
                        chromosomes_used[chromosome] = []
                    chromosomes_used[chromosome].append(results[i])
            print("games done. training chromosomes again...")

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








