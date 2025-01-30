import select
import json
from sim_interface import Simulator

total_players = 11

class ReceivedData():
    def __init__(self, client_id, allocations):
        self.client_id = client_id
        self.allocations = allocations


class GameServer():
    def __init__(self, new_clients, client_id_dict, client_usernames, max_rounds, num_bots, num_humans):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.current_round = 0
        self.simulator = Simulator(len(new_clients), total_players) # creates a new simulator object
        self.start_game(max_rounds, num_bots, num_humans)

        
        

    def start_game(self, max_rounds, num_bots, num_humans):
        round = 1
        global total_players
        # OK SO
        # just take in the client votes, tabluate them, print out all the votes server side.
        # while not all players have answered, we are going to look for the input
        # lets refer to this as a "round" for now

        while round <= max_rounds:
            self.play_round(round, num_bots, num_humans)
            print(f"Played round {round}")
            round += 1

        print("game over")


    def play_round(self, round, num_bots, num_humans):
        client_input = {}
        while True:
            #self.send_state()  # sends out the current game state # there is no current game state atm
            data = self.get_client_data()
            for client, received_json in data.items():
                if "CLIENT_ID" in received_json:
                    client_input[json.loads(received_json)["CLIENT_ID"]] = json.loads(received_json)["ALLOCATIONS"]

            # Check if all clients have provided input
            if len(client_input) == len(self.connected_clients):
                break

        print(client_input)
        print(round)
        current_popularity = self.simulator.execute_round(client_input, round-1)
        # print("current_popularity is as follows: ", current_popularity)


        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = [client_input[str(i + num_bots)] for i in range(num_humans)]

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
            if i < len(self.connected_clients):
                print(json.dumps(message).encode())
                self.connected_clients[i].send(json.dumps(message).encode())

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

