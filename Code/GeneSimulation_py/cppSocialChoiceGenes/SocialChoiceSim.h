//
// Created by Sean on 4/8/2025.
//
#pragma once


#ifndef SOCIALCHOICESIM_H
#define SOCIALCHOICESIM_H

#include <vector>
#include <memory>
#include <map>
#include <unordered_map>
#include <string>
#include <random>
// #include <algorithm>
// #include <numeric>
// #include <cmath>
// #include <iostream>
// #include <iterator>
#include "GameTheoryBot.h"

class SocialChoiceSim {
public:
    SocialChoiceSim(int totalPlayers, int numCauses, int numHumans); // constructor

    void setChromosome(const std::vector<std::vector<float>>& chromosomes);
    std::vector<std::vector<int>> createOptionsMatrix();
    const std::vector<std::vector<int>>& getCurrentOptionsMatrix() const;
    void startRound();
    const std::vector<float>& getProbabilites() const;
    std::unordered_map<int, int> getVotes();
    std::unordered_map<int, int> getVotesSingleChromosome();
    std::pair<int, std::vector<int>> returnWin(const std::unordered_map<int, int>& all_votes);



private:
    void createBots(); // no reason to leave this dangling

    int totalPlayers;
    int numHumans;
    int numBots;
    int cpp = 3;
    int rad = 5;
    int numCauses;
    int typeBot;

    std::map<std::string, float> players;
    std::vector<std::vector<int>> optionsMatrix;
    std::vector<std::vector<int>> currentOptionsMatrix;
    std::unordered_map<int, int> allVotes;
    std::vector<std::unordered_map<int, float>> organizedDistanceMatrix;
    std::vector<GameTheoryBot> bots; // this feels easier to me. maybe.
    std::vector<int> currentVotes;
    std::vector<float> probabilities;
    std::vector<std::vector<int>> allCombinations;

    std::mt19937 gen; // random number generator

};



#endif //SOCIALCHOICESIM_H
