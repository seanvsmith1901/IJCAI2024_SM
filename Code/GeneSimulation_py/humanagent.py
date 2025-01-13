from baseagent import AbstractAgent
from os.path import exists

import numpy as np
import os
import time

class HumanAgent(AbstractAgent):

    def __init__(self):
        super().__init__()
        self.whoami = "Human"
        os.system("del ../State/HumanAllocations.txt")
        os.system("del ../State/visualTraits.txt")
        self.gameParams = {}


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams


    def play_round(self, player_idx, round_num, received, popularities, influence, extra_data):
        numPlayers = len(received)

        while True:
            
            if exists("../State/HumanAllocations.txt"):
                input = open("../State/HumanAllocations.txt", "r")
                r = int(input.readline())
                if r == round_num:
                    allocations = np.zeros(len(popularities), dtype=int)
                    for i in range(0, numPlayers):
                        allocations[i] = int(input.readline())

                    return allocations
                else:
                    input.close()
                    time.sleep(0.1)
            else:
                # human allocations not found
                time.sleep(0.1)
