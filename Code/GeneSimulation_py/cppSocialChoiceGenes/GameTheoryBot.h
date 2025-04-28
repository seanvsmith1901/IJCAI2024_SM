//
// Created by Sean on 4/8/2025.
//

#ifndef GAMETHEORYBOT_H
#define GAMETHEORYBOT_H

#include <vector>
#include <string>
#include "Chromosome.h"

class GameTheoryBot {
public:
    explicit GameTheoryBot(int selfID);

    GameTheoryBot(int selfID, std::string type, std::vector<std::vector<float>>& chromosomes); // constructor

    void setChromosome(const Chromosome& chromosome);
    int getVote(const std::vector<std::vector<int>>& currentOptionsMatrix,
                const std::vector<float>& bigBoyList);

    std::vector<float> generateProbabilities(const std::vector<std::vector<int>>& currentOptionsMatrix);
    // use the traditional get vote here, if you can.
    int getVote(const std::vector<float>& normalizedCauseProbability,
                               const std::vector<std::vector<int>>& currentOptionsMatrix);
    std::vector<float> thinkAboutReward(const std::vector<float> normalizedCauseProbability);
    std::vector<float> getCauseProbability(std::vector<std::vector<int>> allPossibilities);
    std::vector<float> generateProbabilities(std::vector<std::vector<int>> allPossibilities);
    std::vector<std::vector<float>> generateAllPositibilities(std::vector<std::vector<int>> currentOptionsMatrix);
    std::vector<std::vector<float>> createChoicesMatrix(std::vector<std::vector<int>> currentOptionsMatrix);
    std::vector<std::vector<float>> createProbabilityMatrix(std::vector<std::vector<int>> currentOptionsMatrix, std::vector<float> weightsArray);
    std::vector<std::vector<float>> generateCombinations(int currentID, std::vector<float> currentArray);


private:
    int selfId;
    std::string type;
    std::vector<float> chromosome;
    std::string riskAdversity;

    int numPlayers;
    int numCauses;
    std::vector<std::vector<int>> currentOptionsMatrix;
    std::vector<std::vector<float>> probabilityMatrix;

    int useBotType(const std::vector<std::pair<float, float>>& currentRewards);
    std::vector<std::pair<float, float>> thinkAboutReward(const std::vector<float>& normalizedCauseProbability);
    std::vector<float> getCauseProbability(const std::vector<float>& allPossibilities);

    std::vector<std::vector<int>> createChoicesMatrix(const std::vector<std::vector<int>>& currentOptionsMatrix,
                                                      std::vector<int>& choiceListOut);
    std::vector<std::vector<float>> createProbabilityMatrix(const std::vector<std::vector<int>>& choicesMatrix,
                                                            const std::vector<int>& choiceList);

    std::vector<std::vector<float>> generateAllPossibilities(const std::vector<std::vector<int>>& currentOptionsMatrix);
    void generateCombinations(int currentId, std::vector<float>& currentArray, std::vector<std::vector<float>>& results);
    std::vector<double> normalize(const std::vector<double>& probs);
    void set_current_options(const std::vector<std::vector<double>>& options);

};



#endif //GAMETHEORYBOT_H
