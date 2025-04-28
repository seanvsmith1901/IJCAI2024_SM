import sys
import os

sys.path.append(os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication

from ClientConnectionManager import ClientConnectionManager
from combinedLayout.MainWindow import MainWindow


def load_stylesheet(path):
    with open(path, "r") as file:
        return file.read()


if __name__ == "__main__":
    # Create a QApplication first
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("combinedLayout/style.qss"))

    host = '10.55.10.49'  # your local host address
    port = 12346  # The port number to connect to

    connection_manager = ClientConnectionManager(host, port)

    # Send data to the server to initialize the connection
    message = {"NEW_INPUT": "new_input"}
    connection_manager.send_message(message)
    connection_manager.initialize_connection()

    # Get the values from the server needed to initialize the client
    init_vals = connection_manager.get_message()[0]
    client_id = init_vals["CLIENT_ID"]
    num_players = init_vals["NUM_PLAYERS"]
    num_cycles = init_vals["NUM_CYCLES"]

    # Now, create and show the main window
    window = MainWindow(connection_manager, num_players, client_id, num_cycles)
    window.show()

    # Start the event loop
    app.exec()