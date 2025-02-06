# just a small testbed to make sure that all the math was mathing. it is now all mathing the way that I want it to.


from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
from Code.GeneSimulation_py.Server.sim_interface import JHG_simulator
import matplotlib.pyplot as plt
from collections import Counter

# ok now I need to make it play an actual round of JHG here in the sim so I can test the influence matrix. This is annoying.


if __name__ == "__main__":
    # aight let me give you the breakdown on this code.

    sim = Social_Choice_Sim(11, 3) # starts the social choice sim, call it whatever you want
    jhg_sim = JHG_simulator(0, 11) # already done in game_server, so you're chillin
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

    bot_votes = jhg_sim.get_bot_votes(current_options_matrix) # you will need to do this in gameserver.
    # IN GAMESERVER, YOU WILL NEED TO GRAB THE VOTES FROM THE BOTS FROM THE JHG SIM - THAT FUNCTIONALITY DOESN'T EXIST IN SC.
    player_votes = {"9": 1, "10": 1} # made up votes --> get these from client input.

    # you can copy and paste these 3 lines directly into gameserver and they will do what you think they do.
    all_votes = bot_votes | player_votes # you can copy and paste this directly into gameserver. this and the next line.
    curr_round = 0
    sim.add_votes(curr_round, all_votes)
    winning_vote = Counter(all_votes.values()).most_common(1)[0][0]
    sim.apply_vote(winning_vote) # once again needs to be done from gameserver, as that is where winning vote is consolidated.
    for i in range(10):
        current_popularity = jhg_sim.execute_round({}, 0)  # make the bots play a round against eachother
        current_allocations = jhg_sim.get_T() # want to be able to see what moves were actually made.
        print("here were the allocations \n", current_allocations)
        new_relations = jhg_sim.get_influence()
        readable_relations = new_relations.tolist()
        return_values = sim.calculate_relation_strength(new_relations)
        print('here are the return values, \n', return_values)