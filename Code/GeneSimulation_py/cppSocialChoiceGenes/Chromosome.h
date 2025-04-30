//
// Created by Sean on 4/8/2025.
//

#ifndef CHROMOSOME_H
#define CHROMOSOME_H

#include <vector>
#include <functional>  // For std::hash


class Chromosome {
public:
    // Constructor
    Chromosome(const std::vector<double>& chromosome);

    // Setters and Getters
    void setFitness(double fitness);
    void addFitness(double newFitness);
    int getFitness() const;

    std::vector<double> getChromosome() const;
    void resetFitness();

    // Operator Overloading
    double operator[](size_t index) const;  // Access chromosome element
    bool operator==(const Chromosome& other) const;  // Compare chromosomes

    // Hashing for the Chromosome (using std::hash)
    struct ChromosomeHash {
        size_t operator()(const Chromosome& c) const;
    };

private:
    std::vector<double> chromosome;  // Stores the chromosome
    double fitness;  // Stores the fitness value
};



#endif //CHROMOSOME_H
