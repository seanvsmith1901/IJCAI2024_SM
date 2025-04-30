//
// Created by Sean on 4/8/2025.
//

#ifndef GAMETHEORYBOT_H
#define GAMETHEORYBOT_H

#include "ParentBot.h"
#include <vector>
#include <string>
#include "Chromosome.h"

class GameTheoryBot : public ParentBot {
public:
    GameTheoryBot(int selfID, std::string type, std::vector<std::vector<int>> currentOptionsMatrix);


    void setChromosome(const Chromosome& currChromosome);
    int getVote(const std::vector<std::vector<int>>& currentOptionsMatrix,
                std::vector<std::pair<std::vector<int>, double>>& bigBoyList);

    std::vector<double> generateProbabilities(const std::vector<std::vector<int>>& currentOptionsMatrix);
    // use the traditional get vote here, if you can.
    // int getVoteSingleChromosome(const std::vector<float>& normalizedCauseProbability,
    //                            const std::vector<std::vector<int>>& currentOptionsMatrix);
    int useBotType(const std::vector<std::pair<double, double>>& currentRewards);
    // technically this one returns a map of pairs of a value and an expected value. difficil.
    std::vector<std::pair<double, double>> thinkAboutReward(const std::vector<double> normalizedCauseProbability);
    std::vector<double> getCauseProbability(const std::vector<std::pair<std::vector<int>, double>>& allPossibilities);
    std::vector<std::pair<std::vector<int>, double>> generateAllPositibilities(std::vector<std::vector<int>> currentOptionsMatrix);
    std::pair<std::vector<std::vector<int>>, std::vector<int>> createChoicesMatrix(std::vector<std::vector<int>> currentOptionsMatrix);
    std::vector<std::vector<double>> createProbabilityMatrix(std::vector<std::vector<int>> choicesMatrix, std::vector<double> weightsArray, std::vector<std::vector<int>> currentOptionsMatrix);
    void generateCombinations(
        int currentID,
        std::vector<int>& currentArray,
        double& probabilityProduct,
        std::vector<std::vector<double>>& probabilityMatrix,
        int numPlayers,
        int numCauses,
        std::vector<std::pair<std::vector<int>, double>>& results);

    std::vector<double> getChromosome();





private:
    int selfId;
    std::string type;
    std::vector<double> chromosome;
    std::string riskAdversity;

    int numPlayers;
    int numCauses;
    std::vector<std::vector<int>> currentOptionsMatrix;
    std::vector<std::vector<double>> probabilityMatrix;

};



#endif //GAMETHEORYBOT_H
