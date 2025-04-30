//
// Created by Sean on 4/29/2025.
//

#ifndef GREEDYBOT_H
#define GREEDYBOT_H

#include "ParentBot.h"
#include <string>
#include <vector>

class GreedyBot {
public:
    explicit GreedyBot(int selfID); // constructor
    int getVote(const std::vector<std::vector<int>>&) const;
private:
    int selfID;
    std::pmr::string selfType;

};



#endif //GREEDYBOT_H
