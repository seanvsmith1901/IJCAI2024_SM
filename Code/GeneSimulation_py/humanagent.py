from baseagent import AbstractAgent
from os.path import exists

import numpy as np
import os
import platform # need to know if this is windows or linux (or mac)
import time

class HumanAgent(AbstractAgent):

    def __init__(self):
        super().__init__()
        self.whoami = "Human"
        if platform.system() == "Windows":
            print("Running on Windows...")

            # Define the files to be deleted
            human_allocations_file = "../State/HumanAllocations.txt"
            visual_traits_file = "../State/visualTraits.txt"

            # Attempt to delete HumanAllocations.txt
            if os.path.exists(human_allocations_file):
                try:
                    os.remove(human_allocations_file)
                    print("Deleted HumanAllocations.txt successfully.")
                except Exception as e:
                    print(f"Failed to delete HumanAllocations.txt: {e}")
            else:
                print("HumanAllocations.txt does not exist.")

            # Attempt to delete visualTraits.txt
            if os.path.exists(visual_traits_file):
                try:
                    os.remove(visual_traits_file)
                    print("Deleted visualTraits.txt successfully.")
                except Exception as e:
                    print(f"Failed to delete visualTraits.txt: {e}")
            else:
                print("visualTraits.txt does not exist.")
        else:
            print("running on linux or something ig")
            os.system("rm ../State/HumanAllocations.txt")
            os.system("rm ../State/visualTraits.txt")
        self.gameParams = {}


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams

    def getType(self):
        return self.whoami


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
