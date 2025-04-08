//
// Created by Sean on 4/8/2025.
//

#ifndef GAMETHEORYBOT_H
#define GAMETHEORYBOT_H

#include <vector>
#include <string>
#include <tuple>


class GameTheoryBot {
public:
    explicit GameTheoryBot(int selfID);

    GameTheoryBot(int selfID, std::string type, std::vector<std::vector<float>>& chromosomes); // constructor

    void setChromosome(const std::vector<float>& chromosome);
    int getVote(const std::vector<std::vector<int>>& currentOptionsMatrix,
                const std::vector<std::vector<int>>& bigBoyList);

    std::vector<float> generateProbabilities(const std::vector<std::vector<int>>& currentOptionsMatrix);
    int getVoteOptimizedSingle(const std::vector<float>& normalizedCauseProbability,
                               const std::vector<std::vector<int>>& currentOptionsMatrix);

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
    std::vector<float> getCauseProbability(const std::vector<std::vector<float>>& allPossibilities);

    std::vector<std::vector<int>> createChoicesMatrix(const std::vector<std::vector<int>>& currentOptionsMatrix,
                                                      std::vector<int>& choiceListOut);
    std::vector<std::vector<float>> createProbabilityMatrix(const std::vector<std::vector<int>>& choicesMatrix,
                                                            const std::vector<int>& choiceList);

    std::vector<std::vector<float>> generateAllPossibilities(const std::vector<std::vector<int>>& currentOptionsMatrix);
    void generateCombinations(int currentId,
                              std::vector<int>& currentArray,
                              float currentProbability,
                              std::vector<std::vector<float>>& allCombinations);

};



#endif //GAMETHEORYBOT_H
