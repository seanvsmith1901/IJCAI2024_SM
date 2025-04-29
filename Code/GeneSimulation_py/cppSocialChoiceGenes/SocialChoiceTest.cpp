//
// Created by Sean on 4/28/2025.
//

#include <chrono>
#include <iostream>

#include "SocialChoiceSim.h"

int main() {
    int bot_type = 0;
    int total_players = 11;
    int num_causes = 3;
    // I am going to say that I am never expecting this to handle human input. thats silly and weird. pure sims only on this end.
    SocialChoiceSim sim(total_players, num_causes, 0, bot_type);
    // ignore reading in chromosomes for now, just get a greedy bot functioning and we can call it a day
    std::map<int, std::vector<float>> results;
    int num_rounds = 1000;
    for (int i = 0; i < 11; i++) {
        // idek if this works, it might brick on me, might tell me null assingment.
        results[i] = std::vector<float>();
    }
    auto start_time = std::chrono::high_resolution_clock::now();
    int cooperationScore = 0;
    // like I said, no chromosomes yet

    for (int i = 0; i < num_rounds; i++) {
        sim.startRound();
        auto currentOptionsMatrix = sim.getCurrentOptionsMatrix();
        auto botVotes = sim.getVotes();
        std::size_t total_votes = botVotes.size();
        auto [winningVote, roundResults] = sim.returnWin(botVotes);
        if (winningVote != -1) {
            cooperationScore += 1;
        }

        for (std::size_t bot = 0; bot < total_votes; bot++) {
            results[bot].push_back(roundResults[bot]);
        }

    }
    auto end_time = std::chrono::high_resolution_clock::now();
    std::cout<<"This was the total time "<< end_time - start_time << " seconds."<<std::endl;

    std::unordered_map<int, int> sumsPerRound;
    for (auto bot : results) {
        sumsPerRound[bot] = std::vector<float>();
        float currentSum = 0;
        for (auto pair : results[bot]) {
            currentSum += pair;
            sumsPerRound[bot].push_back(currentSum);
        }
    }




    return 0;
}