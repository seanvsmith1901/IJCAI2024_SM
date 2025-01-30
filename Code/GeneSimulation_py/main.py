# sim_interface.py in Server is basically a stripped down version of this that we will be using for our own nefarious purposes.


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
import time

np.set_printoptions(precision=2, suppress=True)


def play_game(agents, rounds, gener, gamer, initial_pops, poverty_line, forcedRandom):

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
        "alpha": alpha_min, #np.random.uniform(alpha_min, alpha_max), 
        "beta": beta_min, #np.random.uniform(beta_min, beta_max), 
        "keep": keep_min, #np.random.uniform(keep_min, keep_max), 
        "give": give_min, #np.random.uniform(give_min, give_max), 
        "steal": steal_min, #np.random.uniform(steal_min, steal_max), 
        "poverty_line": poverty_line,
        "base_popularity": np.array(initial_pops)
        # "base_popularity": np.array([*[base_pop]*(num_players)])
        # "base_popularity": np.array(random.sample(range(1, 200), num_players))
        
    }        

    # # assign the agents to groups
    # agentsPerGroup = num_players / numGroups
    # theGroups = {}
    # for i in range(0, numGroups):
    #     theGroups[i] = set()
    # if hasGovment == True:
    #     theGroups[-1] = {0}
    #     for i in range(1, num_players):
    #         theGroups[int(i / agentsPerGroup)].add(i)
    # else:
    #     for i in range(0, num_players):
    #         theGroups[int(i / agentsPerGroup)].add(i)
        
    # print(theGroups)

    # tell the agents the game params
    # visualTraits = np.zeros(len(agents), dtype=float)
    # if specVs == True:
    #     fp = open("ScenarioIndicator/visualTraits.txt", "r")
    #     if fp.closed:
    #         print(fnombre + " not found")
    #         quit()

    #     i = 0
    #     for line in fp:
    #         if isinstance(agents[i], GeneAgent3):
    #             agents[i].genes_long["visualTrait"] = int(line)
    #         visualTraits[i] = int(line)
    #         i = i+1

    #     fp.close()
    # else:
    #     for i in range(0,len(agents)):
    #         if isinstance(agents[i], GeneAgent3):
    #             visualTraits[i] = agents[i].genes_long["visualTrait"]
    #         elif isinstance(agents[i], HumanAgent):
    #             visualTraits[i] = np.random.randint(0,101)
    #             print('human with ' + str(visualTraits[i]))
    #         else:
    #             visualTraits[i] = 99999

    # TODO: rm contracts

    for a in agents:
        a.setGameParams(game_params, forcedRandom)
        # TODO: post contract


    humanInd = findHumanPlayer(players)
    # print("Human is player " + str(humanInd))

    sim = GameSimulator(game_params)
    for r in range(rounds):
        if humanInd >= 0:
            recordState(r, sim, humanInd, False)     # This records data so that the java human player can interact with this engine
        
        # print("\nRound: " + str(r))
        T = np.eye(num_players) * tkns
        T_prev = sim.get_transaction()




        # use this under the sim.get_player inputs to populate T. The problem! is that I have to distinguish between human and non human players.
        # for i, plyr in enumerate(players): # DON"T RUN THIS UNITL YOU KNOW THAT YOU HAVE EVERYONE
        #     T[i] = plyr.play_round(
        #                 i,
        #                 r,
        #                 T_prev[:, i],
        #                 sim.get_popularity(),
        #                 sim.get_influence(),
        #                 sim.get_extra_data(i)
        #             )

        sim.play_round(T)




        if r == 0:
            runningTotal = np.copy(sim.get_popularity())
        else:
            # runningTotal = (0.8 * runningTotal) + (0.2 * sim.get_popularity())
            runningTotal += sim.get_popularity()

    print("P:\n" + str(sim.engine.P))                

    if humanInd >= 0:
        recordState(rounds, sim, humanInd, True)     # This records data so that the java human player can interact with this engine

    fnombre = "../Results/theGameLogs/log_" + str(gener) + "_" + str(gamer) + ".csv"
    sim.save(fnombre)

    return sim.get_popularity(), runningTotal / rounds

def recordState(round_num, sim, humanPlayerInd, gameOver):
    numPlayers = len(sim.get_popularity())

    output = open("../State/state.tmp", "w")

    # print out the time
    if not gameOver:
        output.write("inprogress\n")
    else:
        output.write("fin\n")       
    output.write(str(numPlayers) + "\n")
    output.write(str(humanPlayerInd) + "\n")
    output.write(str(round_num) + "\n")

    # print out the popularities
    for i in range(0, numPlayers):
        for r in range(0, round_num+1):
            output.write(str(sim.engine.get_popularity(r)[i]) + " ")
        output.write("\n")

    # print out the last round's token allocations
    T_prev = sim.get_transaction()
    for i in range(0, numPlayers):
        for j in range(0, numPlayers):
            # print(int((T_prev[i, j] * numPlayers * 2) + 0.01))
            # output.write(str(int(T_prev[i, j] * numPlayers * 2)) + " ")
            if T_prev[i, j] < 0:
                output.write(str(int((T_prev[i, j] * int(numPlayers*2)) - 0.01)) + " ")
            else:
                output.write(str(int((T_prev[i, j] * int(numPlayers*2)) + 0.01)) + " ")
        output.write("\n")


    # print out all of the previous tornadoValues
    for t in range(0, round_num+1):
        influence = sim.engine.get_influence(t)
        for i in range(0, numPlayers):
            for j in range(0, numPlayers):
                output.write(str(influence[j, i]) + " ")
            output.write("\n")

    output.close()

    os.system("move ../State/state.tmp ../State/state.txt")

def findHumanPlayer(players):
    numPlayers = len(players)
    for i in range(0, numPlayers):
        if players[i].whoami == "Human":
            return i

    return -1

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

def loadPopulationFromScenario():
    fp = open("ScenarioIndicator/theGenotypes.txt", "r")
    if fp.closed:
        print(fnombre + " not found")
        quit()

    thePopulation = []
    for line in fp:
        thePopulation.append(GeneAgent3(line))

    fp.close()

    # now overwrite their visual traits
    fp = open("ScenarioIndicator/visualTraits.txt", "r")
    if fp.closed:
        print(fnombre + " not found")
        quit()

    i = 0
    for line in fp:
        thePopulation[i].genes_long["visualTrait"] = int(line)
        i = i+1

    fp.close()

    return thePopulation


def selectByWeightedFitness(thePopulation, popSize, numPlayers):
    mag = 0.0
    for i in range(0, popSize):
        mag = mag + (thePopulation[i].absoluteFitness * (thePopulation[i].relativeFitness / numPlayers))

    num = np.random.uniform(0, 1.0)
    sum = 0.0
    for i in range(0, popSize):
        sum = sum + (thePopulation[i].absoluteFitness * (thePopulation[i].relativeFitness / numPlayers))

        if (num <= sum):
            return i

    print("didn't select; num = " + str(num) + "; sum = " + str(sum) + "\n")
    
    return (popSize-1)


def selectByFitness(thePopulation, popSize, _rank):
    mag = 0.0
    for i in range(0, popSize):
        # print(str(thePopulation[i].relativeFitness) + " " + str(thePopulation[i].absoluteFitness))
        if (_rank):
            mag = mag + thePopulation[i].relativeFitness
        else:
            mag = mag + thePopulation[i].absoluteFitness

    num = np.random.uniform(0, 1.0)

    sum = 0.0
    for i in range(0, popSize):
        if (_rank):
            sum = sum + (thePopulation[i].relativeFitness / mag)
        else:
            sum = sum + (thePopulation[i].absoluteFitness / mag)

        if (num <= sum):
            return i

    print("didn't select; num = " + str(num) + "; sum = " + str(sum) + "\n")
    
    return (popSize-1)


# def evolvePopulation(thePopulation, popSize):
#     newPopulation = []

#     # generate newPopulation
#     for i in range(0,popSize):
#         # select
#         if i < (popSize / 2):
#             ind = selectByFitness(thePopulation, popSize, True)
#         else:
#             ind = selectByFitness(thePopulation, popSize, False)

#         newPopulation.append(GeneAgent3(thePopulation[ind].getString()))

#         # mutate
#         newPopulation[i].mutate(0.10);  # mutate probability is past as a parameter

#         # splice
#         numb = np.random.uniform(0, 1.0)
#         if (numb <= 0.075):   # splice with probability 0.075
#             ind = selectByFitness(thePopulation, popSize, True)
#             newPopulation[i].splice(thePopulation[ind])

#     return newPopulation


def selectByFitnessObserved(observedPlayInd, _rank):
    mag = 0.0
    for i in range(0, len(observedPlayInd)):
        if (_rank):
            mag = mag + observedPlayInd[i][1]
        else:
            mag = mag + observedPlayInd[i][2]

    num = np.random.uniform(0, 1.0)

    sum = 0.0
    for i in range(0, len(observedPlayInd)):
        if (_rank):
            sum = sum + (observedPlayInd[i][1] / mag)
        else:
            sum = sum + (observedPlayInd[i][2] / mag)

        if (num <= sum):
            return observedPlayInd[i][0]

    print("didn't select; num = " + str(num) + "; sum = " + str(sum) + "\n")
    
    return observedPlayInd[len(observedPlayInd)-1][0]


def evolvePopulationPairs(theGenePools, popSize):
    newGenePools = []

    # generate newGenePools
    for pool in range(0, len(theGenePools)):
        newPopulation = []
        for i in range(0,popSize):
            # select 2 agents from theGenePools[pool]
            if i < (popSize / 5):
                ind1 = selectByFitness(theGenePools[pool], popSize, True)
                ind2 = selectByFitness(theGenePools[pool], popSize, False)
            else:
                ind1 = selectByFitness(theGenePools[pool], popSize, False)
                ind2 = selectByFitness(theGenePools[pool], popSize, False)
            # print(str(ind1) + ": " + str(thePopulation[ind1].popFitness) + ", " + str(thePopulation[ind1].rankFitness) + ";     " + str(ind2) + ": " + str(thePopulation[ind2].popFitness) + ", " + str(thePopulation[ind2].rankFitness))

            words1 = theGenePools[pool][ind1].getString().split("_")
            words2 = theGenePools[pool][ind2].getString().split("_")

            genstr = "genes_"
            numGenes = len(theGenePools[pool][0].genes_long)
            for i in range(1,numGenes+1):
                # print(i)
                # ind = ind1
                if random.randint(0,1) == 0:
                    if i == numGenes:
                        genstr += mutateIt(words1[i])
                    else:
                        genstr += mutateIt(words1[i] + "_")
                else:
                    if i == numGenes:
                        genstr += mutateIt(words2[i])
                    else:
                        genstr += mutateIt(words2[i] + "_")

            # print()
            # print("p1: " + thePopulation[ind1].getString())
            # print("p2: " + thePopulation[ind2].getString())
            # print("ch: " + genstr)

            newPopulation.append(GeneAgent3(genstr))

        newGenePools.append(newPopulation)

    return newGenePools


def mutateIt(gene):
    v = np.random.randint(0,100) 
    if v >= 15:
        return gene
    elif v < 3:
        g = np.random.randint(0,101)
        # print("big randm: " + gene + " to " + str(g))
        return str(g)
    else:
        g = int(gene) + np.random.randint(-5,6)
        # print("randomize: " + gene + " to " + str(g))
        if g < 0:
            g = 0
        elif g > 100:
            g = 100
        return str(g)
    

def evolvePopulationObserved(thePopulation, observedPlay, popSize):
    newPopulation = []

    percentSwitch = 30

    # generate newPopulation
    for i in range(0,popSize):
        # select
        if (len(observedPlay[i]) > 0) and (np.random.randint(0,100) < percentSwitch):
            if np.random.randint(0,2) == 0:
                ind = selectByFitnessObserved(observedPlay[i], True)
            else:
                ind = selectByFitnessObserved(observedPlay[i], False)

            # print("change player " + str(i) + " to player " + str(ind))

            newPopulation.append(GeneAgent3(thePopulation[ind].getString()))

            # mutate
            newPopulation[i].mutate(0.10);  # mutate probability 0.10

            # splice
            numb = np.random.uniform(0, 1.0)
            if (numb <= 0.075):   # splice with probability 0.075
                ind = selectByFitnessObserved(observedPlay[i], True)
                newPopulation[i].splice(thePopulation[ind])

        else:
            newPopulation.append(GeneAgent3(thePopulation[i].getString()))

    return newPopulation


def writeGenerationResults(theGenePools, popSize, gen, agentsPerGame):
    for pool in range(0, len(theGenePools)):
        for p in theGenePools[pool]:
            if (p.count > 0):
                p.relativeFitness = p.relativeFitness / p.count
                p.absoluteFitness = p.absoluteFitness / p.count
            else:
                p.relativeFitness = 0.0
                p.absoluteFitness = 0.0

        theGenePools[pool].sort(key=lambda x: x.absoluteFitness, reverse=True)
        # thePopulation.sort(key=lambda x: x.rankFitness, reverse=True)

        fnombre = "../Results/theGenerations/" + str(pool) + "/gen_" + str(gen) + ".csv"
        output = open(fnombre, "w")

        sm = 0.0
        for i in range(0, popSize):
            sm = sm + theGenePools[pool][i].absoluteFitness
            output.write(theGenePools[pool][i].getString() + "," + str(theGenePools[pool][i].count) + "," + str(f'{theGenePools[pool][i].relativeFitness:.2f}') + "," + str(f'{theGenePools[pool][i].absoluteFitness:.2f}') + "\n")

        output.close()

        print("Average fitness in generation " + str(gen) + " of pool " + str(pool) + ": " + str(sm / popSize))


def writeGenerationResultsSorted(thePopulation, popSize, gen, agentsPerGame):
    for p in thePopulation:
        if (p.count > 0):
            p.relativeFitness = p.relativeFitness / p.count
            p.absoluteFitness = p.absoluteFitness / p.count
        else:
            p.relativeFitness = 0.0
            p.absoluteFitness = 0.0

    thePopulation.sort(key=lambda x: x.absoluteFitness, reverse=True)
    thePopulation.sort(key=lambda x: x.relativeFitness, reverse=True)

    fnombre = "../Results/theGenerations/gen_" + str(gen) + ".csv"
    output = open(fnombre, "w")

    sum = 0.0
    for i in range(0, popSize):
        sum = sum + thePopulation[i].absoluteFitness
        output.write(thePopulation[i].getString() + "," + str(thePopulation[i].count) + "," + str(f'{thePopulation[i].relativeFitness:.2f}') + "," + str(f'{thePopulation[i].absoluteFitness:.2f}') + "\n")

    output.close()

    print("Average population fitness of generation " + str(gen) + ": " + str(sum / popSize))

# def readScript(scriptName):
#     fnombre = "scripts/" + scriptName + ".txt"
#     fp = open(fnombre)

#     numAgents = int(fp.readline())
#     numRounds = int(fp.readline())

#     # thePlan = []
    
#     for r in range(0, numRounds):
#         # round = []
#         fp.readline()
#         for i in range(0, numAgents):
#             words = fp.readline().split(" ")
#             map_object = map(int, words)
#             list_of_integers = list(map_object)
#             if i == 0:
#                 round = [list_of_integers]
#             else:
#                 round.append(list_of_integers)
#         if r == 0:
#             thePlan = [round]
#         else:
#             thePlan.append(round)

#     fp.close()

#     return numAgents, numRounds, thePlan


def define_initial_pops(init_pop, num_players):
    base_pop = 100

    # assign the initial popularities
    if init_pop == "equal":
        initial_pops = [*[base_pop]*(num_players)]
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
            initial_pops[i] = 1.0 / (pow(i+1, 0.7))
        random.shuffle(initial_pops)
    elif init_pop == "highlow":
        initial_pops = random.sample(range(1, 51), num_players)
        for i in range(0,num_players / 2):
            initial_pops[i] += 150
        random.shuffle(initial_pops)
    else:
        print("don't understand init_pop " + str(init_pop) + " so just going with equal")
        initial_pops = [*[base_pop]*(num_players)]

    # normalize initial_pops so average popularity across all agents is 100
    tot_start_pop = base_pop * num_players
    sm = 1.0 * sum(initial_pops)
    for i in range(0, num_players):
        initial_pops[i] /= sm
        initial_pops[i] *= tot_start_pop

    return np.array(initial_pops)


# python3 main.py play [generationFolder] [popSize] [numGeneCopies] [gen] [numAgents] [numRounds] [best_agents/rnd_agents] [init_pop] [poverty_line] [deterministic/nondeterministic] [config]
if __name__ == '__main__':
    if len(sys.argv) < 10:
        print("Not enough argument")
        sys.exit(1)

    if sys.argv[1] == "play":
        if len(sys.argv) != 13:
            print("Not enough argument")
            sys.exit(1)

        theFolder = sys.argv[2]
        popSize = int(sys.argv[3])
        num_gene_copies = int(sys.argv[4])
        theGen = int(sys.argv[5])
        numAgents = int(sys.argv[6])
        numRounds = int(sys.argv[7])

        if sys.argv[8] == "best_agents":
            player_idxs = list(np.arange(0,numAgents))
        elif sys.argv[8] == "rnd_agents":
            # player_idxs = np.random.choice(np.arange(len(theGenePools[0])-1), size=numAgents, replace=False)
            player_idxs = np.random.choice(np.arange(popSize), size=numAgents, replace=False)
        else:
            print("don't understand agentSelection: " + sys.argv[8] + "; Must be best_agents or rnd_agents")
            sys.exit()           

        poverty_line = float(sys.argv[10])

        forcedRandom = False
        if sys.argv[11] == "deterministic":
            forcedRandom = True

        fnombre = "ScenarioIndicator/" + sys.argv[12] + ".txt"
        print(fnombre)
        configuredPlayers = []
        try:
            fp = open(fnombre, 'r')
            Lines = fp.readlines()
            for line in Lines:
                # print("<" + line + ">")
                if line[0:5] == "Human":
                    # print('adding a human player')
                    configuredPlayers.append(HumanAgent())
                elif line[0:8] == "Assassin":
                    # print('adding an assassin')
                    configuredPlayers.append(AssassinAgent())
            fp.close()

        except IOError:
            print('config file not found: ' + str(fnombre))


        print("num configured players: " + str(len(configuredPlayers)))

        theGenePools = loadPopulationFromFile(popSize, theFolder, theGen, num_gene_copies)

        for i in range(0, len(configuredPlayers)):
            player_idxs = np.append(player_idxs, popSize + i)

        initial_pops = define_initial_pops(sys.argv[9], len(player_idxs))

        # print(player_idxs)
        # print(initial_pops)

        plyrs = []
        for i in range(0, len(player_idxs)):
            if player_idxs[i] >= popSize:
                plyrs.append(configuredPlayers[player_idxs[i] - popSize])
            else:
                plyrs.append(theGenePools[player_idxs[i]])
        players = np.array(plyrs)
        # print(len(players))

        result, avePop = play_game(list(players), numRounds, 1000, 1000, initial_pops, poverty_line, forcedRandom)
        print("endPop: " + str(result))
        print("avePop: " + str(avePop))
        print("relPop: " + str(avePop / sum(avePop)))

    # The "evolve" portion of this code is not up-to-date with recent changes (use the C++ to evolve parameter values)
    # elif sys.argv[1] == "evolve":             
    #     if len(sys.argv) != 12:
    #         print("Not enough argument for <evolve>")
    #         sys.exit(1)
       
    #     theFolder = sys.argv[2]
    #     popSize = int(sys.argv[3])
    #     num_gene_pools = int(sys.argv[4])
    #     startIndex = int(sys.argv[5])
    #     numGens = int(sys.argv[6])
    #     gamesPerGen = int(sys.argv[7])
    #     agentsPerGame = int(sys.argv[8])
    #     roundsPerGame = int(sys.argv[9])
    #     poverty_line = float(sys.argv[10])
    #     addGovment = False
    #     if sys.argv[11] == "addGovment":
    #         addGovment = True
        
    #     if num_gene_pools == 1:
    #         pool_delimiters = [99999]
    #     elif num_gene_pools == 2:
    #         pool_delimiters = [100, 99999]
    #     elif num_gene_pools == 3:
    #         pool_delimiters = [75, 125, 99999]
    #     else:
    #         print("no pool_delimiters for " + str(num_gene_pools) + " agent populations")
    #         sys.exit()

    #     if startIndex != 0:
    #         # still need to fix this
    #         theGenePools = loadPopulationFromFile(popSize, theFolder, startIndex-1, num_gene_pools)
    #         theGenePools = evolvePopulationPairs(theGenePools, popSize)
    #     else:
    #         # just create 3 random agent pools
    #         # print("creating random agents")
    #         theGenePools = []
    #         for i in range(0, num_gene_pools):
    #             theGenePools.append([ GeneAgent3("") for i in range(popSize) ])
        
    #     for g in range(startIndex, numGens):    # let's do this for each generation

    #         for p in range(0, gamesPerGen):     # let's do this for each game in each generation
    #             print(str(g) + "-" + str(p))

    #             # decide the initial popularity
    #             possible_dist = ["equal", "random", "step", "power", "highlow"]
    #             sel = np.random.randint(0, len(possible_dist))
    #             initial_pops = define_initial_pops(possible_dist[sel], agentsPerGame)
    #             # print(str(possible_dist[sel]) + ": " + str(initial_pops))
    #             print("i_pops: " + str(initial_pops))
    #             s = sum(initial_pops)
    #             init_relPop = np.zeros(agentsPerGame, dtype=float)
    #             for i in range(0, agentsPerGame):
    #                 init_relPop[i] = initial_pops[i] / s
                
    #             # assign each player to a pool based on their assigned initial popularity
    #             pool_assignments = np.zeros(agentsPerGame, dtype=int)
    #             for i in range(0, agentsPerGame):
    #                 pool_assignments[i] = -1
    #             for i in range(0, agentsPerGame):
    #                 for j in range(0, len(pool_delimiters)):
    #                     if initial_pops[i] < pool_delimiters[j]:
    #                         pool_assignments[i] = j
    #                         break
    #             # print("pool assignments: " + str(pool_assignments))

    #             # time to pick from the gene pools
    #             player_idxs = np.random.choice(np.arange(len(theGenePools[0])), size=agentsPerGame, replace=False)
    #             # print("player_idxs: " + str(player_idxs))
    #             # players = np.asarray(thePopulation)[player_idxs]
    #             plyrs = []
    #             for i in range(0, agentsPerGame):
    #                 plyrs.append(theGenePools[pool_assignments[i]][player_idxs[i]])
    #             players = np.array(plyrs)

    #             f = open("../Results/thePlayers/players_" + str(g) + "_" + str(p) + ".txt", "w")
    #             j = 0
    #             for i in player_idxs:
    #                 f.write(str(pool_assignments[j]) + " " + str(i) + " " + initial_pops[j] + "\n")
    #                 j += 1
    #             f.close()

    #             endPop, avePop = play_game(list(players), roundsPerGame, addGovment, g, p, False, initial_pops, poverty_line, False)

    #             relPop = avePop / sum(avePop)

    #             print(player_idxs)
    #             print(avePop)
    #             print(relPop)
    #             print(sum(avePop) / agentsPerGame)
    #             print()

    #             # update the fitness of the agents that played in the game
    #             for i in range(0, agentsPerGame):
    #                 if theGenePools[pool_assignments[i]][player_idxs[i]].played_genes == True:
    #                     theGenePools[pool_assignments[i]][player_idxs[i]].count = theGenePools[pool_assignments[i]][player_idxs[i]].count + 1
    #                     theGenePools[pool_assignments[i]][player_idxs[i]].absoluteFitness += ((avePop[i] + endPop[i]) / 2.0) / initial_pops[i]
    #                     theGenePools[pool_assignments[i]][player_idxs[i]].relativeFitness += relPop[i] / init_relPop[i]
            
    #         writeGenerationResults(theGenePools, popSize, g, agentsPerGame)
    #         theGenePools = evolvePopulationPairs(theGenePools, popSize)
    else:
        print("Argument format invalid.  Exiting")

