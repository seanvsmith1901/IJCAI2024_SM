import os.path
import time
from collections import Counter

import select
import json
from sim_interface import JHG_simulator
from social_choice_sim import Social_Choice_Sim


class ReceivedData:
    def __init__(self, client_id, allocations):
        self.client_id = client_id
        self.allocations = allocations


class GameServer:
    def __init__(self, new_clients, client_id_dict, client_usernames, max_rounds, num_bots, num_causes, num_players):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.current_round = 0
        self.num_causes = num_causes
        self.jhg_sim = JHG_simulator(len(new_clients), total_players) # creates a new JHG simulator object
        self.sc_sim = Social_Choice_Sim(total_players, self.num_causes)
        self.num_bots = num_bots
        self.save_dict = {}
        self.big_dict = {}
        self.start_game(max_rounds)


    def start_game(self, max_rounds):
        round = 1

        while self.current_round <= max_rounds:
            # This range says how many jhg rounds to play between sc rounds
            for i in range(1):
                self.play_jhg_round(round)
                print(f"Played round {round}")
                round += 1
            self.play_social_choice_round()

        self.save_stuff_small()
        self.save_stuff_big()
        print("game over")

    def play_social_choice_round(self):
        self.sc_sim.start_round()
        new_influence = self.jhg_sim.get_influence().tolist()
        new_relations = self.sc_sim.calculate_relation_strength(new_influence)
        current_options_matrix = self.sc_sim.get_current_options_matrix()
        player_nodes = self.sc_sim.get_player_nodes()
        causes = self.sc_sim.get_causes()
        all_nodes = causes + player_nodes
        message = {
            "ROUND_TYPE" : "sc_init",
            "OPTIONS" : current_options_matrix,
            "NODES" : [node.to_json() for node in all_nodes],
            "UTILITIES" : current_options_matrix,
            #"RELATION_STRENGTH" : new_relations,
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
                        print("NEW FINAL VOTE RECEIVED")
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

        if not (winning_vote_count > total_votes // 2):
            winning_vote = -1

        self.sc_sim.apply_vote(winning_vote)  # once again needs to be done from gameserver, as that is where winning vote is consolidated.
        # aight now you have the winning vote, so what you need to do is export
        # 1. the winning vote, 2. the new utility of each player, and yeah that's pretty much it
        message = {
            "WINNING_VOTE" : winning_vote,
            "NEW_UTILITY" : self.sc_sim.get_player_utility(),
            "ROUND_TYPE" : "sc_over",
        }

        self.append_save_dict(player_votes, winning_vote)

        for i in range(len(self.connected_clients)):
            self.connected_clients[i].send(json.dumps(message).encode())
        time.sleep(2) # force the fetcher to sleep for a little bit so we know which vote has won.
        # and congrats! that should be something of like how we would like to see it. will probably need some polish but
        # that's the "basic" framework that we can expand upon.

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
            else: # we are still playing -- display who is voting for who.
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
                    if len(chunk) < 4096:  # End of message
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
            self.big_dict[self.current_round] = {} # initalize an empty round
        index = len(self.big_dict[self.current_round])+1
        self.big_dict[self.current_round][index] = {} # new index, slap the potnetial or final in there.
        self.big_dict[self.current_round][index][potential_or_final] = new_potential_votes.copy() # it is imperitave that this be a copy. IDK why.

    def save_stuff_big(self):
        desktop_path = os.path.expanduser("~/Desktop")
        folder_path = os.path.join(desktop_path, "sc_sim_jsons", "low_level_jsons")
        low_level_path = "sc_sim_low_level.json"
        # if not os.path.exists(folder_path): # folder should already be guranteed to exist. don't worry about it.
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
