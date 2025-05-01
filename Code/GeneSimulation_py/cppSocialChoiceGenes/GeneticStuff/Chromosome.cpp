//
// Created by Sean on 4/8/2025.
//

#include "Chromosome.h"
#include <vector>


// Constructor
Chromosome::Chromosome(const std::vector<double>& chromosome)
    : chromosome(chromosome), fitness(0) {}

std::vector<double> Chromosome::getChromosome() const {
    return chromosome;
}

// so thats how we do that. this->Fitness (our fitness class object) gets set to fitness
void Chromosome::setFitness(double fitness) {
    this->fitness = fitness;
}

// Add to the fitness value
void Chromosome::addFitness(double newFitness) {
    this->fitness += newFitness;
}

// Reset the fitness value
void Chromosome::resetFitness() {
    this->fitness = 0;
}

int Chromosome::getFitness() const {
    return this->fitness;
}

// overloaidng the [] for direct access
double Chromosome::operator[](size_t index) const {
    return chromosome[index];
}

// Overload the == operator to compare chromosomes
bool Chromosome::operator==(const Chromosome& other) const {
    return this->chromosome == other.chromosome;
}

// custom hash function so we can use it to store the chromosome as a key in a dict.
size_t Chromosome::ChromosomeHash::operator()(const Chromosome& c) const {
    // Hash the chromosome as a vector of doubles
    size_t seed = 0;
    for (const auto& value : c.chromosome) {
        seed ^= std::hash<double>{}(value) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    }
    return seed;
}