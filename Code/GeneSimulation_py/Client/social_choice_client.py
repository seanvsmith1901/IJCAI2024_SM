import sys
import socket
import json

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

    app = QApplication(sys.argv)
    window = MainWindow(client_socket)
    window.show()
    app.exec()

start_client()


