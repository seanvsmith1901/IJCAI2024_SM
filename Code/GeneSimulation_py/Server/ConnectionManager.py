from functools import singledispatchmethod
import socket


class ConnectionManager():
    def __init__(self, host, port):
        self.clients = {}
        self.client_ids = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(12)  # Allow only one connection


    def add_clients(self, num_clients):
        next_id = 0

        # Accept new connections and add them to the connection manager until the specified number of connections have been made
        while len(self.clients) < num_clients:
            client_socket, client_address = self.server_socket.accept()
            self.clients[next_id] = client_socket
            self.client_ids[client_socket] = next_id
            next_id += 1

            data = client_socket.recv(4096)

        print(self.client_ids.values())


    @singledispatchmethod
    def send_message(self, clientInfo, message):
        raise NotImplementedError(f"the clientInfo is of type {type(clientInfo)}. It must be an integer corresponding "
                                  f"with their id or a client_socket object")

    @send_message.register
    def _(self, client_id: int, message: str):
        client_socket = self.clients[client_id]

    def send_setup(self, client, id, num_players, num_causes, max_rounds):
        response = {
            "ID": id,
            "NUM_PLAYERS": num_players,
            "NUM_CAUSES": num_causes,
            "MAX_ROUNDS": max_rounds,
        }