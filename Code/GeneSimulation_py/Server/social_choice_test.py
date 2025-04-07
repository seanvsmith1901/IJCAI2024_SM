# testbed to test genes and display results in a human readable format.
import time
import pandas as pd
from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
from collections import Counter
import statistics
import random
import numpy as np
import os



if __name__ == "__main__":
    bot_type = 3 # 1 is pareto, 2 is greedy, 3 is GT, 4 is random
    sim = Social_Choice_Sim(11, 3, 0, bot_type)  # starts the social choice sim, call it whatever you want
    #chromosomes = [[0.14596498326505314,0.9771860239933535,0.30421736004971067,0.9013883929685444,0.2935735969819985,0.26895617061622723,0.8015444130652044,0.38763987943959655,0.840265769054056,0.9280936968864469,0.32887573919216284,0.4606764827331278,0.8238271261242128,0.11467963071713083,0.5862458509657092,0.3603218802399152,0.512299688934243,0.6368346776639202,0.3636616659220744,0]] * 11
    current_file = "Bots/chromosomesToKeepAround/generation_7.csv"
    # reads it in from the file.
    df = pd.read_csv(current_file, comment="#")
    chromosomes = [df.iloc[0, 1:].tolist()] * 11 # automatically selects the most fit singular instance from whatever chromosome.

    results = {}
    num_rounds = 1
    for i in range(11): # total_players
        results[i] = [] # just throw in all the utilites
    start_time = time.time()
    num_genes = 20
    cooperation_score = 0
    sim.set_chromosome(chromosomes) # in this case its the same every time.

    for i in range(num_rounds): # just a ridicuously large number

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.
        bot_votes = sim.get_votes() # where da magic happens

        total_votes = len(bot_votes)
        winning_vote, round_results = sim.return_win(bot_votes)  # is all votes, works here
        if winning_vote != -1:  # keep track of how often they cooperate.
            cooperation_score += 1

        for bot in range(total_votes):
            results[bot].append(round_results[bot]) # this should work? I should have saved a stable version before hand.

    end_time = time.time()
    print("This was the total time ", end_time - start_time)

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
    std = np.std(new_list)
    mean = np.mean(new_list)
    cv = std / abs(mean) # for the random bot.

    cooperation_score = cooperation_score / num_rounds # as a percent, how often we cooperated.

    print("this was the cooperation score ", cooperation_score)
    print("This was the cv ", cv)
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

    plt.text(0.95, 0.90, f'Coefficient of Variation: {cv:.2f}', # should display the average standard deviation as well.
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
    plt.title('Scores per Round for Each Player With Algorithm ' + str(bot_type))
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()
    if bot_type == 3: # game theory bot special case
        file_name = chromosomes[0][0]

    filename = "scores for " + str(bot_type)

    plt.savefig('scores_plot.png', dpi=300, bbox_inches='tight') # save the fetcher
    plt.show()


