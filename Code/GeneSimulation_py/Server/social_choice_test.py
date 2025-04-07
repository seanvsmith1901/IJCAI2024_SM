# just a small testbed to make sure that all the math was mathing. it is now all mathing the way that I want it to.
import time

from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
from collections import Counter
import statistics
import random
# ok now I need to make it play an actual round of JHG here in the sim so I can test the influence matrix. This is annoying.


if __name__ == "__main__":
    # pure bot sim
    # wanna get some results for pareto optimal
    sim = Social_Choice_Sim(11, 3, 0, 2)  # starts the social choice sim, call it whatever you want
    #chromosomes = [[0.14596498326505314,0.9771860239933535,0.30421736004971067,0.9013883929685444,0.2935735969819985,0.26895617061622723,0.8015444130652044,0.38763987943959655,0.840265769054056,0.9280936968864469,0.32887573919216284,0.4606764827331278,0.8238271261242128,0.11467963071713083,0.5862458509657092,0.3603218802399152,0.512299688934243,0.6368346776639202,0.3636616659220744,0]] * 11
    #chromosomes = [[0.07608630291702134, 0.6384130720727683, 0.19168194910868275, 0.4621622949954527, 0.8947894398834366, 0.6144458421842767, 0.13055966348312054, 0.7007393159760924, 0.12892661702624952, 0.7011314424376426, 0.276691960478721, 0.15631126834587383, 0.3895274814737226, 0.8127386708328449, 0.18970050900353053, 0.7007645540311098, 0.7671485548172058, 0.49097298823917235, 0.2032415957611493, 1]] * 11
    results = {}
    num_rounds = 10000
    for i in range(11): # total_players
        results[i] = [] # just throw in all the utilites
    start_time = time.time()
    num_genes = 20
    cooperation_score = 0
    # chromosomes = [random.uniform(0, 1) for _ in range(num_genes)] * 11
    for i in range(num_rounds): # just a ridicuously large number
        #sim.set_chromosome(chromosomes)
        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.
        bot_votes = sim.get_votes() # where da magic happens

        total_votes = len(bot_votes)
        winning_vote_count = Counter(bot_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(bot_votes.values()).most_common(1)[0][0]
        probs = sim.get_probabilities()
        cooperation_score += 1
        if not (winning_vote_count > total_votes // 2):
            cooperation_score -= 1
            winning_vote = -1

        for i in range(total_votes):
            results[i].append(current_options_matrix[i][winning_vote])
    end_time = time.time()
    print("This was the total time ", end_time - start_time)
    print("here were the resuts ", results)


    sums_per_round = {}
    for bot in results:
        sums_per_round[bot] = []
        current_sum = 0
        for i, new_sum in enumerate(results[bot]):
            current_sum += new_sum
            sums_per_round[bot].append(current_sum)
    statistical_decviation = []
    total_sum_deviation = {}
    deviation_per_round = []

    new_list = []
    for bot in sums_per_round:
        new_list.append(sums_per_round[bot][num_rounds-1])
    deviation_per_round.append(statistics.stdev(new_list))

    average_standard_deviation = deviation_per_round[-1]
    cooperation_score = cooperation_score / num_rounds # as a percent, how often we cooperated.


    print("This is what sums per round looks like ", sums_per_round)
    print("this was the cooperation score ", cooperation_score)

    # Prepare the x-axis (rounds)
    rounds = range(num_rounds) # 10 rounds, so x-values range from 0 to 9
    # Calculate the total score for each round
    total_scores_per_round = [sum(results[player][round_num] for player in results) for round_num in rounds]

    # Calculate the average score per round (by dividing by the number of players)
    num_players = len(results)  # Number of players (bots)
    average_scores_per_round = [total_score / num_players for total_score in total_scores_per_round]

    # Calculate the cumulative average score
    cumulative_average_score = [sum(average_scores_per_round[:i + 1]) for i in range(len(average_scores_per_round))]
    total_average_increase = cumulative_average_score[-1] / num_rounds

    # Set up the plot
    plt.figure(figsize=(10, 6))

    # Loop through each player's scores and plot them
    for player, scores_list in sums_per_round.items():
        plt.plot(rounds, scores_list, marker='o', label=f'Player {player}')

    plt.plot(rounds, cumulative_average_score, marker='x', label='Cumulative Total Score', linewidth=3, color='black')

    plt.text(0.95, 0.90, f'Final Std Dev: {average_standard_deviation:.2f}', # should display the average standard deviation as well.
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

    plt.text(0.95, 0.95, f'Avg Increase: {total_average_increase:.2f}',
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

    plt.text(0.95, 0.85, f'Cooperation Score: {cooperation_score:.2f}',
             # should display the average standard deviation as well.
             horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

    # Adding labels and title
    plt.xlabel('Round')
    plt.ylabel('Score')
    plt.title('Scores per Round for Each Player')
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()
    plt.show()