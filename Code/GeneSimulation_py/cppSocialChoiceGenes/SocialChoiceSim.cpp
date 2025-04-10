//
// Created by Sean on 4/8/2025.
//

#include "socialChoiceSim.h"


SocialChoiceSim::SocialChoiceSim(int totalPlayers, int numCauses, int numHumans)
    : totalPlayers(totalPlayers), numCauses(numCauses), numHumans(numHumans), numBots(totalPlayers-numHumans), cpp(3), rad(5), gen(std::random_device()())
{
    createBots();

    currentOptionsMatrix = {};
    allVotes.clear();
    organizedDistanceMatrix.clear();
    currentVotes.clear();
    probabilities.clear();
}

void SocialChoiceSim::createBots() {

}


void SocialChoiceSim::setChromosome(const std::vector<std::vector<float>>& chromosomes) {

}

std::vector<std::vector<int>> SocialChoiceSim::createOptionsMatrix() {

}
const std::vector<std::vector<int> >& SocialChoiceSim::getCurrentOptionsMatrix() const {

}


void SocialChoiceSim::startRound() {

}
const std::vector<float>& SocialChoiceSim:: getProbabilites() const {

}
std::unordered_map<int, int> SocialChoiceSim::getVotes() {

}
std::unordered_map<int, int> SocialChoiceSim::getVotesSingleChromosome() {

}

std::pair<int, std::vector<int>> SocialChoiceSim::returnWin(const std::unordered_map<int, int>& all_votes) {

}

void createBots();