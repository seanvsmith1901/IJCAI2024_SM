//
// Created by Sean on 4/8/2025.
//



#include <utility>

#include "Chromosome.h"
#include "socialChoiceSim.h"


SocialChoiceSim::SocialChoiceSim(int totalPlayers, int numCauses, int numHumans, int botType)
    : totalPlayers(totalPlayers), numCauses(numCauses), numHumans(numHumans), numBots(totalPlayers-numHumans), cpp(3), rad(5), gen(std::random_device()())
{
    this->totalPlayers = totalPlayers;
    this->numCauses = numCauses;
    this->numHumans = numHumans;
    this->numBots = totalPlayers-numHumans;
    this->cpp = 3;
    this->rad = 5;

    createBots();

    currentOptionsMatrix = {};
    allVotes.clear();
    currentVotes.clear();
    probabilitiesMatrix.clear();
    allCombinations.clear();
}

void SocialChoiceSim::createBots() {// adds bots to the bots vector
    bots.clear(); // first get rid of all the old bots.
    for (int i = 0; i < numBots; i++) {
        GreedyBot newBot(i);
        bots.push_back(newBot);
    }
}


std::vector<std::vector<int>> SocialChoiceSim::createOptionsMatrix() {
    currentOptionsMatrix.clear(); // make sure she's clean first
    currentOptionsMatrix.resize(totalPlayers, std::vector<int>(numCauses));  // get thje matrix to be the right size
    for (int i = 0; i < totalPlayers; ++i) {
        for (int j = 0; j < numCauses; ++j) {
            currentOptionsMatrix[i][j] = rand() % 21 - 10;  // Generate a random number between -10 and 10
        }
    }
    return currentOptionsMatrix;
}
const std::vector<std::vector<int> >& SocialChoiceSim::getCurrentOptionsMatrix() const {
    return currentOptionsMatrix;
}


void SocialChoiceSim::startRound() { // THats it. theres more in the non genetic version.
    this->currentOptionsMatrix = createOptionsMatrix();
}
const std::vector<std::vector<float>> SocialChoiceSim:: getProbabilites() const {
    return probabilitiesMatrix;

}
std::unordered_map<int, int> SocialChoiceSim::getVotes() {
    std::unordered_map<int, int> botVotes;
    // for (int i = 0; i < bots.size(); i++) {
    //     if (allCombinations.empty()) {
    //         allCombinations = generateProbabilities(currentOptionsMatrix);
    //     }
    //     botVotes[i] = bots[i].getVote(currentOptionsMatrix, allCombinations);
    // }
    for (int i = 0; i < bots.size(); ++i) {
        botVotes[i] = bots[i].getVote(currentOptionsMatrix);
    }
    return botVotes;

}


std::pair<int, std::vector<int>> SocialChoiceSim::returnWin(const std::unordered_map<int, int>& all_votes) {
    std::vector<int> results;
    std::unordered_map<int, int> total_votes = all_votes;
    std::unordered_map<int, int> vote_counts;
    for (const auto& [agent, vote] : all_votes) {
        vote_counts[vote]++;
    }
    int winning_vote = -1;
    int winning_vote_count = 0;
    for (const auto& [vote, count] : vote_counts) {
        if (count > winning_vote_count) {
            winning_vote = vote;
            winning_vote_count = count;
        }
    }

    if (!(winning_vote_count < static_cast<int>(all_votes.size()) / 2)) {
        winning_vote = -1;
    }

    if (winning_vote != -1) {
        for (size_t i = 0; i < all_votes.size(); i++) {
            results.push_back(currentOptionsMatrix[i][winning_vote]);
        }
    } else {
        for (size_t i = 0; i < all_votes.size(); i++) {
            results.push_back(0);
        }
    }

    return std::make_pair(winning_vote, results);
}

// std::vector<float> SocialChoiceSim::generateProbabilities(std::vector<std::vector<int>> currentOptionsMatrix) {
//     createChoicesMatrix(std::move(currentOptionsMatrix));
//     std::vector<std::pair<std::vector<int>, double>> results;
//     std::vector<int> currentArray;
//     int currentID = 0;
//     double current_prob = 1;
//     genCombinations(currentID, currentArray, current_prob, results);
//     // results should now hold big boy list if we did this correctly.
//     std::vector<float> cause_probabilities = getCauseProbability(results);
//
// }

// std::vector<float> SocialChoiceSim::getCauseProbability(std::vector<std::pair<std::vector<int>, double> > &results) {
//     std::vector<float> newVector = {1.0}; // fix this later. I'm tired
//     return newVector;
// }

// std::vector<std::vector<float>> SocialChoiceSim::createChoicesMatrix(std::vector<std::vector<int>> currentOptionsMatrix) {
//
// }

// void SocialChoiceSim::setChromosome(const std::vector<Chromosome> chromosomes) {
//     // could add statement to check if the chromosomes size and the bot  size are different, might do that later
//     for (int i = 0; i < chromosomes.size(); i++) {
//         bots[i].setChromosome(chromosomes[i]);
//     }
// }

// void SocialChoiceSim::genCombinations(int currentID, std::vector<int> current_array, double current_prob, std::vector<std::pair<std::vector<int>, double>>& results) {
//     if (currentID == totalPlayers) {
//         // Add the combination and its probability to the results
//         results.emplace_back(current_array, current_prob);
//         return;
//     }
//
//     // Iterate over each cause
//     for (int cause = 0; cause < numCauses; ++cause) {
//         double prob = probabilitiesMatrix[currentID][cause];
//         if (prob > 0) {
//             current_array[currentID] = cause;  // Set the current cause
//             double newProb = prob * current_prob;
//             SocialChoiceSim::genCombinations(currentID+1, current_array, newProb, results);
//         }
//     }
// }