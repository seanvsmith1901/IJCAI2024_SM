# just a small testbed to make sure that all the math was mathing. it is now all mathing the way that I want it to.


from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
from Code.GeneSimulation_py.Server.sim_interface import JHG_simulator
import matplotlib.pyplot as plt
from collections import Counter

# ok now I need to make it play an actual round of JHG here in the sim so I can test the influence matrix. This is annoying.


if __name__ == "__main__":
    # aight let me give you the breakdown on this code.

    # we need the total number of players, the number of causes (should never be different than 3), the total numbe4r of players and the type of bot.
    # is the paretro optimal, I'll add more as we go. 0 will proabbly be greedy, etc.

    sim = Social_Choice_Sim(3, 3, 0, 1) # starts the social choice sim, call it whatever you want
    jhg_sim = JHG_simulator(0, 3) # already done in game_server, so you're chillin
    sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
    current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.



    # print("this is the current player nodes, \n", player_nodes)  # funny graphing stuff if you so desire. shows how to access causes and players for graphing utilities.
    # x = []
    # y = []
    # for cause in causes:
    #     x.append(cause.get_x())


    #     y.append(cause.get_y())
    #
    # for player in player_nodes:
    #     x.append(player.get_x())
    #     y.append(player.get_y())

    # plt.plot(x,y,'o')
    # plt.show()

    bot_votes = sim.get_votes() # you will need to do this in gameserver.
    # IN GAMESERVER, YOU WILL NEED TO GRAB THE VOTES FROM THE BOTS FROM THE JHG SIM - THAT FUNCTIONALITY DOESN'T EXIST IN SC.
    #player_votes = {"9": 1, "10": 1} # made up votes --> get these from client input.

    # right now we are workign with puer bots
    total_votes = len(bot_votes)
    winning_vote_count = Counter(bot_votes.values()).most_common(1)[0][1]
    winning_vote = Counter(bot_votes.values()).most_common(1)[0][0]

    ## Put this back in when you are ready to deal with humans again.
    # all_votes = {**bot_votes, **player_votes}
    # total_votes = len(all_votes)
    # winning_vote_count = Counter(all_votes.values()).most_common(1)[0][1]
    # winning_vote = Counter(all_votes.values()).most_common(1)[0][0]

    if not (winning_vote_count > total_votes // 2):
        winning_vote = -1
    print("this was the winning vote! " , winning_vote)
    sim.apply_vote(winning_vote)  # once again needs to be done from gameserver, as that is where winning vote is consolidated.
