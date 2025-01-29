# refer to "main.py" in ../ for more information

from simulator import GameSimulator
from randomagent import RandomAgent
from geneagent3 import GeneAgent3
from humanagent import HumanAgent
from assassinagent import AssassinAgent
# from scriptagent import ScriptAgent
from govtagent import DummyGovtAgent



import numpy as np
import os
import sys
import random
sim = None # the simulator. have him as a global for now.
import time

np.set_printoptions(precision=2, suppress=True)

class Simulator():
    def __init__(self, num_human_players, num_players):
        # what we need to do is take in the number of human players and generate agents from there.
        self.sim = None # wait a minute, do I need this?
        # now we gotta figure out how to create the players
        # create the agents\
        # fetch i am putthing this off lets figure out how to create the agents. 
        # decide initial population (100 hard coded?)
        # create the poverty line (not sure what THAT should look like)
        # and i have no idea what forced random is supposed to be.
        start_game(agents, initial_pops, poverty_line, forcedRandom)



def start_game(agents, initial_pops, poverty_line, forcedRandom):
    global sim
    players = [
        *agents
    ]

    alpha_min, alpha_max = 0.20, 0.20
    beta_min, beta_max = 0.5, 1.0
    keep_min, keep_max = 0.95, 0.95
    give_min, give_max = 1.30, 1.30
    steal_min, steal_max = 1.6, 1.60

    num_players = len(players)
    base_pop = 100
    tkns = num_players

    game_params = {
        "num_players": num_players,
        "alpha": alpha_min,  # np.random.uniform(alpha_min, alpha_max),
        "beta": beta_min,  # np.random.uniform(beta_min, beta_max),
        "keep": keep_min,  # np.random.uniform(keep_min, keep_max),
        "give": give_min,  # np.random.uniform(give_min, give_max),
        "steal": steal_min,  # np.random.uniform(steal_min, steal_max),
        "poverty_line": poverty_line,
        "base_popularity": np.array(initial_pops)
        # "base_popularity": np.array([*[base_pop]*(num_players)])
        # "base_popularity": np.array(random.sample(range(1, 200), num_players))

    }

    for a in agents:  # sets the game params for all users.
        a.setGameParams(game_params, forcedRandom)

    sim = GameSimulator(
        game_params)  # sets up our sim object - might need to make this global so we can grab it wherever we need it.


def execute_round(allocations):  # all of the player allocations will get passed in here
    # print("\nRound: " + str(r))
    # build allocations here.

    T = np.eye(num_players) * tkns
    T_prev = sim.get_transaction()

    # basically this is where all of the magic needs to happen. Oh, just make a while loop that checks for all player input. return T when finished.

    # T = sim.get_player_inputs(T)

    # use this under the sim.get_player inputs to populate T. The problem! is that I have to distinguish between human and non human players.
    for i, plyr in enumerate(players):  # DON"T RUN THIS UNITL YOU KNOW THAT YOU HAVE EVERYONE
        T[i] = plyr.play_round(
            i,  # player index
            r,  # round
            T_prev[:, i],  # received
            sim.get_popularity(),  # popularity
            sim.get_influence(),  # influence
            sim.get_extra_data(i)  # could NOT tell you waht this is.
        )

    sim.play_round(T)



