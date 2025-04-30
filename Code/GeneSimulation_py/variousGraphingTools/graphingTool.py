import time
import pandas as pd
from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
from collections import Counter
import statistics
import random
import numpy as np
import os
from pathlib import Path
from fileReader import SimulationResult

def big_boy():

    filename = "C:/Users/Sean/Documents/GitHub/IJCAI2024_SM/Code/GeneSimulation_py/cppSocialChoiceGenes/cmake-build-debug/TryThisAgain.txt"
    currentData = SimulationResult.from_file(filename)
    sums_per_round = currentData.sums_per_round
    cumulative_average_score = currentData.cumulative_average_score
    total_average_increase = currentData.total_average_increase
    cooperation_score = currentData.cooperation
    bot_type = currentData.algorithm_type
    cv = currentData.coefficient_of_variation
    rounds = range(len(sums_per_round[0]))


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
    # the following related to saving the fetcher to a file. Not worried about that right now, worry about it later.

    # if bot_type == 3: # game theory bot special case
    #     file_name = "Game Theory " + Path(current_file).stem
    # else:
    #     bot_name = ""
    #     if bot_type == 1:
    #         bot_name = "Pareto"
    #     if bot_type == 2:
    #         bot_name = "Greedy"
    #     if bot_type == 4:
    #         bot_name = "Random"
    #     file_name = str(bot_name)
    #
    # directory = r"C:\Users\Sean\Documents\GitHub\IJCAI2024_SM\Code\GeneSimulation_py\Server\Graphs"
    #
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    # file_path = os.path.join(directory, f"{file_name}.png")
    #
    #
    #plt.savefig(file_path, dpi=300, bbox_inches='tight') # save the fetcher
    plt.show()

if __name__ == "__main__":
    big_boy()