# this fetcher just holds connections and instantiates game servers when we have enough people, think 12. do NOT hold all connections, delete them after passign them down to gameServer

import json
import socket
import copy
import game_server




HUMAN_PLAYERS = 12 # how many human players (clients) we are expecting (This should be 12 for the full study)



connected_clients = {}
client_input = {}
client_usernames = {}
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
client_id_dict = {}
hunters = []
MAX_ROUNDS = 2
round = 1


def start_server(host='127.0.0.1', port=12345):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(12)  # Allow only one connection

    while True: # just keeps running and listening for clients, capable of running multiple servers.
        client_socket, client_address = server_socket.accept()
        connected_clients[len(connected_clients)] = client_socket
        client_id_dict[client_socket] = len(connected_clients)
        data = client_socket.recv(1024)

        try:
            # Deserialize the JSON data
            received_json = json.loads(data.decode())
            #client_usernames[len(connected_clients)] = received_json["USERNAME"] #use this later if ever. might not be relavant
            #client_input[client_socket] = received_json["INPUT"]


            # Create a response
            response = {
                "message": "Hello from the server!",
            }
            # Serialize and send the response as JSON
            client_socket.send(json.dumps(response).encode())
        except json.JSONDecodeError:
            pass # don't do anything but still handle the exception

        if len(connected_clients) == HUMAN_PLAYERS: # when we have all the players that we are expecting
            pass
            # starts a smaller server.

            # passes down the new player list, calls that object (so we should now be cooking) and then clears out the stuff. Do I need to make threads?



if __name__ == "__main__":
    start_server()
