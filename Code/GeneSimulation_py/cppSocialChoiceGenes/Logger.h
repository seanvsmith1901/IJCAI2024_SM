//
// Created by Sean on 4/8/2025.
//

#ifndef LOGGER_H
#define LOGGER_H

#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <numeric>
#include <algorithm>
#include <cmath>
#include "Chromosome.h" // Make sure to include the definition of the Chromosome class.


class Logger {
public:
    Logger();

    // Method to log data for each generation
    void logGeneration(const std::vector<Chromosome>& population, double cooperationScore);

    // Method to save all logged data to CSV files
    void saveLogs(const std::string& folder = "logs");

private:
    // Data members for storing fitness history, diversity history, and cooperation scores
    std::vector<std::tuple<double, double, double>> fitnessHistory;
    std::vector<double> diversityHistory;
    std::vector<double> cooperationScores;

    // Helper function to compute the diversity of the population
    double computeDiversity(const std::vector<Chromosome>& population);
};



#endif //LOGGER_H
