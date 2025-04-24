import time
from collections import Counter

from social_choice_sim import Social_Choice_Sim
from options_creation import generate_two_plus_one_groups


def create_empty_vote_matrix(num_players):
    return [[0 for _ in range(num_players)] for _ in range(num_players)]


class SCManager:
    def __init__(self, connection_manager, num_humans, num_players, num_bots, sc_group_option, vote_cycles):
        self.connection_manager = connection_manager
        self.round_num = 1
        self.save_dict = {}
        self.big_dict = {}
        self.utilities = {i: 0 for i in range(num_humans)}
        self.sc_sim = Social_Choice_Sim(num_players, num_humans, 1)
        self.sc_groups = generate_two_plus_one_groups(num_players, sc_group_option)
        self.num_players = num_players
        self.num_bots = num_bots
        self.vote_cycles = vote_cycles

        # Tracking the SC game over time
        self.options_history = {}
        self.options_votes_history = {}
        # Tracks how the vote of every player would have affected each player had that cause passed
        self.vote_effects = create_empty_vote_matrix(num_players)
        self.vote_effects_history = {}
        self.positive_vote_effects_history = create_empty_vote_matrix(num_players)
        self.negative_vote_effects_history = create_empty_vote_matrix(num_players)

    def init_next_round(self):
        # Initialize the round
        self.sc_sim.start_round(self.sc_groups)
        self.current_options_matrix = self.sc_sim.get_current_options_matrix()
        self.options_history[self.round_num] = self.current_options_matrix
        self.player_nodes = self.sc_sim.get_player_nodes()
        self.causes = self.sc_sim.get_causes()
        self.all_nodes = self.causes + self.player_nodes

        self.connection_manager.distribute_message("SC_INIT", self.round_num, self.current_options_matrix,
                                                   [node.to_json() for node in self.all_nodes],
                                                   self.current_options_matrix)

    def play_social_choice_round(self):
        # self.init_next_round()

        # Run the voting and collect the votes
        player_votes = self.run_sc_voting()
        zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes, self.current_options_matrix, self.round_num)
        self.update_vote_effects(zero_idx_votes, self.current_options_matrix,
                                 self.round_num)  # Tracks the effects of each player's vote on everyone else

        # Calculate the winning vote
        total_votes = len(zero_idx_votes)
        winning_vote_count = Counter(zero_idx_votes.values()).most_common(1)[0][1]
        winning_vote = Counter(zero_idx_votes.values()).most_common(1)[0][0]

        if not (winning_vote_count > total_votes // 2):
            winning_vote = -1

        # Apply the vote and send out the after round info
        if winning_vote == -1:
            new_utilities = {i: 0 for i in range(self.num_players)}
        else:
            self.sc_sim.apply_vote(winning_vote)
            new_utilities = self.sc_sim.get_player_utility()

        self.connection_manager.distribute_message("SC_OVER", self.round_num, winning_vote, new_utilities,
                                                   self.positive_vote_effects_history,
                                                   self.negative_vote_effects_history, zero_idx_votes,
                                                   self.current_options_matrix)

        time.sleep(.5)  # Without this, messages get sent out of order, and the sc_history gets screwed up.
        self.round_num += 1
        self.init_next_round()

    def run_sc_voting(self):
        player_votes = {}
        is_last_cycle = False

        for cycle in range(self.vote_cycles):
            player_votes.clear()
            # Waits for a vote from each client
            while len(player_votes) < self.connection_manager.num_clients:
                responses = self.connection_manager.get_responses()
                for response in responses.values():
                    player_votes[response["CLIENT_ID"]] = response["FINAL_VOTE"]

            zero_idx_votes, one_idx_votes = self.compile_sc_votes(player_votes, self.current_options_matrix,
                                                                  self.round_num)
            if cycle == self.vote_cycles - 1: is_last_cycle = True
            self.connection_manager.distribute_message("SC_VOTES", zero_idx_votes, cycle + 1, is_last_cycle)

        return player_votes

    def compile_sc_votes(self, player_votes, current_options_matrix, round_num):
        bot_votes = self.get_bot_votes(current_options_matrix)

        all_votes = {**bot_votes, **player_votes}
        all_votes_list = [option_num + 1 if option_num != -1 else -1 for option_num in
                          all_votes.values()]  # Convert 0-based votes to 1-based for display, but leave voters of -1 as they are
        self.options_votes_history[round_num] = all_votes  # Saves the history of votes

        return all_votes, all_votes_list

    def update_vote_effects(self, all_votes, current_options_matrix, round_num):
        round_vote_effects = create_empty_vote_matrix(self.num_players)
        for i in range(self.num_players):
            selected_vote = all_votes[i]  # Which option the ith player voted for
            if selected_vote != -1:
                for j in range(self.num_players):
                    vote_effect = current_options_matrix[j][selected_vote]
                    self.vote_effects[j][i] += vote_effect  # The effect of the ith player's vote on the jth player
                    round_vote_effects[i][j] = vote_effect

                    if vote_effect > 0:
                        self.positive_vote_effects_history[i][j] += vote_effect
                    elif vote_effect < 0:
                        self.negative_vote_effects_history[i][j] += vote_effect
        self.vote_effects_history[str(round_num)] = round_vote_effects

    def get_bot_votes(self, current_options_matrix):
        bot_options = current_options_matrix[:self.num_bots]
        votes = {}
        for bot_id, options in enumerate(bot_options):
            votes[bot_id] = options.index(max(options))

        return votes
