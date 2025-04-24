import json
from collections import deque

try:
    from GeneSimulation_py.ConnectionManager import ConnectionManager
except ModuleNotFoundError:
    from Code.GeneSimulation_py.ConnectionManager import ConnectionManager


class ClientConnectionManager(ConnectionManager):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.socket.connect((host, port))

        self.message_type_names = {
            "SUBMIT_JHG": ["CLIENT_ID", "ROUND_NUMBER", "ALLOCATIONS"],
            "SUBMIT_SC": ["CLIENT_ID", "FINAL_VOTE"],
        }


    def initialize_connection(self):
        message = {"NEW_INPUT": "new_input"}
        self.socket.send(json.dumps(message).encode())


    def get_message(self):
        # Extracts each JSON object from a string, to handle the case of multiple methods having been sent.
        def extract_json_objects(response_string):
            decoder = json.JSONDecoder()
            idx = 0
            objects = deque()

            # Loop through the
            while idx < len(response_string):
                try:
                    obj, end_idx = decoder.raw_decode(response_string, idx)
                    objects.append(obj)
                    idx = end_idx
                except json.JSONDecodeError:
                    # If we hit a problem, skip a character and try again
                    idx += 1

            return objects


        while True:
            try:
                # data = self.socket.recv(4096)
                data = ''
                while True:  # Accumulate data until the full message is received
                    chunk = self.socket.recv(4096).decode()
                    data += chunk
                    if len(chunk) < 4096:  # End of the message
                        break
                if data:
                    responses = extract_json_objects(data)

                    return responses

            except (ConnectionError, TimeoutError, OSError) as e:
                print(f"Socket error: {e}")
                continue
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                continue

