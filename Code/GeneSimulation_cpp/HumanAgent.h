#ifndef HUMANAGENT_H
#define HUMANAGENT_H

#include <iostream>
#include <string>
#include <fstream>
#include <unistd.h>

#include "AbstractAgent.h"

class HumanAgent : public AbstractAgent {
public:
    HumanAgent() {
        whoami = "human";
        system("del ../State/HumanAllocations.txt");
        system("del ../State/visualTraits.txt");
    }

    ~HumanAgent() {
        // cout << "calling HumanAgent destructor" << endl;
    }

    void playRound(int numPlayers, int numTokens, int playerIdx, int roundNum, double *received, double *popularities, double **influence, int *allocations) {
        for (int i = 0; i < numPlayers; i++)
            allocations[i] = 0;

        while (true) {
            ifstream input("../State/HumanAllocations.txt");
            if (input) {
                std::string line;
                getline(input, line);
                int r = stoi(line);
                if (r == roundNum) {
                    for (int i = 0; i < numPlayers; i++) {
                        getline(input, line);
                        allocations[i] = stoi(line);
                    }
                    input.close();

                    break;
                }
                else {
                    input.close();
                    usleep(100000);
                }
            }
            else {
                usleep(100000);
            }
        }
    }

    void postContract(int playerIdx) {}

};

#endif