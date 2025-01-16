import select
from multiprocessing import Process
import multiprocessing
import json
import time

class GameServer():
    def __init__(self, new_clients, client_id_dict, client_usernames):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.start_game()


    def start_game(self):
        # OK SO
        # just take in teh client votes, tabluate them, print out all teh votes server side.
        # while not all players have answered, we are going to look for the input
        # lets refer to this as a "round" for now
        print("this is the current tabulation ", self.play_round())


    def play_round(self):
        client_input = {}
        while True:
            #self.send_state()  # sends out the current game state # there is no current game state atm
            data = self.get_client_data()
            for client, received_json in data.items():
                if "VOTE" in received_json and received_json["VOTE"] != None:
                    client_input[self.client_id_dict[client]] = received_json["VOTE"]

            # Check if all clients have provided input
            if len(client_input) == len(self.connected_clients):
                break
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

