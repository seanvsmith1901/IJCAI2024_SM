# refer to "main.py" in ../ for more information
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Code.GeneSimulation_py.geneagent3 import GeneAgent3
from Code.GeneSimulation_py.humanagent import HumanAgent
from Code.GeneSimulation_py.simulator import GameSimulator

# from scriptagent import ScriptAgent



import numpy as np
import random

np.set_printoptions(precision=2, suppress=True)

class JHG_simulator():
    def __init__(self, num_human_players, num_players):
        self.num_players = num_players
        self.sim = None
        self.players = None
        self.start_game(num_human_players, num_players)
        self.T = None



    def start_game(self, num_human_players, num_players):


        init_pop = "equal"

        numAgents = num_players - num_human_players
        configured_players = []
        popSize = 60  # ??? I think? based on the command line arguemnts
        player_idxs = list(np.arange(0, numAgents))  # where numAgents is the number of actual agents, not players.


        for _ in range(num_human_players):
            configured_players.append(HumanAgent())


        for i in range(0, len(configured_players)):
            player_idxs = np.append(player_idxs, popSize + i)


        theFolder = "../../ResultsStudy"
        theGen = 199
        num_gene_copies = 3

        theGenePools = loadPopulationFromFile(popSize, theFolder, theGen, num_gene_copies)


        plyrs = []
        for i in range(0, len(player_idxs)):
            if player_idxs[i] >= popSize:
                plyrs.append(configured_players[player_idxs[i] - popSize])
            else:
                plyrs.append(theGenePools[player_idxs[i]])
        players = np.array(plyrs)
        self.players = players
        agents = list(players)

        initial_pops = self.define_initial_pops(init_pop, len(player_idxs))
        poverty_line = 0
        forcedRandom = False


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

        self.sim = GameSimulator(
            game_params)  # sets up our sim object - might need to make this global so we can grab it wherever we need it.


    def execute_round(self, allocations, round):  # all of the player allocations will get passed in here
        # print("\nRound: " + str(r))
        # build allocations here.

        tkns = self.num_players
        T = np.eye(self.num_players) * tkns
        T_prev = self.sim.get_transaction()
        # print("these are the allocations ", allocations)
        # use this under the sim.get_player inputs to populate T. The problem! is that I have to distinguish between human and non human players.
        for i, plyr in enumerate(self.players):  # DON"T RUN THIS UNITL YOU KNOW THAT YOU HAVE EVERYONE
            if plyr.getType() == "Human":
                T[i] = allocations[str(i)] # ok so that will have to be adjusted, depends on how we are managing client ids. i'll cook up something better later.
            else:
                T[i] = plyr.play_round(
                    i,  # player index
                    round,  # round
                    T_prev[:, i],  # received
                    self.sim.get_popularity(),  # popularity
                    self.sim.get_influence(),  # influence
                    self.sim.get_extra_data(i)  # could NOT tell you waht this is.
                )

        self.sim.play_round(T)
        self.T = T
        return self.sim.get_popularity() # I think this is all we need? maybe?

    def define_initial_pops(self, init_pop, num_players):
        base_pop = 100

        # assign the initial popularities
        if init_pop == "equal":
            initial_pops = [*[base_pop] * (num_players)]
        elif init_pop == "random":
            initial_pops = random.sample(range(1, 200), num_players)
        elif init_pop == "step":
            initial_pops = np.zeros(num_players, dtype=float)
            for i in range(0, num_players):
                initial_pops[i] = i + 1.0
            random.shuffle(initial_pops)
        elif init_pop == "power":
            initial_pops = np.zeros(num_players, dtype=float)
            for i in range(0, num_players):
                initial_pops[i] = 1.0 / (pow(i + 1, 0.7))
            random.shuffle(initial_pops)
        elif init_pop == "highlow":
            initial_pops = random.sample(range(1, 51), num_players)
            for i in range(0, num_players / 2):
                initial_pops[i] += 150
            random.shuffle(initial_pops)
        else:
            print("don't understand init_pop " + str(init_pop) + " so just going with equal")
            initial_pops = [*[base_pop] * (num_players)]

        # normalize initial_pops so average popularity across all agents is 100
        tot_start_pop = base_pop * num_players
        sm = 1.0 * sum(initial_pops)
        for i in range(0, num_players):
            initial_pops[i] /= sm
            initial_pops[i] *= tot_start_pop

        return np.array(initial_pops)

    def get_T(self):
        return self.T

    def get_bot_votes(self, current_options_matrix):
        votes = {}
        for i, player in enumerate(self.players):
            if player.getType() != "Human":
                votes[str(i)] = player.getVote(current_options_matrix, i)
        return votes

def loadPopulationFromFile(popSize, generationFolder, startIndex, num_gene_pools):
    fnombre = generationFolder + "/gen_" + str(startIndex) + ".csv"
    print(fnombre)
    fp = open(fnombre, "r")
    if fp.closed:
        print(fnombre + " not found")
        quit()

    thePopulation = []

    for i in range(0,popSize):
        line = fp.readline()
        words = line.split(",")

        thePopulation.append(GeneAgent3(words[0], num_gene_pools))
        thePopulation[i].count = float(words[1])
        thePopulation[i].relativeFitness = float(words[2])
        thePopulation[i].absoluteFitness = float(words[3])

    fp.close()

    return thePopulation

