from engine import JHGEngine
import json
import socket
import copy
import select
connected_clients = {}
client_input = {}
client_usernames = {}
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
client_id_dict = {}
hunters = []
MAX_ROUNDS = 2
round = 1
HUMAN_PLAYERS = 2 # start with 2 - I might need to make this dynamic somehow. I'll worry about that later.


# from what I was able to gather, I need to make this a proxy object - so we have the server and whatnot getting routed through here.

class GameSimulator:

    def __init__(self, game_params) -> None:
        # all of the client information that we are going to need
        self.client_usernames = None
        self.client_id_dict = None
        self.connected_clients = None
        self.engine = JHGEngine(**game_params)
        self.extra_data = {
            i: {
                j: None for j in range(self.engine.N)
            } for i in range(self.engine.N)
        }
        self.start_server()

    def get_influence(self):
        return self.engine.get_influence()

    def get_prev_influence(self):
        return self.engine.get_prev_influence()

    def get_popularity(self):
        return self.engine.get_popularity()

    def get_transaction(self):
        return self.engine.get_transaction()

    def get_extra_data(self, player_id):
        return self.extra_data[player_id]

    def set_extra_data(self, sender_id, reciever_id, data):
        self.extra_data[reciever_id][sender_id] = data

    def play_round(self, T):
        self.engine.apply_transaction(T)

    def save(self, outFilePath):
        with open(outFilePath, "w") as f:
            param_col_str = f"round,alpha,beta,give,keep,steal"
            pops_col_str = ",".join(f'p{i}' for i in range(len(self.engine.get_popularity())))
            act_col_str = ",".join(f'p{i}=>p{j}' for i in range(len(self.engine.get_popularity())) for j in range(len(self.engine.get_popularity())))
            f.write(f"{param_col_str},{pops_col_str},{act_col_str}\n") # column names
            for t in range(self.engine.t+1):
                param_str = f"{t},{self.engine.alpha},{self.engine.beta},{self.engine.C_g},{self.engine.C_k},{self.engine.C_s}"
                pops_str = ",".join(f'{p}' for p in self.engine.get_popularity(t))
                act_str = ",".join(f'{a}' for a in self.engine.get_transaction(t).flatten())
                f.write(f"{param_str},{pops_str},{act_str}\n")

    def get_player_inputs(self, T):
        # the goal of this function is to populate T - what I need to do is make sure that every player has accepted input
        client_input = {}
        while True:
            data = self.get_client_data()
            for client, received_json in data.items():
                if "NEW_INPUT" in received_json and received_json["NEW_INPUT"] != None:
                    client_input[self.client_id_dict[client]] = received_json["NEW_INPUT"]

            # Check if all clients have provided input
            if len(client_input) == len(self.connected_clients):
                break

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

    def start_server(self, host='127.0.0.1', port=12345):
        # create the TCP socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(12)  # Allow only one connection
        while True:
            client_socket, client_address = server_socket.accept()
            connected_clients[len(connected_clients)] = client_socket
            client_id_dict[client_socket] = len(connected_clients)

            data = client_socket.recv(1024)
            try:
                # Deserialize the JSON data
                received_json = json.loads(data.decode())
                client_usernames[len(connected_clients)] = received_json["USERNAME"]

                # We don't even have a client yet, worry about that later.
                # # Create a response
                # response = {
                #     "message": "Hello from the server!",
                #     "HEIGHT": HEIGHT,
                #     "WIDTH": WIDTH,
                #     "CLIENT_ID" : client_id_dict[client_socket],
                # }
                # # Serialize and send the response as JSON
                # client_socket.send(json.dumps(response).encode())
            except json.JSONDecodeError:
                pass # don't do anything but still handle the exception

            if len(connected_clients) == HUMAN_PLAYERS: # when we have all the players that we are expecting
                # passes down the new player list, calls that object (so we should now be cooking) and then clears out the stuff. Do I need to make threads?
                self.connected_clients = copy.copy(connected_clients)
                self.client_id_dict = client_id_dict
                self.client_usernames = client_usernames
                connected_clients.clear()
                client_id_dict.clear()
                client_usernames.clear()
                break # gets us out of the while true loop


