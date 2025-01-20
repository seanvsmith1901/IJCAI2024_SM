import sys
import socket
import json
from time import sleep

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextLine
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from MainWindow import MainWindow

def start_client():
    # host = '192.168.30.17'  # The server's IP address
    host = '127.0.0.1'  # your local host address cause you're working from home.
    port = 12345  # The port number to connect to
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))

    # Send data to the server to initialize the connection
    message = {"NEW_INPUT": "new_input"}
    client_socket.send(json.dumps(message).encode())

    # If you delete this sleep statement, the second message is sent too quickly and overwhelms the server
    # sleep(.0001)
    # message = {"VOTE": "1"}
    # client_socket.send(json.dumps(message).encode())
    #
    # while True:
    #     data = client_socket.recv(1024)
    #     if data:
    #         # This just has to be wrong. Got to be a better way... But I can't find it.
    #         json_data = json.dumps(json.loads(data.decode()))
    #         if "RESULT" in json_data:
    #             vote_matrix = (json.loads(json_data))["RESULTS"]
    #             print("hi")

    # Runs the gui -- commented out while we work on stuff (need to figure out how to run the above on a slot
    app = QApplication(sys.argv)
    window = MainWindow(client_socket)
    window.show()
    app.exec()

start_client()


