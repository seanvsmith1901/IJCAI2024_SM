#include <iostream>
#include "Logger.h"
#include <chrono>
#include "SocialChoiceSim.h"
#include "Chromosome.h"
#include <vector>

#include "GeneticAlgorithm.h"

int main() {
    int pop_size = 100;
    int num_genes = 20;
    int lower_bound = 0;
    int upper_bound = 1;
    int numtoKeep = 11;

    Logger *logger = new Logger();
    auto start = std::chrono::system_clock::now();
    SocialChoiceSim *sim = new SocialChoiceSim(11, 3, 11); // never different for this edge case
    std::vector<Chromosome> population = GeneticAlgorithm::initializePopulation(pop_size, num_genes, lower_bound, upper_bound)













    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end - start;
    std::cout << "Elapsed Time: " << elapsed_seconds.count() << "s" << std::endl;





    return 0; // so it ends and so I don't forget.
}
