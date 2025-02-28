import json
import sys
import socket

from PyQt6.QtWidgets import QApplication

from PyqtComponents.MainWindow import MainWindow

if __name__ == "__main__":
    host = '127.0.0.1'  # your local host address cause you're working from home.
    port = 12345 # The port number to connect to
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))

    # Send data to the server to initialize the connection
    message = {"NEW_INPUT": "new_input"}
    client_socket.send(json.dumps(message).encode())

    while True:
        data = client_socket.recv(4096)
        if data:
            json_data = json.dumps(json.loads(data.decode()))
            if "ID" in json_data:
                num_players = json.loads(json_data)["NUM_PLAYERS"]
                num_causes = json.loads(json_data)["NUM_CAUSES"]
                id = json.loads(json_data)["ID"]

                break

    message = {"INIT": "init"}
    client_socket.send(json.dumps(message).encode())

    app = QApplication(sys.argv)
    # This is the entrance to the gui
    window = MainWindow(client_socket, num_players, num_causes, id)
    window.show()
    app.exec()