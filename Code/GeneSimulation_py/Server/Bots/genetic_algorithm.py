import random
import time

from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
from collections import Counter
from Code.GeneSimulation_py.Server.Bots.chromosome import Chromosome
import os
import csv

def initalize_population(pop_size, num_genes, lower_bound, upper_bound):
    population = []

    for _ in range(pop_size): # how many we want to create
        chromosome = [random.uniform(lower_bound, upper_bound) for _ in range(num_genes-1)]
        chromosome.append(random.randint(0, 1))
        population.append(Chromosome(chromosome))

    return population

def sort_by_fitness(population):
    return sorted(population, key=lambda chromosome: chromosome.fitness, reverse=True) # highest fitness first

def apply_eliteness(sorted_chromosomes, num_to_keep):
    return sorted_chromosomes[:num_to_keep]

def mutate(chromosome, mutation_rate = 0.01):
    return [
        gene if random.random() > mutation_rate else random.choice([0,1]) for gene in chromosome
    ]

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



if __name__ == '__main__':
    pop_size = 100 # lets just generate 100 chromosomes
    num_genes = 20 # the total parameters I want to explore. look at gameTheory.py.
    lower_bound = 0
    upper_bound = 1
    num_to_keep = 11 # just becuase, why not.

    start_time = time.time()
    # initalize the sim, and sets up a defualt population
    sim = Social_Choice_Sim(11, 3, 0, 3)  # starts the social choice sim (always use these parameters for now)
    population = initalize_population(pop_size, num_genes, lower_bound, upper_bound)


    ## POPULATION INITIALIZING / START ##
    for generation in range(100): # run 200 generations
        # chromosomes_used = {} # where the key is the chromosome, and the attribute is all of the fintesses.
        for i in range(10): # plays 100 games per generation (can prolly make this less)
            selected_population = [random.randint(0, 99) for _ in range(11)]  # 11 random numbers from 1-100
            current_chromosomes = [population[i] for i in selected_population] # sets up the population
            sim.set_chromosome(current_chromosomes) # should set all the chromosomes
            for i in range(10): # play 10 rounds
                sim.start_round()
                bot_votes = sim.get_votes()
                winning_vote, results = sim.return_win(bot_votes) # is all votes, works here
                for i, chromosome in enumerate(current_chromosomes):
                    chromosome.add_fitness(results[i]) # PLEASE be in the right order. if not thats going to be a problem.
            print("games done. training chromosomes again...")

        print("chromosomes trained. Selecting the most fit...")
        population = sort_by_fitness(population)
        top_11 = population[:11] # grabs the 11 top ones

        directory = r"C:\Users\Sean\Documents\GitHub\IJCAI2024_SM\Code\GeneSimulation_py\Server\Bots\chromosomeRepo"

        if not os.path.exists(directory):
            #print(f"Directory {directory} does not exist. Creating it now...")
            os.makedirs(directory)

        file_path = os.path.join(directory, f"generation_{generation}.csv")

        try:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Gene Index", "Chromosome"])  # Header row

                for i, gene in enumerate(top_11):
                    writer.writerow([i + 1] + gene.chromosome)  # Keeps proper CSV formatting

            print(f"Successfully saved {file_path}")

        except Exception as e:
            print(f"Error writing file {file_path}: {e}")


        population = reproduce(population, num_to_keep, pop_size)
    end_time = time.time()
    print("this was the total training time ", end_time - start_time)

    # need to decide which chomosomes to keep






