// //
// // Created by Sean on 4/8/2025.
// //
//
// #include "GeneticAlgorithm.h"
// #include <fstream>
// #include <algorithm>
// #include <random>
//
// GeneticAlgorithm::GeneticAlgorithm(int pop_size, int num_genes, float lower_bound, float upper_bound)
//     : pop_size(pop_size), num_genes(num_genes), lower_bound(lower_bound), upper_bound(upper_bound) {
//     initializePopulation();
// }
//
// void GeneticAlgorithm::initializePopulation() {
//     std::uniform_real_distribution<float> distribution(lower_bound, upper_bound);
//     std::uniform_int_distribution<int> binary_distribution(0, 1);
//
//     population.clear();
//     for (int i = 0; i < pop_size; ++i) {
//         std::vector<float> chromosome;
//         for (int j = 0; j < num_genes - 1; ++j) {
//             chromosome.push_back(distribution(generator));
//         }
//         chromosome.push_back(binary_distribution(generator));  // Last gene is binary
//         population.push_back(Chromosome(chromosome));
//     }
// }
//
// std::vector<Chromosome> GeneticAlgorithm::getPopulation() {
//     return population;
// }
//
// std::vector<Chromosome> GeneticAlgorithm::tournamentSelection(int k, int num_parents) {
//     std::vector<Chromosome> selected;
//     for (int i = 0; i < num_parents; ++i) {
//         std::vector<Chromosome> tournament;
//         for (int j = 0; j < k; ++j) {
//             tournament.push_back(population[rand() % population.size()]);
//         }
//         auto winner = *std::max_element(tournament.begin(), tournament.end(), [](const Chromosome& a, const Chromosome& b) {
//             return a.getFitness() < b.getFitness();
//         });
//         selected.push_back(winner);
//     }
//     return selected;
// }
//
// void GeneticAlgorithm::sortByFitness() {
//     std::sort(population.begin(), population.end(), [](const Chromosome& a, const Chromosome& b) {
//         return a.getFitness() > b.getFitness();  // Highest fitness first
//     });
// }
//
// std::vector<Chromosome> GeneticAlgorithm::applyEliteness(int num_to_keep) {
//     std::vector<Chromosome> elite;
//     for (int i = 0; i < num_to_keep; ++i) {
//         elite.push_back(population[i]);
//     }
//     return elite;
// }
//
// void GeneticAlgorithm::mutate(Chromosome& chromosome, float mutation_rate) {
//     for (size_t i = 0; i < chromosome.getChromosome().size() - 1; ++i) {
//         if (static_cast<float>(rand()) / RAND_MAX < mutation_rate) {
//             chromosome.getChromosome()[i] = lower_bound + (upper_bound - lower_bound) * static_cast<float>(rand()) / RAND_MAX;
//         }
//     }
//
//     if (static_cast<float>(rand()) / RAND_MAX < mutation_rate) {
//         chromosome.getChromosome().back() = 1 - chromosome.getChromosome().back();
//     }
// }
//
// void GeneticAlgorithm::reproduce(int elite_size, int population_size) {
//     std::vector<Chromosome> new_population = applyEliteness(elite_size);
//     while (new_population.size() < population_size) {
//         auto parent1 = population[rand() % elite_size].getChromosome();
//         auto parent2 = population[rand() % elite_size].getChromosome();
//         auto [offspring1, offspring2] = onePointCrossover(parent1, parent2);
//
//         Chromosome offSpring1Chrom(offspring1);
//         Chromosome offSpring2Chrom(offspring2);
//         mutate(offSpring1Chrom);
//         mutate(offSpring2Chrom);
//
//         new_population.push_back(offSpring1Chrom);
//         new_population.push_back(offSpring2Chrom);
//     }
//     population = new_population;
// }
//
// std::pair<Chromosome, Chromosome> GeneticAlgorithm::onePointCrossover(const std::vector<float>& parent1, const std::vector<float>& parent2) {    int crossover_point = rand() % parent1.size();
//     std::vector<float> offspring1(parent1.begin(), parent1.begin() + crossover_point);
//     offspring1.insert(offspring1.end(), parent2.begin() + crossover_point, parent2.end());
//
//     std::vector<float> offspring2(parent2.begin(), parent2.begin() + crossover_point);
//     offspring2.insert(offspring2.end(), parent1.begin() + crossover_point, parent1.end());
//     Chromosome chromosome1 = Chromosome(offspring1);
//     Chromosome chromosome2 = Chromosome(offspring2);
//     return {chromosome1, chromosome2};
// }
//
// void GeneticAlgorithm::saveToFile(const std::vector<Chromosome>& genes_to_save, int gen_number) {
//     std::string file_path = "generation_" + std::to_string(gen_number) + ".csv";
//     std::ofstream file(file_path);
//
//     if (file.is_open()) {
//         file << "Gene Index,C[0],C[1],C[2],C[3],C[4],C[5],C[6],C[7],C[8],C[9],C[10],C[11],C[12],C[13],C[14],C[15],C[16],C[17],C[18],C[19],C[20]\n";
//         for (size_t i = 0; i < genes_to_save.size(); ++i) {
//             file << i + 1;
//             for (const auto& gene : genes_to_save[i].getChromosome()) {
//                 file << "," << gene;
//             }
//             file << "\n";
//         }
//         std::cout << "Successfully saved " << file_path << "\n";
//     } else {
//         std::cerr << "Error writing file " << file_path << "\n";
//     }
// }
//
// void GeneticAlgorithm::resetFitness() {
//     for (auto& chrom : population) {
//         chrom.resetFitness();
//     }
// }
//
