# just a small testbed to make sure that all the math was mathing. it is now all mathing the way that I want it to.


from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
from Code.GeneSimulation_py.Server.sim_interface import JHG_simulator
import matplotlib.pyplot as plt
from collections import Counter


if __name__ == "__main__":
    sim = Social_Choice_Sim(11, 3)
    jhg_sim = JHG_simulator(2, 11)
    current_options_matrix = sim.create_options_matrix()
    print("this is the current options matrix, \n", current_options_matrix)
    player_nodes = sim.create_player_nodes()
    causes = sim.get_causes()

    # print("this is the current player nodes, \n", player_nodes)
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

    bot_votes = jhg_sim.get_bot_votes(current_options_matrix)
    player_votes = {"9": 1, "10": 1}
    all_votes = bot_votes | player_votes
    winning_vote = Counter(all_votes.values()).most_common(1)[0][0]

    sim.apply_vote(winning_vote) # make sure that this is doing what we want it to do