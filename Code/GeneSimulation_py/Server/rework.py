import json
import socket
from time import sleep

from ConnectionManager import ConnectionManager
from game_server import GameServer

# Set to 1 for testing purposes
HUMAN_PLAYERS = 2 # how many players need to join before things start to blow up?
TOTAL_PLAYERS = 5
BOT_PLAYERS = TOTAL_PLAYERS - HUMAN_PLAYERS
NUM_CAUSES = 3
JHG_ROUNDS_PER_SC_ROUND = 1

connected_clients = {}
client_input = {}
client_usernames = {}
client_id_dict = {}
# Set very high for testing purposes
MAX_ROUNDS = 4
round = 1

# See options_creation.py -> group_size_options to understand what this means
SC_GROUP_SIZE = 2

OPTIONS = {
    "HUMAN_PLAYERS": 2,
    "TOTAL_PLAYERS": 5,
}

OPTIONS["BOT_PLAYERS"] = OPTIONS["HUMAN_PLAYERS"] - OPTIONS["TOTAL_PLAYERS"]


# TODO: Check if these are actually needed. I'm not sure what they do...
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
hunters = []


def start_server(host='127.0.0.1', port=12347):
    connectionManager = ConnectionManager(host, port)

    print("Server started")

    connectionManager.add_clients(HUMAN_PLAYERS)
    # while True: # just keeps running and listening for clients, capable of running multiple servers.
    #     client_socket, client_address = connectionManager.server_socket.accept()
    #     connected_clients[len(connected_clients)] = client_socket
    #     client_id_dict[client_socket] = len(connected_clients)
    #     data = client_socket.recv(4096)
    #
    #     if data:
    #         json_data = json.dumps(json.loads(data.decode()))
    #         if "NEW_CLIENT" in json_data:
    #             response = {
    #                 "ID": (str((len(connected_clients) - 1) + BOT_PLAYERS)),
    #                 "NUM_PLAYERS": TOTAL_PLAYERS,
    #                 "NUM_CAUSES": NUM_CAUSES,
    #                 "MAX_ROUNDS": MAX_ROUNDS,
    #             }
    #             # Serialize and send the response as JSON
    #             client_socket.send(json.dumps(response).encode())
    #             sleep(.1)



if __name__ == "__main__":
    start_server()