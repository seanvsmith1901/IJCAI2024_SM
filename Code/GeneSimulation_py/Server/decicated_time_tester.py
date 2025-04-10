# just a small testbed to make sure that all the math was mathing. it is now all mathing the way that I want it to.
import time

from Code.GeneSimulation_py.Server.social_choice_sim import Social_Choice_Sim
import matplotlib.pyplot as plt
from collections import Counter


# ok now I need to make it play an actual round of JHG here in the sim so I can test the influence matrix. This is annoying.
if __name__ == "__main__":
    # pure bot sim
    sim = Social_Choice_Sim(15, 3, 0, 3)  # starts the social choice sim, call it whatever you want
    results = {}

    num_rounds = 10
    average_time = []
    for i in range(num_rounds):
        sim.start_round() # creates the current current options matrix, makes da player nodes, sets up causes, etc.
        current_options_matrix = sim.get_current_options_matrix() # need this for JHG sim and bot votes.
        start_time = time.time()
        bot_votes = sim.get_votes() # where da magic happens
        end_time = time.time()
        total_time = end_time - start_time
        average_time.append(total_time)
        print('this was the total time ', total_time)

    total_average_time = sum(average_time)/len(average_time)
    print('this was the total average time ', total_average_time)
