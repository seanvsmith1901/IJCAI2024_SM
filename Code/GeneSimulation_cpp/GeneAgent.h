#ifndef GENEAGENT_H
#define GENEAGENT_H

#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <sstream>
#include <fstream>

#include <chrono>

#include "defs.h"
#include "AbstractAgent.h"
#include "CommunityEvaluation.h"

using namespace std;

struct PlayerProfile {
    int index;
    double val;
};

struct attackObject {
    int index, amount;
    double gain, priority;

    attackObject(int _index, int _amount, double _gain) {
        index = _index;
        amount = _amount;
        gain = _gain;
        priority = -1.0;
    }
};

struct govMent {
    bool govPlayer;
    double initialFeePercentage, feePercentage;
    string merit;

    govMent() {
        govPlayer = false;
    }

    void installGovMent(ifstream &input) {
        govPlayer = true;
        string line;
        getline(input, line);
        vector<string> words = parse(line);
        initialFeePercentage = stof(words[1]);
        getline(input, line);
        vector<string> words2 = parse(line);
        feePercentage = stof(words2[1]);
        getline(input, line);
        vector<string> words3 = parse(line);
        merit = words3[1];
    }

    vector<string> parse(const string& s) {
        vector<string> tokens;
        string token;
        istringstream tokenStream(s);
        while (getline(tokenStream, token, ' '))
            tokens.push_back(token);
        return tokens;
    }
};

bool compare(PlayerProfile *a, PlayerProfile *b){
	if(a->val > b->val)
		return 1;
	else 
		return 0;
}

class GeneAgent : public AbstractAgent {
public:
    int count;
    double relativeFitness, absoluteFitness;

    int *myGenes, numGenes;
    bool playedGenes;

    GeneAgent() {
        printf("Default constructor shouldn't be used\n");
        exit(1);
    }

    GeneAgent(string geneStr, int _numGeneCopies) {
        numGeneCopies = _numGeneCopies;
        if (geneStr == "") {
            numGenes = predef_NUMGENES * numGeneCopies;
            myGenes = new int[numGenes];
            for (int i = 0; i < numGenes; i++) {
                myGenes[i] = rand() % 101;
            }
        }
        else {
            // printf("%s\n", geneStr.c_str());
            vector<string> words = parse(geneStr);
            numGenes = words.size()-1;

            if (numGenes != (predef_NUMGENES * numGeneCopies)) {
                printf("confusion about the number of genes I should have; %i vs %i\n", predef_NUMGENES, numGenes);
                exit(1);
            }

            myGenes = new int[numGenes];
            for (int i = 1; i < numGenes+1; i++)    // // // put +1 back once generate it
                myGenes[i-1] = stoi(words[i]);
        }

        count = 0;
        relativeFitness = absoluteFitness = 0.0;
        whoami = getString();
        playedGenes = true;
        theTracked = getTracked();
        isInitialized = false;

        setUpRand();

        nPlayers = 0;

        // cout << whoami << endl;
    }

    ~GeneAgent() {
        delete[] myGenes;
        deleteAll(nPlayers);
    }

    string getString() {
        string theStr = "gene";
        for (int i = 0; i < numGenes; i++) {
            theStr += "_" + to_string(myGenes[i]);
        }

        return theStr;
    }

    void playRound(int numPlayers, int numTokens, int playerIdx, int roundNum, double *received, double *popularities, double **influence, int *allocations) {
        // cout << "*** playRound: " << playerIdx << endl;

        // printT(playerIdx, vec2String(received, numPlayers));

        for (int i = 0; i < numPlayers; i++)
            allocations[i] = 0;

        if (theTracked != 99999)
            theTracked = getTracked();

        if (playerIdx == theTracked)
            printf("\n\n\nRound %i (Player %i)\n", roundNum, theTracked);

        
        if (roundNum == 0) {
            initVars(playerIdx, numPlayers, popularities);
            alphaMia = genes[GENE_alpha] / 100.0;
            printT(playerIdx, getString());
        }
        else {
            alphaMia = genes[GENE_alpha] / 100.0;
            updateVars(received, popularities, numTokens, numPlayers, playerIdx);
        }

        computeUsefulQuantities(roundNum, numPlayers, playerIdx, numTokens, influence);

        printT(playerIdx, " Punishable debt: " + vec2String(punishableDebt, numPlayers));

        // group analysis and choice
        vector< set<int> > communities;

        CommunityEvaluation *selectedCommunity = groupAnalysis(roundNum, numPlayers, playerIdx, popularities, influence, communities);

        // some initializations
        for (int i = 0; i < numPlayers; i++)
            attackAlloc[i] = 0;
        int numAttackToks, numGuardoToks, remainingToks, numCoopToks;

        // figure out how many tokens to keep
        estimateKeeping(playerIdx, numPlayers, numTokens, communities);
        printT(playerIdx, "\n estimated keeping: " + vec2String(keepingStrength, numPlayers));

        bool safetyFirst = true;
        if (genes[GENE_safetyFirst] < 50)
            safetyFirst = false;

        numCoopToks = 0;
        int coopInd = -1;
        // printT(playerIdx, "Should I join the co-op: " + to_string(genes[GENE_joinCoop]));
        if (genes[GENE_joinCoop] >= 50) {
            // find the first coop I come across and pay the specified fees
            for (int i = 0; i < numPlayers; i++) {
                if (govPlayers[i]->govPlayer) {
                    // printT(playerIdx, to_string(i) + " is the co-op");
                    if (roundNum == 0) {
                        numCoopToks = (int)((govPlayers[i]->initialFeePercentage / 100.0) * numTokens + 0.99);
                        // allocations[i] = numCoopToks;
                        coopInd = i;
                    }
                    else {
                        numCoopToks = (int)((govPlayers[i]->feePercentage / 100.0) * numTokens + 0.99);
                        // allocations[i] = numCoopToks;
                        coopInd = i;
                    }
                    // printT(playerIdx, "paying fee of " + to_string(numCoopToks) + " to " + to_string(i));

                    break;
                }
            }
        }

        numGuardoToks = cuantoGuardo(roundNum, playerIdx, numPlayers, numTokens, popularities, received, selectedCommunity->s);
        printT(playerIdx, "   numGuardoToks: " + to_string(numGuardoToks));

        // determine who to attack (if any)
        if (roundNum > 0) {
            remainingToks = numTokens - numCoopToks;
            if (safetyFirst)
                remainingToks -= numGuardoToks;
            
            numAttackToks = quienAtaco(roundNum, playerIdx, numPlayers, numTokens, remainingToks, popularities, influence, selectedCommunity->s, communities, attackAlloc);
            printT(playerIdx, "\n Attackings:");
            printT(playerIdx, "   attackVec: " + vec2String(attackAlloc, numPlayers) + "(" + to_string(numAttackToks) + ")");

            if (numAttackToks < 0) {
                printf("why is numAttackToks negative? %i\n", numAttackToks);
            }
        }
        else {
            remainingToks = numTokens - numGuardoToks - numCoopToks;
            numAttackToks = 0;
        }

        if (abs(numAttackToks) > numTokens) {
            printf("que pasa: %i\n", numAttackToks);
        }

        // printT(playerIdx, "numTokens: " + to_string(numTokens));
        // printT(playerIdx, "numAttackToks: " + to_string(numAttackToks));
        // printT(playerIdx, "numGuardoToks: " + to_string(numGuardoToks));
        // printT(playerIdx, "remainingToks: " + to_string(remainingToks));

        int numGivingToks = numTokens - numAttackToks - numGuardoToks - numCoopToks;
        int numGiving = groupGivings(roundNum, numPlayers, numTokens, numGivingToks, playerIdx, influence, popularities, selectedCommunity, attackAlloc, allocations);

        for (int i = 0; i < numPlayers; i++) {
            if ((i == playerIdx) && (allocations[i] < 0)) {
                printf("Caught a problem.  Giving negative tokens to self: %i; %i, %i, %i\n", allocations[i], numTokens, numAttackToks, numGuardoToks);
            }
            allocations[i] -= attackAlloc[i];
        }
        if (coopInd >= 0) {
            if (allocations[coopInd] < 0)
                allocations[coopInd] = numCoopToks;
            else
                allocations[coopInd] += numCoopToks;
        }

        int allocSoFar = 0;
        for (int i = 0; i < numPlayers; i++)
            allocSoFar += abs(allocations[i]);
        int temp = numGuardoToks;
        numGuardoToks = numTokens - allocSoFar;
        if (numGuardoToks < 0) {
            printf("give (%i) + steal: ", numGiving);
            for (int i = 0; i < numPlayers; i++)
                printf("%i ", allocations[i]);
            printf("\n");
        }
        allocations[playerIdx] += numGuardoToks;

        // update prevAllocations and prevInfluence
        for (int i = 0; i < numPlayers; i++) {
            prevAllocations[i] = allocations[i];
            for (int j = 0; j < numPlayers; j++) {
                prevInfluence[i][j] = influence[i][j];
            }
        }

        updateIndebtedness(roundNum, playerIdx, numPlayers, allocations, popularities);

        printT(playerIdx, to_string(playerIdx) + " allocations: " + vec2String(allocations, numPlayers) + " (" + to_string(numGiving) + ")");
        if (allocations[playerIdx] < 0) {
            printf("%i is stealing from self!!!\n", playerIdx);
            printf("safetyFirst? %i\n", (int)safetyFirst);
            printf("remainingToks: %i\n", remainingToks);
            printf("allocSoFar: %i\n", allocSoFar);
            printf("numGuardoToks: %i\n", numGuardoToks);
            printf("prev numGuardoToks: %i\n", temp);
            printf("numGivingToks: %i\n", numGivingToks);
            printf("numAttackToks: %i\n", numAttackToks);
            printf("popularity: %lf\n", popularities[playerIdx]);
            printf("attackAlloc: ");
            for (int i = 0; i < numPlayers; i++) 
                printf("%i ", attackAlloc[i]);
            printf("\n");
        }

        if (selectedCommunity != NULL)
            delete selectedCommunity;
    }

    void postContract(int playerIdx) {}

// ******************************************************************
// 
//      Now all of the functions and data members that make it happen
// 
// ******************************************************************
private:
    int theTracked;
    vector< double * > popHistory;
    double alphaMia;

    int *genes, numGeneCopies;
    bool isInitialized;
    govMent **govPlayers;
    double *tally, *unpaidDebt, *punishableDebt, *expectedReturn, *scaledBackNums;
    double ave_return, received_value, invested_value, ROI;
    int *prevAllocations, *attackAlloc, nPlayers;
    int *theCurComm;
    double **prevInfluence, **inflPos, **inflNeg, **inflNegPrev, **sumInflPos, **newSteals, *inflPos_sumcol, *inflPos_sumrow;
    double *attacksWithMe, *othersAttacksOn, *badGuys, *badGuysCopy;
    double inflictedDamageRatio, expectedDefendFriendDamage;
    double coalitionTarget, underAttack;
    double *meImporta, *keepingStrength;

    double **A_pos, **A_neg;

    int randNums[10000], randCount;

    void setUpRand() {
        randCount = 0;
        ifstream input("../State/rnums.txt");

        for (int i = 0; i < 10000; i++)
            input >> randNums[i];

        input.close();
    }

    int getRand() {
        int num = randNums[randCount];
        randCount ++;
        if (randCount >= 10000)
            randCount = 0;

        return num;
    }

    vector<string> parse(const string& s) {
        vector<string> tokens;
        string token;
        istringstream tokenStream(s);
        while (getline(tokenStream, token, '_'))
            tokens.push_back(token);
        return tokens;
    }

    int getTracked() {
        ifstream input("ScenarioIndicator/theTracked.txt");

        string line;
        getline(input, line);
        int val = stoi(line);

        input.close();

        return val;
    }

    void assassinGenes() {
        playedGenes = false;

        genes[GENE_visualTrait] = 50;
        genes[GENE_alpha] = 1;
        genes[GENE_homophily] = 50;
        genes[GENE_otherishDebtLimits] = 25;
        genes[GENE_coalitionTarget] = 0;
        genes[GENE_fixedUsage] = 50;
        genes[GENE_w_modularity] = 100;
        genes[GENE_w_centrality] = 0;
        genes[GENE_w_collective_strength] = 0;
        genes[GENE_w_familiarity] = 0;
        genes[GENE_w_prosocial] = 0;
        genes[GENE_initialDefense] = 100;
        genes[GENE_minKeep] = 100;
        genes[GENE_defenseUpdate] = 50;
        genes[GENE_defensePropensity] = 50;
        genes[GENE_fearDefense] = 50;
        genes[GENE_safetyFirst] = 0;
        genes[GENE_pillageFury] = 100;
        genes[GENE_pillageDelay] = 10;
        genes[GENE_pillagePriority] = 80;
        genes[GENE_pillageMargin] = 0;
        genes[GENE_pillageFriends] = 0;
        genes[GENE_pillageCompanionship] = 50;
        genes[GENE_vengenceMultiplier] = 100;
        genes[GENE_vengenceMax] = 100;
        genes[GENE_vengencePriority] = 100;
        genes[GENE_defendFriendMultiplier] = 100;
        genes[GENE_defendFriendMax] = 100;
        genes[GENE_defendFriendPriority] = 90;
        genes[GENE_attackGoodGuys] = 100;
        genes[GENE_limitingGive] = 100;
        genes[GENE_groupAware] = 0;
    }

    void assassinDefender() {
        playedGenes = false;

        // poor genes
        myGenes[GENE_visualTrait] = genes[GENE_visualTrait] = 50;
        myGenes[GENE_homophily] = genes[GENE_homophily] = 50;
        myGenes[GENE_alpha] = genes[GENE_alpha] = 20;
        myGenes[GENE_otherishDebtLimits] = genes[GENE_otherishDebtLimits] = 25;
        myGenes[GENE_coalitionTarget] = genes[GENE_coalitionTarget] = 70;
        myGenes[GENE_fixedUsage] = genes[GENE_fixedUsage] = 50;
        myGenes[GENE_w_modularity] = genes[GENE_w_modularity] = 100;
        myGenes[GENE_w_centrality] = genes[GENE_w_centrality] = 50;
        myGenes[GENE_w_collective_strength] = genes[GENE_w_collective_strength] = 80;
        myGenes[GENE_w_familiarity] = genes[GENE_w_familiarity] = 50;
        myGenes[GENE_w_prosocial] = genes[GENE_w_prosocial] = 70;
        myGenes[GENE_initialDefense] = genes[GENE_initialDefense] = 20;
        myGenes[GENE_minKeep] = genes[GENE_minKeep] = 20;
        myGenes[GENE_defenseUpdate] = genes[GENE_defenseUpdate] = 50;
        myGenes[GENE_defensePropensity] = genes[GENE_defensePropensity] = 50;
        myGenes[GENE_fearDefense] = genes[GENE_fearDefense] = 0;
        myGenes[GENE_safetyFirst] = genes[GENE_safetyFirst] = 0;
        myGenes[GENE_pillageFury] = genes[GENE_pillageFury] = 0;
        myGenes[GENE_pillageDelay] = genes[GENE_pillageDelay] = 10;
        myGenes[GENE_pillagePriority] = genes[GENE_pillagePriority] = 0;
        myGenes[GENE_pillageMargin] = genes[GENE_pillageMargin] = 0;
        myGenes[GENE_pillageCompanionship] = genes[GENE_pillageCompanionship] = 50;
        myGenes[GENE_pillageFriends] = genes[GENE_pillageFriends] = 0;
        myGenes[GENE_vengenceMultiplier] = genes[GENE_vengenceMultiplier] = 100;
        myGenes[GENE_vengenceMax] = genes[GENE_vengenceMax] = 100;
        myGenes[GENE_vengencePriority] = genes[GENE_vengencePriority] = 100;
        myGenes[GENE_defendFriendMultiplier] = genes[GENE_defendFriendMultiplier] = 100;
        myGenes[GENE_defendFriendMax] = genes[GENE_defendFriendMax] = 100;
        myGenes[GENE_defendFriendPriority] = genes[GENE_defendFriendPriority] = 90;
        myGenes[GENE_attackGoodGuys] = genes[GENE_attackGoodGuys] = 0;
        myGenes[GENE_limitingGive] = genes[GENE_limitingGive] = 100;
        myGenes[GENE_groupAware] = genes[GENE_groupAware] = 0;
        myGenes[GENE_joinCoop] = genes[GENE_joinCoop] = 0;

        for (int i = predef_NUMGENES; i < numGenes; i++) {
            myGenes[i] = genes[i % predef_NUMGENES];
        }
    }

    void deleteAll(int nmPlayers) {
        if (isInitialized) {
            // cout << "deleting player with: " << nmPlayers << endl;
            delete[] genes;
            delete[] tally;
            delete[] unpaidDebt;
            delete[] punishableDebt;
            delete[] expectedReturn;
            delete[] scaledBackNums;
            delete[] prevAllocations;
            delete[] attackAlloc;

            for (int i = 0; i < nmPlayers; i++) {
                delete[] prevInfluence[i];
                delete[] inflPos[i];
                delete[] inflNeg[i];
                delete[] inflNegPrev[i];
                delete[] sumInflPos[i];
                delete[] newSteals[i];
                delete[] A_pos[i];
                delete[] A_neg[i];
                delete govPlayers[i];
            }

            delete[] govPlayers;
            delete[] inflPos;
            delete[] inflNeg;
            delete[] inflNegPrev;
            delete[] prevInfluence;
            delete[] sumInflPos;
            delete[] inflPos_sumcol;
            delete[] inflPos_sumrow;
            delete[] attacksWithMe;
            delete[] othersAttacksOn;
            delete[] badGuys;
            delete[] badGuysCopy;
            delete[] newSteals;
            delete[] A_pos;
            delete[] A_neg;
            delete[] meImporta;
            delete[] theCurComm;
            delete[] keepingStrength;
        }
    }

    void initVars(int playerIdx, int numPlayers, double *popularities) {
        popHistory.clear();
        popHistory.push_back(popularities);

        if ((numPlayers > nPlayers) && isInitialized) {
            deleteAll(nPlayers);
            isInitialized = false;
        }

        if (!isInitialized) {
            // cout << "initializing player with: " << numPlayers << endl;
            genes = new int[numGenes / numGeneCopies];
            tally = new double[numPlayers];
            unpaidDebt = new double[numPlayers];
            printT(playerIdx, "numPlayers: " + to_string(numPlayers));
            punishableDebt = new double[numPlayers];
            expectedReturn = new double[numPlayers];
            scaledBackNums = new double[numPlayers];
            prevAllocations = new int[numPlayers];
            attackAlloc = new int[numPlayers];

            govPlayers = new govMent*[numPlayers];
            inflPos_sumcol = new double[numPlayers];
            inflPos_sumrow = new double[numPlayers];
            prevInfluence = new double*[numPlayers];
            inflPos = new double*[numPlayers];
            inflNeg = new double*[numPlayers];
            inflNegPrev = new double*[numPlayers];
            sumInflPos = new double*[numPlayers];
            newSteals = new double*[numPlayers];
            A_pos = new double*[numPlayers];
            A_neg = new double*[numPlayers];
            for (int i = 0; i < numPlayers; i++) {
                govPlayers[i] = new govMent();
                prevInfluence[i] = new double[numPlayers];
                inflPos[i] = new double[numPlayers];
                inflNeg[i] = new double[numPlayers];
                inflNegPrev[i] = new double[numPlayers];
                sumInflPos[i] = new double[numPlayers];
                newSteals[i] = new double[numPlayers];
                A_pos[i] = new double[numPlayers];
                A_neg[i] = new double[numPlayers];
            }
            
            attacksWithMe = new double[numPlayers];
            othersAttacksOn = new double[numPlayers];
            badGuys = new double[numPlayers];
            badGuysCopy = new double[numPlayers];
            meImporta = new double[numPlayers];
            theCurComm = new int[numPlayers];
            keepingStrength = new double[numPlayers];

            nPlayers = numPlayers;
            isInitialized = true;
        }

        // copy my genes into genes
        // if (playerIdx < 99999) {
        if (playerIdx == -1) {
            // assassinGenes();
            assassinDefender();
            printT(playerIdx, getString());
        }
        else {
            // copy in the current set of genes
            int currentPool = determineGenePool(playerIdx, numPlayers, popularities);
            int empiezaGene = (currentPool * (numGenes / numGeneCopies));
            // cout << playerIdx << " is in gene pool " << currentPool << "; empiezeGene: " << empiezaGene << endl;
            for (int i = 0; i < numGenes / numGeneCopies; i++)
                genes[i] = myGenes[i + empiezaGene];
            playedGenes = true;

            // cout << getString() << endl;

            // for testing purposes
            // double s = 0.0;
            // for (int i = 0; i < numPlayers; i++)
            //     s += popularities[i];
            // if (popularities[playerIdx] < (s / numPlayers)) {
            //     printT(playerIdx, "I'm among the poor!!!");
            //     genes[GENE_joinCoop] = 100;
            // }
        }

        for (int i = 0; i < numPlayers; i++) {
            findContract(i);
            tally[i] = unpaidDebt[i] = punishableDebt[i] = expectedReturn[i] = scaledBackNums[i] = 0.0;
            ave_return = received_value = invested_value = 0.0;
            ROI = coefs[KEEP_IDX];
        }

        expectedDefendFriendDamage = -99999;
    }
        
    void updateVars(double *received, double *popularities, int numTokens, int numPlayers, int playerIdx) {
        int currentPool = determineGenePool(playerIdx, numPlayers, popularities);
        int empiezaGene = (currentPool * (numGenes / numGeneCopies));
        printT(playerIdx, "gene pool: " + to_string(currentPool));
        // cout << playerIdx << " is in gene pool " << currentPool << "; empiezeGene: " << empiezaGene << endl;
        for (int i = 0; i < numGenes / numGeneCopies; i++)
            genes[i] = myGenes[i + empiezaGene];

        printT(playerIdx, "\nupdateVars:");

        popHistory.push_back(popularities);

        // update tally and punishableDebt
        for (int i = 0; i < numPlayers; i++) {
            if (i == playerIdx)
                tally[i] = 0.0;
            else
                tally[i] += received[i] * numTokens * popHistory[popHistory.size()-2][i];

            if ((tally[i] < 0.0) && (unpaidDebt[i] < 0.0)) {
                punishableDebt[i] = -getMax(unpaidDebt[i], tally[i]);
            }
            else
                punishableDebt[i] = 0.0;

            unpaidDebt[i] = tally[i];
        }

        // printT(playerIdx, "prev_popularities: " + vec2String(popHistory[popHistory.size()-2], numPlayers));
        // printT(playerIdx, "received: " + vec2String(received, numPlayers));
        // printT(playerIdx, "tally: " + vec2String(tally, numPlayers));

        // update scaledBackNums
        getScaleBack(playerIdx, numPlayers);

        printT(playerIdx, " scaled_back: " + vec2String(scaledBackNums, numPlayers));

        // printT(playerIdx, " popHistory: " + vec2String(popHistory[popHistory.size()-2], numPlayers));

        // update info about receiving
        received_value *= 1.0 - alpha;
        for (int i = 0; i < numPlayers; i++) {
            if (i == playerIdx)
                received_value += received[i] * numTokens * popHistory[popHistory.size()-2][i] * coefs[KEEP_IDX];
            else if (received[i] < 0)
                received_value += received[i] * numTokens * popHistory[popHistory.size()-2][i] * coefs[STEAL_IDX];
            else
                received_value += received[i] * numTokens * popHistory[popHistory.size()-2][i] * coefs[GIVE_IDX];
        }
        // printT(playerIdx, " received_value: " + to_string(received_value));
        invested_value *= 1.0 - alpha;
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++)
            s += getMax(prevAllocations[i], 0.0) * popHistory[popHistory.size()-2][playerIdx];
        invested_value += s;
        if (invested_value > 0.0)
            ROI = getMax(received_value / invested_value, coefs[KEEP_IDX]);
        else
            ROI = coefs[KEEP_IDX];
        
        printT(playerIdx, " invested " + to_string(invested_value) + "; got " + to_string(received_value));
        printT(playerIdx, " received: " + vec2String(received, numPlayers));
        printT(playerIdx, " ROI: " + to_string(ROI));
        printT(playerIdx, "");

        // cout << genes[GENE_initialDefense] << endl;
    }

    int determineGenePool(int playerIdx, int numPlayers, double *popularities) {
        // assume either 1 or 3 gene copies
        if (numGeneCopies == 1)
            return 0;

        if (numGeneCopies != 3) {
            cout << "GeneAgent not configured for " << numGeneCopies << " gene copies" << endl;
            exit(-1);
        }

        // compute the mean
        double m = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            m += popularities[i];
        }
        m /= numPlayers;
        double ratio = popularities[playerIdx] / m;
        printT(playerIdx, "ratio: " + to_string(ratio));
        if (ratio > 1.25)
            return 2;
        else if (ratio < 0.75)
            return 0;
        else
            return 1;
    }

    void findContract(int index) {
        string fnombre = "Contracts/contract_" + to_string(index) + ".txt";
        ifstream input(fnombre);

        if (input) {
            govPlayers[index]->installGovMent(input);
            input.close();
        }
    }

    void updateIndebtedness(int roundNum, int playerIdx, int numPlayers, int *allocations, double *popularities) {
        for (int i = 0; i < numPlayers; i++) {
            if (i == playerIdx)
                tally[i] = 0.0;
            else
                tally[i] -= getMax(allocations[i], 0.0) * popularities[playerIdx];
        }

        double lmbda = 1.0 / (roundNum + 1.0);
        if (lmbda < alpha)
            lmbda = alpha;

        double s = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            expectedReturn[i] = ((1.0-lmbda) * expectedReturn[i]) + (lmbda * allocations[i] * popularities[playerIdx]);
            s += expectedReturn[i];
        }
        
        ave_return = s / numPlayers;
    }

    void printT(int ind, string msg) {
        if (ind == theTracked)
            cout << msg << endl;
    }

    string vec2String(double *vec, int len) {
        string s;
        for (int i = 0; i < len; i++) {
            s += to_string(vec[i]) + " ";
        }

        return s;
    }

    string vec2String(int *vec, int len) {
        string s;
        for (int i = 0; i < len; i++)
            s += to_string(vec[i]) + " ";

        return s;
    }

    string vec2String(bool *vec, int len) {
        string s;
        for (int i = 0; i < len; i++)
            s += to_string((int)(vec[i])) + " ";

        return s;
    }

    double getMax(double o1, double o2) {
        if (o1 > o2)
            return o1;
        return o2;
    }

    void getScaleBack(int playerIdx, int numPlayers) {
        double debtLimit, denom, perc;

        for (int i = 0; i < numPlayers; i++) {
            scaledBackNums[i] = 1.0;

            if ((i == playerIdx) || govPlayers[i]->govPlayer)
                continue;

            if (punishableDebt[i] > 0.0) {
                debtLimit = genes[GENE_otherishDebtLimits] / 25.0;
                printT(playerIdx, to_string(debtLimit));
                if (debtLimit > 0.0) {
                    denom = getMax(expectedReturn[i], ave_return) * debtLimit;

                    if (denom == 0)
                        scaledBackNums[i] = 0.0;
                    else {
                        perc = 1.0 - (punishableDebt[i] / denom);
                        if (perc > 0.0)
                            scaledBackNums[i] = perc;
                        else
                            scaledBackNums[i] = 0.0;
                    }
                }
            }
        }
    }

    void computeUsefulQuantities(int roundNum, int numPlayers, int playerIdx, int numTokens, double **influence) {
        int i, j;

        if (roundNum > 0) {
            for (i = 0; i < numPlayers; i++) {
                for (j = 0; j < numPlayers; j++) {
                    inflNegPrev[i][j] = inflNeg[i][j];
                }
            }
        }
        else {
            for (i = 0; i < numPlayers; i++) {
                for (j = 0; j < numPlayers; j++) {
                    inflNegPrev[i][j] = 0.0;
                }
            }
        }

        for (i = 0; i < numPlayers; i++) {
            for (j = 0; j < numPlayers; j++) {
                inflPos[i][j] = getMax(influence[i][j], 0.0);
                inflNeg[i][j] = getMax(-influence[i][j], 0.0);
            }
        }

        for (i = 0; i < numPlayers; i++) {
            inflPos_sumcol[i] = sumMCol(inflPos, i, numPlayers);
            inflPos_sumrow[i] = sumMRow(inflPos, i, numPlayers);
        }

        if (roundNum == 0) {
            for (i = 0; i < numPlayers; i++) {
                for (j = 0; j < numPlayers; j++)
                    sumInflPos[i][j] = 0.0;
                attacksWithMe[i] = othersAttacksOn[i] = badGuys[i] = 0.0;
            }
            inflictedDamageRatio = 1.0;
        }
        else {
            for (i = 0; i < numPlayers; i++) {
                for (j = 0; j < numPlayers; j++)
                    sumInflPos[i][j] += inflPos[i][j];
            }

            double w = 0.2, val, amount, sumAmount, newRatio;
            for (i = 0; i < numPlayers; i++) {
                val = 0.0;
                for (j = 0; j < numPlayers; j++) {
                    amount = getMax(-(influence[j][i] - (prevInfluence[j][i] * (1.0 - alpha))), 0.0);
                    val += amount;
                    if ((playerIdx != i) && (prevAllocations[i] < 0.0))
                        attacksWithMe[j] -= amount;
                }
                sumAmount = val;
                val -= getMax(-(influence[playerIdx][i] - (prevInfluence[playerIdx][i] * (1.0 - alpha))), 0.0);
                othersAttacksOn[i] = (othersAttacksOn[i] * w) + ((1.0 - w) * val);
                if ((i != playerIdx) && (prevAllocations[i] < 0.0)) {
                    if (expectedDefendFriendDamage != -99999) {
                        newRatio = sumAmount / expectedDefendFriendDamage;
                        inflictedDamageRatio = 0.5 * inflictedDamageRatio + 0.5 * newRatio;
                    }
                }
            }

            // see which players are bad guys
            for (i = 0; i < numPlayers; i++) {
                badGuys[i] *= (1.0 - alpha);
                badGuysCopy[i] = badGuys[i];
                for (j = 0; j < numPlayers; j++)
                    newSteals[i][j] = inflNeg[i][j] - (inflNegPrev[i][j] * (1.0 - alpha));
            }

            for (i = 0; i < numPlayers; i++) {
                for (j = 0; j < numPlayers; j++) {
                    if (newSteals[i][j] > 5.0) {
                        if (badGuysCopy[j] < 0.2) {
                            if (badGuysCopy[i] < 0.2)
                                printT(playerIdx, ">>>>>> me thinks " + to_string(i) + " is a new bad guy");
                            badGuys[i] += newSteals[i][j];
                            if (badGuys[i] > 1.0)
                                badGuys[i] = 1.0;
                        }
                        else {
                            double sumrow = sumMRow(inflNeg, j, numPlayers);
                            double sumcol = sumMCol(inflNeg, j, numPlayers);
                            if ((sumrow * 0.9) < sumcol) {
                                printT(playerIdx, ">>>>>> bad guy " + to_string(j) + " has paid for its crimes");
                                badGuys[j] = 0.0;
                            }
                        }
                    }
                }
            }

            // print stuff
            printT(playerIdx, "   que mala onda: " + vec2String(badGuys, numPlayers));
            printT(playerIdx, " attacksWithMe: " + vec2String(attacksWithMe, numPlayers));
            printT(playerIdx, " othersAttacksOn: " + vec2String(othersAttacksOn, numPlayers));
            printT(playerIdx, "");

            // if (playerIdx == theTracked) {
            //     printT(playerIdx, "inflNeg:");
            //     for (int i = 0; i < numPlayers; i++) {
            //         for (int j = 0; j < numPlayers; j++) {
            //             printf("%.3lf ", inflNeg[i][j]);
            //         }
            //         printf("\n");
            //     }
            //     printf("\n");
            // }

        }
    }

    double sumMCol(double **x, int ind, int numPlayers) {
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++)
            s += x[i][ind];
        
        return s;
    }

    double sumMRow(double **x, int ind, int numPlayers) {
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++)
            s += x[ind][i];
        
        return s;
    }

    double sumVec(double *v, int len) {
        double sm = 0.0;
        for (int i = 0; i < len; i++)
            sm += v[i];

        return sm;
    }

    double sumVec(int *v, int len) {
        int sm = 0.0;
        for (int i = 0; i < len; i++)
            sm += v[i];

        return sm;
    }

    string getCommunitiesString(vector< set<int> > c) {
        string str = "{";
        for (int s = 0; s < c.size(); s++) {
            str += "(";
            for (set<int>::iterator itr = c[s].begin(); itr != c[s].end(); itr++) {
                str += to_string(*itr) + " ";
            }
            str += "),";
        }
        str += "}";

        return str;
    }

    CommunityEvaluation *groupAnalysis(int roundNum, int numPlayers, int playerIdx, double *popularities, double **influence, vector< set<int> > &communities) {
        CommunityEvaluation *elijo = NULL;

        computeAdjacencyMatrices(numPlayers);

        double modularity;
        if (roundNum == 0) {
            modularity = louvainMethod_phase1(numPlayers, A_pos, A_neg, communities);
            printT(playerIdx, "");
            printT(playerIdx, " communities: " + getCommunitiesString(communities));
            printT(playerIdx, " modularity: " + to_string(modularity));

            coalitionTarget = computeCoalitionTarget(roundNum, numPlayers, popularities, communities, playerIdx);

            elijo = randomSelections(numPlayers, playerIdx, popularities);

            printT(playerIdx, "chosen community: " + elijo->getString_short());
        }
        else {

            // std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
            // if (playerIdx == theTracked) {
            //     printT(playerIdx, "A_pos");
            //     for (int i = 0; i < numPlayers; i++) {
            //         for (int j = 0; j < numPlayers; j++) {
            //             printf("%.3lf ", A_pos[i][j]);
            //         }
            //         printf("\n");
            //     }
            //     printf("\n");
            //     printT(playerIdx, "A_neg");
            //     for (int i = 0; i < numPlayers; i++) {
            //         for (int j = 0; j < numPlayers; j++) {
            //             printf("%.3lf ", A_neg[i][j]);
            //         }
            //         printf("\n");
            //     }
            //     printf("\n");
            // }

            vector< set<int> > communities_ph1;
            double modularity_ph1 = louvainMethod_phase1(numPlayers, A_pos, A_neg, communities_ph1);
            printT(playerIdx, " communities_ph1: " + getCommunitiesString(communities_ph1));
            printT(playerIdx, " modularity_ph1: " + to_string(modularity_ph1));

            // std::chrono::steady_clock::time_point p1 = std::chrono::steady_clock::now();
            // double phase1 = std::chrono::duration_cast<std::chrono::microseconds>(p1 - begin).count() / 1000000.0;
            // printT(playerIdx, "phase1: " + to_string(phase1));

            vector< set<int> > communities_mega;
            modularity = louvainMethod_phase2(numPlayers, A_pos, A_neg, modularity_ph1, communities_ph1, communities_mega);

            // std::chrono::steady_clock::time_point p2 = std::chrono::steady_clock::now();
            // double phase2 = std::chrono::duration_cast<std::chrono::microseconds>(p2 - p1).count() / 1000000.0;
            // printT(playerIdx, "phase2: " + to_string(phase2));

            enumerateCommunities(modularity_ph1, communities_ph1, modularity, communities_mega, communities);
            printT(playerIdx, " communities: " + getCommunitiesString(communities));
            printT(playerIdx, " modularity: " + to_string(modularity));
            printT(playerIdx, "");

            coalitionTarget = computeCoalitionTarget(roundNum, numPlayers, popularities, communities, playerIdx);

            printT(playerIdx, "coalitionTarget: " + to_string(coalitionTarget));

            // std::chrono::steady_clock::time_point p3 = std::chrono::steady_clock::now();
            // double enumCom = std::chrono::duration_cast<std::chrono::microseconds>(p3 - p2).count() / 1000000.0;
            // printT(playerIdx, "enumCom: " + to_string(enumCom));

            elijo = envisionCommunities(numPlayers, playerIdx, popularities, influence, A_pos, A_neg, communities_ph1, communities, modularity);

            printT(playerIdx, "\nchosen community: " + elijo->getString_short());
            printT(playerIdx, elijo->getString());

            // std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
            // double envision = std::chrono::duration_cast<std::chrono::microseconds>(end - p3).count() / 1000000.0;
            // printT(playerIdx, "envision: " + to_string(envision));

            // double totalAnalysis = std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count() / 1000000.0;
            // // std::cout << "totalAnalysis = " << totalAnalysis << " seconds" << std::endl;
            // printT(playerIdx, "totalAnalysis: " + to_string(totalAnalysis));
        }

        // printT(playerIdx, " coalitionTarget: " + to_string(coalitionTarget));

        return elijo;
    }

    CommunityEvaluation *envisionCommunities(int numPlayers, int playerIdx, double *popularities, double **influence, double **A_pos, double **A_neg, vector< set<int> > communities_ph1, vector< set<int> > communities, double modularity) {
        vector<CommunityEvaluation *> potentialCommunities;

        // cout << "*** envision " << playerIdx << endl;

        // printT(playerIdx, "popularities: " + vec2String(popularities, numPlayers));

        // std::chrono::steady_clock::time_point zero = std::chrono::steady_clock::now();

        int s_idx = findCommunity(playerIdx, communities);
        // printT(playerIdx, "my community: " + getSetString(communities[s_idx]));

        // Change on June 2
        double curCommSize = 0.0;
        for (set<int>::iterator i = communities[s_idx].begin(); i != communities[s_idx].end(); i++) {
            // printT(playerIdx, to_string(popularities[*i]));
            curCommSize += popularities[*i];
        }
        curCommSize /= sumVec(popularities, numPlayers);

        // std::chrono::steady_clock::time_point uno = std::chrono::steady_clock::now();
        // double findComm = std::chrono::duration_cast<std::chrono::microseconds>(uno - zero).count() / 1000000.0;
        // printT(playerIdx, "    findComm: " + to_string(findComm));

        // printT(playerIdx, "curCommSize: " + to_string(curCommSize));

        // cout << "make sets" << endl;

        vector< set<int> > c = communities;

        // std::chrono::steady_clock::time_point dos = std::chrono::steady_clock::now();
        // double copyComm = std::chrono::duration_cast<std::chrono::microseconds>(dos - uno).count() / 1000000.0;
        // printT(playerIdx, "    copyComm: " + to_string(copyComm));

        double m = determineCommunities(numPlayers, playerIdx, popularities, c, s_idx, A_pos, A_neg);

        // std::chrono::steady_clock::time_point tres = std::chrono::steady_clock::now();
        // double determineComm = std::chrono::duration_cast<std::chrono::microseconds>(tres - dos).count() / 1000000.0;
        // printT(playerIdx, "    determineComm: " + to_string(determineComm));

        set<int> s = communities[s_idx];
        removeMostlyDead(&s, playerIdx, popularities);

        // std::chrono::steady_clock::time_point cuatro = std::chrono::steady_clock::now();
        // double removeDead = std::chrono::duration_cast<std::chrono::microseconds>(cuatro - tres).count() / 1000000.0;
        // printT(playerIdx, "    removeDead: " + to_string(removeDead));

        potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));

        // std::chrono::steady_clock::time_point cinco = std::chrono::steady_clock::now();
        // double addComm = std::chrono::duration_cast<std::chrono::microseconds>(cinco - cuatro).count() / 1000000.0;
        // printT(playerIdx, "    addComm: " + to_string(addComm));

        // cout << "one" << endl;

        // combine with any other group
        for (int i = 0; i < communities.size(); i++) {
            if (i != s_idx) {
                c = communities;
                c[s_idx].insert(c[i].begin(), c[i].end());
                if (!alreadyIn(c[s_idx], potentialCommunities)) {
                    // printT(playerIdx, "new set: " + getSetString(c[s_idx]));
                    c.erase(c.begin()+i);
                    // printT(playerIdx, getCommunitiesString(c));
                    int ind = findCommunity(playerIdx, c);
                    set<int> s = c[ind];
                    double m = determineCommunities(numPlayers, playerIdx, popularities, c, ind, A_pos, A_neg);
                    removeMostlyDead(&s, playerIdx, popularities);
                    potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                }
            }
        }

        // cout << "two" << endl;

        // move to a different group
        for (int i = 0; i < communities.size(); i++) {
            if (i != s_idx) {
                c = communities;
                c[i].insert(playerIdx);
                if (!alreadyIn(c[i], potentialCommunities)) {
                    c[s_idx].erase(playerIdx);
                    int ind = findCommunity(playerIdx, c);
                    set<int> s = c[ind];
                    double m = determineCommunities(numPlayers, playerIdx, popularities, c, ind, A_pos, A_neg);
                    removeMostlyDead(&s, playerIdx, popularities);
                    potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                }
            }
        }

        // cout << "three" << endl;

        // add a member from another group
        for (int i = 0; i < numPlayers; i++) {
            if (communities[s_idx].find(i) == communities[s_idx].end()) {
                c = communities;
                for (int j = 0; j < c.size(); j++) {
                    if (c[j].find(i) != c[j].end()) {
                        c[j].erase(i);
                        break;
                    }
                }
                c[s_idx].insert(i);
                if (!alreadyIn(c[s_idx], potentialCommunities)) {
                    double m = determineCommunities(numPlayers, playerIdx, popularities, c, s_idx, A_pos, A_neg);
                    set<int> s = c[s_idx];
                    removeMostlyDead(&s, playerIdx, popularities);
                    potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                }
            }
        }

        // cout << "four" << endl;

        // subtract a member from the group (that isn't playerIdx)
        for (set<int>::iterator i = communities[s_idx].begin(); i != communities[s_idx].end(); i++) {
            if (*i != playerIdx) {
                c = communities;
                c[s_idx].erase(*i);
                if (!alreadyIn(c[s_idx], potentialCommunities)) {
                    set<int> ns;
                    ns.insert(*i);
                    c.push_back(ns);
                    double m = determineCommunities(numPlayers, playerIdx, popularities, c, s_idx, A_pos, A_neg);
                    set<int> s = c[s_idx];
                    // printT(playerIdx, getSetString(s) + ": " + to_string(m));
                    removeMostlyDead(&s, playerIdx, popularities);
                    potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                }
            }
        }

        // cout << "half" << endl;

        int s2_idx = findCommunity(playerIdx, communities_ph1);
        if (communities[s_idx] != communities_ph1[s2_idx]) {    // Change on May 29
            s_idx = s2_idx;

            vector< set<int> > c = communities_ph1;    // does this make a deep copy?
            double m = determineCommunities(numPlayers, playerIdx, popularities, c, s_idx, A_pos, A_neg);
            set<int> s = communities_ph1[s_idx];
            removeMostlyDead(&s, playerIdx, popularities);
            potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));

            // combine with any other group
            for (int i = 0; i < communities_ph1.size(); i++) {
                if (i != s_idx) {
                    c = communities_ph1;
                    c[s_idx].insert(c[i].begin(), c[i].end());
                    if (!alreadyIn(c[s_idx], potentialCommunities)) {
                        // printT(playerIdx, "new set: " + getSetString(c[s_idx]));
                        c.erase(c.begin()+i);
                        // printT(playerIdx, getCommunitiesString(c));
                        int ind = findCommunity(playerIdx, c);
                        set<int> s = c[ind];
                        double m = determineCommunities(numPlayers, playerIdx, popularities, c, ind, A_pos, A_neg);
                        removeMostlyDead(&s, playerIdx, popularities);
                        potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                    }
                }
            }

            // move to a different group
            for (int i = 0; i < communities_ph1.size(); i++) {
                if (i != s_idx) {
                    c = communities_ph1;
                    c[i].insert(playerIdx);
                    if (!alreadyIn(c[i], potentialCommunities)) {
                        c[s_idx].erase(playerIdx);
                        int ind = findCommunity(playerIdx, c);
                        set<int> s = c[ind];
                        double m = determineCommunities(numPlayers, playerIdx, popularities, c, ind, A_pos, A_neg);
                        removeMostlyDead(&s, playerIdx, popularities);
                        potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                    }
                }
            }

            // add a member from another group
            for (int i = 0; i < numPlayers; i++) {
                if (communities_ph1[s_idx].find(i) == communities_ph1[s_idx].end()) {
                    c = communities_ph1;
                    for (int j = 0; j < c.size(); j++) {
                        if (c[j].find(i) != c[j].end()) {
                            c[j].erase(i);
                            break;
                        }
                    }
                    c[s_idx].insert(i);
                    if (!alreadyIn(c[s_idx], potentialCommunities)) {
                        double m = determineCommunities(numPlayers, playerIdx, popularities, c, s_idx, A_pos, A_neg);
                        // printT(playerIdx, getCommunitiesString(c));
                        set<int> s = c[s_idx];
                        removeMostlyDead(&s, playerIdx, popularities);
                        potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                    }
                }
            }

            // subtract a member from the group (that isn't playerIdx)
            for (set<int>::iterator i = communities_ph1[s_idx].begin(); i != communities_ph1[s_idx].end(); i++) {
                if (*i != playerIdx) {
                    c = communities_ph1;
                    c[s_idx].erase(*i);
                    if (!alreadyIn(c[s_idx], potentialCommunities)) {
                        set<int> ns;
                        ns.insert(*i);
                        c.push_back(ns);
                        double m = determineCommunities(numPlayers, playerIdx, popularities, c, s_idx, A_pos, A_neg);
                        set<int> s = c[s_idx];
                        removeMostlyDead(&s, playerIdx, popularities);
                        potentialCommunities.push_back(new CommunityEvaluation(s, m, getCentrality(s, playerIdx, popularities), getCollectiveStrength(popularities, s, curCommSize, numPlayers), getFamiliarity(s, playerIdx, numPlayers, influence), getIngroupAntisocial(s, playerIdx)));
                    }
                }
            }
        }

        // cout << "made sets" << endl;

        double min_mod = modularity;
        for (int c = 0; c < potentialCommunities.size(); c++) {
            // printT(playerIdx, to_string(potentialCommunities[c]->modularity));
            if (potentialCommunities[c]->modularity < min_mod)
                min_mod = potentialCommunities[c]->modularity;
        }

        // printT(playerIdx, "min_mod: " + to_string(min_mod));

        int elegir = 0;
        double mx = -99999.0;
        for (int c = 0; c < potentialCommunities.size(); c++) {
            // printT(playerIdx, to_string(potentialCommunities[c]->modularity) + " " + to_string(min_mod) + " " + to_string(modularity) + " " + to_string(min_mod));
            if (modularity == min_mod)
                potentialCommunities[c]->modularity = 1.0;
            else
                potentialCommunities[c]->modularity = (potentialCommunities[c]->modularity - min_mod) / (modularity - min_mod);

            // Change on May 9
            potentialCommunities[c]->computeScore(genes);
            if (potentialCommunities[c]->score > mx) {
                elegir = c;
                mx = potentialCommunities[c]->score;
            }

            // if (playerIdx == theTracked)
            //     cout << potentialCommunities[c]->getString() << endl;
        }

        // adding this in on May 4
        double mejor;
        for (int i = 0; i < numPlayers; i++)
            meImporta[i] = 0.0;
        for (set<int>::iterator i = potentialCommunities[elegir]->s.begin(); i != potentialCommunities[elegir]->s.end(); i++) {
            mejor = 1.0;
            if (*i != playerIdx) {
                for (int c = 0; c < potentialCommunities.size(); c++) {
                    if (potentialCommunities[c]->s.find(*i) == potentialCommunities[c]->s.end())
                        mejor = -getMax(-mejor, -((potentialCommunities[elegir]->score - potentialCommunities[c]->score) / potentialCommunities[elegir]->score));
                }
            }
            meImporta[*i] = mejor;
        }

        // printT(playerIdx, "meImporta: " + vec2String(meImporta, numPlayers));

        // cout << "done envision" << endl;
        
        // delete the unselected communities
        for (int c = 0; c < potentialCommunities.size(); c++) {
            if (c != elegir)
                delete potentialCommunities[c];
        }

        return potentialCommunities[elegir];
    }

    bool alreadyIn(set<int> s, vector<CommunityEvaluation *> potentialCommunities) {
        for (int c = 0; c < potentialCommunities.size(); c++) {
            if (potentialCommunities[c]->s == s)
                return true;
        }

        return false;
    }

    string getSetString(set<int> s) {
        string str = "";
        for (set<int>::iterator itr = s.begin(); itr != s.end(); itr++) {
            str += to_string(*itr) + " ";
        }

        return str;
    }


    void removeMostlyDead(set<int> *s, int playerIdx, double *popularities) {
        // cout << "mostly: " << getSetString(*s) << endl;
        if (popularities[playerIdx] < 10.0)
            return;

        for (set<int>::iterator i = s->begin(); i != s->end(); i++) {
            if (popularities[*i] < (0.1 * popularities[playerIdx])) {
                s->erase(*i);
                i = s->begin();
            }
        }
        // cout << "dead" << endl;
    }

    double determineCommunities(int numPlayers, int playerIdx, double *popularities, vector< set<int> > c, int s_idx, double **A_pos, double **A_neg) {
        // cout << "x: " << s_idx << endl;

        // std::chrono::steady_clock::time_point zero = std::chrono::steady_clock::now();

        set<int> s = c[s_idx];
        c.erase(c.begin() + s_idx);
        vector< set<int> > c_mega, c_prime;

        // std::chrono::steady_clock::time_point uno = std::chrono::steady_clock::now();
        // double removeComm = std::chrono::duration_cast<std::chrono::microseconds>(uno - zero).count() / 1000000.0;
        // printT(playerIdx, "        removeComm: " + to_string(removeComm));

        // cout << "y" << endl;
        double m = louvainMethod_phase2(numPlayers, A_pos, A_neg, 0.0, c, c_mega);  // is default modularity_ph1 = 0.0 ok

        // std::chrono::steady_clock::time_point dos = std::chrono::steady_clock::now();
        // double phase2 = std::chrono::duration_cast<std::chrono::microseconds>(dos - uno).count() / 1000000.0;
        // printT(playerIdx, "        phase2: " + to_string(phase2));

        enumerateCommunities(0, c, 1, c_mega, c_prime);
        c_prime.push_back(s);

        // std::chrono::steady_clock::time_point tres = std::chrono::steady_clock::now();
        // double enumComm = std::chrono::duration_cast<std::chrono::microseconds>(tres - dos).count() / 1000000.0;
        // printT(playerIdx, "        enumComm: " + to_string(enumComm));

        // cout << "z" << endl;
        // printT(playerIdx, "c_prime: " + getCommunitiesString(c_prime));
        for (int j = 0; j < c_prime.size(); j++) {
            for (set<int>::iterator i = c_prime[j].begin(); i != c_prime[j].end(); i++)
                theCurComm[*i] = j;
        }
        m = computeSignedModularity(numPlayers, theCurComm, A_pos, A_neg);
        // m = computeSignedModularity(numPlayers, c_prime, A_pos, A_neg);

        // std::chrono::steady_clock::time_point cuatro = std::chrono::steady_clock::now();
        // double signedMod = std::chrono::duration_cast<std::chrono::microseconds>(cuatro - tres).count() / 1000000.0;
        // printT(playerIdx, "        signedMod: " + to_string(signedMod));

        // cout << "w" << endl;

        return m;
    }

    double computeSignedModularity(int numPlayers, int *cur_comm, double **A_pos, double **A_neg) {
        double *k = new double[numPlayers];
        for (int i = 0; i < numPlayers; i++) {
            k[i] = sumVec(A_pos[i], numPlayers);
        }
        double m = sumVec(k, numPlayers);

        double modu = alphaMia * computeModularity(numPlayers, cur_comm, A_pos, k, m);

        for (int i = 0; i < numPlayers; i++) {
            k[i] = sumVec(A_neg[i], numPlayers);
        }
        m = sumVec(k, numPlayers);
        modu -= (1.0 - alphaMia) * computeModularity(numPlayers, cur_comm, A_neg, k, m);

        delete[] k;

        return modu;
    }

    // double computeSignedModularity(int numPlayers, vector< set<int> > c, double **A_pos, double **A_neg) {
    //     double m = alphaMia * computeModularity2(numPlayers, c, A_pos);
    //     m -= (1.0 - alphaMia) * computeModularity2(numPlayers, c, A_neg);

    //     return m;
    // }

    int findCommunity(int playerIdx, vector< set<int> > communities) {
        for (int i = 0; i < communities.size(); i++) {
            if (communities[i].find(playerIdx) != communities[i].end())
                return i;
        }

        printf("Problem: Didn't find a community\n");
        exit(1);

        return -1;
    }

    void enumerateCommunities(double modularity_ph1, vector< set<int> > communities_ph1, double modularity, vector< set<int> > communities_mega, vector< set<int> > &communities) {
        if (modularity > modularity_ph1) {
            for (int m = 0; m < communities_mega.size(); m++) {
                set<int> s;
                for (set<int>::iterator i = communities_mega[m].begin(); i != communities_mega[m].end(); i++) {
                    for (set<int>::iterator j = communities_ph1[*i].begin(); j != communities_ph1[*i].end(); j++) {
                        s.insert(*j);
                    }
                }
                communities.push_back(s);
            }
        }
        else {
            communities = communities_ph1;
        }
    } 

    CommunityEvaluation *randomSelections(int numPlayers, int playerIdx, double *popularities) {
        // set<int> plyrs;
        // for (int i = 0; i < numPlayers; i++) {
        //     if (playerIdx != i)
        //         plyrs.insert(i);
        // }

        int num;
        set<int> s;
        s.insert(playerIdx);
        double pop = popularities[playerIdx];
        double total_pop = sumVec(popularities, numPlayers);
        while ((pop / total_pop) < coalitionTarget) {
            // REMOVING RANDOM
            // num = rand() % plyrs.size();
            // set<int>::iterator itr = plyrs.begin();
            // for (int i = 0; i < num; i++, itr++);
            // s.insert(*itr);
            // plyrs.erase(*itr);
            // pop += popularities[*itr];

            if (forcedRandom)
                num = (getRand() + playerIdx) % numPlayers;
            else
                num = rand() % numPlayers;

            // printT(playerIdx, "num: " + to_string(num));
            if (s.find(num) == s.end()) {
                s.insert(num);
                pop += popularities[num];
                // printT(playerIdx, "s_now: " + getSetString(s));
            }
            
        }

        return new CommunityEvaluation(s, 0.0, 0.0, 0.0, 0.0, 0.0);
    }

    double computeCoalitionTarget(int roundNum, int numPlayers, double *popularities, vector< set<int> > communities, int playerIdx) {
        if (genes[GENE_coalitionTarget] < 80) {
            if (genes[GENE_coalitionTarget] < 5)
                return 0.05;
            else
                return genes[GENE_coalitionTarget] / 100.0;
        }
        else if (roundNum < 3)
            return 0.51;
        else {
            bool in_mx = false;
            int mx_ind = -1;
            vector<double> fuerza;
            double tot_pop = sumVec(popularities, numPlayers);
            for (int s = 0; s < communities.size(); s++) {
                double tot = 0.0;
                for (set<int>::iterator itr = communities[s].begin(); itr != communities[s].end(); itr++)
                    tot += popularities[*itr];
                fuerza.push_back(tot/ tot_pop);
                if (mx_ind == -1)
                    mx_ind = 0;
                else if (tot > fuerza[mx_ind]) {
                    mx_ind = fuerza.size()-1;
                    if (communities[s].find(playerIdx) != communities[s].end())
                        in_mx = true;
                    else
                        in_mx = false;
                }
            }
            sort(fuerza.begin(), fuerza.end(), greater<double>());
            
            if (playerIdx == theTracked) {
                printf("    fuerza: ");
                for (int i = 0; i < fuerza.size(); i++)
                    printf("%lf ", fuerza[i]);
                printf("\n");
            }

            if (in_mx)
                return -getMax(-(fuerza[1] + 0.05), -55);
            else
                return -getMax(-(fuerza[0] + 0.05), -55);;
        }

        printf("Error: shoud never reach here\n");
        exit(1);

        return -1;
    }

    void computeAdjacencyMatrices(int numPlayers) {
        double theAve, theMin, theMax;
        for (int i = 0; i < numPlayers; i++) {
            A_pos[i][i] = inflPos[i][i];
            A_neg[i][i] = inflNeg[i][i];
            for (int j = i+1; j < numPlayers; j++) {
                theAve = (inflPos[i][j] + inflPos[j][i]) / 2.0;
                theMin = -getMax(-inflPos[i][j], -inflPos[j][i]);
                A_pos[i][j] = A_pos[j][i] = (theAve + theMin) / 2.0;

                theAve = (inflNeg[i][j] + inflNeg[j][i]) / 2.0;
                theMax = getMax(inflNeg[i][j], inflNeg[j][i]);
                A_neg[i][j] = A_neg[j][i] = theMax; // (theAve + theMax) / 2.0;
            }
        }
    }

    double louvainMethod_phase1(int numPlayers, double **A_pos, double **A_neg, vector< set<int> > &communities) {
        if (numPlayers == 0)
            return 0.0;

        // set up all the variables
        int *currentCommunities = new int[numPlayers];
        set<int> theGroups;
        for (int i = 0; i < numPlayers; i++) {
            currentCommunities[i] = i;
            theGroups.insert(i);
        }

        int **comMatrix = new int*[numPlayers];
        for (int i = 0; i < numPlayers; i++) {
            comMatrix[i] = new int[numPlayers];
            for (int j = 0; j < numPlayers; j++) {
                if (i == j)
                    comMatrix[i][j] = 1;
                else
                    comMatrix[i][j] = 0;
            }
        }
        double *K_pos = new double[numPlayers];
        double *K_neg = new double[numPlayers];
        for (int i = 0; i < numPlayers; i++) {
            K_pos[i] = sumMRow(A_pos, i, numPlayers);
            K_neg[i] = sumMRow(A_neg, i, numPlayers);
        }
        double m_pos = sumVec(K_pos, numPlayers);
        double m_neg = sumVec(K_neg, numPlayers);

        int *comCounts = new int[numPlayers];
        for (int i = 0; i < numPlayers; i++)
            comCounts[i] = 1;

        // now loop until nobody wants to change groups
        bool hayCambio = true;
        int mx_com;
        double best_dQ, dQ_pos, dQ_neg, dQ;
        while (hayCambio) {
            hayCambio = false;
            for (int i = 0; i < numPlayers; i++) {
                mx_com = currentCommunities[i];
                best_dQ = 0.0;
                for (set<int>::iterator itr = theGroups.begin(); itr != theGroups.end(); itr++) {
                    int j = *itr;
                    if (currentCommunities[i] == j)
                        continue;
                    
                    dQ_pos = move_i_to_j(numPlayers, comMatrix, m_pos, K_pos, A_pos, i, j, currentCommunities[i]);
                    dQ_neg = move_i_to_j(numPlayers, comMatrix, m_neg, K_neg, A_neg, i, j, currentCommunities[i]);
                    // printf("   dQ_pos: %lf; dQ_neg: %lf\n", dQ_pos, dQ_neg);

                    dQ = alphaMia * dQ_pos - (1.0 - alphaMia) * dQ_neg;
                    if (dQ > best_dQ) {
                        mx_com = j;
                        best_dQ = dQ;
                    }
                }

                if (best_dQ > 0.0) {
                    comMatrix[currentCommunities[i]][i] = 0;
                    comCounts[currentCommunities[i]] -= 1;
                    if (comCounts[currentCommunities[i]] <= 0)
                        theGroups.erase(currentCommunities[i]);
                    comMatrix[mx_com][i] = 1;
                    comCounts[mx_com] += 1;
                    currentCommunities[i] = mx_com;
                    hayCambio = true;
                }
            }
        }

        // create the communities
        for (int i = 0; i < numPlayers; i++) {
            if (comCounts[i] > 0) {
                set<int> s;
                for (int j = 0; j < numPlayers; j++) {
                    if (comMatrix[i][j] == 1)
                        s.insert(j);
                }
                communities.push_back(s);
            }
        }

        // compute the modularity
        double the_modularity = alphaMia * computeModularity(numPlayers, currentCommunities, A_pos, K_pos, m_pos);
        the_modularity -= (1.0 - alphaMia) * computeModularity(numPlayers, currentCommunities, A_neg, K_neg, m_neg);

        delete[] currentCommunities;
        for (int i = 0; i < numPlayers; i++)
            delete[] comMatrix[i];
        delete[] comMatrix;
        delete[] K_pos;
        delete[] K_neg;
        delete[] comCounts;

        return the_modularity;
    }

    double louvainMethod_phase2(int numPlayers, double **A_pos, double **A_neg, double modularity_ph1, vector< set<int> > communities_ph1, vector< set<int> > &communities_mega) {
        int numCommunities = communities_ph1.size();
        double modularity;
        // cout << "    numCommunities: " << numCommunities << endl;

        // if (numCommunities > 1) {
        double **B_pos = new double*[numCommunities];
        double **B_neg = new double*[numCommunities];
        for (int i = 0; i < numCommunities; i++) {
            B_pos[i] = new double[numCommunities];
            B_neg[i] = new double[numCommunities];
            for (int j = 0; j < numCommunities; j++) {
                B_pos[i][j] = 0.0;
                B_neg[i][j] = 0.0;
                for (set<int>::iterator k = communities_ph1[i].begin(); k != communities_ph1[i].end(); k++) {
                    for (set<int>::iterator m = communities_ph1[j].begin(); m != communities_ph1[j].end(); m++) {
                        B_pos[i][j] += A_pos[*k][*m];
                        B_neg[i][j] += A_neg[*k][*m];
                    }
                }
            }
            // cout << vec2String(B_pos[i], numCommunities) << endl;
        }

        modularity = louvainMethod_phase1(numCommunities, B_pos, B_neg, communities_mega);

        for (int i = 0; i < numCommunities; i++) {
            delete[] B_pos[i];
            delete[] B_neg[i];
        }
        delete[] B_pos;
        delete[] B_neg;
        // }
        // else {
        //     communities_mega = communities_ph1;
        //     modularity = modularity_ph1;
        // }

        return modularity;
    }

    double computeModularity(int numPlayers, int *currentCommunities, double **A, double *k, double m) {
        if (m == 0)
            return 0.0;
        
        double Q = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            for (int j = 0; j < numPlayers; j++) {
                Q += deltar(currentCommunities, i, j) * (A[i][j] - ((k[i] * k[j]) / (2*m)));
            }
        }
        Q /= 2*m;

        return Q;
    }

    int deltar(int *currentCommunities, int i, int j) {
        if (currentCommunities[i] == currentCommunities[j])
            return 1;
        else
            return 0;
    }

    double computeModularity2(int numPlayers, vector< set<int> > communities, double **A) {
        double *k = new double[numPlayers];
        for (int i = 0; i < numPlayers; i++) {
            k[i] = sumVec(A[i], numPlayers);
        }
        double m = sumVec(k, numPlayers);

        if (m == 0)
            return 0.0;
        
        double Q = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            for (int j = 0; j < numPlayers; j++) {
                Q += deltar2(communities, i, j) * (A[i][j] - ((k[i] * k[j]) / (2*m)));
            }
        }
        Q /= 2*m;

        delete[] k;

        return Q;
    }

    int deltar2(vector< set<int> > c, int i, int j) {
        for (int s = 0; s < c.size(); s++) {
            if ((c[s].find(i) != c[s].end()) && (c[s].find(j) != c[s].end()))
                return 1;
        }

        return 0;
    }

    double move_i_to_j(int numPlayers, int **comMatrix, double m, double *K, double **A, int i, int com_j, int com_i) {
        // first, what is the change in modularity from putting i into j's community
        double sigma_in = 0.0;
        for (int k = 0; k < numPlayers; k++) {
            if (comMatrix[com_j][k] == 1)
                sigma_in += vecDotProduct(comMatrix[com_j], A[k], numPlayers);
        }
        double sigma_tot = vecDotProduct(comMatrix[com_j], K, numPlayers);
        double k_iin = vecDotProduct(comMatrix[com_j], A[i], numPlayers);
        double twoM = 2.0 * m;

        if (twoM == 0.0)
            return 0.0;

        double a = (sigma_in + 2*k_iin) / twoM;
        double b = (sigma_tot + K[i]) / twoM;
        double c = sigma_in / twoM;
        double d = sigma_tot / twoM;
        double e = K[i] / twoM;
        double dQ_in = (a - (b*b)) - (c - d*d - e*e);

        // second, what is the change in modularity from removing i from its community
        int *com = new int[numPlayers];
        for (int k = 0; k < numPlayers; k++)
            com[k] = comMatrix[com_i][k];
        com[i] = 0;
        sigma_in = 0.0;
        for (int k = 0; k < numPlayers; k++) {
            if (com[k] == 1)
                sigma_in += vecDotProduct(com, A[k], numPlayers);
        }
        sigma_tot = vecDotProduct(com, K, numPlayers);
        k_iin = vecDotProduct(com, A[i], numPlayers);

        a = (sigma_in + 2*k_iin) / twoM;
        b = (sigma_tot + K[i]) / twoM;
        c = sigma_in / twoM;
        d = sigma_tot / twoM;
        e = K[i] / twoM;
        double dQ_out = (a - (b*b)) - (c - d*d - e*e);

        delete[] com;

        return dQ_in - dQ_out;
    }

    double vecDotProduct(double *v1, double *v2, int numPlayers) {
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            s += v1[i] * v2[i];
        }
        return s;
    }

    double vecDotProduct(int *v1, double *v2, int numPlayers) {
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            s += v1[i] * v2[i];
        }
        return s;
    }

    double vecColDotProduct(double *v, double **M, int index, int numPlayers) {
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            s += v[i] * M[i][index];
        }
        return s;
    }

    double vecColDotProduct(int *v, double **M, int index, int numPlayers) {
        double s = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            s += v[i] * M[i][index];
        }
        return s;
    }

    double getCentrality(set<int> s, int playerIdx, double *popularities) {
        double group_sum = 0.0;
        double mx = 0.0;
        int num_greater = 0;
        for (set<int>::iterator i = s.begin(); i != s.end(); i++) {
            group_sum += popularities[*i];
            if (popularities[*i] > mx)
                mx = popularities[*i];
            if (popularities[*i] > popularities[playerIdx])
                num_greater ++;
        }

        if ((group_sum > 0.0) && (s.size() > 1)) {
            double ave_sum = group_sum / s.size();
            double aveVal = popularities[playerIdx] / ave_sum;
            double mxVal = popularities[playerIdx] / mx;
            double rankVal = 1.0 - (num_greater / (s.size() - 1.0));

            return (aveVal + mxVal + rankVal) / 3.0;
        }
        else
            return 1.0;
    }

    double getCollectiveStrength(double *popularities, set<int> s, double curCommSize, int numPlayers) {
        double proposed = 0.0;
        for (set<int>::iterator i = s.begin(); i != s.end(); i++) {
            proposed += popularities[*i];
        }
        proposed /= sumVec(popularities, numPlayers);

        double target;
        if (genes[GENE_coalitionTarget] == 0)
            target = 0.01;
        else
            target = genes[GENE_coalitionTarget] / 100.0;

        double base = 1.0 - (fabs(target - curCommSize) / target);
        if (base < 0.01)
            base = 0.01;
        base *= base;

        // cout << getSetString(s) << ": " << proposed << "; " << target << "; " << to_string(curCommSize) << "; " << to_string(base) << endl;
        if (fabs(proposed - curCommSize) <= 0.03)
            return base;
        else if (fabs(curCommSize - target) < fabs(proposed - target)) {
            double nbase = 1.0 - (fabs(target - proposed) / target);
            if (nbase < 0.01)
                nbase = 0.01;
            return nbase * nbase;
        }
        else {
            double baseline = (1.0 + base) / 2.0;
            double w = fabs(proposed - target) / fabs(curCommSize - target);
            return ((1.0 - w) * 1.0) + (baseline * w);
        }
    }

    double getFamiliarity(set<int> s, int playerIdx, int numPlayers, double **influence) {
        double mag = sumMCol(inflPos, playerIdx, numPlayers);
        double familiarity;
        if (mag > 0.0) {
            double randval = mag / numPlayers;
            double ind_loyalty = 0.0;
            double scaler = 1.0;
            for (set<int>::iterator i = s.begin(); i != s.end(); i++) {
                if ((scaledBackNums[*i] < 0.05) and (*i != playerIdx))
                    scaler *= (s.size() - 1.0) / s.size();

                if ((influence[*i][playerIdx] * scaledBackNums[*i]) > randval)
                    ind_loyalty += influence[*i][playerIdx] * scaledBackNums[*i];
                else
                    ind_loyalty += (influence[*i][playerIdx] * scaledBackNums[*i]) - randval;
            }
            familiarity = getMax(0.01, scaler * (ind_loyalty / mag));
        }
        else
            familiarity = 1.0;

        if (familiarity < 0.0)
            familiarity = 0.0;

        return familiarity;
    }

    double getIngroupAntisocial(set<int> s, int playerIdx) {
        double scl = 1.0;
        double piece = 1.0 / s.size();
        double remain = 1.0 - piece;
        for (set<int>::iterator i = s.begin(); i != s.end(); i++) {
            if (*i != playerIdx) {
                double the_investment = 0.0;
                double the_return = 0.0;
                for (set<int>::iterator j = s.begin(); j != s.end(); j++) {
                    if (*i != *j) {
                        the_investment += sumInflPos[*j][*i];
                        the_return += sumInflPos[*i][*j];
                    }
                }

                if (the_investment > 0.0) {
                    double val = the_return / the_investment;
                    if (val > 1.0)
                        val = 1.0;
                    scl *= piece * val + remain;
                }
            }
        }

        return scl;
    }

    int groupGivings(int roundNum, int numPlayers, int numTokens, int numGivingToks, int playerIdx, double **influence, double *popularities, CommunityEvaluation *selectedCommunity, int *attackAlloc, int *groupAlloc) {
        if (numGivingToks <= 0) {
            for (int i = 0; i < numPlayers; i++)
                groupAlloc[i] = 0;
            return 0;
        }

        // cout << "groupGivings: " << playerIdx << endl;
        printT(playerIdx, "\n Group Givings (" + to_string(numTokens) + ", " + to_string(numGivingToks) + ")");

        int numTokens_g = groupAllocateTokens(playerIdx, numPlayers, numGivingToks, roundNum, influence, popularities, selectedCommunity, attackAlloc, groupAlloc);

        printT(playerIdx, "  tokens intially kept in give: " + to_string(numGivingToks - numTokens_g));
        groupAlloc[playerIdx] += numGivingToks - numTokens_g;
        if ((groupAlloc[playerIdx] < 0) || (numTokens_g < 0) || (numTokens_g > numGivingToks)) {
            printf("Something is wrong: went negative to self or negative to others or giving more than have in groupGivings\n");
            printf("numGivingToks: %i\n", numGivingToks);
            printf("numTokens_g: %i\n", numTokens_g);
        }
        printT(playerIdx, "   initial groupAlloc: " + vec2String(groupAlloc, numPlayers));

        if (popularities[playerIdx] > 0.0001) {
            int shave = dialBack(numPlayers, numTokens, playerIdx, groupAlloc, popularities);
            // printT(playerIdx, "     shave " + to_string(shave) + " tokens");
            printT(playerIdx, "   groupAlloc: " + vec2String(groupAlloc, numPlayers));
        }

        if (groupAlloc[playerIdx] < 0) {
            printf("Something is wrong 2: went negative to self in groupGivings\n");
            printf("numGivingToks: %i\n", numGivingToks);
            printf("numTokens_g: %i\n", numTokens_g);
            printf("my popularity: %lf\n", popularities[playerIdx]);
        }

        return sumVec(groupAlloc, numPlayers);
    }

    int groupAllocateTokens(int playerIdx, int numPlayers, int numGivingTokens, int roundNum, double **influence, double *popularities, CommunityEvaluation *selectedCommunity, int *attackAlloc, int *groupAlloc) {
        // cout << "groupAllocateTokens" << endl;
        set<int> s_modified = selectedCommunity->s;
        s_modified.erase(playerIdx);
        for (int i = 0; i < numPlayers; i++) {
            if ((attackAlloc[i] != 0) && (s_modified.find(i) != s_modified.end()))
                s_modified.erase(i);
        }

        // printT(playerIdx, getSetString(s_modified));

        // cout << "erased" << endl;

        for (int i = 0; i < numPlayers; i++)
            groupAlloc[i] = 0;

        int numAllocated = numGivingTokens;
        if (roundNum == 0) {
            if (s_modified.size() == 0)
                groupAlloc[playerIdx] = numGivingTokens;
            else {
                int num;
                for (int i = 0; i < numGivingTokens; i++) {
                    // REMOVING RANDOM
                    // int num = rand() % s_modified.size();
                    if (forcedRandom) {
                        int v = getRand();
                        num = (v + (playerIdx+1)) % s_modified.size();
                        // printT(playerIdx, "num: " + to_string(v));
                    }
                    else
                        num = rand() % s_modified.size();
                    // printT(playerIdx, to_string(num));
                    set<int>::iterator j = s_modified.begin();
                    for (int c = 0; c < num; c++, j++);
                    // printT(playerIdx, "sel: " + to_string(*j));

                    groupAlloc[*j] ++;
                }
            }
        }
        else {
            int commSize = s_modified.size() + 1;
            if (commSize <= 1)
                groupAlloc[playerIdx] = numGivingTokens;
            else {
                vector<PlayerProfile *> profile;
                double mag = 0.0;
                for (set<int>::iterator i = s_modified.begin(); i != s_modified.end(); i++) {
                    if (scaledBackNums[*i] > 0.0) {
                        PlayerProfile *p = new PlayerProfile;
                        p->index = *i;
                        p->val = (inflPos[*i][playerIdx] + 0.01) * scaledBackNums[*i];
                        profile.push_back(p);
                        mag += p->val;
                    }
                }

                if (mag > 0.0) {
                    sort(profile.begin(), profile.end(), compare);

                    // printf("profile %i: ", playerIdx);
                    // for (int k = 0; k < profile.size(); k++)
                    //     printf("(%i, %.2lf),", profile[k]->index, profile[k]->val);
                    // printf("\n");

                    int remainingToks = numGivingTokens;
                    commSize = profile.size();
                    double fixedUsage = ((genes[GENE_fixedUsage] / 100.0) * numGivingTokens) / commSize;
                    double flexTokens = numGivingTokens - (fixedUsage * commSize);
                    for (int i = 0; i < profile.size(); i++) {
                        // cout << i << ": " << profile[i]->index << ", " << profile[i]->val << endl;
                        int give_em = (int)(fixedUsage + flexTokens * (profile[i]->val / mag) + 0.5);
                        if (remainingToks >= give_em) {
                            groupAlloc[profile[i]->index] += give_em;
                            remainingToks -= give_em;
                        }
                        else {
                            groupAlloc[profile[i]->index] += remainingToks;
                            remainingToks = 0;
                        }
                    }

                    while (remainingToks > 0) {
                        for (int i = 0; i < commSize; i++) {
                            groupAlloc[profile[i]->index] ++;
                            remainingToks --;
                            if (remainingToks == 0)
                                break;
                        }
                    }

                }
                else {
                    printT(playerIdx, "    can't figure out who to give my tokens to");
                    numAllocated = 0;
                }
                // clean up profile
                for (int i = 0; i < profile.size(); i++)
                    delete profile[i];
            }
        }        

        return numAllocated;
    }

    int dialBack(int numPlayers, int numTokens, int playerIdx, int *groupAlloc, double *popularities) {
        double perc_lmt = genes[GENE_limitingGive] / 100.0;

        int shave = 0, lmt;
        for (int i = 0; i < numPlayers; i++) {
            if (i == playerIdx)
                continue;
            
            if (groupAlloc[i] > 0) {
                lmt = (int)(((popularities[i] / popularities[playerIdx]) * numTokens * perc_lmt) + 0.5);
                if (lmt < groupAlloc[i]) {
                    shave += groupAlloc[i] - lmt;
                    groupAlloc[i] = lmt;
                }
            }
        }

        groupAlloc[playerIdx] += shave;

        return shave;
    }

    void estimateKeeping(int playerIdx, int numPlayers, int numTokens, vector< set<int> > communities) {
        for (int i = 0; i < numPlayers; i++) {
            keepingStrength[i] = getMax(isKeeping(i, numPlayers), fearKeeping(numPlayers, playerIdx, communities, i));
            // printT(playerIdx, to_string(i) + " is keeping " + to_string(isKeeping(i, numPlayers)));
            // printT(playerIdx, to_string(i) + " fear keeping " + to_string(fearKeeping(numPlayers, communities, i)));
            keepingStrength[i] *= numTokens;
        }
    }

    double isKeeping(int otherIdx, int numPlayers) {
        double meAmount = 0.0;
        double totalAmount = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            // if (govPlayers[i]->govPlayer || (i == otherIdx))
            if (i == otherIdx)
                continue;

            if (inflNeg[otherIdx][i] > 0.0) {
                totalAmount += inflNeg[otherIdx][i] / coefs[STEAL_IDX];
                meAmount -= inflNeg[otherIdx][i];
            }
            else {
                totalAmount += inflPos[otherIdx][i] / coefs[GIVE_IDX];
            }
        }

        meAmount = (meAmount + inflPos[otherIdx][otherIdx] - inflNeg[otherIdx][otherIdx]) / coefs[KEEP_IDX];
        totalAmount += meAmount;

        if (totalAmount > 0.0)
            return meAmount / totalAmount;
        else
            return 1.0;
    }

    double fearKeeping(int numPlayers, int playerIdx, vector< set<int> > communities, int agentIdx) {
        bool *amigos = new bool[numPlayers];
        double *enemigos = new double[numPlayers];
        for (int i = 0; i < numPlayers; i++) {
            amigos[i] = false;
            enemigos[i] = 1.0;
        }

        // printT(playerIdx, getCommunitiesString(communities));

        for (int s = 0; s < communities.size(); s++) {
            if (communities[s].find(agentIdx) != communities[s].end()) {
                for (set<int>::iterator i = communities[s].begin(); i != communities[s].end(); i++) {
                    amigos[*i] = true;
                    enemigos[*i] = 0.0;
                }
            }
        }

        double sm = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            if (amigos[i])
                sm = getMax(vecColDotProduct(enemigos, inflNeg, i, numPlayers), sm);
        }

        // printT(playerIdx, vec2String(amigos, numPlayers));
        // printT(playerIdx, to_string(sm));

        delete[] amigos;
        delete[] enemigos;

        double fearTokens;
        double denom = 0.0;
        for (int i = 0; i < numPlayers; i++)
            denom += inflPos[i][agentIdx];
        if (denom > 0.0)
            fearTokens = (sm / denom);
        else
            fearTokens = 0.0;
        fearTokens = -getMax(-1.0, -fearTokens * (genes[GENE_fearDefense] / 50.0)); // assume everyone else has the same fear I do

        return fearTokens;
    }

    int cuantoGuardo(int roundNum, int playerIdx, int numPlayers, int numTokens, double *popularities, double *received, set<int> selectedCommunity) {
        // Change on July 12
        if (popularities[playerIdx] <= povertyLine)
            return 0.0;

        if (roundNum == 0)
            underAttack = (genes[GENE_initialDefense] / 100.0) * popularities[playerIdx];
        else {
            double totalAttack = 0.0;
            for (int i = 0; i < numPlayers; i++)
                totalAttack += getMax(0.0, -received[i]) * popularities[i];
            double dUpdate = genes[GENE_defenseUpdate] / 100.0;
            underAttack = (underAttack * (1.0 - dUpdate)) + (totalAttack * dUpdate);
        }

        double caution = genes[GENE_defensePropensity] / 50.0;
        double selfDefenseTokens = -getMax(-numTokens, -(int)(((underAttack * caution) / popularities[playerIdx]) * numTokens + 0.5));

        printT(playerIdx, "selfDefenseTokens: " + to_string(selfDefenseTokens));

        // are there attacks on my friends by outsiders?  if so, consider keeping more tokens
        // this can be compared to the self.fear_keeping function
        int *amigos = new int[numPlayers];
        int *enemigos = new int[numPlayers];
        for (int i = 0; i < numPlayers; i++)
            amigos[i] = enemigos[i] = 1;

        for (int i = 0; i < numPlayers; i++) {
            if (selectedCommunity.find(i) != selectedCommunity.end())
                enemigos[i] = 0;
            else
                amigos[i] = 0;
        }

        double sm = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            if (amigos[i])
                sm = getMax(vecColDotProduct(enemigos, inflNeg, i, numPlayers), sm);
        }

        delete[] amigos;
        delete[] enemigos;

        double fearTokens;
        double denom = 0.0;
        for (int i = 0; i < numPlayers; i++)
            denom += inflPos[i][playerIdx];
        if (denom > 0.0)
            fearTokens = (int)(((sm / denom) * numTokens) + 0.5);
        else
            fearTokens = 0.0;
        fearTokens = (int)(fearTokens * (genes[GENE_fearDefense] / 50.0) + 0.5); // assume everyone else has the same fear I do

        printT(playerIdx, "fearTokens: " + to_string(fearTokens));

        int tokensGuardado = -getMax(-getMax(selfDefenseTokens, fearTokens), -numTokens);
        int minGuardado = (int)((genes[GENE_minKeep] / 100.0) * numTokens + 0.5);
        tokensGuardado = getMax(tokensGuardado, minGuardado);

        return tokensGuardado;
    }

    int quienAtaco(int roundNum, int playerIdx, int numPlayers, int numTokens, int remainingToks, double *popularities, double **influence, set<int> selectedCommunity, vector< set<int> > communities, int *attackToks) {
        for (int i = 0; i < numPlayers; i++)
            attackToks[i] = 0;

        if (remainingToks <= 0)
            return 0;

        int numAttackToks = 0;
        int *groupCat = new int[numPlayers];

        groupCompare(numPlayers, playerIdx, popularities, communities, groupCat);

        attackObject pillageChoice = pillageTheVillage(roundNum, playerIdx, numPlayers, selectedCommunity, numTokens, remainingToks, popularities, influence, groupCat);
        attackObject vengenceChoice = takeVengence(roundNum, playerIdx, numPlayers, selectedCommunity, numTokens, remainingToks, popularities, influence);
        attackObject defendFriendChoice = defendFriend(playerIdx, numPlayers, numTokens, remainingToks, popularities, influence, selectedCommunity, communities, groupCat);

        printT(playerIdx, "   pillageChoice: " + to_string(pillageChoice.index) + ", " + to_string(pillageChoice.amount));
        printT(playerIdx, "   vengenceChoice: " + to_string(vengenceChoice.index) + ", " + to_string(vengenceChoice.amount));
        printT(playerIdx, "   defendFriendChoice: " + to_string(defendFriendChoice.index) + ", " + to_string(defendFriendChoice.amount));

        vector<attackObject> attackPossibilities;
        int highIndex = -1;
        if (pillageChoice.index >= 0) {
            pillageChoice.priority = genes[GENE_pillagePriority];
            attackPossibilities.push_back(pillageChoice);
            highIndex = 0;
        }
        if (vengenceChoice.index >= 0) {
            vengenceChoice.priority = genes[GENE_vengencePriority];
            attackPossibilities.push_back(vengenceChoice);
            if (highIndex < 0)
                highIndex = 0;
            else if (vengenceChoice.priority > attackPossibilities[highIndex].priority)
                highIndex = attackPossibilities.size() - 1;
        }
        if (defendFriendChoice.index >= 0) {
            defendFriendChoice.priority = genes[GENE_defendFriendPriority];
            attackPossibilities.push_back(defendFriendChoice);
            if (highIndex < 0)
                highIndex = 0;
            else if (defendFriendChoice.priority > attackPossibilities[highIndex].priority)
                highIndex = attackPossibilities.size() - 1;
        }

        // decide which attack to do
        if (highIndex >= 0) {
            if ((attackPossibilities[highIndex].index != defendFriendChoice.index) || (attackPossibilities[highIndex].amount != defendFriendChoice.amount))
                expectedDefendFriendDamage = -99999;

            numAttackToks = attackPossibilities[highIndex].amount;
            attackToks[attackPossibilities[highIndex].index] = numAttackToks;
        }
        else {
            expectedDefendFriendDamage = -99999;
        }

        delete[] groupCat;

        if ((abs(numAttackToks) > numTokens) || (numAttackToks > remainingToks) || (numAttackToks < 0)) {
            printf(">>>>>>>>>>>ought oh: %i, %i, %i\n", numAttackToks, numTokens, remainingToks);
            cout << "  popularity: " << popularities[playerIdx] << endl;
            cout << "  pillageChoice: " << pillageChoice.index << ", " << pillageChoice.amount << endl;
            cout << "  vengenceChoice: " << vengenceChoice.index << ", " << vengenceChoice.amount << endl;
            cout << "  defendFriendChoice: " << defendFriendChoice.index << ", " << defendFriendChoice.amount << endl;
        }

        return numAttackToks;
    }

    attackObject defendFriend(int playerIdx, int numPlayers, int numTokens, int remainingToks, double *popularities, double **influence, set<int> selectedCommunity, vector< set<int> > communities, int *groupCat) {
        attackObject defendFriendDefault(-1, 0, 0.0);

        expectedDefendFriendDamage = -99999;

        // Change on May 5
        if ((popularities[playerIdx] <= 0) || (inflPos_sumcol[playerIdx] <= 0) || (genes[GENE_defendFriendPriority] < 50))
            return defendFriendDefault;

        // printT(playerIdx, "meImport: " + vec2String(meImporta, numPlayers));

        double *myCommVec = new double[numPlayers];
        for (int i = 0; i < numPlayers; ++i) {
            myCommVec[i] = 0.0;
        }	    
        for (set<int>::iterator i = selectedCommunity.begin(); i != selectedCommunity.end(); i++) {
            if ((*i == playerIdx) || (meImporta[*i] > 0.1))
                myCommVec[*i] = 1.0;
            else
                myCommVec[*i] = 0.0;
        }

        printT(playerIdx, "myCommVec: " + vec2String(myCommVec, numPlayers));

        double *badMarks = new double[numPlayers];
        int worstInd = -1;
        double worstVal = 0.0;
        for (int i = 0; i < numPlayers; i++) {
            // Change on May 6
            // if ((govPlayers[i]->govPlayer || (i == playerIdx) || ((genes[GENE_attackGoodGuys] < 50) && (badGuys[i] < 0.2)) || groupCat[i] == 2))

            // Change on Aug 23
            if (((i == playerIdx) || ((genes[GENE_attackGoodGuys] < 50) && (badGuys[i] < 0.2)) || groupCat[i] == 2))
                continue;

            printT(playerIdx, to_string(i));

            badMarks[i] = vecDotProduct(inflNeg[i], myCommVec, numPlayers);
            if (badMarks[i] > 0.0)
                badMarks[i] -= vecColDotProduct(myCommVec, inflNeg, i, numPlayers);

            // Change on July 12
            if ((popularities[i] - povertyLine) < badMarks[i]) {
                printT(playerIdx, "   scaling back bad marks for " + to_string(i));
                badMarks[i] = popularities[i] - povertyLine;
            }

            printT(playerIdx, to_string(i) + ": " + to_string(badMarks[i]));
            
            if ((badMarks[i] > worstVal) && (myCommVec[i] == 0)) {
                worstInd = i;
                worstVal = badMarks[worstInd];
            }
        }

        printT(playerIdx, "   badMarks: " + vec2String(badMarks, numPlayers));
        printT(playerIdx, "   worseInd: " + to_string(worstInd));

        if (worstInd >= 0) {
            double tokensNeeded = numTokens * badMarks[worstInd] / (popularities[playerIdx] * coefs[STEAL_IDX] * alpha);
            tokensNeeded += keepingStrength[worstInd] * (popularities[worstInd] / popularities[playerIdx]);
            double multiplicador = genes[GENE_defendFriendMultiplier] / 33.0;
            tokensNeeded *= multiplicador;
            double attackStrength = vecDotProduct(popularities, myCommVec, numPlayers) * inflictedDamageRatio;
            double myPart = tokensNeeded * (popularities[playerIdx] / attackStrength);
            int cantidad = -getMax(-(int)(myPart+0.5), -(int)(((genes[GENE_defendFriendMax] / 100.0) * numTokens) + 0.5));
            cantidad = -getMax(-cantidad, -remainingToks);

            printT(playerIdx, "   cantidad: " + to_string(cantidad));
            printT(playerIdx, "   tokensNeeded: " + to_string(tokensNeeded));
            printT(playerIdx, "   myPart: " + to_string(myPart));

            if ((cantidad >= (myPart - 1)) && (tokensNeeded > 0)) {
                printT(playerIdx, "considering");
                // see if the attack is a good idea
                // Change on June 6
                double gain = (tokensNeeded * popularities[playerIdx]) - (popularities[worstInd] * keepingStrength[worstInd]);
                double stealROI = (gain * coefs[STEAL_IDX]) / (tokensNeeded * popularities[playerIdx]);
                double immGainPerToken = (stealROI - ROI) * popularities[playerIdx] * alpha;

                // Change on May 12
                double vengenceAdvantage;
                if ((groupCat[worstInd] == 0) && (genes[GENE_groupAware] >= 50.0))
                    vengenceAdvantage = immGainPerToken + 2.0 * ((gain * alpha) / tokensNeeded);
                else
                    vengenceAdvantage = immGainPerToken + ((gain * alpha) / tokensNeeded);

                if (vengenceAdvantage > 0.0) {
                    expectedDefendFriendDamage = gain * alpha * coefs[STEAL_IDX] / numTokens;
                    attackObject o(worstInd, cantidad, vengenceAdvantage);

                    if ((abs(cantidad) > numTokens) || (cantidad > remainingToks)) {
                        printf("\nproblem with defendFriend\n");
                        printf("worstInd = %i\n", worstInd);
                        printf("badMark = %lf\n", badMarks[worstInd]);
                        printf("cantidad = %i\n", cantidad);
                        printf("tokensNeeded: %lf\n", tokensNeeded);
                        printf("myPart: %lf\n", myPart);
                        printf("attackStrength: %lf\n", attackStrength);
                        printf("inflictedDamageRatio: %lf\n", inflictedDamageRatio);
                        printf("popularities * myCommVec:");
                        for (int b = 0; b < numPlayers; b++)
                            printf("%.2lf (%.2lf)  ", popularities[b], myCommVec[b]);
                        printf("\n");
                    }

                    delete[] myCommVec;
                    delete[] badMarks;
                    return o;
                }
            }
        }

        delete[] myCommVec;
        delete[] badMarks;

        return defendFriendDefault;
    }

    attackObject takeVengence(int roundNum, int playerIdx, int numPlayers, set<int> selectedCommunity, int numTokens, int remainingToks, double *popularities, double **influence) {
        attackObject vengenceDefault(-1, 0, 0.0);

        if ((popularities[playerIdx] <= 0.0) || (genes[GENE_vengencePriority] < 50))
            return vengenceDefault;

        double multiplicador = genes[GENE_vengenceMultiplier] / 33.0;
        double vengenceMax = numTokens * (genes[GENE_vengenceMax] / 100.0);
        vengenceMax = -getMax(-vengenceMax, -remainingToks);

        double ratioPredictedSteals = 1.0;
        double predictedSteals = 0.0;
        for (int i = 0; i < numPlayers; i++)
            predictedSteals += getMax(-attacksWithMe[i], 0.0);
        if (attacksWithMe[playerIdx] < 0)
            ratioPredictedSteals = predictedSteals / (-attacksWithMe[playerIdx]);

        vector<attackObject> vengencePossibilities;
        for (int i = 0; i < numPlayers; i++) {
            // if (govPlayers[i]->govPlayer || (i == playerIdx))
            // Change on Aug 23
            if (i == playerIdx)
                continue;

            if ((influence[i][playerIdx] < 0.0) && (-influence[i][playerIdx] > (0.05 * popularities[playerIdx])) && (influence[i][playerIdx] < influence[playerIdx][i]) && (popularities[i] > 0.01)) { 
                double keeping_strength_w = keepingStrength[i] * (popularities[i] / popularities[playerIdx]);
                double theScore = numTokens * ((influence[i][playerIdx] - influence[playerIdx][i]) / (popularities[playerIdx] * coefs[STEAL_IDX] * alpha));
                int cantidad = (int)(-getMax(1.0 * (theScore - keeping_strength_w) * multiplicador, -vengenceMax) + 0.5);

                // Change on July 12
                if (cantidad == 0)
                    continue;

                double myWeight = popularities[playerIdx] * cantidad;
                double ratio = ratioPredictedSteals;
                double ratio2 = (myWeight + ((othersAttacksOn[i] / alpha) * numTokens)) / myWeight;
                if (ratio2 > ratioPredictedSteals)
                    ratio = ratio2;
                double gain = myWeight - (popularities[i] * keepingStrength[i] / ratio);
                while (((((gain*ratio)/numTokens) * alpha * coefs[STEAL_IDX]) > (popularities[i]-povertyLine)) && (cantidad > 0)) {
                    cantidad --;
                    if (cantidad == 0)
                        break;

                    myWeight = popularities[playerIdx] * cantidad;
                    ratio = ratioPredictedSteals;
                    ratio2 = (myWeight + ((othersAttacksOn[i] / alpha) * numTokens)) / myWeight;
                    if (ratio2 > ratioPredictedSteals)
                        ratio = ratio2;
                    gain = myWeight - (popularities[i] * keepingStrength[i] / ratio);
                }
                //////////

                if (cantidad == 0)
                    continue;
                
                // double myWeight = popularities[playerIdx] * cantidad;
                // double ratio = ratioPredictedSteals;
                // double ratio2 = (myWeight + ((othersAttacksOn[i] / alpha) * numTokens)) / myWeight;
                // if (ratio2 > ratioPredictedSteals)
                //     ratio = ratio2;
                // double gain = myWeight - (popularities[i] * keepingStrength[i] / ratio);

                double stealROI = (gain * coefs[STEAL_IDX]) / (cantidad * popularities[playerIdx]);
                double damage = (gain / numTokens) * coefs[STEAL_IDX] * alpha;
                double immGainPerToken = (stealROI - ROI) * ((cantidad / ((double)numTokens)) * popularities[playerIdx]) * alpha;
                immGainPerToken /= cantidad;

                double vengenceAdvantage = immGainPerToken + (damage / cantidad);

                // printT(playerIdx, "against " + to_string(i) + ": " + to_string(vengenceAdvantage));
                // printT(playerIdx, "   " + to_string(immGainPerToken));
                // printT(playerIdx, "   " + to_string(damage));
                // printT(playerIdx, "   " + to_string(cantidad));
                // printT(playerIdx, "   " + to_string(stealROI));

                if (vengenceAdvantage > 0.0) {
                    attackObject o(i, cantidad, vengenceAdvantage); // immGainPerToken);
                    // printT(playerIdx, "adding: " + to_string(i) + ", " + to_string(cantidad) + ", " + to_string(vengenceAdvantage));
                    vengencePossibilities.push_back(o);
                }
            }
        }

        if (vengencePossibilities.size() > 0) {
            // printf("takeVengence: %i\n", playerIdx);
            return selectAttack(vengencePossibilities);
        }

        return vengenceDefault;
    }

    // determines relationship (in size) of player_idx's group with that of the other groups
    //   -1: in same group
    //   0: (no competition) player_idx's group is much bigger
    //   1: (rivals) player_idx's group if somewhat the same size and one of us is in the most powerful group
    //   2: (fear) player_idx's group is much smaller
    void groupCompare(int numPlayers, int playerIdx, double *popularities, vector< set<int> > communities, int *groupCat) {
        int i;

        for (i = 0; i < numPlayers; i++)
            groupCat[i] = 0;

        if (genes[GENE_groupAware] < 50)
            return;

        int *commIdx = new int[numPlayers];
        for (i = 0; i < numPlayers; i++)
            commIdx[i] = 0;
        double *poders = new double[communities.size()];
        for (i = 0; i < communities.size(); i++)
            poders[i] = 0.0;

        for (int c = 0; c < communities.size(); c++) {
            for (set<int>::iterator j = communities[c].begin(); j != communities[c].end(); j++) {
                commIdx[*j] = c;
                poders[c] += popularities[*j];
            }
        }

        double mx_poder = 0.0;
        for (i = 0; i < communities.size(); i++) {
            if (poders[i] > mx_poder)
                mx_poder = poders[i];
        }

        double scaler = 1.3;        // this is arbitary for now
        for (i = 0; i < numPlayers; i++) {
            if (commIdx[i] == commIdx[playerIdx])
                groupCat[i] = -1;
            else if (poders[commIdx[i]] > (scaler * poders[commIdx[playerIdx]]))
                groupCat[i] = 2;
            else if (((scaler * poders[commIdx[i]]) > poders[commIdx[playerIdx]]) && ((poders[commIdx[i]] == mx_poder) || (poders[commIdx[playerIdx]] == mx_poder)))
                groupCat[i] = 1;
            else if (popularities[i] > popularities[playerIdx])
                groupCat[i] = 1;
        }

        printT(playerIdx, "\n  Compare the groups:");
        printT(playerIdx, "        commIdx: " + vec2String(commIdx, numPlayers));
        printT(playerIdx, "        poders: " + vec2String(poders, communities.size()));
        printT(playerIdx, "        groupCat: " + vec2String(groupCat, numPlayers));
        
        delete[] commIdx;
        delete[] poders;
    }

    attackObject pillageTheVillage(int roundNum, int playerIdx, int numPlayers, set<int> selectedCommunity, int numTokens, int remainingToks, double *popularities, double **influence, int *groupCat) {
        attackObject pillageDefault(-1, 0, 0.0);

        if ((popularities[playerIdx] <= 0.0) || (roundNum < (genes[GENE_pillageDelay] / 10.0)) || (genes[GENE_pillagePriority] < 50))
            return pillageDefault;
        
        int numAttackTokens = -getMax(-remainingToks, -(int)(numTokens * (genes[GENE_pillageFury] / 100.0) + 0.5));
        if (numAttackTokens <= 0)
            return pillageDefault;

        printT(playerIdx, "\n Pillage info (" + to_string(numAttackTokens) + "):");

        double predictedSteals = 0.0;
        for (int i = 0; i < numPlayers; i++)
            predictedSteals += getMax(-attacksWithMe[i], 0.0);

        double ratioPredictedSteals = 1.0;
        if (attacksWithMe[playerIdx] < 0.0)
            ratioPredictedSteals = predictedSteals / (-attacksWithMe[playerIdx]);

        if (roundNum < 5)
            ratioPredictedSteals *= (genes[GENE_pillageCompanionship] + 100.0) / 100.0;

        printT(playerIdx, "    ratioPredictedSteals: " + to_string(ratioPredictedSteals));

        // determine the possibilities
        vector<attackObject> pillagePossibilities;
        for (int i = 0; i < numPlayers; i++) {
            // Changes on May 6
            // if (govPlayers[i]->govPlayer || (i == playerIdx))
            // Change on Aug 23
            if (i == playerIdx)
                continue;

            // Change on May 6
            if ((groupCat[i] < 2) && ((selectedCommunity.find(i) == selectedCommunity.end()) || (genes[GENE_pillageFriends] >= 50))) { // player_idx is not fearful of the group player i is in and player_idx is willing to pillage friends (if i is a friend)
                double cantidad = numAttackTokens;
                double myWeight = popularities[playerIdx] * cantidad;
                double ratio = ratioPredictedSteals;
                double ratio2 = (myWeight + ((othersAttacksOn[i] / alpha) * numTokens)) / myWeight;
                if (ratio2 > ratioPredictedSteals)
                    ratio = ratio2;
                double gain = myWeight - (popularities[i] * keepingStrength[i] / ratio);

                // Change on July 12
                while (((((gain*ratio)/numTokens) * alpha * coefs[STEAL_IDX]) > (popularities[i]-povertyLine)) && (cantidad > 0)) {
                    cantidad --;
                    if (cantidad == 0)
                        break;

                    myWeight = popularities[playerIdx] * cantidad;
                    ratio = ratioPredictedSteals;
                    ratio2 = (myWeight + ((othersAttacksOn[i] / alpha) * numTokens)) / myWeight;
                    if (ratio2 > ratioPredictedSteals)
                        ratio = ratio2;
                    gain = myWeight - (popularities[i] * keepingStrength[i] / ratio);
                }

                if (cantidad == 0)
                    continue;

                double stealROI = (gain * coefs[STEAL_IDX]) / (cantidad * popularities[playerIdx]);
                double damage = (gain / numTokens) * coefs[STEAL_IDX] * alpha;
                double immGainPerToken = stealROI * ((cantidad / numTokens) * popularities[playerIdx]) * alpha;
                double friendPenalty = (1.0 - beta) * (damage / popularities[i]) * influence[i][playerIdx];
                immGainPerToken -= friendPenalty;
                immGainPerToken -= ROI * ((cantidad / numTokens) * popularities[playerIdx]) * alpha;
                immGainPerToken /= cantidad;

                printT(playerIdx, "   " + to_string(i) + " immGainPerToken: " + to_string(immGainPerToken));

                double securityThreatAdvantage = immGainPerToken + (damage / cantidad);
                double myGrowth, theirGrowth;
                if (roundNum > 3) {
                    myGrowth = (popHistory[roundNum][playerIdx] - popHistory[roundNum-4][playerIdx]) / 4.0;
                    theirGrowth = (popHistory[roundNum][i] - popHistory[roundNum-4][i]) / 4.0;
                }
                else {
                    myGrowth = theirGrowth = 0.0;
                }

                // Change on May 6
                if (((theirGrowth > (1.5 * myGrowth)) && (popularities[i] > popularities[playerIdx]) && (selectedCommunity.find(i) == selectedCommunity.end())) || (groupCat[i] == 1)) {
                    immGainPerToken += securityThreatAdvantage;
                }

                // Change on May 11
                double margin = genes[GENE_pillageMargin] / 100.0;
                if (immGainPerToken > margin) {
                    attackObject o(i, cantidad, immGainPerToken);
                    pillagePossibilities.push_back(o);
                }
            }
        }

        printT(playerIdx, "");

        if (pillagePossibilities.size() > 0) {
            printT(playerIdx, "***** gonna pillage");
            // printf("pillageTheVillage\n");
            return selectAttack(pillagePossibilities);
        }

        return pillageDefault;
    }

    attackObject selectAttack(vector<attackObject> attackPossibilities) {   
        double mag = 0.0;
        for (int i = 0; i < attackPossibilities.size(); i++)
            mag += attackPossibilities[i].gain;
        
        // REMOVING RANDOM
        // double num = rand() / ((double)RAND_MAX);
        double num;
        if (forcedRandom)
            num = getRand() / 1000.0;
        else
            num = rand() / ((double)RAND_MAX);

        double sumr = 0.0;
        for (int i = 0; i < attackPossibilities.size(); i++) {
            sumr += attackPossibilities[i].gain / mag;
            if (num <= sumr)
                return attackPossibilities[i];
        }

        printf("shouldn't get here: num = %lf; sumr = %lf\n", num, sumr);
        exit(1);

        attackObject attackDefault(-1, 0, 0.0);
        return attackDefault;
    }

};

#endif
