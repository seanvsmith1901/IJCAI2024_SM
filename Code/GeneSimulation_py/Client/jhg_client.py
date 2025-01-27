import json
import sys
import socket

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication

from PyqtComponents.MainWindow import MainWindow
from RoundState import RoundState
from PyqtComponents.BodyLayout import BodyLayout

if __name__ == "__main__":
    # host = '192.168.30.17'  # The server's IP address
    host = '127.0.0.1'  # your local host address cause you're working from home.
    port = 12346  # The port number to connect to
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