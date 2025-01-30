from .baseagent import AbstractAgent
import random
import numpy as np
import heapq
import sys
import math
import copy

class CommunityEvaluation():

    def __init__(self, _s, _modularity, _centrality, _collective_strength, _familiarity, _prosocial):
        self.s = _s
        self.modularity = _modularity
        self.centrality = _centrality
        self.collective_strength = _collective_strength
        self.familiarity = _familiarity
        self.prosocial = _prosocial

        self.score = 0.0
        self.target = 0.0


    # Change on May 9
    def compute_score(self, genes):
        self.score = 1.0
        self.score = ((100-genes["w_modularity"]) + (genes["w_modularity"] * self.modularity)) / 100.0
        self.score *= ((100-genes["w_centrality"]) + (genes["w_centrality"] * self.centrality)) / 100.0
        self.score *= ((100-genes["w_collective_strength"]) + (genes["w_collective_strength"] * self.collective_strength)) / 100.0
        self.score *= ((100-genes["w_familiarity"]) + (genes["w_familiarity"] * self.familiarity)) / 100.0
        self.score *= ((100-genes["w_prosocial"]) + (genes["w_prosocial"] * self.prosocial)) / 100.0

        # Change on May 12
        # REMOVING RANDOM
        # self.score += random.random() / 10000.0    # random tie-breaking


    def print(self):
        # print(str(self.s) + ": " + str(self.modularity))
        print()
        print("set: " + str(self.s))
        print("   modularity: " + str(self.modularity))
        print("   centrality: " + str(self.centrality))
        # cs_weight = pow(0.5, abs((self.collective_strength - self.target) / .125))
        print("   collective_strength: " + str(self.collective_strength))
        print("   familiarity: " + str(self.familiarity))
        print("   prosocial: " + str(self.prosocial))
        # print("   viability: " + str(self.viability))
        print("   score: " + str(self.score))
        print()


class GeneAgent3(AbstractAgent):

    def __init__(self, geneStr, _num_gene_copies):  # Change on Sep 21
        super().__init__()
        self.num_gene_copies = _num_gene_copies     # Change on Sep 21
        self.whoami = "gene"
        self.count = 0
        self.relativeFitness = 0.0
        self.absoluteFitness = 0.0
        self.gameParams = {}

        # Changes in May
        if geneStr == "":
            # Change on May 12
            # Change on Sep 21
            self.genes_long = []
            for i in range(0, self.num_gene_copies):
                gene_set = {
                    "visualTrait": np.random.randint(0,101),        # not used
                    "homophily": np.random.randint(0,101),          # not used
                    "alpha": np.random.randint(0,101),
                    "otherishDebtLimits": np.random.randint(0,101),
                    "coalitionTarget": np.random.randint(0,101),
                    "fixedUsage": np.random.randint(0,101),     # proportion of tokens to give out evenly in group_allocate
                    "w_modularity": np.random.randint(0,101),
                    "w_centrality": np.random.randint(0,101),
                    "w_collective_strength": np.random.randint(0,101),
                    "w_familiarity": np.random.randint(0,101),
                    "w_prosocial": np.random.randint(0,101),
                    "initialDefense": np.random.randint(0,101),
                    "minKeep": np.random.randint(0,101),
                    "defenseUpdate": np.random.randint(0,101),
                    "defensePropensity": np.random.randint(0,101),
                    "fearDefense": np.random.randint(0,101),
                    "safetyFirst": np.random.randint(0,101),
                    "pillageFury": np.random.randint(0,101),
                    "pillageDelay": np.random.randint(0,101),
                    "pillagePriority": np.random.randint(0,101),
                    "pillageMargin": np.random.randint(0,101),
                    "pillageCompanionship": np.random.randint(0,101),
                    "pillageFriends": np.random.randint(0,101),
                    "vengenceMultiplier": np.random.randint(0,101),
                    "vengenceMax": np.random.randint(0,101),
                    "vengencePriority": np.random.randint(0,101),
                    "defendFriendMultiplier": np.random.randint(0,101),
                    "defendFriendMax": np.random.randint(0,101),
                    "defendFriendPriority": np.random.randint(0,101),
                    "attackGoodGuys": np.random.randint(0,101),
                    "limitingGive": np.random.randint(0,101),
                    "groupAware": np.random.randint(0,101),
                    "joinCoop": np.random.randint(0,101),           # Change Sep 21 (not used)
                }
                self.genes_long.append(gene_set)
        else:
            # read geneStr to set up the genotype
            words = geneStr.split("_")
            # Change on May 12
            # Change on Sep 21
            self.genes_long = []
            count = 0
            for i in range(0, self.num_gene_copies):
                gene_set = {
                    "visualTrait": int(words[1+count]),             # not used
                    "homophily": int(words[2+count]),               # not used
                    "alpha": int(words[3+count]),
                    "otherishDebtLimits": int(words[4+count]),
                    "coalitionTarget": int(words[5+count]),
                    "fixedUsage": int(words[6+count]),
                    "w_modularity": int(words[7+count]),
                    "w_centrality": int(words[8+count]),
                    "w_collective_strength": int(words[9+count]),
                    "w_familiarity": int(words[10+count]),
                    "w_prosocial": int(words[11+count]),
                    "initialDefense": int(words[12+count]),
                    "minKeep": int(words[13+count]),
                    "defenseUpdate": int(words[14+count]),
                    "defensePropensity": int(words[15+count]),
                    "fearDefense": int(words[16+count]),
                    "safetyFirst": int(words[17+count]),
                    "pillageFury": int(words[18+count]),
                    "pillageDelay": int(words[19+count]),
                    "pillagePriority": int(words[20+count]),
                    "pillageMargin": int(words[21+count]),
                    "pillageCompanionship": int(words[22+count]),
                    "pillageFriends": int(words[23+count]),
                    "vengenceMultiplier": int(words[24+count]),
                    "vengenceMax": int(words[25+count]),
                    "vengencePriority": int(words[26+count]),
                    "defendFriendMultiplier": int(words[27+count]),
                    "defendFriendMax": int(words[28+count]),
                    "defendFriendPriority": int(words[29+count]),
                    "attackGoodGuys": int(words[30+count]),
                    "limitingGive": int(words[31+count]),
                    "groupAware": int(words[32+count]),
                    "joinCoop": int(words[33+count]),           # Change Sep 21 (not used)
                }
                self.genes_long.append(gene_set)
                count = count + 33

        self.theTracked = self.getTracked()
        self.played_genes = True

        fp = open("../../State/rnums.txt", "r")

        self.randNums = []
        for i in range(0,10000):
            self.randNums.append(int(fp.readline()))
        self.randCount = 0

        fp.close()

    
    def getRand(self):
        num = self.randNums[self.randCount]
        self.randCount = self.randCount + 1
        if self.randCount >= 10000:
            self.randCount = 0
        return num


    def getTracked(self):
        f = open("../ScenarioIndicator/theTracked.txt", "r")
        val = int(f.readline())
        f.close()

        return val


    def assassinGenes(self):
        self.played_genes = False

        self.genes["visualTrait"] = 50
        self.genes["alpha"] = 1
        self.genes["homophily"] = 50
        self.genes["otherishDebtLimits"] = 25
        self.genes["coalitionTarget"] = 0
        self.genes["fixedUsage"] = 50
        self.genes["w_modularity"] = 100
        self.genes["w_centrality"] = 0
        self.genes["w_collective_strength"] = 0
        self.genes["w_familiarity"] = 0
        self.genes["w_prosocial"] = 0
        self.genes["initialDefense"] = 100
        self.genes["minKeep"] = 100
        self.genes["defenseUpdate"] = 50
        self.genes["defensePropensity"] = 50
        self.genes["fearDefense"] = 50
        self.genes["safetyFirst"] = 0
        self.genes["pillageFury"] = 100
        self.genes["pillageDelay"] = 10
        self.genes["pillagePriority"] = 80
        self.genes["pillageMargin"] = 0
        self.genes["pillageFriends"] = 0
        self.genes["pillageCompanionship"] = 50
        self.genes["vengenceMultiplier"] = 100
        self.genes["vengenceMax"] = 100
        self.genes["vengencePriority"] = 100
        self.genes["defendFriendMultiplier"] = 100
        self.genes["defendFriendMax"] = 100
        self.genes["defendFriendPriority"] = 90
        self.genes["attackGoodGuys"] = 100
        self.genes["limitingGive"] = 100
        self.genes["groupAware"] = 0


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def getString(self):
        theStr = "genes"
        # Change on Sep 21
        for i in range(0, len(self.genes_long)):
            for key in self.genes_long[i]:
                theStr = theStr + "_" + str(self.genes_long[i][key])

        return theStr


    def play_round(self, player_idx, round_num, received, popularities, influence, extra_data):
        self.printT(player_idx, str(received))

        # set up some variables
        if self.theTracked != 99999:
            self.theTracked = self.getTracked()

        # self.printT(player_idx, str(influence))

        if round_num == 0:
            self.pop_history = []
        self.pop_history.append(popularities)

        num_players = len(popularities)
        num_tokens = num_players * 2

        if player_idx == self.theTracked:
            print()
            print("\n\nRound " + str(round_num) + " (Player " + str(self.theTracked) + ")")

        if round_num == 0:
            self.initVars(player_idx, extra_data, num_players, popularities)
            self.alpha = self.genes["alpha"] / 100.0
            self.printT(player_idx, self.getString())
        else:
            self.alpha = self.genes["alpha"] / 100.0
            self.updateVars(received, popularities, num_tokens, num_players, player_idx)

        self.computeUsefulQuantities(round_num, num_players, influence, player_idx, num_tokens)

        if player_idx == self.theTracked:
            print(" Punishable debt: " + str(self.punishable_debt))
            # if round_num > 0:
            #     self.compute_homophily(num_players)

        # group analysis and choice
        communities, selected_community = self.group_analysis(round_num, num_players, player_idx, popularities, influence)

        # figure out how many tokens to keep
        self.estimate_keeping(player_idx, num_players, num_tokens, communities)
        self.printT(player_idx, "\n estimated keeping: " + str(np.round( [float(i) for i in self.keeping_strength], 1)))

        if self.genes["safetyFirst"] < 50:
            safety_first = False
        else:
            safety_first = True

        guardo_toks = self.cuanto_guardo(round_num, player_idx, num_players, num_tokens, popularities, received, selected_community.s)
        self.printT(player_idx, "   guardo_toks: " + str(guardo_toks))

        # # determine who to attack (if any)
        if (round_num > 0):# and (player_idx == 0):
            remaining_toks = num_tokens
            if safety_first:
                # self.printT(player_idx, "    safety first!!")
                remaining_toks -= guardo_toks

            attack_alloc, num_attack_toks = self.quien_ataco(round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community.s, communities)
            self.printT(player_idx, "\n Attackings:")
            self.printT(player_idx, "   attack_vec: " + str(attack_alloc) + " (" + str(num_attack_toks) + ")")
            # self.printT(player_idx, "")
        else:
            attack_alloc = np.zeros(num_players, dtype=int)
            remaining_toks = num_tokens - guardo_toks
            num_attack_toks = 0

        # if not safety_first:
        #     guardo_toks = min(guardo_toks, num_tokens-num_attack_toks)

        # self.printT(player_idx, "num_tokens: " + str(num_tokens))
        # self.printT(player_idx, "num_attack_toks: " + str(num_attack_toks))
        # self.printT(player_idx, "guardo_toks: " + str(guardo_toks))
        # self.printT(player_idx, "remaining_toks: " + str(remaining_toks))

        # figure out who to give tokens to
        groups_alloc, num_group_gives = self.group_givings(round_num, num_players, num_tokens, num_tokens-num_attack_toks-guardo_toks, player_idx, influence, popularities, selected_community, attack_alloc)

        # update some variables
        transaction_vec = groups_alloc - attack_alloc

        # Change made on 6/16
        guardo_toks = num_tokens - sum(np.absolute(transaction_vec))
        transaction_vec[player_idx] += guardo_toks

        self.prev_popularities = popularities
        self.prev_allocations = transaction_vec
        self.prev_influence = influence

        self.updateIndebtedness(round_num, player_idx, transaction_vec, popularities)

        if player_idx == self.theTracked:
            print(str(player_idx) + " transaction_vec: " + str(transaction_vec) + " (" + str(num_group_gives) + ")")

        if transaction_vec[player_idx] < 0:
            print(str(player_idx) + " is stealing from self!!!")

        return transaction_vec


    def initVars(self, player_idx, extra_data, num_players, popularities):
        # Change on Sep 21
        the_pool = self.determine_gene_pool(player_idx, popularities)
        self.genes = copy.deepcopy(self.genes_long[the_pool]) 

        self.played_genes = True
        if player_idx == -1:# and (np.random.randint(0,2) == 1):
            self.assassinGenes()
        self.govPlayer = self.determineGovment(num_players, extra_data)
        self.tally = np.zeros(num_players, dtype=float)
        self.unpaid_debt = np.zeros(num_players)
        self.punishable_debt = np.zeros(num_players, dtype=float)
        self.expectedReturn = np.zeros(num_players, dtype=float)
        self.ave_return = 0.0
        self.scaled_back_nums = np.ones(num_players, dtype=float)
        self.received_value = 0.0
        self.invested_value = 0.0
        self.ROI = self.gameParams["keep"]

    
    def updateVars(self, received, popularities, num_tokens, num_players, player_idx):
        # Change on Sep 21
        the_pool = self.determine_gene_pool(player_idx, popularities)
        self.printT(player_idx, "gene pool: " + str(the_pool))
        self.genes = copy.deepcopy(self.genes_long[the_pool]) 

        self.printT(player_idx, "\nupdateVars:")
        self.tally += (received * num_tokens) * self.prev_popularities
        self.tally[player_idx] = 0

        # self.printT(player_idx, "prev_popularities: " + str(self.prev_popularities))
        # self.printT(player_idx, "received: " + str(received))
        # self.printT(player_idx, "tally: " + str(self.tally))

        self.punishable_debt = np.zeros(num_players, dtype=float)
        for i in range(num_players):
            if (self.tally[i] < 0.0) and (self.unpaid_debt[i] < 0.0):
                self.punishable_debt[i] = -max(self.unpaid_debt[i], self.tally[i])
                
        self.unpaid_debt = self.tally.copy()

        for i in range(num_players):
            if i != player_idx:
                self.scaled_back_nums[i] = self.scale_back(player_idx, i)
                 
        self.printT(player_idx, " scale_back: " + str(self.scaled_back_nums))

        self.received_value *= 1.0 - self.gameParams["alpha"]
        for i in range(num_players):
            if i == player_idx:
                self.received_value += received[i] * num_tokens * self.prev_popularities[i] * self.gameParams["keep"]
            elif received[i] < 0:
                self.received_value += received[i] * num_tokens * self.prev_popularities[i] * self.gameParams["steal"]
            elif received[i] > 0:
                self.received_value += received[i] * num_tokens * self.prev_popularities[i] * self.gameParams["give"]
        self.invested_value *= 1.0 - self.gameParams["alpha"]
        self.invested_value += sum(self.prev_allocations.clip(0)) * self.prev_popularities[player_idx]
        if self.invested_value > 0.0:
            self.ROI = self.received_value / self.invested_value
        else:
            self.ROI = self.gameParams["keep"]
        if self.ROI < self.gameParams["keep"]:
            self.ROI = self.gameParams["keep"]
        self.printT(player_idx, " invested " + str(self.invested_value) + "; got " + str(self.received_value))
        self.printT(player_idx, " received: " + str(received * num_tokens))           
        self.printT(player_idx, " ROI: " + str(self.ROI))            
        self.printT(player_idx, "")


    # Change on Sep 21
    def determine_gene_pool(self, player_idx, popularities):
        if self.num_gene_copies == 1:
            return 0

        if self.num_gene_copies != 3:
            print('geneagent not configured for ' + str(self.num_gene_copies) + ' gene copies')
            os.exit()

        # compute the mean
        m = sum(popularities) / len(popularities)

        ratio = popularities[player_idx] / m

        self.printT(player_idx, "ratio: " + str(ratio))

        if ratio > 1.25:
            return 2
        elif ratio < 0.75:
            return 0
        else:
            return 1
        

    def determineGovment(self, num_players, extra_data):
        is_govment = np.zeros(num_players, dtype=int)
        taxes = {}
        for p_id, data in extra_data.items():
            if data is not None and data.get('is_government', False):
                is_govment[int(p_id)] = 1

        return is_govment


    def estimate_keeping(self, player_idx, num_players, num_tokens, communities):
        self.keeping_strength = []
        for i in range(0, num_players):
            keeping_strength_i = max(self.is_keeping(i, num_players), self.fear_keeping(num_players, player_idx, communities, i))
            # self.printT(player_idx, str(i) + " is keeping " + str(self.is_keeping(i, num_players)))
            # self.printT(player_idx, str(i) + " fear keeping " + str(self.fear_keeping(num_players, communities, i)))
            self.keeping_strength.append(keeping_strength_i * num_tokens)


    def computeUsefulQuantities(self, round_num, num_players, influence, player_idx, num_tokens):
        if round_num > 0:
            self.infl_neg_prev = np.copy(self.infl_neg)
        else:
            self.infl_neg_prev = np.negative(influence).clip(0)

        self.infl_pos = np.positive(influence).clip(0)
        self.infl_neg = np.negative(influence).clip(0)

        self.infl_pos_sumcol = self.infl_pos.sum(axis=0)
        self.infl_pos_sumrow = self.infl_pos.sum(axis=1)

        if round_num == 0:
            self.sum_infl_pos = np.zeros((num_players, num_players), dtype=float)
            self.attacks_with_me = np.zeros(num_players, dtype=float)
            self.others_attacks_on = np.zeros(num_players, dtype=float)

            # Change on May 4-5
            self.inflicted_damage_ratio = 1.0
            self.bad_guys = np.zeros(num_players, dtype=float)
        else:
            self.sum_infl_pos += self.infl_pos

            w = 0.2
            for i in range(0, num_players):
                val = sum(np.negative(influence[:,i] - ((self.prev_influence[:,i] * (1.0 - self.gameParams["alpha"])))).clip(0))
                val -= np.negative(influence[player_idx][i] - ((self.prev_influence[player_idx][i] * (1.0 - self.gameParams["alpha"])))).clip(0)
                self.others_attacks_on[i] = (self.others_attacks_on[i] * w) + ((1.0-w) * val)
                if i != player_idx:
                    if self.prev_allocations[i] < 0:
                        # Change on May 4
                        amount = (np.negative(influence[:,i] - (self.prev_influence[:,i] * (1.0 - self.gameParams["alpha"]))).clip(0))
                        self.attacks_with_me -= amount
                        if self.expected_defend_friend_damage != -99999:
                            new_ratio = sum(amount) / self.expected_defend_friend_damage
                            self.inflicted_damage_ratio = 0.5 * self.inflicted_damage_ratio + 0.5 * new_ratio
                            # self.printT(player_idx, "******* inflicted " + str(sum(amount)) + " vs " + str(self.expected_defend_friend_damage))
                            # self.printT(player_idx, "******* inflicted_damage_ratio: " + str(self.inflicted_damage_ratio))

            # Change on May 5
            # see if player i is a bad guy
            self.bad_guys *= (1.0 - self.gameParams["alpha"])
            bad_guys_copy = self.bad_guys.copy()
            new_steals = self.infl_neg - (np.negative(self.prev_influence).clip(0) * (1.0 - self.gameParams["alpha"]))
            for i in range(num_players):
                for j in range(num_players):
                    if (new_steals[i][j] > 5.0):
                        if (bad_guys_copy[j] < 0.2):
                            if self.bad_guys[i] < 0.2:
                                self.printT(player_idx, ">>>>>> me thinks " + str(i) + " is a new bad guy")
                            self.bad_guys[i] += new_steals[i][j] / 1.0
                            if self.bad_guys[i] > 1.0:
                                self.bad_guys[i] = 1.0
                        elif (sum(self.infl_neg[j]) * 0.9) < sum(self.infl_neg[:,j]):
                            self.printT(player_idx, ">>>>>> bad guy " + str(j) + " has paid for its crimes")
                            self.bad_guys[j] = 0.0

            self.printT(player_idx, "   que mala onda: " + str(self.bad_guys))
            # if new_steals_by_i > 0.1:
            #     self.printT(player_idx, "player " + str(i) + " stole " + str(new_steals_by_i))

            self.printT(player_idx, " attacks_with_me: " + str(self.attacks_with_me))
            self.printT(player_idx, " others_attacks_on: " + str(self.others_attacks_on))
            self.printT(player_idx, "")
            # self.printT(player_idx, "infl_neg:")
            # self.printT(player_idx, str(self.infl_neg))


    # determines the proportion of total popularity player_idx would like to have in its selected group
    def compute_coalition_target(self, round_num, popularities, communities, player_idx):
        # compute self.coalition_target
        if self.genes["coalitionTarget"] < 80:
            if self.genes["coalitionTarget"] < 5:
                return 0.05
            else:
                return self.genes["coalitionTarget"] / 100.0
        elif round_num < 3:
            return 0.51
        else:
            in_mx = False
            mx_ind = -1
            fuerza = []
            tot_pop = sum(popularities)
            for s in communities:
                tot = 0.0
                for i in s:
                    tot += popularities[i]

                fuerza.append(tot / tot_pop)
                if mx_ind == -1:
                    mx_ind = 0
                elif tot > fuerza[mx_ind]:
                    mx_ind = len(fuerza)-1
                    if player_idx in s:
                        in_mx = True
                    else:
                        in_mx = False

            fuerza.sort(reverse=True)
            self.printT(player_idx, "   fuerza: " + str(fuerza))
            if in_mx:
                return min(fuerza[1] + 0.05, 55)
            else:
                return min(fuerza[0] + 0.05, 55)


    # determines how much each player owes player_idx
    def updateIndebtedness(self, round_num, player_idx, transaction_vec, popularities):
        # update the tally of indebtedness
        self.tally -= np.positive(transaction_vec).clip(0) * popularities[player_idx]
        self.tally[player_idx] = 0

        lmbda = 1.0 / (round_num + 1.0)
        if lmbda < self.gameParams["alpha"]:
            lmbda = self.gameParams["alpha"]
        self.expectedReturn = ((1-lmbda) * self.expectedReturn) + (lmbda * (transaction_vec * popularities[player_idx]))
        # self.printT(player_idx, "   expectedReturn: " + str(self.expectedReturn))
        self.ave_return = sum(self.expectedReturn) / len(self.expectedReturn)


    # def elegir_amigos(self, round_num, num_players, player_idx, popularities, influence, A, communities, modularity):
    #     potential_communities = []
    #     if round_num == 0:
    #         init_comm_size = int(num_players * (self.genes["coalitionTarget"] / 100.0) + 0.5)

    #         plyrs = set()
    #         for i in range(num_players):
    #             if player_idx != i:
    #                 plyrs.add(i)

    #         s = set()
    #         s.add(player_idx)
    #         pop = popularities[player_idx]
    #         total_pop = sum(popularities)
    #         # coalitionTarget = self.genes["coalitionTarget"] / 100.0
    #         while ((pop / total_pop) < self.coalition_target): #coalitionTarget):
    #             sel = random.sample(plyrs, 1)
    #             s.add(sel[0])
    #             plyrs.remove(sel[0])
    #             pop += popularities[sel[0]]

    #         potential_communities.append(CommunityEvaluation(s, 0.0, 0.0, 0.0, 0.0, 0.0))
    #     else:
    #         considered_sets = self.generate_sets(num_players, player_idx, communities, popularities)
    #         # self.printT(player_idx, "considered sets: " + str(len(considered_sets)))
            
    #         min_mod = modularity
    #         for s in considered_sets:
    #             hyp_modularity = self.ease_of_formation_b(num_players, A, s)
    #             if hyp_modularity < min_mod:
    #                 min_mod = hyp_modularity
    #             potential_communities.append(CommunityEvaluation(s, hyp_modularity, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

    #         # compute scores (after normalizing modularity)
    #         for c in potential_communities:
    #             c.modularity = (c.modularity - min_mod) / (modularity - min_mod)
    #             c.compute_score(self.genes, self.coalition_target)

    #             # if player_idx == self.theTracked:
    #             #     self.get_ingroup_antisocial(c.s, player_idx)


    #         potential_communities.sort(key=lambda x: x.score, reverse=True)

    #         self.printT(player_idx, "\n GroupSelection: " + str(potential_communities[0].s))
    #         # print("Top group for player " + str(player_idx))
    #         # for i in range(len(potential_communities)):
    #         #     potential_communities[i].print()
    #         # print("")

    #     return potential_communities[0]


    def group_givings(self, round_num, num_players, num_tokens, num_giving_tokens, player_idx, influence, popularities, selected_community, attack_alloc):
        # Change on 6/16
        if (num_giving_tokens <= 0):
            self.printT(player_idx, "              nothing left to give")
            group_alloc = np.zeros(num_players, dtype=int)
            return group_alloc, 0

        self.printT(player_idx, "\n Group Givings (" + str(num_tokens) + ", " + str(num_giving_tokens) + ")")

        # allocate tokens based on homophily
        # homophily_vec = self.get_homophily_vec(num_players, player_idx)
        # homophily_alloc, num_tokens_h = self.homophily_allocate_tokens(round_num, num_players, num_giving_tokens, player_idx, homophily_vec, popularities, attack_alloc)
        # self.printT(player_idx, "homophily_tokens: " + str(num_tokens_h))
        homophily_alloc = np.zeros(num_players, dtype=float)
        num_tokens_h = 0

        group_alloc, num_tokens_g = self.group_allocate_tokens(player_idx, num_players, num_giving_tokens - num_tokens_h, round_num, influence, popularities, selected_community, attack_alloc)

        # for now, just keep tokens that you don't know what to do with
        self.printT(player_idx, "  tokens initially kept in give: " + str((num_giving_tokens - (num_tokens_h + num_tokens_g))))
        group_alloc[player_idx] += (num_giving_tokens - (num_tokens_h + num_tokens_g))
        # self.printT(player_idx, "   homophily allocations: " + str(homophily_alloc) + " (" + str(num_tokens_h) + ")")
        self.printT(player_idx, "   initial group_alloc: " + str(group_alloc))

        # Change on June 21 and July 12
        if popularities[player_idx] > 0.0001:
            group_alloc, shave = self.dial_back(num_players, num_tokens, player_idx, homophily_alloc + group_alloc, popularities)
            # self.printT(player_idx, "     shave " + str(shave) + " tokens")
            self.printT(player_idx, "   group_alloc: " + str(group_alloc))
        self.printT(player_idx, "")

        # return homophily_alloc + group_alloc, num_tokens_h + num_tokens_g
        return group_alloc, sum(group_alloc)


    def dial_back(self, num_players, num_tokens, player_idx, give_alloc, popularities):
        perc_lmt = self.genes["limitingGive"] / 100.0

        shave = 0
        for i in range(num_players):
            if i == player_idx:
                continue

            if give_alloc[i] > 0:
                lmt = int(((popularities[i] / popularities[player_idx]) * num_tokens * perc_lmt) + 0.5)
                if lmt < give_alloc[i]:
                    shave += give_alloc[i] - lmt
                    give_alloc[i] = lmt

        give_alloc[player_idx] += shave

        return give_alloc, shave


    def get_visualhomophily_similarity(self, player_idx, other):
        diff = abs(self.visualTraits[player_idx] - self.visualTraits[other])
        if diff < 20:
            return 1.0
        else:
            return 0.0
        

    def printT(self, player_idx, s):
        if player_idx == self.theTracked:
            print(s)
        

    def compute_adjacency(self, num_players):
        A = self.infl_pos.copy()
        for i in range(num_players):
            A[i][i] = self.infl_pos[i][i]
            for j in range(i+1, num_players):
                theAve = (self.infl_pos[i][j] + self.infl_pos[j][i]) / 2.0 
                theMin = min(self.infl_pos[i][j], self.infl_pos[j][i])
                A[i][j] = (theAve + theMin) / 2.0
                A[j][i] = A[i][j]

        return A


    def compute_neg_adjacency(self, num_players):
        A = self.infl_neg.copy()
        for i in range(num_players):
            A[i][i] = self.infl_neg[i][i]
            for j in range(i+1, num_players):
                theAve = (self.infl_neg[i][j] + self.infl_neg[j][i]) / 2.0 
                theMax = max(self.infl_neg[i][j], self.infl_neg[j][i])
                A[i][j] = theMax #(theAve + theMax) / 2.0
                A[j][i] = A[i][j]

        return A


    def get_homophily_vec(self, num_players, player_idx):
        homophily_vec = np.zeros(num_players, dtype=float)
        for i in range(num_players):
            if i != player_idx:                
                if (self.genes["homophily"] > 66) and (self.get_visualhomophily_similarity(player_idx, i) > 0.0):
                    # homophily_vec[i] = self.get_visualhomophily_similarity(player_idx, i) * ((self.genes["homophily"] - 66) / 34.0)
                    homophily_vec[i] = 1.0
                elif (self.genes["homophily"] < 34) and (self.get_visualhomophily_similarity(player_idx, i) == 0.0):
                    # homophily_vec[i] = 1 - self.get_visualhomophily_similarity(player_idx, i) * ((34 - self.genes["homophily"]) / 34.0)
                    homophily_vec[i] = 1.0
                else:
                    homophily_vec[i] = 0.0

        return homophily_vec


    def group_allocate_tokens(self, player_idx, num_players, num_tokens, round_num, influence, popularities, the_community, attack_alloc):
        # if player_idx == self.theTracked:
        #     print()
        #     print("This is my community:")
        #     the_community.print()
        # s_modified = the_community.s.copy()
        s_modified = sorted(the_community.s)
        for i in range(num_players):
            if attack_alloc[i] != 0:
                if i in s_modified:
                    # print("remove " + str(i) + " from " + str(s_modified))
                    s_modified.remove(i)

        # self.printT(player_idx, str(s_modified))

        toks = np.zeros(num_players, dtype=float)

        num_allocated = num_tokens
        if round_num == 0:
            if len(s_modified) == 1:
                toks[player_idx] = num_tokens
            else:
                for i in range(num_tokens):
                    # REMOVING RANDOM
                    # sel = random.sample(s_modified, 1)[0]
                    # while sel == player_idx:
                    #     sel = random.sample(s_modified, 1)[0]
                    # toks[sel] += 1

                    if self.forced_random:
                        v = self.getRand()
                        num = (v + (player_idx+1)) % (len(s_modified)-1)
                        # self.printT(player_idx, "num: " + str(v))
                    else:
                        num = np.random.randint(0,1001) % (len(s_modified)-1)

                    # self.printT(player_idx, str(num))
                    c = 0
                    sel = -1
                    for s in s_modified:
                        if s != player_idx:
                            if c == num:
                                sel = s
                                break
                            c += 1

                    if sel == -1:
                        print(str(num) + "; " + str(c) + "; " + str(s_modified))
                        sys.exit()

                    # self.printT(player_idx, "sel: " + str(sel))
                    
                    toks[sel] += 1
        else:
            comm_size = len(s_modified)
            if comm_size <= 1:
                toks[player_idx] = num_tokens
            else:
                profile = []
                mag = 0.0
                for i in s_modified:
                    if (i != player_idx):# and (self.punishable_debt[i] < limite):
                        sb = self.scaled_back_nums[i] #self.scale_back(player_idx, i)
                        if sb > 0.0:
                            val = (self.infl_pos[i][player_idx]+0.01) * sb
                            # if self.punishable_debt[i] > 0:
                            #     val *= 1.0 - (self.punishable_debt[i] / limite)
                            profile.append((i, val))
                            mag += val
                    # elif i != player_idx:
                    #     self.printT(player_idx, "player " + str(i) + " excluded")

                
                if mag > 0.0:
                    profile.sort(key=lambda a: a[1], reverse=True)

                    # print("profile " + str(player_idx) + ": " + str(profile))

                    remaining_toks = num_tokens
                    comm_size = len(profile)                    
                    fixed_usage = ((self.genes["fixedUsage"] / 100.0) * num_tokens) / comm_size
                    # self.printT(player_idx, "fixed_usage = " + str(fixed_usage))
                    flex_tokens = num_tokens - (fixed_usage * comm_size)
                    # flex_tokens = num_tokens - comm_size
                    for i in range(comm_size):
                        # give_em = int(1 + flex_tokens * (profile[i][1] / mag) + 0.5)
                        give_em = int(fixed_usage + flex_tokens * (profile[i][1] / mag) + 0.5)
                        if remaining_toks >= give_em:
                            toks[profile[i][0]] += give_em
                            remaining_toks -= give_em
                        else:
                            toks[profile[i][0]] += remaining_toks
                            remaining_toks = 0

                    while remaining_toks > 0:
                        for i in range(comm_size):
                            toks[profile[i][0]] += 1
                            remaining_toks -= 1
                            if remaining_toks == 0:
                                break

                else:
                    # need to make a new friend
                    self.printT(player_idx, "    can't figure out who to give my tokens to")

                    num_allocated = 0
                #     for i in range(num_players):
                #         toks[np.random.randint(0,num_players)] += 1
    
        return toks, num_allocated

    
    # for now, this function does nothing; the homophily mechanism needs to be revisited
    def homophily_allocate_tokens(self, round_num, num_players, num_tokens, player_idx, homophily_vec, popularities, attack_alloc):
        toks = np.zeros(num_players, dtype=float)

        return toks, 0

        # numero = sum(homophily_vec)
        # if numero <= 0:
        #     t_h = 0
        #     return toks, t_h

        # H = self.genes["homophily"]
        # if H > 66:
        #     t_h = math.ceil(num_tokens/2 * ((H-66) / 34.0))
        # elif H < 34:
        #     t_h = math.ceil(num_tokens/2 * ((34-H) / 34.0))
        # else:
        #     print("shouldn't ever get here")
        #     sys.exit()

        # ingroup = []
        # for i in range(num_players):
        #     if (homophily_vec[i] > 0) and (attack_alloc[i] == 0):
        #         ingroup.append(i)

        # if round_num == 0:
        #     # randomly send t_h tokens to people in my group
        #     for i in range(t_h):
        #         toks[ingroup[np.random.randint(0,len(ingroup))]] += 1
        # else:
        #     comm_size = numero

        #     profile = []
        #     mag = 0.0
        #     # limite = (num_tokens / numero) * popularities[player_idx]
        #     # self.printT(player_idx, "limite: " + str(limite))
        #     for i in ingroup:
        #         sb = self.scaled_back_nums[i] #self.scale_back(player_idx, i)
        #         if sb > 0.0:
        #             val = (self.infl_pos[i][player_idx] + random.random()) * sb
        #             profile.append((i, val))
        #             mag += val

        #     if mag > 0.0:
        #         profile.sort(key=lambda a: a[1], reverse=True)

        #         # prune back if needed
        #         pop = popularities[player_idx]
        #         total_pop = sum(popularities)
        #         # coalitionTarget = self.genes["coalitionTarget"] / 100.0
        #         comm_size = 0
        #         while ((pop / total_pop) < self.coalition_target) and (comm_size < len(profile)):
        #             comm_size += 1

        #         if comm_size == 0:
        #             return toks, 0

        #         if comm_size < len(profile):
        #             for i in range(comm_size, len(profile)):
        #                 mag -= profile[i][1]
                
        #         remaining_toks = t_h
        #         # comm_size = len(profile)
        #         for i in range(comm_size):
        #             give_em = int(t_h * (profile[i][1] / mag) + 0.5)
        #             if remaining_toks >= give_em:
        #                 toks[profile[i][0]] += give_em
        #                 remaining_toks -= give_em
        #             else:
        #                 toks[profile[i][0]] += remaining_toks
        #                 remaining_toks = 0
 
        #         while remaining_toks > 0:
        #             for i in range(comm_size):
        #                 toks[profile[i][0]] += 1
        #                 remaining_toks -= 1
        #                 if remaining_toks <= 0:
        #                     if remaining_toks < 0:
        #                         print("PROBLEM: remaining_toks negative: " + str(remaining_toks))
        #                         sys.exit()
        #                     break
        #     else:
        #         t_h = 0

        # return toks, t_h


    def scale_back(self, player_idx, quien):
        if self.govPlayer[quien] == 1:  # for now, don't scale back payments to the gov'ment
            return 1

        # consider scaling back if the other person is in debt to me
        if self.punishable_debt[quien] > 0:
            debtLimit = self.genes["otherishDebtLimits"] / 25.0
            self.printT(player_idx, debtLimit)
            if debtLimit > 0:
                denom = max(self.expectedReturn[quien], self.ave_return) * debtLimit
                # self.printT(player_idx, "   denom for " + str(quien) + ": " + str(denom))
                if denom == 0:
                    return 0.0
                else:
                    perc = 1.0 - (self.punishable_debt[quien] / denom) #(self.expectedReturn[quien] * debtLimit))
                    if perc > 0.0:
                        # self.printT(player_idx, "backoff " + str(quien) + " by " + str(perc) + "(debtLimit = " + str(debtLimit) + ")")
                        return perc
                    else:
                        # self.printT(player_idx, "exclude " + str(quien) + " completely (debtLimit = " + str(debtLimit) + "; perc = " + str(perc) + ")")
                        return 0.0

        return 1.0


    # the following two functions are just used for information purposes
    # def get_truehomophily_vec(self, num_players, player_idx):
    #     homophily_vec = np.zeros(num_players, dtype=float)
    #     for i in range(num_players):
    #         if i != player_idx:                
    #             if self.get_visualhomophily_similarity(player_idx, i) > 0.0:
    #                 homophily_vec[i] = 1.0
    #             else:
    #                 homophily_vec[i] = 0.0

    #     return homophily_vec


    # def compute_homophily(self, num_players):
    #     homoph_cnts = 0.0
    #     tot_cnts = 0.0
    #     homoph_infls = 0.0
    #     tot_infls = 0.0
    #     for i in range(num_players):
    #         homophily_vec = self.get_truehomophily_vec(num_players, i)
    #         # print("   " + str(homophily_vec))
    #         homoph_cnts += sum(homophily_vec)
    #         tot_cnts += num_players-1
    #         homoph_infls += np.dot(homophily_vec, self.infl_pos[i])
    #         tot_infls += sum(self.infl_pos[i]) - self.infl_pos[i][i]

    #     cnts = homoph_cnts / tot_cnts
    #     infls = homoph_infls / tot_infls

    #     # print(" Population homophily: " + str(infls / cnts) + " (" + str(cnts) + " vs " + str(infls) + ")")


    # decide how many tokens to keep
    def cuanto_guardo(self, round_num, player_idx, num_players, num_tokens, popularities, received, selected_community):
        # Change on July 12
        if popularities[player_idx] <= self.gameParams["poverty_line"]:
            return 0

        if round_num == 0:
            self.underAttack = (self.genes["initialDefense"] / 100.0) * popularities[player_idx]
        else:
            totalAttack = np.dot(np.negative(received[0:num_players]).clip(0), popularities[0:num_players])
            dUpdate = self.genes["defenseUpdate"] / 100.0
            self.underAttack = (self.underAttack * (1.0 - dUpdate)) + (totalAttack * dUpdate)

        caution = self.genes["defensePropensity"] / 50.0
        self_defense_tokens = min(num_tokens, int(((self.underAttack * caution) / popularities[player_idx]) * num_tokens + 0.5))

        # are there attacks on my friends by outsiders?  if so, consider keeping more tokens
        # this can be compared to the self.fear_keeping function
        amigos = np.ones(num_players, dtype=int)
        enemigos = np.ones(num_players, dtype=int)
        for i in range(num_players):
            if i in selected_community:
                enemigos[i] = 0
            else:
                amigos[i] = 0

        sm = 0.0
        for i in range(num_players):
            if amigos[i]:
                sm = max(np.dot(enemigos, self.infl_neg[:,i]), sm)

        denom = sum(self.infl_pos[:,player_idx])
        if denom > 0:
            fear_tokens = int((sm / sum(self.infl_pos[:,player_idx]) * num_tokens) + 0.5)
        else:
            fear_tokens = 0
        fear_tokens = int(fear_tokens * (self.genes["fearDefense"] / 50.0) + 0.5)

        tokens_guardado = min(max(self_defense_tokens, fear_tokens), num_tokens)

        min_guardado = int((self.genes["minKeep"] / 100.0) * num_tokens + 0.5)
        tokens_guardado = max(tokens_guardado, min_guardado)

        return tokens_guardado


    # Changes in May
    def quien_ataco(self, round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities):
        # my_community = set()
        # for s in communities:
        #     if player_idx in s:
        #         my_community = s
        #         break
        # self.printT(player_idx, "   attacks with me prior: " + str(self.attacks_with_me_prior(num_players, player_idx, my_community, popularities, self.genes["warFury"] / 100.0)))

        group_cat = self.groupCompare(num_players, player_idx, popularities, communities)

        pillage_choice = self.pillage_the_village(round_num, player_idx, num_players, selected_community, num_tokens, remaining_toks, popularities, influence, group_cat)
        vengence_choice = self.take_vengence(round_num, player_idx, num_players, selected_community, num_tokens, remaining_toks, popularities, influence)
        defend_friend_choice = self.defend_friend(player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities, group_cat)
        # # startwar_choice = self.start_guerra(round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities)
        # # joinwar_choice = self.join_guerra(round_num, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities)

        self.printT(player_idx, "   pillage_choice: " + str(pillage_choice))
        self.printT(player_idx, "   vengence_choice: " + str(vengence_choice))
        self.printT(player_idx, "   defend_friend_choice: " + str(defend_friend_choice))
        # # self.printT(player_idx, "   startwar_choice: " + str(startwar_choice))
        # # self.printT(player_idx, "   joinwar_choice: " + str(joinwar_choice))

        attack_toks = np.zeros(num_players, dtype=int)
        # # if pillage_choice[0] >= 0:
        # #     attack_toks[pillage_choice[0]] = pillage_choice[1]

        attack_possibilities = []
        if (pillage_choice[0] >= 0):
            attack_possibilities.append((self.genes["pillagePriority"], pillage_choice[0], pillage_choice[1]))
        if (vengence_choice[0] >= 0):
            attack_possibilities.append((self.genes["vengencePriority"], vengence_choice[0], vengence_choice[1]))
        if (defend_friend_choice[0] >= 0):
            attack_possibilities.append((self.genes["defendFriendPriority"], defend_friend_choice[0], defend_friend_choice[1]))

        # # decide which attack to do
        if len(attack_possibilities) > 0:
            attack_possibilities.sort(key=lambda a: a[0], reverse=True)
            self.printT(player_idx, "  Sorted attack: " + str(attack_possibilities))
            if (attack_possibilities[0][1] != defend_friend_choice[0]) or (attack_possibilities[0][2] != defend_friend_choice[1]):
                self.expected_defend_friend_damage = -99999
            attack_toks[attack_possibilities[0][1]] = attack_possibilities[0][2]
        else:
            self.expected_defend_friend_damage = -99999

        # # self.printT(player_idx, "        expected_defend_friend_damage: " + str(self.expected_defend_friend_damage))

        return attack_toks, sum(attack_toks)


    # determines relationship (in size) of player_idx's group with that of the other groups
    #   -1: in same group
    #   0: (no competition) player_idx's group is much bigger
    #   1: (rivals) player_idx's group if somewhat the same size and one of us is in the most powerful group
    #   2: (fear) player_idx's group is much smaller
    def groupCompare(self, num_players, player_idx, popularities, communities):
        group_cat = np.zeros(num_players, dtype=int)
        if self.genes["groupAware"] < 50:
            # don't do anything different -- player is not group aware
            return group_cat

        comm_idx = np.zeros(num_players, dtype=int)
        poders = np.zeros(len(communities), dtype=float)
        for c in range(len(communities)):
            for i in communities[c]:
                comm_idx[i] = c
                poders[c] += popularities[i]

        mx_poder = max(poders)

        scaler = 1.3        # this is arbitary for now
        for i in range(num_players):
            if comm_idx[i] == comm_idx[player_idx]:
                group_cat[i] = -1
            elif poders[comm_idx[i]] > (scaler * poders[comm_idx[player_idx]]):
                group_cat[i] = 2
            elif ((scaler * poders[comm_idx[i]]) > poders[comm_idx[player_idx]]) and ((poders[comm_idx[i]] == mx_poder) or (poders[comm_idx[player_idx]] == mx_poder)):
                group_cat[i] = 1
            elif popularities[i] > popularities[player_idx]: # i'm in a bigger group, but they are more powerful than me (so we are rivals -- i use my group size to justify my attack)
                group_cat[i] = 1

        self.printT(player_idx, "\n  Compare the groups:")
        self.printT(player_idx, "        comm_idx: " + str(comm_idx))
        self.printT(player_idx, "        poders: " + str(poders))
        self.printT(player_idx, "        group_cat: " + str(group_cat) + "\n")

        return group_cat


    def defend_friend(self, player_idx, num_players, num_tokens, remaining_toks, popularities, influence, selected_community, communities, group_cat):
        self.expected_defend_friend_damage = -99999

        # Change on May 5
        if (popularities[player_idx] <= 0) or (self.infl_pos_sumcol[player_idx] <= 0) or (self.genes["defendFriendPriority"] < 50):
            return (-1, 0)

        # self.printT(player_idx, "meImporta: " + str(self.me_importa))

        my_comm_vec = np.zeros(num_players, dtype=float)
        for i in selected_community:
            if (i == player_idx) or (self.me_importa[i] > 0.1):   # TODO: verify this threshold -- it is set arbitrarily without testing (seems okay for now)
                my_comm_vec[i] = 1.0

        # self.printT(player_idx, "\n  my_comm_vec: " + str(my_comm_vec))

        bad_marks = np.zeros(num_players, dtype=float)
        worst_ind = -1
        worst_val = 0
        for i in range(0,num_players):
            # Change on May 6
            if (self.govPlayer[i] == 1) or (i == player_idx) or ((self.genes["attackGoodGuys"] < 50) and (self.bad_guys[i] < 0.2)) or (group_cat[i] == 2):
                continue

            # self.printT(player_idx, str(i))

            bad_marks[i] = np.dot(self.infl_neg[i], my_comm_vec)
            if bad_marks[i] > 0:
                bad_marks[i] -= np.dot(self.infl_neg[:,i], my_comm_vec)

            # Change on July 12
            if ((popularities[i] - self.gameParams["poverty_line"]) < bad_marks[i]):
                self.printT(player_idx, "   scaling back bad marks for " + str(i))
                bad_marks[i] = popularities[i] - self.gameParams["poverty_line"]

            # Change on June 16
            if (bad_marks[i] > worst_val) and (my_comm_vec[i] == 0):
                worst_ind = i
                worst_val = bad_marks[worst_ind]

        # self.printT(player_idx, "    bad_marks: " + str(bad_marks))
        # self.printT(player_idx, "    worst_ind: " + str(worst_ind))

        if (worst_ind >= 0):
            # see how many tokens I should use on this attack
            tokens_needed = num_tokens * bad_marks[worst_ind] / (popularities[player_idx] * self.gameParams["steal"] * self.gameParams["alpha"])
            tokens_needed += self.keeping_strength[worst_ind] * (popularities[worst_ind] / popularities[player_idx])
            multiplicador = self.genes["defendFriendMultiplier"] / 33.0
            tokens_needed *= multiplicador
            attack_strength = np.dot(popularities, my_comm_vec) * self.inflicted_damage_ratio
            my_part = tokens_needed * (popularities[player_idx] / attack_strength)
            cantidad = min(int(my_part+0.5), int(((self.genes["defendFriendMax"] / 100.0) * num_tokens) + 0.5), remaining_toks)
            # self.printT(player_idx, "    consider attacking player " + str(worst_ind) + " with " + str(my_part) + "; reduced = " + str(cantidad))
            # self.printT(player_idx, "    tokens_needed: " + str(tokens_needed))
            if (cantidad >= (my_part - 1)) and (tokens_needed > 0):
                # see if the attack is a good idea
                # Change on June 6
                gain = (tokens_needed * popularities[player_idx]) - (popularities[worst_ind] * self.keeping_strength[worst_ind])
                steal_ROI = (gain * self.gameParams["steal"]) / (tokens_needed * popularities[player_idx])
                imm_gain_per_token = (steal_ROI - self.ROI) * popularities[player_idx] * self.gameParams["alpha"]
                # self.printT(player_idx, "    steal_ROI: " + str(steal_ROI))
                # self.printT(player_idx, "    gain: " + str(gain))

                # Change on May 12
                if (group_cat[worst_ind] == 0) and (self.genes["groupAware"] >= 50):
                    # defend more violently against weaker groups (if group aware)
                    vengence_advantage = imm_gain_per_token + 2.0 * ((gain * self.gameParams["alpha"]) / tokens_needed)
                else:
                    vengence_advantage = imm_gain_per_token + (gain * self.gameParams["alpha"]) / tokens_needed
                # self.printT(player_idx, "    imm_gain_per_token: " + str(imm_gain_per_token) + "; vengence_advantage = " + str(vengence_advantage))

                if vengence_advantage > 0.0:
                    self.expected_defend_friend_damage = gain * self.gameParams["alpha"] * self.gameParams["steal"] / num_tokens
                    return (worst_ind, cantidad)

        return (-1, 0)


    def take_vengence(self, round_num, player_idx, num_players, selected_community, num_tokens, tokens_remaining, popularities, influence):
        # Change on May 5
        if (popularities[player_idx] <= 0.0) or (self.genes["vengencePriority"] < 50):
            return (-1, 0)

        multiplicador = self.genes["vengenceMultiplier"] / 33.0

        # Change on June 21
        vengence_max = min(num_tokens * self.genes["vengenceMax"] / 100.0, tokens_remaining)

        # self.printT(player_idx, "\n Vengence info:")

        # self.printT(player_idx, "attackLow: " + str(lowPoint) + "; attackHigh: " + str(highPoint) + "; attackFury: " + str(numAttackTokens))
        # self.printT(player_idx, "numAttackTokens: " + str(numAttackTokens))
        # self.attacks_on = np.zeros(num_players, dtype=float)

        ratio_predicted_steals = 1.0
        predicted_steals = sum(np.negative(self.attacks_with_me).clip(0))
        if self.attacks_with_me[player_idx] < 0:
            ratio_predicted_steals = predicted_steals / (-self.attacks_with_me[player_idx])

        # self.printT(player_idx, " ratio_predicted_steals: " + str(ratio_predicted_steals))

        vengence_possibilities = []
        for i in range(0, num_players):
            if (self.govPlayer[i] == 1) or (i == player_idx):
                continue

            if (influence[i][player_idx] < 0.0) and (-influence[i][player_idx] > (0.05 * popularities[player_idx])) and (influence[i][player_idx] < influence[player_idx][i]) and (popularities[i] > 0.01):
                keeping_strength_w = self.keeping_strength[i] * (popularities[i] / popularities[player_idx])
                theScore = num_tokens * ((influence[i][player_idx] - influence[player_idx][i]) / (popularities[player_idx] * self.gameParams["steal"] * self.gameParams["alpha"]))
                cantidad = int(min(-1.0 * (theScore - keeping_strength_w) * multiplicador, vengence_max) + 0.5)

                # Change on July 12
                if cantidad == 0:
                    continue

                my_weight = popularities[player_idx] * cantidad
                ratio = ratio_predicted_steals
                ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                if ratio2 > ratio_predicted_steals:
                    ratio = ratio2
                gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                while ((((gain*ratio)/num_tokens) * self.gameParams["alpha"] * self.gameParams["steal"]) > (popularities[i]-self.gameParams["poverty_line"])) and (cantidad > 0):
                    cantidad -= 1
                    if cantidad == 0:
                        break

                    my_weight = popularities[player_idx] * cantidad
                    ratio = ratio_predicted_steals
                    ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                    if ratio2 > ratio_predicted_steals:
                        ratio = ratio2
                    gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                ########

                if cantidad == 0:
                    continue
                # self.printT(player_idx, "   cantidad: " + str(cantidad))

                # Change on July 12 (commenting out the following since they are computed above)
                # my_weight = popularities[player_idx] * cantidad
                # ratio = ratio_predicted_steals
                # ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                # if ratio2 > ratio_predicted_steals:
                #     ratio = ratio2
                # gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                
                steal_ROI = (gain * self.gameParams["steal"]) / (cantidad * popularities[player_idx])
                damage = (gain / num_tokens) * self.gameParams["steal"] * self.gameParams["alpha"]

                imm_gain_per_token = (steal_ROI - self.ROI) * ((cantidad / num_tokens) * popularities[player_idx]) * self.gameParams["alpha"]
                imm_gain_per_token /= cantidad

                vengence_advantage = imm_gain_per_token + damage / cantidad

                # self.printT(player_idx, "against " + str(i) + ": " + str(vengence_advantage))
                # self.printT(player_idx, "   " + str(imm_gain_per_token))
                # self.printT(player_idx, "   " + str(damage))
                # self.printT(player_idx, "   " + str(cantidad))
                # self.printT(player_idx, "   " + str(steal_ROI))

                if vengence_advantage > 0.0:
                    # self.printT(player_idx, "adding: " + str(i) + ", " + str(cantidad) + ", " + str(vengence_advantage))
                    vengence_possibilities.append((i, vengence_advantage, cantidad))

        # random selection
        if len(vengence_possibilities) > 0:
            mag = 0.0
            for i in range(0, len(vengence_possibilities)):
                mag += vengence_possibilities[i][1]

            # REMOVING RANDOM
            # num = np.random.uniform(0, 1.0)
            if self.forced_random:
                num = self.getRand() / 1000.0
            else:
                num = np.random.randint(0,1001) / 1000.0

            sumr = 0.0
            for i in range(0, len(vengence_possibilities)):
                sumr += (vengence_possibilities[i][1] / mag)

                if (num <= sumr):
                    # self.printT(player_idx, "plan to attack player " + str(attackPossibility[i][0]) + " with " + str(numAttackTokens))
                    return (vengence_possibilities[i][0], vengence_possibilities[i][2])

        return (-1, 0)


    # Change on May 5-6
    def pillage_the_village(self, round_num, player_idx, num_players, selected_community, num_tokens, tokens_remaining, popularities, influence, group_cat):
        if (popularities[player_idx] <= 0.0) or (round_num < (self.genes["pillageDelay"] / 10.0)) or (self.genes["pillagePriority"] < 50):
            return (-1, 0)

        # self.printT(player_idx, "pillage tokens remaining: " + str(tokens_remaining))

        num_attack_tokens = min(tokens_remaining, int(num_tokens * (self.genes["pillageFury"] / 100.0) + 0.5))
        if num_attack_tokens <= 0:
            return (-1, 0)

        self.printT(player_idx, "\n Pillage info (" + str(num_attack_tokens) + "):")

        ratio_predicted_steals = 1.0
        predicted_steals = sum(np.negative(self.attacks_with_me).clip(0))
        if self.attacks_with_me[player_idx] < 0:
            ratio_predicted_steals = predicted_steals / (-self.attacks_with_me[player_idx])

        if round_num < 5:
            ratio_predicted_steals *= (self.genes["pillageCompanionship"] + 100.0) / 100.0

        self.printT(player_idx, "    ratio_predicted_steals: " + str(ratio_predicted_steals))

        pillage_possibilities = []
        for i in range(0, num_players):
            # Changes on May 6
            if (self.govPlayer[i] == 1) or (i == player_idx):
                continue

            # Change on May 6
            if (group_cat[i] < 2) and ((i not in selected_community) or (self.genes["pillageFriends"] >= 50)):  # player_idx is not fearful of the group player i is in and player_idx is willing to pillage friends (if i is a friend)
                cantidad = num_attack_tokens
                my_weight = popularities[player_idx] * cantidad
                ratio = ratio_predicted_steals
                ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                if ratio2 > ratio_predicted_steals:
                    ratio = ratio2
                gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                
                # Change on July 12
                while ((((gain*ratio)/num_tokens) * self.gameParams["alpha"] * self.gameParams["steal"]) > (popularities[i]-self.gameParams["poverty_line"])) and (cantidad > 0):
                    cantidad -= 1
                    if cantidad == 0:
                        break

                    my_weight = popularities[player_idx] * cantidad
                    ratio = ratio_predicted_steals
                    ratio2 = (my_weight + ((self.others_attacks_on[i] / self.gameParams["alpha"]) * num_tokens)) / my_weight
                    if ratio2 > ratio_predicted_steals:
                        ratio = ratio2
                    gain = my_weight - (popularities[i] * self.keeping_strength[i] / ratio)
                
                if cantidad == 0:
                    continue

                steal_ROI = (gain * self.gameParams["steal"]) / (cantidad * popularities[player_idx])
                damage = (gain / num_tokens) * self.gameParams["steal"] * self.gameParams["alpha"]

                # self.printT(player_idx, "    steal_ROI " + str(i) + ": " + str(steal_ROI))

                imm_gain_per_token = steal_ROI * ((cantidad / num_tokens) * popularities[player_idx]) * self.gameParams["alpha"]
                friend_penalty = (1.0 - self.gameParams["beta"]) * (damage / popularities[i]) * influence[i][player_idx]
                imm_gain_per_token -= friend_penalty
                imm_gain_per_token -= self.ROI * ((cantidad / num_tokens) * popularities[player_idx]) * self.gameParams["alpha"]
                imm_gain_per_token /= cantidad

                self.printT(player_idx, "    " + str(i) + " imm_gain_per_token: " + str(imm_gain_per_token))

                # identify security threats
                security_threat_advantage = imm_gain_per_token + damage / cantidad
                if round_num > 3:
                    my_growth = (self.pop_history[round_num][player_idx] - self.pop_history[round_num-4][player_idx]) / 4.0
                    their_growth = (self.pop_history[round_num][i] - self.pop_history[round_num-4][i]) / 4.0
                else:
                    my_growth = 0
                    their_growth = 0

                # Change on May 6
                if ((their_growth > (1.5 * my_growth)) and (popularities[i] > popularities[player_idx]) and (not i in selected_community)) or (group_cat[i] == 1):
                    # self.printT(player_idx, "      security_threat_advantage: " + str(security_threat_advantage) + " (" + str(their_growth) + " vs " + str(my_growth) + ")")
                    # self.printT(player_idx, "")
                    imm_gain_per_token += security_threat_advantage

                # Change on May 11
                margin = self.genes["pillageMargin"] / 100.0
                if imm_gain_per_token > margin:
                    pillage_possibilities.append((i, imm_gain_per_token, cantidad))

        self.printT(player_idx, "")

        # self.printT(player_idx, "Possible pillage: " + str(pillage_possibilities))

        # random selection
        if len(pillage_possibilities) > 0:
            self.printT(player_idx, "***** gonna pillage")
            mag = 0.0
            for i in range(0, len(pillage_possibilities)):
                mag += pillage_possibilities[i][1]
            # REMOVING RANDOM
            # num = np.random.uniform(0, 1.0)
            if self.forced_random:
                num = self.getRand() / 1000.0
            else:
                num = np.random.randint(0,1001) / 1000.0

            sumr = 0.0
            for i in range(0, len(pillage_possibilities)):
                sumr += (pillage_possibilities[i][1] / mag)

                if (num <= sumr):
                    # self.printT(player_idx, "plan to attack player " + str(attackPossibility[i][0]) + " with " + str(numAttackTokens))
                    return (pillage_possibilities[i][0], pillage_possibilities[i][2])

        return (-1, 0)


    def find_community_vec(self, num_players, communities, plyr):
        my_comm_vec = np.zeros(num_players, dtype=int)
        for s in communities:
            if plyr in s:
                for i in s:
                    my_comm_vec[i] = 1

                break

        return my_comm_vec


    # def attacks_with_me_prior(self, num_players, player_idx, selected_community, popularities, fury):
    #     awm_prior = np.zeros(num_players, dtype=float)

    #     for i in selected_community:
    #         awm_prior[i] = popularities[i] * (self.gameParams["alpha"]) * fury
    #         if i != player_idx:
    #             awm_prior[i] *= (self.genes["otherFury"] / 100.0)

    #     return awm_prior


    def is_keeping(self, other_idx, num_players):
        meAmount = 0.0
        totalAmount = 0.0
        for i in range(0, num_players):
            if self.govPlayer[i] == 1:
                continue

            if i != other_idx:
                if self.infl_neg[other_idx][i] > 0.0:
                    totalAmount += self.infl_neg[other_idx][i] / self.gameParams["steal"]
                    meAmount -= self.infl_neg[other_idx][i]
                else:
                    totalAmount += self.infl_pos[other_idx][i] / self.gameParams["give"]

        meAmount = (meAmount + self.infl_pos[other_idx][other_idx] - self.infl_neg[other_idx][other_idx]) / self.gameParams["keep"]
        totalAmount += meAmount

        # return meAmount
        if totalAmount > 0:
            return meAmount / totalAmount
        else:
            return 1.0


    def fear_keeping(self, num_players, player_idx, communities, agent_idx):
        amigos = self.find_community_vec(num_players, communities, agent_idx)
        enemigos = 1.0 - amigos

        # self.printT(player_idx, str(communities))

        sm = 0.0
        for i in range(num_players):
            if amigos[i]:
                sm = max(np.dot(enemigos, self.infl_neg[:,i]), sm)

        # self.printT(player_idx, str(amigos))
        # self.printT(player_idx, str(sm))

        denom = sum(self.infl_pos[:,agent_idx])
        if denom > 0:
            fear_tokens = (sm / sum(self.infl_pos[:,agent_idx]))
        else:
            fear_tokens = 0.0
        fear_tokens = min(1.0, fear_tokens * (self.genes["fearDefense"] / 50.0))   # assume everyone else has the same fear I do

        return fear_tokens


    def group_analysis(self, round_num, num_players, player_idx, popularities, influence):
        # B = [[29.0, 0, 13, 2, 6, 0, 0, 23, 16, 0, 2],[2, 14, 0, 19, 1, 30, 8, 1, 0, 16, 2],[13, 0, 16, 3, 7, 0, 3, 25, 13, 0, 2],[2, 13, 2, 25, -7, 7, 0, 4, -8, 14, 0],[3, 2, 3, -23, 39, 2, 0, 9, 9, 3, 2],[0, 37, 0, 13, 0, 12, 33, 0, 0, 3, 0],[1, 11, 1, 0, 0, 34, 19, 0, 6, 12, 0],[22, 0, 19, -29, 14, 0, 1, 45, 3, 0, 0],[19, 2, 17, 0, 22, 0, 4, 6, 10, 1, 2],[1, 12, 0, 19, -19, 4, 7, 0, -13, 55, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 74]]
        # influence = np.array(B)
        # self.infl_pos = np.positive(influence).clip(0)
        # self.infl_neg = np.negative(influence).clip(0)
        # self.scaled_back_nums = np.ones(num_players, dtype=float)

        if round_num == 0:
            A_pos = self.compute_adjacency(num_players)
            A_neg = self.compute_neg_adjacency(num_players)

            communities, modularity = self.louvain_c_method_phase1(num_players, A_pos, A_neg)
            self.printT(player_idx, "")
            self.printT(player_idx, " communities: " + str(communities))
            self.printT(player_idx, " modularity: " + str(modularity))

            self.coalition_target = self.compute_coalition_target(round_num, popularities, communities, player_idx)
            # self.printT(player_idx, " coalition_target: " + str(self.coalition_target))

            elijo = self.random_selections(num_players, player_idx, popularities)

            self.printT(player_idx, "chosen community: " + str(elijo.s))
        else:
            A_pos = self.compute_adjacency(num_players)
            A_neg = self.compute_neg_adjacency(num_players)

            # self.printT(player_idx, "A_pos")
            # self.printT(player_idx, str(A_pos))
            # self.printT(player_idx, "A_neg")
            # self.printT(player_idx, str(A_neg))

            # empieza = time.time()

            communities_ph1, modularity_ph1 = self.louvain_c_method_phase1(num_players, A_pos, A_neg)
            # p1 = time.time()
            # self.printT(player_idx, "phase1: " + str(p1 - empieza))

            self.printT(player_idx, " communities_ph1: " + str(communities_ph1))
            self.printT(player_idx, " modularity_ph1: " + str(modularity_ph1))
            # self.printT(player_idx, "")
            # self.printT(player_idx, "phase1 communities: " + str(communities_ph1))
            # self.printT(player_idx, "phase1 modularity: " + str(modularity_ph1))
            # self.printT(player_idx, "")

            communities_mega, modularity = self.louvain_method_phase2(communities_ph1, A_pos, A_neg)
            
            # p2 = time.time()
            # self.printT(player_idx, "phase2: " + str(p2 - p1))

            communities = self.enumerate_community(modularity_ph1, communities_ph1, modularity, communities_mega)

            self.printT(player_idx, " communities: " + str(communities))
            self.printT(player_idx, " modularity: " + str(modularity))
            self.printT(player_idx, "")

            self.coalition_target = self.compute_coalition_target(round_num, popularities, communities, player_idx)
            self.printT(player_idx, " coalition_target: " + str(self.coalition_target))

            # p3 = time.time()
            # self.printT(player_idx, "enumComm: " + str(p3 - p2))

            elijo = self.envision_communities(num_players, player_idx, popularities, influence, A_pos, A_neg, communities_ph1, communities, modularity)

            self.printT(player_idx, "\nchosen community: " + str(elijo.s))
            if player_idx == self.theTracked:
                elijo.print()

            # fin = time.time()
            # # self.printT(player_idx, "envision: " + str(fin - p3))
            # self.printT(player_idx, "totalAnalysis: " + str(fin - empieza))


        return communities, elijo


    def random_selections(self, num_players, player_idx, popularities):
        # init_comm_size = int(num_players * (self.genes["coalitionTarget"] / 100.0) + 0.5)

        # plyrs = set()
        # for i in range(num_players):
        #     if player_idx != i:
        #         plyrs.add(i)

        s = set()
        s.add(player_idx)
        pop = popularities[player_idx]
        total_pop = sum(popularities)
        # coalitionTarget = self.genes["coalitionTarget"] / 100.0
        while ((pop / total_pop) < self.coalition_target):
            # REMOVING RANDOM
            # sel = random.sample(plyrs, 1)
            # s.add(sel[0])
            # plyrs.remove(sel[0])
            # pop += popularities[sel[0]]

            if self.forced_random:
                num = (self.getRand() + player_idx) % num_players
            else:
                num = np.random.randint(0,1001) % num_players

            # self.printT(player_idx, "num: " + str(num))
            if (num not in s):
                s.add(num)
                pop += popularities[num]
                # self.printT(player_idx, "s_now: " + str(s))

        s = sorted(s)
        # self.printT(player_idx, "s_now: " + str(s))

        return CommunityEvaluation(s, 0.0, 0.0, 0.0, 0.0, 0.0)


    def remove_mostly_dead(self, s, player_idx, popularities):
        d = set()
        s_n = set()
        if popularities[player_idx] < 10.0:
            return s, d

        for i in s:
            if i == player_idx:
                s_n.add(i)
            elif popularities[i] < (0.1 * popularities[player_idx]):
                d.add(i)
            else:
                s_n.add(i)

        return s_n, d


    def envision_communities(self, num_players, player_idx, popularities, influence, A_pos, A_neg, communities_ph1, communities, modularity):
        potential_communities = []

        # print("player " + str(player_idx))

        # self.printT(player_idx, "popularities: " + str(popularities));

        # zero = time.time()

        s_idx = self.find_community(player_idx, communities)
        # self.printT(player_idx, "my community: " + str(communities[s_idx]))

        # Change on June 2
        cur_comm_size = 0.0
        # for i in range(len(communities[s_idx])):
        for i in communities[s_idx]:
            # self.printT(player_idx, str(popularities[i]))
            cur_comm_size += popularities[i]
        cur_comm_size /= sum(popularities)
        # self.printT(player_idx, "cur_comm_size: " + str(cur_comm_size))

        # uno = time.time()
        # self.printT(player_idx, "    findComm: " + str(uno - zero))

        c = self.make_deep_copy(communities)

        # dos = time.time()
        # self.printT(player_idx, "    copyComm: " + str(dos - uno))

        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)
        # print(s)

        # tres = time.time()
        # self.printT(player_idx, "    determineComm: " + str(tres - dos))

        s, d = self.remove_mostly_dead(s, player_idx, popularities)

        # cuatro = time.time()
        # self.printT(player_idx, "    removeDead: " + str(cuatro - tres))

        potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

        # cinco = time.time()
        # self.printT(player_idx, "    addComm: " + str(cinco - cuatro))

        # combine with any other group
        for i in range(len(communities)):
            if i != s_idx:
                c = self.make_deep_copy(communities)
                c[s_idx] = c[s_idx].union(c[i])
                if not self.already_in(c[s_idx], potential_communities):
                    c.pop(i)
                    # self.printT(player_idx, str(c))
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, self.find_community(player_idx, c), A_pos, A_neg)
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

        # move to a different group
        for i in range(len(communities)):
            if i != s_idx:
                c = self.make_deep_copy(communities)
                c[i].add(player_idx)
                if not self.already_in(c[i], potential_communities):
                    c[s_idx].remove(player_idx)
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, i, A_pos, A_neg)
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

        # add a member from another group
        for i in range(num_players):
            if i not in communities[s_idx]:
                c = self.make_deep_copy(communities)
                for s in c:
                    if i in s:
                        s.remove(i)
                        break
                c[s_idx].add(i)
                if not self.already_in(c[s_idx], potential_communities):
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

        # subtract a member from the group (that isn't player_idx)
        for i in communities[s_idx]:
            if i != player_idx:
                c = self.make_deep_copy(communities)
                c[s_idx].remove(i)
                if not self.already_in(c[s_idx], potential_communities):
                    c.append({i})
                    s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)
                    # self.printT(player_idx, str(s) + ": " + str(m))
                    s, d = self.remove_mostly_dead(s, player_idx, popularities)
                    potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))


        s2_idx = self.find_community(player_idx, communities_ph1)
        # if (s_idx != s2_idx):       # I believe that this is wrong; should be: if (communities[s_idx] != communities_ph1[s2_idx]):
        if (communities[s_idx] != communities_ph1[s2_idx]):
            s_idx = s2_idx
            # put in the original with combined other groups
            c = self.make_deep_copy(communities_ph1)
            s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)
            s, d = self.remove_mostly_dead(s, player_idx, popularities)
            potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

            # combine with any other group
            for i in range(len(communities_ph1)):
                if i != s_idx:
                    c = self.make_deep_copy(communities_ph1)
                    c[s_idx] = c[s_idx].union(c[i])
                    # print("considering " + str(c[s_idx]) + "(" + str(c[s_idx]) + " union " + str(c[i]) + ")")
                    if not self.already_in(c[s_idx], potential_communities):
                        c.pop(i)
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, self.find_community(player_idx, c), A_pos, A_neg)
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

            # move to a different group
            for i in range(len(communities_ph1)):
                if i != s_idx:
                    c = self.make_deep_copy(communities_ph1)
                    c[i].add(player_idx)
                    if not self.already_in(c[i], potential_communities):
                        c[s_idx].remove(player_idx)
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, i, A_pos, A_neg)
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

            # add a member from another group
            for i in range(num_players):
                if i not in communities_ph1[s_idx]:
                    c = self.make_deep_copy(communities_ph1)
                    for s in c:
                        if i in s:
                            s.remove(i)
                            break
                    c[s_idx].add(i)
                    if not self.already_in(c[s_idx], potential_communities):
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)
                        # self.printT(player_idx, str(c_prime))
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

            # subtract a member from the group (that isn't player_idx)
            for i in communities_ph1[s_idx]:
                if i != player_idx:
                    c = self.make_deep_copy(communities_ph1)
                    c[s_idx].remove(i)
                    if not self.already_in(c[s_idx], potential_communities):
                        c.append({i})
                        s, c_prime, m = self.determine_communities(num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg)
                        s, d = self.remove_mostly_dead(s, player_idx, popularities)
                        potential_communities.append(CommunityEvaluation(s, m, self.get_centrality(s, player_idx, popularities), self.get_collective_strength(popularities, s, cur_comm_size), self.get_familiarity(s, player_idx, num_players, influence), self.get_ingroup_antisocial(s, player_idx)))

        min_mod = modularity
        for c in potential_communities:
            # self.printT(player_idx, str(c.modularity))
            if c.modularity < min_mod:
                min_mod = c.modularity

        # self.printT(player_idx, "min_mod = " + str(min_mod))

        elegir = potential_communities[0]
        mx = -99999
        # self.printT(player_idx, " target: " + str(self.genes["coalitionTarget"]))
        for c in potential_communities:
            # self.printT(player_idx, str(c.modularity) + " " + str(min_mod) + " " + str(modularity) + " " + str(min_mod))
            if modularity == min_mod:
                c.modularity = 1.0
            else:
                c.modularity = (c.modularity - min_mod) / (modularity - min_mod)

            # Change on May 9
            c.compute_score(self.genes) #, self.coalition_target)
            if c.score > mx:
                elegir = c
                mx = c.score

            # if player_idx == self.theTracked:
            #     c.print()

        # adding this in on May 4
        self.me_importa = np.zeros(num_players, dtype=float)
        for i in elegir.s:
            mejor = 1.0
            if i != player_idx:
                for c in potential_communities:
                    if i not in c.s:
                        mejor = min(mejor, (elegir.score - c.score) / elegir.score)
            self.me_importa[i] = mejor

        # self.printT(player_idx, "me_importa: " + str(self.me_importa))

        return elegir


    def already_in(self, s, potential_communities):
        for c in potential_communities:
            if s == c.s:
                return True

        return False


    # def already_in(self, all_sets, u):
    #     for s in all_sets:
    #         if s == u:
    #             return True

    #     return False


    def determine_communities(self, num_players, player_idx, popularities, influence, c, s_idx, A_pos, A_neg):
        # zero = time.time()

        s = c.pop(s_idx)

        # uno = time.time()
        # self.printT(player_idx, "        removeComm: " + str(uno - zero))

        c_mega, m = self.louvain_method_phase2(c, A_pos, A_neg)

        # dos = time.time()
        # self.printT(player_idx, "        phase2: " + str(dos - uno))

        c_prime = self.enumerate_community(0, c, 1, c_mega)
        c_prime.append(s)

        # tres = time.time()
        # self.printT(player_idx, "        enumComm: " + str(tres - dos))

        # self.printT(player_idx, "c_prime: " + str(c_prime))
        # print(c_prime)
        cur_comms = np.zeros(num_players, dtype=int)
        for j in range(0,len(c_prime)):
            for i in c_prime[j]:
                # print(str(j) + " has " + str(i))
                cur_comms[i] = j
        # print(cur_comms)
        m = self.compute_signed_modularity(num_players, cur_comms, A_pos, A_neg)
        # m = self.compute_signed_modularity(num_players, c_prime, A_pos, A_neg)

        # cuatro = time.time()
        # self.printT(player_idx, "        signedMod: " + str(cuatro - tres))
        # print(s)

        return s, c_prime, m


    def compute_signed_modularity(self, num_players, cur_comms, A_pos, A_neg):
        modu = self.alpha * self.compute_modularity(num_players, cur_comms, A_pos)
        modu -= (1.0 - self.alpha) * self.compute_modularity(num_players, cur_comms, A_neg)

        return modu


    # def compute_signed_modularity(self, num_players, c, A_pos, A_neg):
    #     m = self.alpha * self.compute_modularity2(num_players, c, A_pos)
    #     m -= (1.0 - self.alpha) * self.compute_modularity2(num_players, c, A_neg)

    #     return m


    def make_deep_copy(self, comm):
        c = []
        for s in comm:
            c.append(s.copy())

        return c


    def find_community(self, player_idx, communities):
        for i in range(len(communities)):
            if player_idx in communities[i]:
                return i

        print("Problem: Didn't find a community")
        sys.exit()

        return -1


    def louvain_c_method_phase1(self, num_players, A_pos, A_neg):
        current_communities = list(range(num_players))

        if num_players == 0:
            communities = []
            return communities, 0.0
        
        the_groups = set(range(num_players))
        com_matrix = np.identity(num_players)
        # print(len(A_pos))
        m_pos = sum(sum(A_pos))
        K_pos = sum(A_pos)
        m_neg = sum(sum(A_neg))
        K_neg = sum(A_neg)
        com_counts = np.ones(num_players, dtype=int)
        hay_cambio = True

        while hay_cambio:
            hay_cambio = False
            for i in range(num_players):
                mx_com = current_communities[i]
                best_dQ = 0.0
                for j in the_groups:
                    if current_communities[i] == j:
                        continue

                    dQ_pos = self.move_i_to_j(num_players, com_matrix, m_pos, K_pos, A_pos, i, j, current_communities[i])
                    dQ_neg = self.move_i_to_j(num_players, com_matrix, m_neg, K_neg, A_neg, i, j, current_communities[i])
                    # print("   dQ_pos: " + str(dQ_pos) + "; dQ_neg: " + str(dQ_neg))

                    dQ = self.alpha * dQ_pos - (1-self.alpha) * dQ_neg
                    if dQ > best_dQ:
                        mx_com = j
                        best_dQ = dQ

                if best_dQ > 0.0:
                    com_matrix[current_communities[i]][i] = 0
                    com_counts[current_communities[i]] -= 1
                    if (com_counts[current_communities[i]] <= 0):
                        the_groups.remove(current_communities[i])
                    com_matrix[mx_com][i] = 1
                    com_counts[mx_com] += 1
                    current_communities[i] = mx_com
                    hay_cambio = True

        communities = []
        for i in range(num_players):
            if com_counts[i] > 0:
                s = set()
                for j in range(num_players):
                    if com_matrix[i][j] == 1:
                        s.add(j)
                communities.append(s)

        the_modularity = self.alpha * self.compute_modularity(num_players, current_communities, A_pos)
        the_modularity -= (1 - self.alpha) * self.compute_modularity(num_players, current_communities, A_neg)

        return communities, the_modularity


    def move_i_to_j(self, num_players, com_matrix, m, K, A, i, com_j, com_i):
        # first, what is the change in modularity from putting i into j's community
        sigma_in = 0.0
        for k in range(num_players):
            if com_matrix[com_j][k] == 1:
                sigma_in += np.dot(com_matrix[com_j], A[k])

        sigma_tot = np.dot(com_matrix[com_j], K)
        k_iin = np.dot(com_matrix[com_j], A[i])
        twoM = 2.0*m

        if twoM == 0:
            return 0.0

        a = (sigma_in + 2*k_iin) / twoM
        b = (sigma_tot + K[i]) / twoM
        c = sigma_in / twoM
        d = sigma_tot / twoM
        e = K[i] / twoM
        dQ_in = (a - (b*b)) - (c - d*d - e*e)

        # second, what is the change in modularity from removing i from its community
        com = com_matrix[com_i].copy()
        com[i] = 0
        sigma_in = 0.0
        for k in range(num_players):
            if com[k] == 1:
                sigma_in += np.dot(com, A[k])

        sigma_tot = np.dot(com, K)

        k_iin = np.dot(com, A[i])

        a = (sigma_in + 2*k_iin) / twoM
        b = (sigma_tot + K[i]) / twoM
        c = sigma_in / twoM
        d = sigma_tot / twoM
        e = K[i] / twoM
        dQ_out = (a - (b*b)) - (c - d*d - e*e)

        return dQ_in - dQ_out


    def compute_modularity(self, num_players, current_communities, A):
        k = sum(A)
        m = sum(k)

        if m == 0:
            return 0.0

        Q = 0
        for i in range(num_players):
            for j in range(num_players):
                Q += self.deltar(current_communities, i, j) * (A[i][j] - ((k[i] * k[j]) / (2*m)))
        Q /= 2*m

        return Q


    def deltar(self, current_communities, i, j):
        if current_communities[i] == current_communities[j]:
            return 1
        else:
            return 0


    def compute_modularity2(self, num_players, communities, A):
        k = sum(A)
        m = sum(k)

        if m == 0:
            return 0.0

        Q = 0
        for i in range(num_players):
            for j in range(num_players):
                Q += self.deltar2(communities, i, j) * (A[i][j] - ((k[i] * k[j]) / (2*m)))
        Q /= 2*m

        return Q
        

    def deltar2(self, communities, i, j):
        for s in communities:
            if (i in s) and (j in s):
                return 1
        
        return 0


    def louvain_method_phase2(self, communities_ph1, A_pos, A_neg):
        num_communities = len(communities_ph1)
        # print("    num_communities: " + str(num_communities))
        
        # Lump individuals into communities: compute B_pos and B_neg
        B_pos = np.zeros((num_communities, num_communities), dtype=float)
        B_neg = np.zeros((num_communities, num_communities), dtype=float)

        for i in range(num_communities):
            for j in range(num_communities):
                for k in communities_ph1[i]:
                    for m in communities_ph1[j]:
                        B_pos[i][j] += A_pos[k][m]
                        B_neg[i][j] += A_neg[k][m]

        # print(B_pos)

        return self.louvain_c_method_phase1(num_communities, B_pos, B_neg)


    def enumerate_community(self, modularity_ph1, communities_ph1, modularity, communities_mega):
        if modularity > modularity_ph1:
            communities = []
            for m in communities_mega:
                communities.append(set())
                for i in m:
                    for j in communities_ph1[i]:
                        communities[len(communities)-1].add(j)
                    
        else:
            communities = communities_ph1

        return communities


    # Change on May 9
    def get_collective_strength(self, popularities, s, cur_comm_size):
        proposed = 0.0
        for i in s:
            proposed += popularities[i]
        proposed /= sum(popularities)
        
        if self.genes["coalitionTarget"] == 0:
            target = 0.01
        else:
            target = self.genes["coalitionTarget"] / 100.0

        base = 1.0 - (abs(target - cur_comm_size) / target)
        if base < 0.01:
            base = 0.01
        base *= base

        # print(str(s) + ": " + str(proposed) + "; " + str(target) + "; " + str(cur_comm_size) + "; " + str(base))
        if abs(proposed-cur_comm_size) <= 0.03:
            return base
        elif abs(cur_comm_size - target) < abs(proposed - target):
            nbase = 1.0 - (abs(target - proposed) / target)
            if nbase < 0.01:
                nbase = 0.01
            return nbase * nbase
        else:
            baseline = (1.0 + base) / 2.0
            w = abs(proposed - target) / abs(cur_comm_size - target)
            return ((1.0 - w) * 1.0) + (baseline * w)

    
    # comparison to average, rank, comparison to top
    def get_centrality(self, s, player_idx, popularities):
        group_sum = 0
        mx = 0.0
        num_greater = 0
        for i in s:
            group_sum += popularities[i]
            if popularities[i] > mx:
                mx = popularities[i]
            if popularities[i] > popularities[player_idx]:
                num_greater += 1

        if (group_sum > 0.0) and (len(s) > 1):
            ave_sum = group_sum / len(s)
            aveVal = popularities[player_idx] / ave_sum
            mxVal = popularities[player_idx] / mx
            rankVal = 1 - (num_greater / (len(s)-1.0))

            return (aveVal + mxVal + rankVal) / 3.0
        else:
            return 1.0


    def get_familiarity(self, s, player_idx, num_players, influence):
        mag = sum(self.infl_pos[:,player_idx])
        if mag > 0.0:
            randval = mag / num_players
            ind_loyalty = 0.0
            scaler = 1.0
            for i in s:
                if (self.scaled_back_nums[i] < 0.05) and (i != player_idx):
                    scaler *= ((len(s) - 1) / len(s))
                    
                if (influence[i][player_idx] * self.scaled_back_nums[i]) > randval:
                    ind_loyalty += influence[i][player_idx] * self.scaled_back_nums[i] #self.scale_back(player_idx, i)
                else:
                    ind_loyalty += (influence[i][player_idx] * self.scaled_back_nums[i]) - randval
            familiarity = max(0.01, scaler * (ind_loyalty / mag))
        else:
            familiarity = 1.0

        if familiarity < 0.0:
            familiarity = 0.0

        return familiarity

    
    def get_ingroup_antisocial(self, s, player_idx):
        # if i isn't giving much compared to what they receive
        # if i is keeping a lot more than is normal
        # if i isn't reciprocating with me
        # if i is stealing from people in s
        # if i is stealing from people in other groups without cause

        # then maybe i'm less inclined to have i in my group
        scl = 1.0
        piece = 1.0 / len(s)
        remain = 1.0 - piece
        for i in s:
            if i != player_idx:
                the_investment = 0.0
                the_return = 0.0
                for j in s:
                    if i != j:
                        the_investment += self.sum_infl_pos[j][i]
                        the_return += self.sum_infl_pos[i][j]

                if the_investment > 0.0:
                    val = the_return / the_investment
                    if val > 1.0:
                        val = 1.0
                    scl *= piece * val + remain

        # self.printT(player_idx, str(s) + ": " + str(scl))
        return scl
