//
// Created by Sean Smith on 6/5/2026.
//

#ifndef IJCAI2024_SM_LOGGER_H
#define IJCAI2024_SM_LOGGER_H
#include <utility>
#include <vector>
#include <string>
#include "AbstractAgent.h"

#include <nlohmann/json.hpp>  // Include the JSON library

// GAME SECTION: Has a game informaiton object and then a list that we can just add things too
class GameInformation {
public:
    GameInformation(std::vector<float> new_popularities, std::vector<std::vector<float>> new_influences, int newRoundNum) {
        popularities = std::move(new_popularities);
        influences = std::move(new_influences);
        roundNum = newRoundNum;
    }
    // lets add a little getter action
    const std::vector<float>& getPopularities() const { return popularities; }
    const std::vector<std::vector<float>>& getInfluences() const { return influences; }
    int getRoundNum() const { return roundNum; }

private:
    std::vector<float> popularities;
    std::vector<std::vector<float>> influences;
    int roundNum = 0;
};

class AgentObject {
public:
    AgentObject(const AbstractAgent& agent) {  // Take by const reference
        if (agent.whoami == "geneAgent") {
            geneVector = agent.myGenes;
            algorithmType = 1;
        }
        // TODO: add support for other agents here.
    }

    // little getter action.
    const std::string& getGeneVector() const { return geneVector; }
    int getAlgorithmType() const { return algorithmType; }

private:
    std::vector<int> geneVector;
    int algorithmType = -1;
};


class JHGLogger {
public:
    // add agents on init
    JHGLogger(const std::vector<AbstractAgent>& currAgents) {
        for (const auto& agent : currAgents) {
            auto new_agent = AgentObject(agent);
            agents.push_back(new_agent);
        }
    }
    // add a game when required, given the new popularities, new influences, and newRoundNum.
    void addGame(std::vector<float> new_popularities, std::vector<std::vector<float>> new_influences, int newRoundNum) {
        auto newGame = GameInformation(std::move(new_popularities), std::move(new_influences), newRoundNum);
        games.push_back(newGame);
    }

    void writeToFile(cost std::string& path) {
        ;
    }

private:
    std::vector<AgentObject> agents; // holds the agents algorithm type and possible gene string
    std::vector<GameInformation> games; // holds a list of game information objects w/ influence and pops per round
};

// Method definition - can go here or in a separate .cpp file
inline nlohmann::json JHGLogger::toJson() const {
    nlohmann::json j;

    // Serialize agents
    j["agents"] = nlohmann::json::array();
    for (const auto& agent : agents) {
        j["agents"].push_back({
            {"algorithmType", agent.getAlgorithmType()},
            {"genes", agent.getGeneVector()}
        });
    }

    // Serialize rounds
    j["rounds"] = nlohmann::json::array();
    for (const auto& game : games) {
        j["rounds"].push_back({
            {"roundNum", game.getRoundNum()},
            {"popularities", game.getPopularities()},  // Fixed: added ()
            {"influences", game.getInfluences()}       // Fixed: added ()
        });
    }

    return j;
}


#endif //IJCAI2024_SM_LOGGER_H
