import time
from collections import Counter

from options_creation import generate_two_plus_one_groups
from sim_interface import JHG_simulator
from social_choice_sim import Social_Choice_Sim


class GameServer:
    def __init__(self, connection_manager, options):
        #General
        self.connection_manager = connection_manager
        self.num_players = options["TOTAL_PLAYERS"]
        self.jhg_rounds_per_sc_round = options["JHG_ROUNDS_PER_SC_ROUND"]

        # JHG
        self.current_round = 1
        self.jhg_sim = JHG_simulator(self.connection_manager.num_clients, options["TOTAL_PLAYERS"]) # creates a new JHG simulator object
        self.num_bots = options["NUM_BOTS"]

        # SC
        self.sc_round = 0
        self.save_dict = {}
        self.big_dict = {}
        self.utilities = {i: 0 for i in range(options["NUM_HUMANS"])}
        self.sc_sim = Social_Choice_Sim(options["TOTAL_PLAYERS"])
        self.sc_groups = generate_two_plus_one_groups(options["TOTAL_PLAYERS"], options["SC_GROUP_SIZE"])

        # Tracking the SC game over time
        self.options_history = {}
        self.options_votes_history = {}
        # Tracks how the vote of every player would have affected each player had that cause passed
        self.vote_effects = [[0 for _ in range(options["TOTAL_PLAYERS"])] for _ in range(options["TOTAL_PLAYERS"])]
        self.vote_effects_history = {}
        self.positive_vote_effects_history = [[0 for _ in range(options["TOTAL_PLAYERS"])] for _ in range(options["TOTAL_PLAYERS"])]
        self.negative_vote_effects_history = [[0 for _ in range(options["TOTAL_PLAYERS"])] for _ in range(options["TOTAL_PLAYERS"])]

    def play_jhg_round(self, round):
        client_input = self.connection_manager.get_responses() # Gets responses of type "JHG"
        current_popularity = self.jhg_sim.execute_round(client_input, round-1)

        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()

        received = self.get_received(allocations_matrix)
        sent = self.get_sent(allocations_matrix)
        unique_messages = [received, sent]
        self.connection_manager.distribute_message("JHG_OVER", round, list(current_popularity), unique_messages = unique_messages)

        return client_input


    def play_social_choice_round(self, round):
        # Initialize the round
        self.sc_sim.start_round(self.sc_groups)
        new_influence = self.jhg_sim.get_influence().tolist()
        current_options_matrix = self.sc_sim.get_current_options_matrix()
        self.options_history[round] = current_options_matrix
        player_nodes = self.sc_sim.get_player_nodes()
        causes = self.sc_sim.get_causes()
        all_nodes = causes + player_nodes
        player_votes = {}
        player_fake_votes = {}

        self.connection_manager.distribute_message("SC_INIT", current_options_matrix, [node.to_json() for node in all_nodes], current_options_matrix, new_influence)


        # Keeps listening for client votes until all players have voted
        while len(player_votes) < self.connection_manager.num_clients:
            responses = self.connection_manager.get_responses()
            for response in responses.values():
                if response["TYPE"] == "POTENTIAL_SC_VOTE":
                    if response["CLIENT_ID"] not in player_fake_votes or player_fake_votes[response["CLIENT_ID"]] !=response["POTENTIAL_SC_VOTE"]:
                        player_fake_votes[response["CLIENT_ID"]] = response["POTENTIAL_SC_VOTE"]
                elif response["TYPE"] == "SUBMIT_SC":
                    if response["FINAL_VOTE"] not in player_votes or player_votes[response["FINAL_VOTE"]] != response["FINAL_VOTE"]:
                        player_votes[str(response["CLIENT_ID"])] = response["FINAL_VOTE"]
            self.connection_manager.distribute_message("SC_VOTES", player_fake_votes)
                        # ### Sean's saving stuff ###
                        # self.append_stuff_big(player_fake_votes, "POTENTIAL_VOTE")

            # sends out all the potential votes that we have made and redistributes them so that everyone can see them.

        bot_votes = self.jhg_sim.get_bot_votes(current_options_matrix)

        all_votes = {**bot_votes, **player_votes}
        all_votes_list = [option_num + 1 for option_num in all_votes.values()] # Adds one for display purposes
        self.options_votes_history[round] = all_votes # Saves the history of votes

        # Tracks the effects of each player's vote on everyone else
        self.update_vote_effects(all_votes, current_options_matrix, round)

        total_votes = len(all_votes)
        winning_vote_count = Counter(all_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(all_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > total_votes // 2):
            winning_vote = -1

        self.sc_sim.apply_vote(winning_vote)  # once again needs to be done from gameserver, as that is where winning vote is consolidated.
        # aight now you have the winning vote, so what you need to do is export
        # 1. the winning vote, 2. the new utility of each player, and yeah, that's pretty much it

        new_utilities = self.sc_sim.get_player_utility()

        self.connection_manager.distribute_message("SC_OVER", winning_vote, new_utilities,
                                                   self.positive_vote_effects_history, self.negative_vote_effects_history,
                                                   all_votes_list, current_options_matrix)
        # ### Sean's saving stuff ###
        # self.append_save_dict(player_votes, winning_vote)

        # Note: Removing this time.sleep will brick the program... So, unless you're ready to redo how the server connection works, it stays.
        time.sleep(.5) # Force the fetcher to sleep for a little bit so we know which vote has won. And congrats!

        self.connection_manager.distribute_message("SWITCH_ROUND", "jhg")


    def get_received(self, allocations_matrix):
        received_dict = {}
        for client_id in self.connection_manager.clients.keys():
            received = [0 for player in range(self.num_players)]
            for player in range(self.num_players):
                received[player] = allocations_matrix[player][client_id + self.connection_manager.num_bots]
            received_dict[client_id] = received

        return received_dict

    def get_sent(self, allocations_matrix):
        sent_dict = {}
        for client_id in self.connection_manager.clients.keys():
            sent = [0 for player in range(self.num_players)]
            for player in range(self.num_players):
                sent[player] = allocations_matrix[client_id + self.connection_manager.num_bots][player]
            sent_dict[client_id] = sent

        return sent_dict


    def update_vote_effects(self, all_votes, current_options_matrix, round):
        round_vote_effects = [[0 for _ in range(self.num_players)] for _ in
                              range(self.num_players)]  # The effects of just this round
        for i in range(self.num_players):
            selected_vote = all_votes[str(i)]  # Which option the ith player voted for
            for j in range(self.num_players):
                vote_effect = current_options_matrix[j][selected_vote]
                self.vote_effects[j][i] += vote_effect  # The effect of the ith player's vote on the jth player
                round_vote_effects[i][j] = vote_effect

                if vote_effect > 0:
                    self.positive_vote_effects_history[i][j] += vote_effect
                elif vote_effect < 0:
                    self.negative_vote_effects_history[i][j] += vote_effect
        self.vote_effects_history[str(round)] = round_vote_effects

        ### Sean's saving stuff ###
        # def append_save_dict(self, all_votes, winning_vote): # just adds the new vote dict to the fetcher.
        #     all_votes["winning_cause"] = winning_vote
        #     if self.current_round not in self.save_dict:
        #         self.save_dict[self.current_round] = all_votes
        #
        # def append_stuff_big(self, new_potential_votes, potential_or_final):
        #     if self.current_round not in self.big_dict:
        #         self.big_dict[self.current_round] = {} # initialize an empty round
        #     index = len(self.big_dict[self.current_round])+1
        #     self.big_dict[self.current_round][index] = {} # new index, slap the potential or final in there.
        #     self.big_dict[self.current_round][index][potential_or_final] = new_potential_votes.copy() # it is imperative that this be a copy. IDK why.
        #
        # def save_stuff_big(self):
        #     desktop_path = os.path.expanduser("~/Desktop")
        #     folder_path = os.path.join(desktop_path, "sc_sim_jsons", "low_level_jsons")
        #     low_level_path = "sc_sim_low_level.json"
        #     # if not os.path.exists(folder_path): # folder should already be guaranteed to exist. don't worry about it.
        #     #     os.makedirs(folder_path)
        #
        #     file_path_2 = os.path.join(folder_path, low_level_path)
        #     unique_file_path_2 = self.get_unique_filename(file_path_2)
        #
        #     with open(unique_file_path_2, "w") as f:
        #         json.dump(self.big_dict, f, indent=4)
        #
        #
        # def save_stuff_small(self):
        #     desktop_path = os.path.expanduser("~/Desktop")
        #     folder_path = os.path.join(desktop_path, "sc_sim_jsons")
        #     top_level_path = "sc_top_level_json"
        #
        #     file_path_1 = os.path.join(folder_path, top_level_path)
        #     unique_file_path_1 = self.get_unique_filename(file_path_1)
        #
        #     with open(unique_file_path_1, "w") as f:
        #         json.dump(self.save_dict, f, indent=4)
        #
        #
        # def get_unique_filename(self, file_path):
        #     if not os.path.exists(file_path):
        #         return file_path
        #     else:
        #         base, extension = os.path.splitext(file_path)
        #         counter = 1
        #         while os.path.exists(f"{base}_{counter}{extension}"):
        #             counter += 1
        #         return f"{base}_{counter}{extension}"