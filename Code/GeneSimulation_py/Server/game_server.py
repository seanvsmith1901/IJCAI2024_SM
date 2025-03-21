import os.path
import time
from collections import Counter

import select
import json

from options_creation import generate_two_plus_one_groups
from sim_interface import JHG_simulator
from social_choice_sim import Social_Choice_Sim


class ReceivedData:
    def __init__(self, client_id, allocations):
        self.client_id = client_id
        self.allocations = allocations


class GameServer:
    def __init__(self, new_clients, client_id_dict, client_usernames, max_rounds, num_bots, num_causes, num_players, group_sizes_option):
        #General
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.num_players = num_players
        self.client_usernames = client_usernames

        # JHG
        self.current_round = 0
        self.jhg_sim = JHG_simulator(len(new_clients), num_players) # creates a new JHG simulator object
        self.num_bots = num_bots

        # SC
        self.num_causes = num_causes
        self.save_dict = {}
        self.big_dict = {}
        self.utilities = None
        self.sc_sim = Social_Choice_Sim(num_players, self.num_causes)

        self.sc_groups = generate_two_plus_one_groups(num_players, group_sizes_option)

        # Tracking the SC game over time
        self.options_history = {}
        self.options_votes_history = {}
        self.vote_effects = []  # Tracks how the vote of every player would have affected each player had that cause passed
        self.vote_effects_history = {}
        self.positive_vote_effects_history = []  # Tracks every positive vote effect by the ith player on the jth player
        self.negative_vote_effects_history = []  # Tracks every negative vote effect by the ith player on the jth player

        self.start_game(max_rounds)


    def start_game(self, max_rounds):
        round = 1
        sc_round = 0
        self.utilities = {i: 0 for i in range(self.num_players)}
        self.vote_effects = [[0 for _ in range(self.num_players)] for _ in range(self.num_players)]
        self.positive_vote_effects_history = [[0 for _ in range(self.num_players)] for _ in range(self.num_players)]
        self.negative_vote_effects_history = [[0 for _ in range(self.num_players)] for _ in range(self.num_players)]

        while self.current_round <= max_rounds:
            # This range says how many jhg rounds to play between sc rounds
            for i in range(1):
                self.play_jhg_round(round)
                print(f"Played round {round}")
                round += 1
                print("New round")
            self.play_social_choice_round(sc_round)
            sc_round += 1
            print("New round")

        self.save_stuff_small()
        self.save_stuff_big()
        print("game over")

    def play_social_choice_round(self, round):
        self.sc_sim.start_round(self.sc_groups)
        new_influence = self.jhg_sim.get_influence().tolist()
        # new_relations = self.sc_sim.calculate_relation_strength(new_influence)
        current_options_matrix = self.sc_sim.get_current_options_matrix()
        self.options_history[round] = current_options_matrix
        player_nodes = self.sc_sim.get_player_nodes()
        causes = self.sc_sim.get_causes()
        all_nodes = causes + player_nodes

        message = {
            "ROUND_TYPE" : "sc_init",
            "OPTIONS" : current_options_matrix,
            "NODES" : [node.to_json() for node in all_nodes],
            "UTILITIES" : current_options_matrix,
            "INFLUENCE_MAT": new_influence,
            # "RELATION_STRENGTH": new_relations,
        }

        for i in range(len(self.connected_clients)):
            self.connected_clients[i].send(json.dumps(message).encode())

        player_votes = {}
        player_fake_votes = {}
        # Keeps listening for client votes until all players have voted
        # TODO: send the displayed vote to the bots so they can interact with the system.
        while len(player_votes) < len(self.connected_clients):
            data = self.get_client_data()
            for client, received_json in data.items():
                if "FINAL_VOTE" in received_json:
                    if received_json["FINAL_VOTE"] not in player_votes or player_votes[received_json["FINAL_VOTE"]] != received_json["FINAL_VOTE"]:
                        player_votes[received_json["CLIENT_ID"]] = received_json["FINAL_VOTE"]
                        self.append_stuff_big(player_fake_votes, "FINAL_VOTE")
                if "POTENTIAL_VOTE" in received_json:
                    # if there are no votes or if the vote is different, update and pass it down.
                    if received_json["CLIENT_ID"] not in player_fake_votes or player_fake_votes[received_json["CLIENT_ID"]] != received_json["POTENTIAL_VOTE"]:
                        player_fake_votes[received_json["CLIENT_ID"]] = received_json["POTENTIAL_VOTE"]
                        self.append_stuff_big(player_fake_votes, "POTENTIAL_VOTE")
            # sends out all the potential votes that we have made and redistributes them so that everyone can see them.
            message = {
                "ROUND_TYPE" : "sc_vote",
                "POTENTIAL_VOTES" : player_fake_votes,
            }
            for i in range(len(self.connected_clients)):
                self.connected_clients[i].send(json.dumps(message).encode())

        bot_votes = self.jhg_sim.get_bot_votes(current_options_matrix)

        all_votes = {**bot_votes, **player_votes}
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

        message = {
            "ROUND_TYPE": "sc_over",
            "WINNING_VOTE": winning_vote,
            "NEW_UTILITIES": new_utilities,
            "VOTE_EFFECTS": self.vote_effects,
            "POSITIVE_VOTE_EFFECTS": self.positive_vote_effects_history,
            "NEGATIVE_VOTE_EFFECTS": self.negative_vote_effects_history,
        }

        self.append_save_dict(player_votes, winning_vote)

        for i in range(len(self.connected_clients)):
            self.connected_clients[i].send(json.dumps(message).encode())

        # Note: Removing this time.sleep will brick the program... So, unless you're ready to redo how the server connection works, it stays.
        time.sleep(.5) # Force the fetcher to sleep for a little bit so we know which vote has won. And congrats!

        message = {
            "SWITCH_ROUND": "jhg",
        }
        for i in range(len(self.connected_clients)):
            self.connected_clients[i].send(json.dumps(message).encode())

    def play_jhg_round(self, round):
        client_input = self.get_client_input()
        current_popularity = self.jhg_sim.execute_round(client_input, round-1)

        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()

        # Sends a list containing
        for i in range(self.num_players):
            message = {
                "ROUND_TYPE": "jhg",
                "ROUND": round,
                "RECEIVED": self.get_received(i, allocations_matrix),
                "SENT": self.get_sent(i, allocations_matrix),
                "POPULARITY": list(current_popularity),
            }
            # Only sends the message to connected clients.
            if i >= self.num_bots:
                self.connected_clients[i - self.num_bots].send(json.dumps(message).encode())

        return client_input


    def get_client_input(self):
        client_input = {}
        while True:
            data = self.get_client_data()
            for client, received_json in data.items():
                if "CLIENT_ID" in received_json:
                    client_input[json.loads(received_json)["CLIENT_ID"]] = json.loads(received_json)["ALLOCATIONS"]

            # Check if all clients have provided input
            if len(client_input) == len(self.connected_clients):
                break
            # this isn't the most elegant solution, but it means that we can see all submitted votes. I want us to also be able to see unsubmitted votes.
            else: # we are still playing -- display who is voting for whom.
                message = {
                    "CURRENT_VOTES" : client_input,
                }
                for i in range(len(self.connected_clients)):
                    self.connected_clients[i].send(json.dumps(message).encode())

        return client_input

    def get_received(self, id, allocations_matrix):
        received = [0 for _ in range(self.num_players)]
        for j in range(self.num_players):
            received[j] = allocations_matrix[j][id]

        return received

    def get_sent(self, id, allocations_matrix):
        sent = [0 for _ in range(self.num_players)]
        for j in range(self.num_players):
            sent[j] = allocations_matrix[id][j]

        return sent


    def get_client_data(self):
        ready_to_read, _, _ = select.select(list(self.connected_clients.values()), [], [], 0.1)
        data = {}
        for client in ready_to_read:
            try:
                msg = ''
                while True:  # Accumulate data until the full message is received
                    chunk = client.recv(4096).decode()
                    msg += chunk
                    if len(chunk) < 4096:  # End of the message
                        break
                if msg:
                    data[client] = json.loads(msg)
            except Exception as e:
                pass
        return data

    def append_save_dict(self, all_votes, winning_vote): # just adds the new vote dict to the fetcher.
        all_votes["winning_cause"] = winning_vote
        if self.current_round not in self.save_dict:
            self.save_dict[self.current_round] = all_votes

    def append_stuff_big(self, new_potential_votes, potential_or_final):
        if self.current_round not in self.big_dict:
            self.big_dict[self.current_round] = {} # initialize an empty round
        index = len(self.big_dict[self.current_round])+1
        self.big_dict[self.current_round][index] = {} # new index, slap the potential or final in there.
        self.big_dict[self.current_round][index][potential_or_final] = new_potential_votes.copy() # it is imperative that this be a copy. IDK why.

    def save_stuff_big(self):
        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, "sc_sim_jsons", "low_level_jsons")
        low_level_path = "sc_sim_low_level.json"
        # if not os.path.exists(folder_path): # folder should already be guaranteed to exist. don't worry about it.
        #     os.makedirs(folder_path)

        file_path_2 = os.path.join(folder_path, low_level_path)
        unique_file_path_2 = self.get_unique_filename(file_path_2)

        with open(unique_file_path_2, "w") as f:
            json.dump(self.big_dict, f, indent=4)


    def save_stuff_small(self):
        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, "sc_sim_jsons")
        top_level_path = "sc_top_level_json"

        file_path_1 = os.path.join(folder_path, top_level_path)
        unique_file_path_1 = self.get_unique_filename(file_path_1)

        with open(unique_file_path_1, "w") as f:
            json.dump(self.save_dict, f, indent=4)


    def get_unique_filename(self, file_path):
        if not os.path.exists(file_path):
            return file_path
        else:
            base, extension = os.path.splitext(file_path)
            counter = 1
            while os.path.exists(f"{base}_{counter}{extension}"):
                counter += 1
            return f"{base}_{counter}{extension}"

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