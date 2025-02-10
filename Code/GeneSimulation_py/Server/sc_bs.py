# this fetcher just holds connections and instantiates game servers when we have enough people, think 12. do NOT hold all connections, delete them after passign them down to gameServer

import json
import socket
from game_server import GameServer



# Set to 1 for testing purposes
HUMAN_PLAYERS = 1 # how many players need to join before things start to blow up.
TOTAL_PLAYERS = 11
BOT_PLAYERS = TOTAL_PLAYERS - HUMAN_PLAYERS
NUM_CAUSES = 3

connected_clients = {}
client_input = {}
client_usernames = {}
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
client_id_dict = {}
hunters = []
# Set very high for testing purposes
MAX_ROUNDS = 100
round = 1


def start_server(host='127.0.0.1', port=12346):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(12)  # Allow only one connection

    print("Server started")

    while True: # just keeps running and listening for clients, capable of running multiple servers.
        client_socket, client_address = server_socket.accept()
        connected_clients[len(connected_clients)] = client_socket
        client_id_dict[client_socket] = len(connected_clients)
        data = client_socket.recv(4096)

        try:
            # Create a response
            response = {
                "ID": (str((len(connected_clients) - 1) + BOT_PLAYERS)),
                "NUM_PLAYERS": TOTAL_PLAYERS,
                "NUM_CAUSES": NUM_CAUSES,
            }
            # Serialize and send the response as JSON
            client_socket.send(json.dumps(response).encode())
        except json.JSONDecodeError:
            pass # don't do anything but still handle the exception

        if len(connected_clients) == HUMAN_PLAYERS: # when we have all the players that we are expecting
            GameServer(connected_clients, client_id_dict, client_usernames, MAX_ROUNDS, BOT_PLAYERS, NUM_CAUSES) # might need to make a copy and overwrite connected clients
            # readies for another game maybe possibly. who knows. will prolly never test.
            connected_clients.clear()
            client_id_dict.clear()
            client_usernames.clear()


if __name__ == "__main__":
    start_server()
