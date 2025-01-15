#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cmath>

#include "AbstractAgent.h"
#include "GeneAgent.h"
#include "HumanAgent.h"
#include "CoOpAgent.h"
#include "assassinAgent.h"
#include "JHGEngine.h"

using namespace std;

struct PopularityMetrics {
    double avePop, endPop, relPop;
};

vector<string> split(const string& s) {
   vector<string> tokens;
   string token;
   istringstream tokenStream(s);
   while (getline(tokenStream, token, ','))
      tokens.push_back(token);
   return tokens;
}

GeneAgent **loadPopulationsFromFile(string theFolder, int theGen, int popSize, int numGeneCopies) {
    // allocate memory for theGenePools
    GeneAgent **theGenePools = new GeneAgent*[popSize];
    string fnombre = theFolder + "/gen_" + to_string(theGen) + ".csv";
    ifstream input(fnombre);
    for (int i = 0; i < popSize; i++) {
        // read in all of the GeneAgents
        // cout << "theGen: " << theGen << endl;
        // string fnombre = theFolder + "/" + to_string(i) + "/gen_" + to_string(theGen) + ".csv";
        
        string line;
        getline(input, line);
        vector<string> words = split(line);

        theGenePools[i] = new GeneAgent(words[0], numGeneCopies);
        theGenePools[i]->count = stoi(words[1]);
        theGenePools[i]->relativeFitness = stod(words[2]);
        theGenePools[i]->absoluteFitness = stod(words[3]);

    }
    input.close();

    return theGenePools;
}

GeneAgent **loadPopulationsFromFile(string fnombre, int popSize, int numGeneCopies) {
    // allocate memory for theGenePools
    GeneAgent **theGenePools = new GeneAgent*[popSize];
    ifstream input(fnombre);
    for (int i = 0; i < popSize; i++) {
        string line;
        getline(input, line);
        vector<string> words = split(line);

        theGenePools[i] = new GeneAgent(words[0], numGeneCopies);
        theGenePools[i]->count = stoi(words[1]);
        theGenePools[i]->relativeFitness = stod(words[2]);
        theGenePools[i]->absoluteFitness = stod(words[3]);

    }
    input.close();

    return theGenePools;
}

void deleteGenePool(GeneAgent **theGenePools, int popSize) {    
    for (int j = 0; j < popSize; j++) {
        delete theGenePools[j];
    }
    delete[] theGenePools;
}

void shuffle(double *initialPopularities, int numPlayers) {
    int n1, n2;
    double tmp;
    for (int i = 0; i < numPlayers; i++) {
        n1 = rand() % numPlayers;
        n2 = rand() % numPlayers;
        tmp = initialPopularities[n1];
        initialPopularities[n1] = initialPopularities[n2];
        initialPopularities[n2] = tmp;
    }
}

double sumVec(double *v, int len) {
    double sm = 0.0;
    for (int i = 0; i < len; i++)
        sm += v[i];

    return sm;
}

void defineInitialPopularities(string initPopType, int numPlayers, double *initialPopularities) {
    double basePop = 100.0;

    // assign the initial popularities
    if (initPopType == "equal") {
        for (int i = 0; i < numPlayers; i++)
            initialPopularities[i] = basePop;
    }
    else if (initPopType == "random") {
        for (int i = 0; i < numPlayers; i++)
            initialPopularities[i] = (rand() % 200) + 1.0;
    }
    else if (initPopType == "step") {
        for (int i = 0; i < numPlayers; i++)
            initialPopularities[i] = i + 1.0;
        shuffle(initialPopularities, numPlayers);
    }
    else if (initPopType == "power") {
        for (int i = 0; i < numPlayers; i++)
            initialPopularities[i] = 1.0 / pow(i+1, 0.7);
        shuffle(initialPopularities, numPlayers);
    }
    else if (initPopType == "highlow") {
        for (int i = 0; i < numPlayers / 2; i++) {
            initialPopularities[i] = 1.0 + rand() % 50 + 150;
        }
        for (int i = numPlayers / 2; i < numPlayers; i++) {
            initialPopularities[i] = 1.0 + rand() % 50;
        }
        shuffle(initialPopularities, numPlayers);
    }
    else {
        printf("don't understand init_pop %s, so just going with equal\n", initPopType.c_str());
        for (int i = 0; i < numPlayers; i++)
            initialPopularities[i] = basePop;
    }

    double totStartPop = basePop * numPlayers;
    double sm = sumVec(initialPopularities, numPlayers);
    for (int i = 0; i < numPlayers; i++) {
        initialPopularities[i] /= sm;
        initialPopularities[i] *= totStartPop;
    }
}

void recordState(int roundNum, JHGEngine *jhg, int humanInd, bool gameOver) {
    ofstream output("../State/state.tmp");

    if (!gameOver)
        output << "inprogress" << endl;
    else
        output << "fin" << endl;
    output << jhg->numPlayers << endl;
    output << humanInd << endl;
    output << roundNum << endl;

    // print out the popularities
    for (int i = 0; i < jhg->numPlayers; i++) {
        for (int r = 0; r < roundNum+1; r++)
            output << jhg->P[r][i] << " ";
        output << endl;
    }

    // print out the last round's token allocations
    for (int i = 0; i < jhg->numPlayers; i++) {
        for (int j = 0; j < jhg->numPlayers; j++) {
            if (jhg->T[roundNum][i][j] < 0)
                output << (int)(jhg->T[roundNum][i][j] * jhg->numTokens - 0.01) << " ";
            else
                output << (int)(jhg->T[roundNum][i][j] * jhg->numTokens + 0.01) << " ";
        }
        output << endl;
    }

    // print out the current tornadoValues
    // for (int i = 0; i < jhg->numPlayers; i++) {
    //     for (int j = 0; j < jhg->numPlayers; j++)
    //         output << jhg->I[roundNum][j][i] << " ";
    //     output << endl;
    // }

    for (int t = 0; t <= roundNum; t++) {
        for (int i = 0; i < jhg->numPlayers; i++) {
            for (int j = 0; j < jhg->numPlayers; j++)
                output << jhg->I[t][j][i] << " ";
            output << endl;
        }
    }

    // print out the previous tornadoValues
    // for (int i = 0; i < jhg->numPlayers; i++) {
    //     for (int j = 0; j < jhg->numPlayers; j++)
    //         if (roundNum > 0)
    //             output << jhg->I[roundNum-1][j][i] << " ";
    //         else
    //             output << jhg->I[0][j][i] << " ";
    //     output << endl;
    // }

    output.close();

    system("mv ../State/state.tmp ../State/state.txt");
}

PopularityMetrics *playGame(AbstractAgent **agents, int numPlayers, int numRounds, int gener, int gamer, double *initialPopularities, double povertyLine, bool forcedRandom) {
    double alpha = 0.2;
    double beta = 0.5;
    double coefs[3] = {0.95, 1.3, 1.6};

    // delete all existing contracts
    system("rm Contracts/*");

    // tell agents the game parameters and give each the chance to post a contract
    for (int i = 0; i < numPlayers; i++) {
        agents[i]->setGameParams(coefs, alpha, beta, povertyLine, forcedRandom);
        // printf("%s\n", ((GeneAgent *)agents[i])->getString().c_str());
        agents[i]->postContract(i);
    }

    int humanInd = -1;
    for (int i = 0; i < numPlayers; i++) {
        if (agents[i]->whoami == "human") {
            humanInd = i;
            break;
        }
    }

    // int numTokens = numPlayers;
    int numTokens = 2 * numPlayers;

    // allocate some memory for transactions
    double *received = new double[numPlayers];
    int **transactions = new int*[numPlayers];
    for (int i = 0; i < numPlayers; i++)
        transactions[i] = new int[numPlayers];
    
    PopularityMetrics *pmetrics = new PopularityMetrics[numPlayers];
    for (int i = 0; i < numPlayers; i++) {
        pmetrics[i].avePop = 0.0;
        pmetrics[i].endPop = 0.0;
    }

    // set up the game simulator
    JHGEngine *jhg = new JHGEngine(coefs, alpha, beta, povertyLine, numPlayers, numTokens, numRounds, initialPopularities);
    for (int r = 0; r < numRounds; r++) {
        if (humanInd >= 0)
            recordState(r, jhg, humanInd, false);

        // get each player's token allocations
        for (int i = 0; i < numPlayers; i++) {
            for (int j = 0; j < numPlayers; j++) {
                received[j] = jhg->T[r][j][i];
            }
            // printf("%i is %s\n", i, agents[i]->whoami.c_str()); fflush(stdout);
            agents[i]->playRound(numPlayers, numTokens, i, r, received, jhg->P[r], jhg->I[r], transactions[i]);
            // cout << "d" << endl;
        }

        // std::chrono::steady_clock::time_point antes = std::chrono::steady_clock::now(); 
        // std::chrono::steady_clock::time_point antes = std::chrono::steady_clock::now(); 

        // compute changes
        jhg->playRound(transactions);

        // std::chrono::steady_clock::time_point despues = std::chrono::steady_clock::now(); 
        // double jhgUpdateTime = std::chrono::duration_cast<std::chrono::microseconds>(despues - antes).count() / 1000000.0;
        // printf("round time: %lf\n", jhgUpdateTime);

        // record popularities
        for (int i = 0; i < numPlayers; i++) {
            pmetrics[i].avePop += jhg->P[jhg->t][i] / numRounds;
            pmetrics[i].endPop = jhg->P[jhg->t][i];
        }
    }

    jhg->printP();

    if (humanInd >= 0)
        recordState(numRounds, jhg, humanInd, true);

    // log game
    string fnombre = "../Results/theGameLogs/log_" + to_string(gener) + "_" + to_string(gamer) + ".csv";
    jhg->save(fnombre);

    for (int i = 0; i < numPlayers; i++)
        delete[] transactions[i];
    delete[] transactions;
    delete[] received;
    delete jhg;

    return pmetrics;
}

int selectByFitness(GeneAgent **thePopulation, int popSize, bool _rank) {
    double mag = 0.0;
    for (int i = 0; i < popSize; i++) {
        if (_rank)
            mag += thePopulation[i]->relativeFitness;
        else
            mag += thePopulation[i]->absoluteFitness;
    }

    double num = rand() / ((double)RAND_MAX);
    double sum = 0.0;
    for (int i = 0; i < popSize; i++) {
        if (_rank)
            sum += thePopulation[i]->relativeFitness / mag;
        else
            sum += thePopulation[i]->absoluteFitness / mag;

        if (num <= sum)
            return i;
    }

    printf("didn't select; num = %lf; sum = %lf\n", num, sum);
    exit(1);

    return popSize-1;
}

int mutateIt(int gene) {
    int v = rand() % 100;
    if (v >= 15)
        return gene;
    else if (v < 3)
        return rand() % 101;
    else {
        int g = gene + (rand() % 11) - 5;
        if (g < 0)
            g = 0;
        if (g > 100)
            g = 100;
        return g;
    }
}

GeneAgent **evolvePopulationPairs(GeneAgent **theGenePool_prev, int popSize, int numGeneCopies) {
    cout << "theGenePool_prev[0]->numGenes: " << theGenePool_prev[0]->numGenes << endl;
    GeneAgent **theGenePool = new GeneAgent*[popSize];
    for (int i = 0; i < popSize; i++) {
        // select 2 agents from theGenePools_prev[pool]
        int ind1, ind2;
        if (i < (popSize / 5.0)) {
            ind1 = selectByFitness(theGenePool_prev, popSize, true);
            ind2 = selectByFitness(theGenePool_prev, popSize, false);
        }
        else {
            ind1 = selectByFitness(theGenePool_prev, popSize, false);
            ind2 = selectByFitness(theGenePool_prev, popSize, false);
        }

        string geneStr = "genes_";

        for (int g = 0; g < theGenePool_prev[0]->numGenes; g++) {
            if ((rand() % 2) == 0) {
                geneStr += to_string(mutateIt(theGenePool_prev[ind1]->myGenes[g]));
                if (g < (theGenePool_prev[0]->numGenes-1))
                    geneStr += "_";
            }
            else {
                geneStr += to_string(mutateIt(theGenePool_prev[ind2]->myGenes[g]));
                if (g < (theGenePool_prev[0]->numGenes-1))
                    geneStr += "_";
            }
        }

        theGenePool[i] = new GeneAgent(geneStr, numGeneCopies);
    }


    return theGenePool;
}

int compareEm(GeneAgent *a, GeneAgent *b) {
    if(a->absoluteFitness > b->absoluteFitness)
		return 1;
	else 
		return 0;
}

void writeGenerationResults(GeneAgent **theGenePools, int popSize, int gen, int agentsPerGame) {
    for (int i = 0; i < popSize; i++) {
        if (theGenePools[i]->count > 0) {
            theGenePools[i]->relativeFitness /= theGenePools[i]->count;
            theGenePools[i]->absoluteFitness /= theGenePools[i]->count;
        }
        else {
            theGenePools[i]->relativeFitness = 0.0;
            theGenePools[i]->absoluteFitness = 0.0;
        }
    }

    vector<GeneAgent *> v;
    for (int i = 0; i < popSize; i++)
        v.push_back(theGenePools[i]);
    sort(v.begin(), v.end(), compareEm);
    // sort(theGenePools[pool], theGenePools[pool]+(numPops*n*2), compareEm);

    // print to file
    string fnombre = "../Results/theGenerations/gen_" + to_string(gen) + ".csv";
    ofstream output(fnombre);       
    double sm = 0.0;
    for (int i = 0; i < popSize; i++) {
        sm += v[i]->absoluteFitness;
        // output << theGenePools[pool][i]->getString() << "," << theGenePools[pool][i]->count << "," << theGenePools[pool][i]->relativeFitness << "," << theGenePools[pool][i]->absoluteFitness << endl;
        output << v[i]->getString() << "," << v[i]->count << "," << v[i]->relativeFitness << "," << v[i]->absoluteFitness << endl;
    }

    output.close();

    cout << "Average fitness in generation " << gen << ": " << (sm / popSize) << endl;
}

// To compile: g++ main.cpp -o jhgsim
// 
// To evolve genes, run the program as follows:
//      ./jhgsim evolve [generationFolder] [popSize] [numGeneCopies] [startGen] [numGens] [gamesPerGen] [agentsPerGame] [roundsPerGame] [povertyLine] [config] [equal/varied]
// 
// To run a game using gene-strings from a particular generation:
//      ./jhgsim play [generationFolder] [popSize] [numGeneCopies] [gen] [numAgents] [numRounds] [best_agents/rnd_agents] [initPopType] [povertyLine] [deterministic/nondeterministic] [config] 
// 
int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("don't know what mode to run the program in\n");
        return -1;
    }

    srand(time(NULL));

    if (!strcmp(argv[1], "play")) {
        if (argc != 13) {
            printf("wrong number of parameters to specify how to *play*: %i\n", argc);
            return -1;
        }

        // store the command-line parameters in the appropriate format
        string theFolder = argv[2];
        int popSize = atoi(argv[3]);
        int numGeneCopies = atoi(argv[4]);
        int theGen = atoi(argv[5]);
        int numAgents = atoi(argv[6]);
        int numRounds = atoi(argv[7]);
        string agentSelections = argv[8];
        if ((agentSelections != "best_agents") && (agentSelections != "rnd_agents")) {
            printf("don't understand agentSelection: %s; Must be best_agents or rnd_agents\n", agentSelections.c_str());
            return -1;
        }
        string initPopType = argv[9];
        if ((initPopType != "equal") && (initPopType != "random") && (initPopType != "step") && (initPopType != "power") && (initPopType != "highlow")) {
            printf("don't understand initPopType: %s\n", initPopType.c_str());
            return -1;
        }
        double povertyLine = (double)(atoi(argv[10]));

        bool forcedRandom = false;
        if (!strcmp(argv[11], "deterministic"))
            forcedRandom = true;

        // load extra players specified in the configuration file
        vector<AbstractAgent *> configuredPlayers;

        string fnombre = "ScenarioIndicator/";
        fnombre += argv[12];
        fnombre += ".txt";
        ifstream in(fnombre);
        if (!in) {
            cout << "config file not found: " << fnombre << endl;
        }
        else {
            string line;
            while (!in.eof()) {
                getline(in, line);
                if (line == "Human")
                    configuredPlayers.push_back(new HumanAgent());
                else if (line == "Assassin")
                    configuredPlayers.push_back(new assassinAgent());
                else if ((line.length() >= 4) && (line.substr(0,4) == "CoOp"))
                    configuredPlayers.push_back(new CoOpAgent(line));
            }
            in.close();
        }

        cout << "num configured players: " << configuredPlayers.size() << endl;

        // load in the population(s) of generation "theGen"
        GeneAgent **theGenePools = loadPopulationsFromFile(theFolder, theGen, popSize, numGeneCopies);
        int numPlayers = numAgents + configuredPlayers.size();
        int *plyrIdxs = new int[numPlayers];

        // determine which GeneAgents will participate
        if (agentSelections == "best_agents") {
            for (int i = 0; i < numAgents; i++)
                plyrIdxs[i] = i;
        }
        else {
            for (int i = 0; i < numAgents; i++)
                plyrIdxs[i] = rand() % popSize;
        }

        // add in the configured players
        for (int i = 0; i < configuredPlayers.size(); i++)
            plyrIdxs[numAgents+i] = popSize + i;

        // now get the initial popularities
        double *initialPopularities = new double[numPlayers];
        defineInitialPopularities(initPopType, numPlayers, initialPopularities);

        AbstractAgent **agents = new AbstractAgent*[numPlayers];
        for (int i = 0; i < numPlayers; i++) {
            if (plyrIdxs[i] >= popSize)
                agents[i] = configuredPlayers[plyrIdxs[i] - popSize];
            else
                agents[i] = theGenePools[plyrIdxs[i]];
        }

        PopularityMetrics *pmetrics = playGame(agents, numPlayers, numRounds, 1000, 1000, initialPopularities, povertyLine, forcedRandom);

        delete[] pmetrics;
        delete[] plyrIdxs;
        delete[] initialPopularities;
        // delete[] poolAssignments;
        deleteGenePool(theGenePools, popSize);
        delete[] agents;

        // delete extra players specified by the configuration file
        for (int i = 0; i < configuredPlayers.size(); i++) {
            // cout << configuredPlayers[i]->whoami << endl;
            if (configuredPlayers[i]->whoami == "human")
                delete ((HumanAgent *)configuredPlayers[i]);
            else if (configuredPlayers[i]->whoami == "assassin")
                delete ((assassinAgent *)configuredPlayers[i]);
            else if ((configuredPlayers[i]->whoami.length() >= 4) && (configuredPlayers[i]->whoami.substr(0,4) == "CoOp"))
                delete ((CoOpAgent *)configuredPlayers[i]);
            else {
                cout << "don't know how to delete " << configuredPlayers[i]->whoami << " player " << i << endl;
            }
        }
    }
    else if (!strcmp(argv[1], "evolve")) {
        if (argc != 13) {
            printf("wrong number of parameters to specify how to evolve the population(s)\n");
            return -1;
        }

        // store the command-line parameters in the appropriate format
        string theFolder = argv[2];
        int popSize = atoi(argv[3]);
        int numGeneCopies = atoi(argv[4]);
        int startIndex = atoi(argv[5]);
        int numGens = atoi(argv[6]);
        int gamesPerGen = atoi(argv[7]);
        int agentsPerGame = atoi(argv[8]);
        int roundsPerGame = atoi(argv[9]);
        double povertyLine = atof(argv[10]);

        // load extra players specified in the configuration file
        vector<AbstractAgent *> configuredPlayers;

        string fnombre = "ScenarioIndicator/";
        fnombre += argv[11];
        fnombre += ".txt";
        ifstream in(fnombre);
        if (!in) {
            cout << "config file not found: " << fnombre << endl;
        }
        else {
            string line;
            while (!in.eof()) {
                getline(in, line);
                if (line == "Human")
                    configuredPlayers.push_back(new HumanAgent());
                else if (line == "Assassin")
                    configuredPlayers.push_back(new assassinAgent());
                if ((line.length() >= 4) && (line.substr(0,4) == "CoOp"))
                    configuredPlayers.push_back(new CoOpAgent(line));
            }
            in.close();
        }

        cout << "num configured players: " << configuredPlayers.size() << endl;

        GeneAgent **theGenePools, **theGenePools_old;
        if (startIndex != 0) {
            theGenePools_old = loadPopulationsFromFile(theFolder, startIndex-1, popSize, numGeneCopies);
            theGenePools = evolvePopulationPairs(theGenePools_old, popSize, numGeneCopies);

            // delete theGenePools_old
            deleteGenePool(theGenePools_old, popSize);
        }
        else {
            theGenePools = new GeneAgent*[popSize];
            for (int j = 0; j < popSize; j++) {
                theGenePools[j] = new GeneAgent("", numGeneCopies);
            }
        }
        int numPlayers = agentsPerGame + configuredPlayers.size();

        string possibleInitPops[5] = {"equal", "random", "step", "power", "highlow"};
        double *initialPopularities = new double[numPlayers];
        double *initialRelativePopularities = new double[numPlayers];
        int *plyrIdxs = new int[numPlayers];
        AbstractAgent **agents = new AbstractAgent*[numPlayers];

        int mxPlayers = numPlayers;

        int sel;
        for (int gen = startIndex; gen < numGens; gen++) {  // let's do this for each generation
            for (int game = 0; game < gamesPerGen; game++) {  // let's do this for each generation

                // time to pick individuals from the gene pools
                for (int i = 0; i < agentsPerGame; i++) {
                    plyrIdxs[i] = rand() % popSize;
                    agents[i] = theGenePools[plyrIdxs[i]];
                }

                // add in the configured players
                numPlayers = agentsPerGame;
                for (int i = agentsPerGame; i < mxPlayers; i++) {
                    if (((rand() % 1) == 0) || (game == 0)) {
                        // printf("adding configured player %i\n", i);
                        plyrIdxs[numPlayers] = popSize + i;
                        agents[numPlayers] = configuredPlayers[i-agentsPerGame];
                        numPlayers ++;
                    }
                }
                // printf("numPlayers: %i\n", numPlayers);

                printf("\n%i-%i\n", gen, game);
                if (!strcmp("varied", argv[12]))
                    sel = rand() % 5;
                else
                    sel = 0;
                cout << possibleInitPops[sel] << endl;
                defineInitialPopularities(possibleInitPops[sel], numPlayers, initialPopularities);
                
                printf("i_pops: ");
                double s = 0.0;
                for (int i = 0; i < numPlayers; i++) {
                    printf("%.1lf ", initialPopularities[i]);
                    s += initialPopularities[i];
                }
                printf("\n");

                for (int i = 0; i < numPlayers; i++)
                    initialRelativePopularities[i] = initialPopularities[i] / s;

                // record who the players were
                ofstream f("../Results/thePlayers/players_" + to_string(gen) + "_" + to_string(game) + ".txt");
                for (int i = 0; i < numPlayers; i++)
                    f << plyrIdxs[i] << " " << initialPopularities[i] << endl;
                f.close();

                // cout << "start the game" << endl;
                // for (int i = 0; i < numPlayers; i++)
                //     cout << agents[i]->whoami << endl;

                // play the game
                PopularityMetrics *pmetrics = playGame(agents, numPlayers, roundsPerGame, gen, game, initialPopularities, povertyLine, false);

                // cout << "end the game" << endl;

                // compute relative popularity
                s = 0.0;
                for (int i = 0; i < numPlayers; i++)
                    s += pmetrics[i].avePop;
                for (int i = 0; i < numPlayers; i++)
                    pmetrics[i].relPop = pmetrics[i].avePop / s;

                // print to terminal
                printf("Indices: ");
                for (int i = 0; i < numPlayers; i++) {
                    printf("%i ", plyrIdxs[i]);
                }
                printf("\n");
                printf("avePop: ");
                for (int i = 0; i < numPlayers; i++) {
                    printf("%.2lf ", pmetrics[i].avePop);
                }
                printf("\n");
                printf("\n");
                printf("relPop: ");
                for (int i = 0; i < numPlayers; i++) {
                    printf("%.3lf ", pmetrics[i].relPop);
                }
                printf("\n");
                printf("average popularity: %lf\n\n", s / agentsPerGame);

                // update the fitness of the agents that played in the game
                for (int i = 0; i < agentsPerGame; i++) {
                    if (theGenePools[plyrIdxs[i]]->playedGenes) {
                        theGenePools[plyrIdxs[i]]->count ++;
                        theGenePools[plyrIdxs[i]]->absoluteFitness += ((pmetrics[i].avePop + pmetrics[i].endPop) / 2.0);// / initialPopularities[i];
                        theGenePools[plyrIdxs[i]]->relativeFitness += pmetrics[i].relPop;// / initialRelativePopularities[i];
                    }
                }

                delete[] pmetrics;
            }

            writeGenerationResults(theGenePools, popSize, gen, agentsPerGame);

            // evolve population
            theGenePools_old = theGenePools;
            theGenePools = evolvePopulationPairs(theGenePools_old, popSize, numGeneCopies);
            deleteGenePool(theGenePools_old, popSize);
        }

        deleteGenePool(theGenePools, popSize);
        delete[] initialPopularities;
        delete[] initialRelativePopularities;
        // delete[] poolAssignments;
        delete[] plyrIdxs;
        delete[] agents;

        // delete extra players specified by the configuration file
        for (int i = 0; i < configuredPlayers.size(); i++) {
            if (configuredPlayers[i]->whoami == "human")
                delete ((HumanAgent *)configuredPlayers[i]);
            else if (configuredPlayers[i]->whoami == "assassin")
                delete ((assassinAgent *)configuredPlayers[i]);
            else if ((configuredPlayers[i]->whoami.length() >= 4) && (configuredPlayers[i]->whoami.substr(0,4) == "CoOp"))
                delete ((CoOpAgent *)configuredPlayers[i]);
            else {
                cout << "don't know how to delete " << configuredPlayers[i]->whoami << endl;
            }
        }
    }

    // ./jhgsim playMixed [agentMix] [numRounds] [initPopType]
    //      example to play a game with 12 agents (3 of each type) for 30 rounds with equal initial popularities:
    //              ./jhgsim playMixed 000111222333 30 equal
    //      for the agent mix: 0 = CAB-e1; 1 = CAB-v1; 2 = CAB-e3; 3 = CAB-v3
    else if (!strcmp(argv[1], "playMixed")) {
        if (argc != 5) {
            cout << "wrong number of parameters" << endl;
        }

        string agentMix = argv[2];
        int numPlayers = agentMix.length();
        int numRounds = atoi(argv[3]);
        string initPopType = argv[4];

        // load in all of the agents
        int numPerPool = 10;     // number of agents specified in each gene pool (mine is 10, your's is probably 60)
        GeneAgent **CAB_e1 = loadPopulationsFromFile("../BestBots/CAB-e1.csv", numPerPool, 1);
        GeneAgent **CAB_v1 = loadPopulationsFromFile("../BestBots/CAB-v1.csv", numPerPool, 1);
        GeneAgent **CAB_e3 = loadPopulationsFromFile("../BestBots/CAB-e3.csv", numPerPool, 3);
        GeneAgent **CAB_v3 = loadPopulationsFromFile("../BestBots/CAB-v3.csv", numPerPool, 3);

        AbstractAgent **agents = new AbstractAgent*[numPlayers];
        cout << "numAgents: " << numPlayers << endl;
        for (int i = 0; i < agentMix.length(); i++) {
            switch (agentMix[i]) {
                case '0': 
                    // cout << "CAB-e1" << endl; 
                    agents[i] = CAB_e1[rand() % numPerPool];
                    break;
                case '1': 
                    // cout << "CAB-v1" << endl;
                    agents[i] = CAB_v1[rand() % numPerPool];
                    break;
                case '2': 
                    // cout << "CAB-e3" << endl;
                    agents[i] = CAB_e3[rand() % numPerPool];
                    break;
                case '3': 
                    // cout << "CAB-v3" << endl;
                    agents[i] = CAB_v3[rand() % numPerPool];
                    break;
                default: cout << "agent type not found" << endl;
            }
        }

        double *initialPopularities = new double[numPlayers];
        defineInitialPopularities(initPopType, numPlayers, initialPopularities);
        
        PopularityMetrics *pmetrics = playGame(agents, numPlayers, numRounds, 1000, 1000, initialPopularities, 0.0, false);

        // delete stuff
        deleteGenePool(CAB_e1, numPerPool);
        deleteGenePool(CAB_v1, numPerPool);
        deleteGenePool(CAB_e3, numPerPool);
        deleteGenePool(CAB_v3, numPerPool);

        delete[] agents;
        delete[] pmetrics;
        delete[] initialPopularities;
    }
    else {
        printf("Command %s not found\n", argv[1]);
    }

    return 0;
}