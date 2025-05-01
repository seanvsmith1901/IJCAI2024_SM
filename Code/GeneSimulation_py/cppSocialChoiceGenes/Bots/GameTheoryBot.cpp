//
// Created by Sean on 4/8/2025.
//

#include "GameTheoryBot.h"
#include <algorithm>  // for std::max
#include <map>        // for frequency counting
#include <iostream>   // optional, for debugging
#include <numeric>
#include <utility>

#include "Chromosome.h"


// Constructor
GameTheoryBot::GameTheoryBot(int selfID, std::string type, std::vector<std::vector<int>> currentOptionsMatrix)
    : selfId(selfID), type("GT"), numPlayers(11), numCauses(3), currentOptionsMatrix(std::move(currentOptionsMatrix)) {
    this->chromosome = std::vector<double>(); // just give it a blank chromosome that we can mess with later.
    // Initialize other stuff if needed
}


void GameTheoryBot::setChromosome(const Chromosome& currChromosome) {
    chromosome = currChromosome.getChromosome();
}

int GameTheoryBot::getVote(const std::vector<std::vector<int>>& currentOptionsMatrix,
            std::vector<std::pair<std::vector<int>, double>>& bigBoyList) {
    std::vector<double> causeProbability = getCauseProbability(bigBoyList);
    std::vector<double> normalizedCauseProbability = std::vector<double>(); // thank goodness C++ finally allows me to just create copies normally.
    // this normalizes the fetcher.
    double totalSum = std::accumulate(causeProbability.begin(), causeProbability.end(), 0.0);
    for (auto const& element : causeProbability) {
        normalizedCauseProbability.push_back(element / totalSum);
    }

    // this just allows us to use class objects instead of passing them around. Saves overhead on the recursive functions.
    this->currentOptionsMatrix = currentOptionsMatrix;
    this->numPlayers = currentOptionsMatrix.size();
    this->numCauses = currentOptionsMatrix[0].size();

    std::vector<std::pair<double, double>> currentRewards = thinkAboutReward(normalizedCauseProbability);
    auto const& currentChromosome = getChromosome();
    int currentVote = useBotType(currentRewards);

    return currentVote;

}

// std::vector<double> GameTheoryBot::generateProbabilities(const std::vector<std::vector<int>>& currentOptionsMatrix) {
//     const std::vector<double> weightsArray = getChromosome();
//     this->currentOptionsMatrix = currentOptionsMatrix;
//     auto choiceMatrixAndList = createChoicesMatrix(currentOptionsMatrix);
//     std::vector<std::vector<int>> choicesMatrix = choiceMatrixAndList.first;
//     std::vector<int> choiceList = choiceMatrixAndList.second;
//
//
//     std::vector<std::vector<double>> probabilityMatrix = createProbabilityMatrix(choicesMatrix, weightsArray, currentOptionsMatrix);
//
//     this->numPlayers = currentOptionsMatrix.size();
//     this->numCauses = currentOptionsMatrix[0].size();
//     // this->probabilityMatrix = probabilityMatrix;
//
//
//     std::vector<int> ones(this->numPlayers + 1, 1); // [1, 1, ..., 1]
//
//     std::vector<std::pair<std::vector<int>, double>> bigBoyList;
//     double startingProb = 1.0;
//     generateCombinations(0, ones, startingProb, probabilityMatrix, numPlayers, numCauses, bigBoyList);
//
//     std::vector<double> causeProbability = getCauseProbability(bigBoyList);
//     auto normalizedCauseProbability = std::vector<double>();
//
//     double totalSum = std::accumulate(causeProbability.begin(), causeProbability.end(), 0);
//     for (auto const& element : causeProbability) {
//         normalizedCauseProbability.push_back(element / totalSum);
//     }
//     return normalizedCauseProbability;
//
//
// }

int GameTheoryBot::useBotType(const std::vector<std::pair<double, double>>& currentRewards) {
    // right now risk aversion isn't coming into play, but I can fix that pretty easily pretty quick here. leave it like this for now.

    // Find index of max .second value
    int maxIndex = -1;
    double maxChance = -1.0;

    for (int i = 0; i < currentRewards.size(); ++i) {
        if (currentRewards[i].second > maxChance) {
            maxChance = currentRewards[i].second;
            maxIndex = i;
        }
    }
    return maxIndex - 1; // Adjust offset


    // Placeholder for other bot types, or return default
    return -1;
}

// technically this one returns a map of pairs of a value and an expected value. difficil.
std::vector<std::pair<double, double>> GameTheoryBot::thinkAboutReward(const std::vector<double> normalizedCauseProbability) {
    std::vector<std::pair<double, double>> currentRewards;
    double expectedReward = 0.0;
    for (int i = 0; i < normalizedCauseProbability.size(); i++) {
        if (i == 0) {
            expectedReward = 0.0;
        } else {
            expectedReward = normalizedCauseProbability[i] * currentOptionsMatrix[selfId][i-1];
        }

        currentRewards.emplace_back(normalizedCauseProbability[i], expectedReward);
    }
    return currentRewards;
}
std::vector<double> GameTheoryBot::getCauseProbability(
    const std::vector<std::pair<std::vector<int>, double>>& allPossibilities
) {
    int numCauses = 3;
    std::vector<double> causeProbability(numCauses + 1, 0.0); // index 0 = no majority

    if (allPossibilities.empty() || allPossibilities[0].first.empty()) {
        return causeProbability; // return all 0s if data is invalid
    }

    int totalVotes = static_cast<int>(allPossibilities[0].first.size());

    for (const auto& [votes, probability] : allPossibilities) {
        std::unordered_map<int, int> freqs;
        int maxItem = -1;
        int maxCount = 0;

        for (int vote : votes) {
            int count = ++freqs[vote];
            if (count > maxCount) {
                maxCount = count;
                maxItem = vote;
            }
        }

        if (maxCount > totalVotes / 2) {
            if (maxItem >= 0 && maxItem <= numCauses)
                causeProbability[maxItem] += probability;
        } else {
            causeProbability[0] += probability; // No majority
        }
    }

    return causeProbability;
}

std::vector<std::pair<std::vector<int>, double>> GameTheoryBot::generateAllPositibilities(std::vector<std::vector<int>> currentOptionsMatrix) {
    const std::vector<double> weightsArray = getChromosome();
    this->currentOptionsMatrix = currentOptionsMatrix;
    auto choiceMatrixAndList = createChoicesMatrix(currentOptionsMatrix);
    std::vector<std::vector<int>> choicesMatrix = choiceMatrixAndList.first;
    std::vector<int> choiceList = choiceMatrixAndList.second;


    std::vector<std::vector<double>> probabilityMatrix = createProbabilityMatrix(choicesMatrix, weightsArray, currentOptionsMatrix);

    numPlayers = currentOptionsMatrix.size();
    numCauses = currentOptionsMatrix[0].size();


    std::vector<int> ones(this->numPlayers + 1, 1); // [1, 1, ..., 1]

    std::vector<std::pair<std::vector<int>, double>> bigBoyList;
    double startingProb = 1.0;
    generateCombinations(0, ones, startingProb, probabilityMatrix, numPlayers, numCauses, bigBoyList);

   return bigBoyList;

}

std::pair<std::vector<std::vector<int>>, std::vector<int>> GameTheoryBot::createChoicesMatrix(std::vector<std::vector<int>> currentOptionsMatrix) {
    auto newProbabilitiesMatrix = currentOptionsMatrix;
    for (auto& row : newProbabilitiesMatrix) { // double check the behavior of this fetcher.
        row.insert(row.begin(), 0);
        auto sortedRow = row;
        std::sort(sortedRow.begin(), sortedRow.end());

        std::unordered_map<int, int> rowIndexMap;
        for (size_t idx = 0; idx < sortedRow.size(); idx++) {
            rowIndexMap[sortedRow[idx]] = static_cast<int>(idx) -1; // handle the off by 1 error.
        }

        for (int& val : row) {
            val = rowIndexMap[val];
        }
    }
    auto numRows = newProbabilitiesMatrix.size();
    auto numCols = newProbabilitiesMatrix[0].size();
    std::vector<int> columnSums(numCols, 0);

    for (size_t col = 0; col < numCols; col++) {
        for (size_t row = 0; row < numRows; row++) {
            columnSums[col] += newProbabilitiesMatrix[row][col];
        }
    }

    std::vector<int> sortedSums = columnSums;
    std::sort(sortedSums.begin(), sortedSums.end());

    std::unordered_map<int, int> indexMap;
    for (size_t idx = 0; idx < sortedSums.size(); idx++) {
        indexMap[sortedSums[idx]] = static_cast<int>(idx) - 1;
    }

    std::vector<int> columnPreferences;
    for (int val : columnSums) {
        columnPreferences.push_back(indexMap[val]);
    }

    return {newProbabilitiesMatrix, columnPreferences};

}

std::vector<std::vector<double>> GameTheoryBot::createProbabilityMatrix(std::vector<std::vector<int>> choicesMatrix, std::vector<double> weightsArray, std::vector<std::vector<int>> currentOptionsMatrix) {
    int numCols = choicesMatrix[0].size();
    int numRows = choicesMatrix.size();
    int randomNumber = 2 + 2;
    std::vector<int> totalSums;
    for (int j = 0; j < numCols; j++) {
        int newSum = 0;
        for (int i = 0; i < numRows; i++) {
            newSum += choicesMatrix[i][j];
        }
        totalSums.push_back(newSum);
    }
    // we need this to become a copy of it, but then replace it with a double. very fun.
    std::vector<std::vector<double>> probabilityMatrix(numRows, std::vector<double>(numCols));

    for (int i = 0; i < numRows; i++) {
        for (int j = 0; j < numCols; j++) {
            if (j == 0) {
                int maxUtility = *std::max_element(currentOptionsMatrix[i].begin(), currentOptionsMatrix[i].end());
                int newUtility = 0 - maxUtility;

                if (newUtility > 0) {
                    probabilityMatrix[i][j] = weightsArray[0];
                } else {
                    int choiceVal = choicesMatrix[i][j];
                    if (choiceVal == 2) {
                        probabilityMatrix[i][j] = weightsArray[1];
                    }
                    else if (choiceVal == 1)
                        probabilityMatrix[i][j] = weightsArray[2];
                    else if (choiceVal == 0)
                        probabilityMatrix[i][j] = weightsArray[3];
                    else if (choiceVal == -1)
                        probabilityMatrix[i][j] = weightsArray[4];
                }
            } else {
                int optionVal = currentOptionsMatrix[i][j-1];
                int choiceVal = choicesMatrix[i][j];

                if (totalSums[j] > 0 && optionVal > 0) {
                    if (choiceVal == 2)
                        probabilityMatrix[i][j] = weightsArray[5];
                    else if (choiceVal == 1)
                        probabilityMatrix[i][j] = weightsArray[6];
                    else if (choiceVal == 0)
                        probabilityMatrix[i][j] = weightsArray[7];
                    else if (choiceVal == -1)
                        probabilityMatrix[i][j] = weightsArray[8];
                } else if (totalSums[j] > 0 && optionVal <= 0) {
                    if (choiceVal == 2)
                        probabilityMatrix[i][j] = weightsArray[9];
                    else if (choiceVal == 1)
                        probabilityMatrix[i][j] = weightsArray[10];
                    else if (choiceVal == 0)
                        probabilityMatrix[i][j] = weightsArray[11];
                    else if (choiceVal == -1)
                        probabilityMatrix[i][j] = weightsArray[12];
                } else if (totalSums[j] <= 0 && optionVal > 0) {
                    if (choiceVal == 2)
                        probabilityMatrix[i][j] = weightsArray[13];
                    else if (choiceVal == 1)
                        probabilityMatrix[i][j] = weightsArray[14];
                    else if (choiceVal == 0)
                        probabilityMatrix[i][j] = weightsArray[15];
                    else if (choiceVal == -1)
                        probabilityMatrix[i][j] = weightsArray[16];
                } else if (totalSums[j] <= 0 && optionVal <= 0) {
                    probabilityMatrix[i][j] = weightsArray[17];
                }
            }
        }
    }
    return probabilityMatrix;

}
void GameTheoryBot::generateCombinations(
    int currentID,
    std::vector<int>& currentArray,
    double& probabilityProduct,
    std::vector<std::vector<double>>& probabilityMatrix,
    const int numPlayers,
    const int numCauses,
    std::vector<std::pair<std::vector<int>, double>>& results
) {
    if (currentID == numPlayers) {
        //if (probabilityProduct >= threshold) {
        results.emplace_back(currentArray, probabilityProduct);
        //}
        return;
    }
    for (int cause = 0; cause < numCauses; cause++) {
        double prob = probabilityMatrix[currentID][cause];
        if (prob > 0) {
            currentArray[currentID] = cause;
            probabilityProduct *= prob;

            generateCombinations(
                currentID + 1,
                currentArray,
                probabilityProduct,
                probabilityMatrix,
                numPlayers,
                numCauses,
                results
                );

            probabilityProduct /= prob;
        }
    }
}

std::vector<double> GameTheoryBot::getChromosome() {
    return this->chromosome;
}

std::string GameTheoryBot::getMyType() {
    return this->type;
}