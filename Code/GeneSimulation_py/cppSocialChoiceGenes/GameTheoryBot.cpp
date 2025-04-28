//
// Created by Sean on 4/8/2025.
//

#include "GameTheoryBot.h"
#include <algorithm>  // for std::max
#include <map>        // for frequency counting
#include <iostream>   // optional, for debugging

#include "Chromosome.h"
#include <Eigen/Dense>

// Constructor
GameTheoryBot::GameTheoryBot(int selfID, std::string type, std::vector<std::vector<float>>& chromosomes)
    : selfId(selfID), type("GT"), numPlayers(11), numCauses(3) {
    // Initialize other stuff if needed
}

// Set the chromosome
void GameTheoryBot::setChromosome(const Chromosome& currChromosome) {
    chromosome = currChromosome.getChromosome(); //
}

// Get vote based on current options and internal logic
int GameTheoryBot::getVote(const std::vector<std::vector<int>>& currentOptionsMatrix,
                const std::vector<float>& bigBoyList) {

    auto cause_probability = get_cause_probability(big_boy_list);
    auto normalized = normalize(cause_probability);

    this->current_options_matrix = current_options_matrix;
    num_players = current_options_matrix.size();
    num_causes = current_options_matrix[0].size();

    auto current_rewards = think_about_reward(normalized);
    int vote = use_bot_type(current_rewards);
    return vote;
}

// Generate normalized probabilities for each cause
std::vector<float> GameTheoryBot::generateProbabilities(const std::vector<std::vector<int>>& optionsMatrix) {
    set_current_options(current_options_matrix);
    auto big_boy_list = generate_all_possibilities();
    auto cause_probability = get_cause_probability(big_boy_list);
    return normalize(cause_probability);
}

// Optimized version of getVote using precomputed probabilities
int GameTheoryBot::getVote(const std::vector<float>& normalizedCauseProbability,
                                          const std::vector<std::vector<int>>& optionsMatrix) {
    return 0; // placeholder
}

// Decide vote based on current reward landscape and risk adversity
int GameTheoryBot::useBotType(const std::vector<std::pair<float, float>>& currentRewards) {
    return 0; // placeholder
}

// Evaluate the expected reward for each option
std::vector<std::pair<float, float>> GameTheoryBot::thinkAboutReward(const std::vector<float>& normalizedProb) {
    std::vector<std::pair<double, double>> rewards;
    for (size_t i = 0; i < normalized_cause_probability.size(); ++i) {
        float expected_reward = (i == 0) ? 0.0 : normalized_cause_probability[i] * current_options_matrix[self_id][i - 1];
        rewards.emplace_back(normalized_cause_probability[i], expected_reward);
    }
    return rewards;
}

// Get cause-level probability from all possible vote combinations
std::vector<float> GameTheoryBot::getCauseProbability(const std::vector<float>& allPossibilities) {
    std::vector<double> cause_probability(num_causes + 1, 0.0);
    int total_votes = possibilities.empty() ? 0 : possibilities[0].size();
    for (const auto& possibility : possibilities) {
        std::vector<int> freqs(num_causes + 1, 0);
        int max_item = 0, max_count = 0;

        for (int item : possibility) {
            freqs[item]++;
            if (freqs[item] > max_count) {
                max_count = freqs[item];
                max_item = item;
            }
        }

        if (max_count > total_votes / 2) {
            cause_probability[max_item] += 1.0; // need weighted probs here
        } else {
            cause_probability[0] += 1.0;
        }
    }
    return cause_probability;
}

// Generate all possible vote combinations (brute-force)
std::vector<std::vector<float>> GameTheoryBot::generateAllPossibilities(const std::vector<std::vector<int>>& optionsMatrix) {
    // Recursive version later; placeholder
    std::vector<std::vector<float>> dummy;
    return dummy;
}

// Create preference ranking matrix and column preference vector
 std::vector<std::vector<int>> GameTheoryBot::createChoicesMatrix(const std::vector<std::vector<int>>& currentOptionsMatrix, std::vector<int>& choiceListOut) {
    return {}; // placeholder
}

// Generate probability matrix from choices + weights
std::vector<std::vector<float>> GameTheoryBot::createProbabilityMatrix(const std::vector<std::vector<int>>& choicesMatrix, const std::vector<int>& choiceList) {
    return std::vector<std::vector<float>>();
}

// Recursive combo generator — might take some finessing
void GameTheoryBot::generateCombinations(int currentId, std::vector<float>& currentArray,
                                         std::vector<std::vector<float>>& results) {

}

std::vector<double> GameTheoryBot::normalize(const std::vector<double>& input) {
    double sum = std::accumulate(input.begin(), input.end(), 0.0);
    std::vector<double> output;
    output.reserve(input.size());
    for (double x : input) {
        output.push_back(x / sum);
    }
    return output;
}

void GameTheoryBot::set_current_options(const std::vector<std::vector<double>>& options) {
    current_options_matrix = options;
    num_players = options.size();
    num_causes = options[0].size();
}