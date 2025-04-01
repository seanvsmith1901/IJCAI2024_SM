# just a small testbed to make sure that all the math was mathing. it is now all mathing the way that I want it to.
import time

from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
from Code.GeneSimulation_py.Server.sim_interface import JHG_simulator
import matplotlib.pyplot as plt
from collections import Counter
from Code.GeneSimulation_py.Client.PyqtComponents.MainWindow import MainWindow

# ok now I need to make it play an actual round of JHG here in the sim so I can test the influence matrix. This is annoying.


if __name__ == "__main__":
    # pure bot sim
    sim = Social_Choice_Sim(11, 3, 0, 3)  # starts the social choice sim, call it whatever you want
    results = {}
    num_rounds = 1000
    for i in range(11): # total_players
        results[i] = [] # just throw in all the utilites

    for i in range(num_rounds): # just a ridicuously large number

        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.
        bot_votes = sim.get_votes() # where da magic happens

        total_votes = len(bot_votes)
        winning_vote_count = Counter(bot_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(bot_votes.values()).most_common(1)[0][0]
        probs = sim.get_probabilities()
        ## Put this back in when you are ready to deal with humans again.
        # all_votes = {**bot_votes, **player_votes}
        # total_votes = len(all_votes)
        # winning_vote_count = Counter(all_votes.values()).most_common(1)[0][1]
        # winning_vote = Counter(all_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > total_votes // 2):
            winning_vote = -1

        for i in range(total_votes):
            results[i].append(current_options_matrix[i][winning_vote])

    print("here were the resuts ", results)
        #print("This was the current options matrix \n", current_options_matrix, "\n this were the probabilities \n", probs, " \n these were the actual votes \n", bot_votes, " and here was the winning vote ", winning_vote)
    # Number of rounds (assuming all bots have the same number of rounds)
    num_rounds = len(next(iter(results.values())))  # length of the list of scores for a single bot
    sums_per_round = {}
    for bot in results:
        sums_per_round[bot] = []
        current_sum = 0
        for i, new_sum in enumerate(results[bot]):
            current_sum += new_sum
            sums_per_round[bot].append(current_sum)
    print("This is what sums per round looks like ", sums_per_round)


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

    plt.text(0.95, 0.95, f'Avg Increase: {total_average_increase:.2f}',
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