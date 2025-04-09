//
// Created by Sean on 4/8/2025.
//

#include "GameTheoryBot.h"
#include <algorithm>  // for std::max
#include <map>        // for frequency counting
#include <iostream>   // optional, for debugging

// Constructor
GameTheoryBot::GameTheoryBot(int selfID, std::string type, std::vector<std::vector<float>>& chromosomes)
    : selfId(selfID), type("GT"), numPlayers(11), numCauses(3) {
    // Initialize other stuff if needed
}

// Set the chromosome
void GameTheoryBot::setChromosome(const std::vector<float>& chromosomeVec) {
    chromosome = chromosomeVec;
}

// Get vote based on current options and internal logic
int GameTheoryBot::getVote(const std::vector<std::vector<int>>& currentOptionsMatrix,
                const std::vector<std::vector<int>>& bigBoyList) {
    // stub logic here
    return 0;
}

// Generate normalized probabilities for each cause
std::vector<float> GameTheoryBot::generateProbabilities(const std::vector<std::vector<int>>& optionsMatrix) {
    return std::vector<float>(); // placeholder
}

// Optimized version of getVote using precomputed probabilities
int GameTheoryBot::getVoteOptimizedSingle(const std::vector<float>& normalizedCauseProbability,
                                          const std::vector<std::vector<int>>& optionsMatrix) {
    return 0; // placeholder
}

// Decide vote based on current reward landscape and risk adversity
int GameTheoryBot::useBotType(const std::vector<std::pair<float, float>>& currentRewards) {
    return 0; // placeholder
}

// Evaluate the expected reward for each option
std::vector<std::pair<float, float>> GameTheoryBot::thinkAboutReward(const std::vector<float>& normalizedProb) {
    return std::vector<std::pair<float, float>>(); // placeholder
}

// Get cause-level probability from all possible vote combinations
std::vector<float> GameTheoryBot::getCauseProbability(const std::vector<std::vector<float>>& allPossibilities) {
    return std::vector<float>(); // placeholder
}

// Generate all possible vote combinations (brute-force)
std::vector<std::vector<float>> GameTheoryBot::generateAllPossibilities(const std::vector<std::vector<int>>& optionsMatrix) {
    return std::vector<std::vector<float>>(); // placeholder
}

// Create preference ranking matrix and column preference vector
 std::vector<std::vector<int>> GameTheoryBot::createChoicesMatrix(const std::vector<std::vector<int>>& currentOptionsMatrix, std::vector<int>& choiceListOut) {
    return {}; // placeholder
}

// Generate probability matrix from choices + weights
std::vector<std::vector<float>> GameTheoryBot::createProbabilityMatrix(const std::vector<std::vector<int>>& choicesMatrix, const std::vector<int>& choiceList) {
    return std::vector<std::vector<float>>();
}

// Recursive combo generator — might take some finessing
void GameTheoryBot::generateCombinations(int currentId, std::vector<float>& currentArray,
                                         std::vector<std::vector<float>>& results) {
    return;
    // stub
}
