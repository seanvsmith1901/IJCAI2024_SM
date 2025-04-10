//
// Created by Sean on 4/8/2025.
//

#include "Chromosome.h"
#include "socialChoiceSim.h"


SocialChoiceSim::SocialChoiceSim(int totalPlayers, int numCauses, int numHumans)
    : totalPlayers(totalPlayers), numCauses(numCauses), numHumans(numHumans), numBots(totalPlayers-numHumans), cpp(3), rad(5), gen(std::random_device()())
{
    createBots();

    currentOptionsMatrix = {};
    allVotes.clear();
    currentVotes.clear();
    probabilities.clear();
    allCombinations.clear();
}

void SocialChoiceSim::createBots() {// adds bots to the bots vector
    bots.clear(); // first get rid of all the old bots.
    for (int i = 0; i < numBots; i++) {
        GameTheoryBot newBot(i);
        bots.push_back(newBot);
    }
}

void SocialChoiceSim::setChromosome(const std::vector<Chromosome> chromosomes) {
    // could add statement to check if the chromosomes size and the bot  size are different, might do that later
    for (int i = 0; i < chromosomes.size(); i++) {
        bots[i].setChromosome(chromosomes[i]);
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
const std::vector<float>& SocialChoiceSim:: getProbabilites() const {
    return probabilities;

}
std::unordered_map<int, int> SocialChoiceSim::getVotes() {
    std::unordered_map<int, int> botVotes;
    for (int i = 0; i < bots.size(); i++) {
        if (allCombinations.empty()) {
            allCombinations = generateProbabilities(currentOptionsMatrix);
        }
        botVotes[i] = bots[i].getVote(allCombinations, currentOptionsMatrix);
    }
    return botVotes;

}

std::vector<int> generateProbabilities(std::vector<int> currentOptionsMatrix) {
    ;
}

std::pair<int, std::vector<float>> SocialChoiceSim::returnWin(const std::unordered_map<int, int>& all_votes) {

}



void createBots();