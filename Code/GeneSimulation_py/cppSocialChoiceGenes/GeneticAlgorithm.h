//
// Created by Sean on 4/8/2025.
//

#ifndef GENETICALGORITHM_H
#define GENETICALGORITHM_H

#include "Chromosome.h"
#include <vector>
#include <random>
#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <ctime>
#include <cstdlib>


class GeneticAlgorithm {
public:
    // Constructor to initialize the population
    GeneticAlgorithm(int pop_size, int num_genes, float lower_bound, float upper_bound);

    // Population manipulation methods
    void initializePopulation();
    std::vector<Chromosome> tournamentSelection(int k = 5, int num_parents = 11);
    void sortByFitness();
    std::vector<Chromosome> applyEliteness(int num_to_keep);
    void mutate(Chromosome& chromosome, float mutation_rate = 0.05f);
    void reproduce(int elite_size, int population_size);
    void saveToFile(const std::vector<Chromosome>& genes_to_save, int gen_number);

    // Fitness reset method
    void resetFitness();

    // Getters and setters
    const std::vector<Chromosome>& getPopulation() const { return population; }
    void setPopulation(const std::vector<Chromosome>& pop) { population = pop; }


private:
    // Helper methods
    std::pair<Chromosome, Chromosome> onePointCrossover(const std::vector<float>& parent1, const std::vector<float>& parent2);

    std::vector<Chromosome> population;
    int pop_size;
    int num_genes;
    float lower_bound;
    float upper_bound;
    std::default_random_engine generator;
};



#endif //GENETICALGORITHM_H
