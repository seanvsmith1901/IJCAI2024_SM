from collections import Counter

from options_creation import generate_two_plus_one_groups
from sim_interface import JHG_simulator
from social_choice_sim import Social_Choice_Sim

def create_empty_vote_matrix(num_players):
    return [[0 for _ in range(num_players)] for _ in range(num_players)]


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
        self.vote_effects = create_empty_vote_matrix(options["TOTAL_PLAYERS"])
        self.vote_effects_history = {}
        self.positive_vote_effects_history = create_empty_vote_matrix(options["TOTAL_PLAYERS"])
        self.negative_vote_effects_history = create_empty_vote_matrix(options["TOTAL_PLAYERS"])


    # --- JHG Functions --- #


    def play_jhg_round(self, round_num):
        client_input = self.connection_manager.get_responses() # Gets responses of type "JHG"
        current_popularity = self.jhg_sim.execute_round(client_input, round_num-1)

        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()

        sent_dict, received_dict = self.get_sent_and_received(allocations_matrix)
        unique_messages = [received_dict, sent_dict]
        self.connection_manager.distribute_message("JHG_OVER", round_num, list(current_popularity), unique_messages = unique_messages)

        return client_input


    def get_sent_and_received(self, allocations_matrix):
        sent_dict = {}
        received_dict = {}
        bot_offset = self.connection_manager.num_bots

        for client_id in self.connection_manager.clients.keys():
            sent = [0 for _ in range(self.num_players)]
            received = [0 for _ in range(self.num_players)]
            for player in range(self.num_players):
                sent[player] = allocations_matrix[client_id + bot_offset][player]
                received[player] = allocations_matrix[player][client_id + bot_offset]
            sent_dict[client_id] = sent
            received_dict[client_id] = received

        return sent_dict, received_dict


    # --- JHG Functions --- #


    def play_social_choice_round(self, round_num):
        # Initialize the round
        self.sc_sim.start_round(self.sc_groups)
        new_influence = self.jhg_sim.get_influence().tolist()
        current_options_matrix = self.sc_sim.get_current_options_matrix()
        self.options_history[round_num] = current_options_matrix
        player_nodes = self.sc_sim.get_player_nodes()
        causes = self.sc_sim.get_causes()
        all_nodes = causes + player_nodes

        self.connection_manager.distribute_message("SC_INIT", current_options_matrix, [node.to_json() for node in all_nodes], current_options_matrix, new_influence)

        # Run the voting and collect the votes
        player_votes = self.run_sc_voting()
        zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes, current_options_matrix, round_num)
        self.update_vote_effects(zero_idx_votes, current_options_matrix, round_num) # Tracks the effects of each player's vote on everyone else

        # Calculate the winning vote
        total_votes = len(zero_idx_votes)
        winning_vote_count = Counter(zero_idx_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(zero_idx_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > total_votes // 2):
            winning_vote = -1

        # Apply the vote and send out the after round info
        self.sc_sim.apply_vote(winning_vote)
        new_utilities = self.sc_sim.get_player_utility()

        self.connection_manager.distribute_message("SC_OVER", winning_vote, new_utilities,
                                                   self.positive_vote_effects_history, self.negative_vote_effects_history,
                                                   one_idx_votes, current_options_matrix)


    def run_sc_voting(self):
        player_votes = {}
        player_fake_votes = {}

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

        return player_votes


    def compile_sc_votes(self, player_votes, current_options_matrix, round_num):
        bot_votes = self.jhg_sim.get_bot_votes(current_options_matrix)

        all_votes = {**bot_votes, **player_votes}
        all_votes_list = [option_num + 1 for option_num in all_votes.values()]  # Convert 0-based votes to 1-based for display
        self.options_votes_history[round_num] = all_votes  # Saves the history of votes

        return all_votes, all_votes_list


    def update_vote_effects(self, all_votes, current_options_matrix, round_num):
        round_vote_effects = create_empty_vote_matrix(self.num_players)
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
        self.vote_effects_history[str(round_num)] = round_vote_effects