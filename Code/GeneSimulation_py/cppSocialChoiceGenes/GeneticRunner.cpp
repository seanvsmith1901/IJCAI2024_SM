#include <iostream>
#include "Logger.h"
#include <chrono>
#include "SocialChoiceSim.h"
#include "Chromosome.h"
#include <vector>
#include <string>
#include "GeneticAlgorithm.h"


// this can be thought of as "SocialChoiceTest" but I'm not gonn arename it just yet.

int main() {
    int pop_size = 100;
    int num_genes = 20;
    int lower_bound = 0;
    int upper_bound = 1;
    int numtoKeep = 11;

    Logger logger{};

    auto start = std::chrono::system_clock::now();

    SocialChoiceSim sim(11, 3, 11); // never different for this edge case
    GeneticAlgorithm geneticAlgorithm(pop_size, num_genes, lower_bound, upper_bound);
    geneticAlgorithm.initializePopulation();
    std::vector<Chromosome> population = geneticAlgorithm.getPopulation();
    std::vector<float> fitness_history;
    std::vector<float> diversity_history;
    auto startTime = std::chrono::system_clock::now();
    std::srand(static_cast<unsigned int>(time(0))); // generate the random seed here instead.

    for (int generation = 0; generation < 200; generation++) { // for generation in generations
        int cooperationScore = 0;
        std::map<Chromosome, std::vector<float>> chromosomesUsed; // a map of chromosomes to a list of their fitnersses
        for (int i = 0; i < 10; i++) {
            std::vector<Chromosome> currentPopulation;

            std::vector<int> selectedPopulation;

            // this is a pain - we need to create reandom numbers as add them to the population.
            for (int i = 0; i < numtoKeep; i++) {
                selectedPopulation.push_back(std::rand() % 100);
            }
            for (int idx: selectedPopulation) {
                currentPopulation.push_back(population[idx]);
            }
            sim.setChromosome(currentPopulation); // take in the chromosomes and set them as appropriate for the bots.

            for (int i = 0; i < 10; ++i) { // trial size
                sim.startRound();
                auto botVotes = sim.getVotes();
                auto pair = sim.returnWin(botVotes);
                int winningVote = pair.first;
                std::vector<int> results = pair.second;
                if (winningVote != -1) {
                    cooperationScore++;
                }
                for (size_t i = 0; i < currentPopulation.size(); i++) {
                    // this might be broken, as per chat, but Imma keep it this way.
                    Chromosome chromosome = currentPopulation[i];

                    if (chromosomesUsed.find(chromosome) == chromosomesUsed.end()) {
                        chromosomesUsed[chromosome] = std::vector<float>();
                    }
                    chromosomesUsed[chromosome].push_back(results[i]);
                }
            }
        }
        for (auto pair : chromosomesUsed) {
            Chromosome chromosome = pair.first;
            std::vector<float> fitnesses = pair.second;

            float sum = std::accumulate(fitnesses.begin(), fitnesses.end(), 0.0f);
            float mean = sum / fitnesses.size();

            chromosome.addFitness(mean);
            // chromsosomes done. training chromosomes again...

        }
        geneticAlgorithm.sortByFitness();
        auto population = geneticAlgorithm.getPopulation();
        logger.logGeneration(population, generation);

        auto top11 = geneticAlgorithm.tournamentSelection();
        geneticAlgorithm.saveToFile(top11, generation); // with this work? No clue!
        for (auto chromosome : population) { // clear the fitnesses before throwing them to the ether.
            chromosome.resetFitness();
        }

        geneticAlgorithm.reproduce(11, pop_size);
        population = geneticAlgorithm.getPopulation();
    }
    logger.saveLogs();
    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end - start;
    std::cout << "Elapsed Time: " << elapsed_seconds.count() << "s" << std::endl;
    return 0; // so it ends and so I don't forget.
}


