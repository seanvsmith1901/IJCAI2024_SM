import json
import sys
import socket

from PyQt6.QtWidgets import QApplication
# from PyqtComponents.MainWindow import MainWindow
from combinedLayout.MainWindow import MainWindow

if __name__ == "__main__":
    # Create a QApplication first
    app = QApplication(sys.argv)

    host = '127.0.0.1'  # your local host address
    port = 12347  # The port number to connect to
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
            json_data = json.loads(data.decode())
            if "ID" in json_data:
                num_players = json_data["NUM_PLAYERS"]
                num_causes = json_data["NUM_CAUSES"]
                max_rounds = json_data["MAX_ROUNDS"]
                id = json_data["ID"]
                break

    message = {"INIT": "init"}
    client_socket.send(json.dumps(message).encode())

    # Now, create and show the main window
    window = MainWindow(client_socket, num_players, num_causes, id, max_rounds)
    window.show()

    # Start the event loop
    app.exec()