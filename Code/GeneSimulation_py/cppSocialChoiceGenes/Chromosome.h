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
    Chromosome(const std::vector<float>& chromosome);

    // Setters and Getters
    void setFitness(float fitness);
    void addFitness(float newFitness);
    int getFitness() const;

    std::vector<float> getChromosome() const;
    void resetFitness();

    // Operator Overloading
    float operator[](size_t index) const;  // Access chromosome element
    bool operator==(const Chromosome& other) const;  // Compare chromosomes

    // Hashing for the Chromosome (using std::hash)
    struct ChromosomeHash {
        size_t operator()(const Chromosome& c) const;
    };

private:
    std::vector<float> chromosome;  // Stores the chromosome
    float fitness;  // Stores the fitness value
};



#endif //CHROMOSOME_H
