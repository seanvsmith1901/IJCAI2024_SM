//
// Created by Sean on 4/8/2025.
//

#include "Logger.h"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <filesystem>
#include <stdexcept>


Logger::Logger() {
    // Constructor initializes empty data histories
}

void Logger::logGeneration(const std::vector<Chromosome>& population, double cooperationScore) {
    // Get fitnesses from population
    std::vector<double> fitnesses;
    for (const auto& c : population) {
        fitnesses.push_back(c.getFitness());
    }

    // Calculate average and max fitness
    double avgFitness = std::accumulate(fitnesses.begin(), fitnesses.end(), 0.0) / fitnesses.size();
    double maxFitness = *std::ranges::max_element(fitnesses);

    // Compute population diversity
    double diversity = computeDiversity(population);

    // Append the results to history
    fitnessHistory.push_back(std::make_tuple(avgFitness, maxFitness, cooperationScore));
    diversityHistory.push_back(diversity);
    cooperationScores.push_back(cooperationScore);
}

void Logger::saveLogs(const std::string& folder) {
    std::cout << "Saving it all to a CSV..." << std::endl;

    // Create the directory if it doesn't exist
    std::filesystem::create_directory(folder);

    // Save fitness data
    std::ofstream fitnessFile(folder + "/fitness.csv");
    fitnessFile << "Generation,Average,Max,Coop" << std::endl;
    for (size_t i = 0; i < fitnessHistory.size(); ++i) {
        fitnessFile << i << ","
                    << std::get<0>(fitnessHistory[i]) << ","
                    << std::get<1>(fitnessHistory[i]) << ","
                    << std::get<2>(fitnessHistory[i]) << std::endl;
    }

    // Save diversity data
    std::ofstream diversityFile(folder + "/diversity.csv");
    diversityFile << "Generation,Diversity" << std::endl;
    for (size_t i = 0; i < diversityHistory.size(); ++i) {
        diversityFile << i << ","
                      << diversityHistory[i] << std::endl;
    }
}

double Logger::computeDiversity(const std::vector<Chromosome>& population) {
    // Assuming Chromosome has a method getChromosome() that returns a vector of genes
    std::vector<std::vector<float>> geneMatrix;
    for (const auto& chrom : population) {
        geneMatrix.push_back(chrom.getChromosome());
    }

    // Compute the standard deviation for each gene across the population
    size_t numGenes = geneMatrix[0].size();
    std::vector<double> geneStdDevs(numGenes, 0.0);

    for (size_t i = 0; i < numGenes; ++i) {
        std::vector<float> geneColumn;
        for (const auto& chrom : geneMatrix) {
            geneColumn.push_back(chrom[i]);
        }

        double mean = std::accumulate(geneColumn.begin(), geneColumn.end(), 0.0) / geneColumn.size();
        double variance = 0.0;
        for (const auto& value : geneColumn) {
            variance += std::pow(value - mean, 2);
        }
        geneStdDevs[i] = std::sqrt(variance / geneColumn.size());
    }

    // Return the mean of the standard deviations across all genes
    return std::accumulate(geneStdDevs.begin(), geneStdDevs.end(), 0.0) / geneStdDevs.size();
}