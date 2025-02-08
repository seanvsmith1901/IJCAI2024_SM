from collections import Counter

import select
import json
from sim_interface import JHG_simulator
from social_choice_sim import Social_Choice_Sim

total_players = 11

class ReceivedData:
    def __init__(self, client_id, allocations):
        self.client_id = client_id
        self.allocations = allocations


class GameServer:
    def __init__(self, new_clients, client_id_dict, client_usernames, max_rounds, num_bots, num_causes):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.current_round = 0
        self.num_causes = num_causes
        self.jhg_sim = JHG_simulator(len(new_clients), total_players) # creates a new JHG simulator object
        self.sc_sim = Social_Choice_Sim(total_players, self.num_causes)
        self.num_bots = num_bots

        self.start_game(max_rounds)


    def start_game(self, max_rounds):
        round = 1
        global total_players

        while round <= max_rounds:
            for i in range(1):
                next_round_type = "jhg"
                if i == 2:
                    next_round_type = "sc"
                self.play_jhg_round(round, next_round_type)
                print(f"Played round {round}")
                round += 1
            self.play_social_choice_round()


        print("game over")

    def play_social_choice_round(self):
        # before we play the round, lets get the info out to all the players.
        # influence_matrix = self.jhg_sim.get_influence()
        # return_values = self.sc_sim.calculate_relation_strength(influence_matrix)
        #
        # message = {
        #     "RELATIONS" : return_values,
        # }
        #
        # for i in range(len(self.connected_clients)):
        #     self.connected_clients[i].send(json.dumps(message).encode())


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

        # might need to rethink the way that we are taking input in from the client.
        # because right now they are making those decisions independently, which means that the bots will never be able to lie.
        # very, very odd. Maybe scramble it somehow?
        # anyway just try to iron this out for now and come back to this very interesting problem later.


        # player_votes = self.get_client_input() # OK how can I make the bots see what the players are voting for and use that appropriately?
        player_votes = {}
        # Keeps listening for client votes until all players have voted
        # TODO: send the displayed vote to the bots so they can interact with the system.
        while len(player_votes) < len(self.connected_clients):
            data = self.get_client_data()
            for client, received_json in data.items():
                if "FINAL_VOTE" in received_json:
                    print("Final vote received")
                    print(type(received_json["FINAL_VOTE"]))
                    player_votes[received_json["CLIENT_ID"]] = received_json["FINAL_VOTE"]


        bot_votes = self.jhg_sim.get_bot_votes(current_options_matrix)

        all_votes = bot_votes | player_votes
        winning_vote = Counter(all_votes.values()).most_common(1)[0][0]
        self.sc_sim.apply_vote(winning_vote)  # once again needs to be done from gameserver, as that is where winning vote is consolidated.
        # aight now you have the winning vote, so what you need to do is export
        # 1. the winning vote, 2. the new utility of each player, and yeah that's pretty much it
        message = {
            "WINNING_VOTE" : winning_vote,
            "NEW_UTILITY" : self.sc_sim.get_player_utility()
        }
        for i in range(len(self.connected_clients)):
            self.connected_clients[i].send(json.dumps(message).encode())
        # and congrats! that should be something of like how we would like to see it. will probably need some polish but
        # that's the "basic" framework that we can expand upon.

    def play_jhg_round(self, round, next_round_type):
        client_input = self.get_client_input()
        current_popularity = self.jhg_sim.execute_round(client_input, round-1)

        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()

        # Sends a list containing
        for i in range(11):
            message = {
                "ROUND_TYPE": "jhg",
                "ROUND": round,
                "RECEIVED": self.get_received(i, allocations_matrix),
                "SENT": self.get_sent(i, allocations_matrix),
                "POPULARITY": list(current_popularity),
                "NEXT_ROUND_TYPE": next_round_type,
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
        return client_input

    def get_received(self, id, allocations_matrix):
        received = [0 for _ in range(11)]
        for j in range(11):
            received[j] = allocations_matrix[j][id]

        return received

    def get_sent(self, id, allocations_matrix):
        sent = [0 for _ in range(11)]
        for j in range(11):
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

