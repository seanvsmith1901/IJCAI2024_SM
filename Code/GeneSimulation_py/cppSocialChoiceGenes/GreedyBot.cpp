//
// Created by Sean on 4/29/2025.
//

#include "GreedyBot.h"

#include <iostream>
#include <ostream>

GreedyBot::GreedyBot(int selfID) {
    this->selfID = selfID;
    this->selfType = "G";
}

int GreedyBot::getVote(const std::vector<std::vector<int>>& currentOptionsMatrix) const {
    const std::vector<int>& currentRow = currentOptionsMatrix[selfID];
    int currentMax = -100; // we should never have reason to generate a smaller value
    int currentVote = -2; // also impossible
    for (int i = 0; i < currentRow.size(); i++) {
        if (currentRow[i] > currentMax) {
            currentMax = currentRow[i];
            currentVote = i;
        }
    }
    if (currentMax < 0) {
        currentVote = -1;
    }

    std::cout << "This is the current vote ! " << currentVote << " based off of this max " << currentMax << std::endl;
    return currentVote;
}