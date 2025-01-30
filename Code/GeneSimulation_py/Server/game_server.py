import select
from multiprocessing import Process
import multiprocessing
import json

class ReceivedData():
    def __init__(self, client_id, allocations):
        self.client_id = client_id
        self.allocations = allocations


class GameServer():
    def __init__(self, new_clients, client_id_dict, client_usernames, max_rounds):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.start_game(max_rounds)



    def start_game(self, max_rounds):
        round = 1

        while round <= max_rounds:
            self.play_round(round)
            round += 1

        print("game over")


    def play_round(self, round):
        client_input = {}
        while True:
            #self.send_state()  # sends out the current game state # there is no current game state atm
            data = self.get_client_data()
            for client, received_json in data.items():
                if "CLIENT_ID" in received_json:
                    client_input[json.loads(received_json)["CLIENT_ID"]] \
                        = ReceivedData(json.loads(received_json)["CLIENT_ID"], json.loads(received_json)["ALLOCATIONS"])

            # Check if all clients have provided input
            if len(client_input) == len(self.connected_clients):
                break


        # Creates a 2d array where each row corresponds to the allocation list of the player with the associated id
        allocations_matrix = [client_input[str(i)].allocations for i in range(len(self.connected_clients))]

        # This is temporary to expand the allocations matrix for 11 players. Eventually, all slots will be used and this will be deleted
        for i in range(11 - len(allocations_matrix)):
            allocations_matrix.append([0 for i in range(11)])
        print(allocations_matrix)

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
        for i in range(11):
            message = {
                "ROUND": round,
                "RECEIVED": self.get_received(i, allocations_matrix),
                "SENT": self.get_sent(i, allocations_matrix),
            }

            # Only sends the message to connected clients.
            if i < len(self.connected_clients):
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

