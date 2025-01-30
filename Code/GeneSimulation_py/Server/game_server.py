import select
from multiprocessing import Process
import multiprocessing
import json
import time
from sim_interface import Simulator

total_players = 11

# from Code.GeneSimulation_py.main import play_game


class GameServer():
    global total_players
    def __init__(self, new_clients, client_id_dict, client_usernames):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.current_round = 0
        self.simulator = Simulator(len(new_clients), total_players) # creates a new simulator object
        self.start_game()



    def start_game(self):
        # OK SO
        # just take in the client votes, tabluate them, print out all the votes server side.
        # while not all players have answered, we are going to look for the input
        # lets refer to this as a "round" for now
        print("lets just see if we can get here first, make sure we don't brick")

        while True:
            print("this is the current tabulation ", self.play_round())


    def play_round(self):
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

        print("this shouldn't go off until we have actually started, but it is possible that I will need to assemble a blank matrix to start ")
        current_popularity = self.simulator.execute_round(client_input, self.current_round)
        self.current_round += 1  # its expecing the first round to be 0? I guess?
        print("current_popularity is as follows: ", current_popularity)

        # # Create a matrix to encode votes. Each row is a user (arranged by id), each column is the player they voted for
        # vote_matrix = [[0 for _ in range(len(self.connected_clients))] for _ in range(len(self.connected_clients))]
        # for i in range(len(client_input)):
        #     # Because the client ids are 1 indexed (not 0 indexed), you have to use the +1 to convert to one indexing
        #     # for client_input (expects the client id), and -1 to convert back to zero indexing for vote_matrix
        #     vote_matrix[i][int(client_input[i+1])-1] = 1
        #
        # vote_matrix_json = json.dumps(vote_matrix)

        # Sends a message to each client. This should eventually be moved to its own function that sends the game state
        message = {"RESULT": 1}
        for i in range(len(self.connected_clients)):
            self.connected_clients[i].send(json.dumps(message).encode())

        return client_input


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

