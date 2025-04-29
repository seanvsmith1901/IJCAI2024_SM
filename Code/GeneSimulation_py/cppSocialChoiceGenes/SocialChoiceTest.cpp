//
// Created by Sean on 4/28/2025.
//

#include <chrono>    // for the start and end times
#include <iostream>  // printing to console and whatnot
#include <fstream>   // for writing to files
#include <vector>    // you already know whats good
#include <numeric>   // for std::accumulate
#include <cmath>     // for std::sqrt, std::pow

#include "SocialChoiceSim.h"

double Mean(const std::vector<double>& data) {
    if (data.empty()) return 0.0;
    double sum = std::accumulate(data.begin(), data.end(), 0.0);
    return sum / data.size();
}

double stddev(const std::vector<double>& data) {
    if (data.size() < 2) return 0.0;
    double m = Mean(data);
    double accum = 0.0;
    for (double x : data) {
        accum += (x - m) * (x - m);
    }
    return std::sqrt(accum / data.size());  // population stddev
    // For sample stddev, use: std::sqrt(accum / (data.size() - 1));
}




int main() {
    int bot_type = 0;
    int total_players = 11;
    int num_causes = 3;
    // I am going to say that I am never expecting this to handle human input. thats silly and weird. pure sims only on this end.
    SocialChoiceSim sim(total_players, num_causes, 0, bot_type);
    // ignore reading in chromosomes for now, just get a greedy bot functioning and we can call it a day
    std::map<int, std::vector<double>> results;
    int num_rounds = 100;
    for (int i = 0; i < 11; i++) {
        // idek if this works, it might brick on me, might tell me null assingment.
        results[i] = std::vector<double>();
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

    std::unordered_map<int, std::vector<double>> sumsPerRound;
    for (auto bot : results) {
        sumsPerRound[bot.first] = std::vector<double>();
        double currentSum = 0;
        for (auto pair : bot.second) {
            currentSum += pair;
            sumsPerRound[bot.first].push_back(currentSum);
        }
    }
    std::vector<double> standardDeviation;
    std::unordered_map<int, double> totalSumDeviation;
    std::vector<double> deviationsPerRound;

    std::vector<double> newVector;
    for (auto bot : sumsPerRound) {
        newVector.push_back(sumsPerRound[bot.first][num_rounds-1]);
    }
    // find the std and the mean here. no way they built in like they should be.
    double std = stddev(newVector);
    double mean = Mean(newVector);
    double variance = std / std::abs(mean);

    double newCooperationScore = static_cast<double>(cooperationScore) / num_rounds;


    // totalScoresPerRound
    std::vector<double> totalScoresPerRound(num_rounds, 0.0);

    for (int i = 0; i < num_rounds; i++) {
        for (const auto& player : results) {
            for (const auto& scoreVector : player.second) {
                totalScoresPerRound[i] += player.second[i];
            }
        }
    }


    // averateScoresPerRound
    std::vector<double> averageScoresPerRound;
    for (auto totalScore : totalScoresPerRound) {
        averageScoresPerRound.push_back(totalScore / total_players);
    }


    // cumulativeAverageScore
    std::vector<double> cumulativeAverageScore(averageScoresPerRound.size());
    double runningSum = 0.0;
    std::partial_sum(
        averageScoresPerRound.begin(),
        averageScoresPerRound.end(),
        cumulativeAverageScore.begin());


    double totalSum = std::accumulate(averageScoresPerRound.begin(), averageScoresPerRound.end(), 0.0);
    double totalAverageIncrease = totalSum / num_rounds;


    std::ofstream outPutFile;
    outPutFile.open("TryThisAgain.txt");
    if (outPutFile.is_open()) {
        std::cout << "We have opened the file" << std::endl;
        // algorithmType, cumulativeTotalScore(perRound), totalScore, avgIncrease, coefficientOfVariation, CooperationScore
        // that should be everything we need. first we need to get the sim not coughing up blood.

        outPutFile << "Algorithm Type " << bot_type << std::endl;
        outPutFile << "mean " << mean << std::endl;
        outPutFile << "standard deviation " << std << std::endl;

        outPutFile << "Cooperation " << newCooperationScore << std::endl;

        outPutFile << "Average Score Per Round ";
        for (const auto& element : averageScoresPerRound) {
            outPutFile << element << ", ";
        }
        outPutFile << std::endl;

        outPutFile << "Sums Per Round ";
        for (const auto& pair : sumsPerRound) {
            outPutFile << pair.first << ",";
            for (const auto& element : pair.second) {
                outPutFile << element << ",";
            }
        }
        outPutFile << std::endl;


        outPutFile << "Total Average Increase " << totalAverageIncrease << std::endl;
        outPutFile << "Cumulative Average Score ";
        for (const auto& element : cumulativeAverageScore) {
            outPutFile << element << ", ";
        }
        outPutFile << std::endl;

        outPutFile.close();

    } else {
        std::cout << "Error opening output file." << std::endl;
    }





    return 0;
}



