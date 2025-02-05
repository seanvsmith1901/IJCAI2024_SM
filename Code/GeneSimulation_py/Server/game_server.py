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
    def __init__(self, new_clients, client_id_dict, client_usernames, max_rounds, num_bots, num_humans):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.current_round = 0
        self.num_causes = 3
        self.jhg_sim = JHG_simulator(len(new_clients), total_players) # creates a new JHG simulator object
        self.sc_sim = Social_Choice_Sim(total_players, self.num_causes)

        self.start_game(max_rounds, num_bots, num_humans)

        
        

    def start_game(self, max_rounds, num_bots, num_humans):
        round = 1
        global total_players
        # OK SO
        # just take in the client votes, table them, print out all the votes server side.
        # while not all players have answered, we are going to look for the input
        # lets refer to this as a "round" for now

        while round <= max_rounds:
            for i in range(3):
                self.play_round(round, num_bots, num_humans)
                print(f"Played round {round}")
                round += 1
            self.social_choice_round()

        print("game over")

    def social_choice_round(self):
        current_options_matrix = self.sc_sim.create_options_matrix()
        player_nodes = self.sc_sim.create_player_nodes()
        causes = self.sc_sim.get_causes()
        all_nodes = causes + player_nodes
        message = {
            "OPTIONS" : current_options_matrix,
            "NODES" : [node.to_json() for node in all_nodes],
        }
        for client in self.connected_clients:
            client.send(json.dumps(message))

        votes = {}
        self.get_bot_votes(current_options_matrix)


    def get_bot_votes(self, current_options_matrix):
        self.jhg_sim.get_bot_votes(current_options_matrix)





    def get_client_input(self):
        client_input = {}
        while True:
            # self.send_state()  # sends out the current game state # there is no current game state atm
            data = self.get_client_data()
            for client, received_json in data.items():
                if "CLIENT_ID" in received_json:
                    client_input[json.loads(received_json)["CLIENT_ID"]] = json.loads(received_json)["ALLOCATIONS"]

            # Check if all clients have provided input
            if len(client_input) == len(self.connected_clients):
                break
        return client_input


    def play_round(self, round, num_bots, num_humans):
        client_input = self.get_client_input()

        print(client_input)
        print(round)
        current_popularity = self.jhg_sim.execute_round(client_input, round-1)
        # print("current_popularity is as follows: ", current_popularity)


        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = self.jhg_sim.get_T()
        print(allocations_matrix)

        # This is temporary to expand the allocations matrix for 11 players. Eventually, all slots will be used and this will be deleted
        for i in range(11 - len(allocations_matrix)):
            allocations_matrix.append([0 for i in range(11)])

        # For now, this code doesn't work because we are not filling out the full 11 players. Below code accounts for this error
        # for i in range(len(self.connected_clients) - 1):
        #     received = [0 for i in range(len(self.connected_clients))]
        #     for j in range(len(self.connected_clients) - 1):
        #         received[j] = allocations_matrix[j][i]
        #
        #
        #     message = {
        #         "RESULT": 1,
        #         "RECEIVED": received,
        #     }
        #     self.connected_clients[i].send(json.dumps(message).encode())

        # Sends a list containing
        print(current_popularity)
        for i in range(11):
            message = {
                "ROUND": round,
                "RECEIVED": self.get_received(i, allocations_matrix),
                "SENT": self.get_sent(i, allocations_matrix),
                "POPULARITY": list(current_popularity),
            }
            # Only sends the message to connected clients.
            if i >= num_bots:
                print(json.dumps(message))
                self.connected_clients[i - num_bots].send(json.dumps(message).encode())

        return client_input

    def get_received(self, id, allocations_matrix):
        received = [0 for i in range(11)]
        for j in range(11):
            received[j] = allocations_matrix[j][id]

        return received

    def get_sent(self, id, allocations_matrix):
        sent = [0 for i in range(11)]
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
                    chunk = client.recv(1024).decode()
                    msg += chunk
                    if len(chunk) < 1024:  # End of message
                        break
                if msg:
                    data[client] = json.loads(msg)
            except Exception as e:
                pass
        return data

