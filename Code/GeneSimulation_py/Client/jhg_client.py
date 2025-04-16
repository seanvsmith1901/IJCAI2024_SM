import sys
import os
import traceback

from PyQt6.QtGui import QPainter

sys.path.append(os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication

from ClientConnectionManager import ClientConnectionManager
# from combinedLayout.MainWindow import MainWindow
from combinedLayout.redesign import MainWindow

from PyQt6.QtCore import qInstallMessageHandler, QtMsgType

# Trying to track down where the QPainter error is coming from
def qt_message_handler(mode, context, message):
    if 'QBackingStore::endPaint() called with active painter' in message:
        print("⚠️ QBackingStore paint error detected!")
        print("📍 Python stack at the time:")
        traceback.print_stack()


_real_begin = QPainter.begin

def debug_begin(self, *args, **kwargs):
    print("🎨 QPainter.begin called with:", args[0] if args else "Unknown")
    traceback.print_stack()
    return _real_begin(self, *args, **kwargs)

QPainter.begin = debug_begin


def load_stylesheet(path):
    with open(path, "r") as file:
        return file.read()


if __name__ == "__main__":
    qInstallMessageHandler(qt_message_handler)
    # Create a QApplication first
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("combinedLayout/style.qss"))

    host = '127.0.0.1'  # your local host address
    port = 12345  # The port number to connect to

    connection_manager = ClientConnectionManager(host, port)

    # Send data to the server to initialize the connection
    message = {"NEW_INPUT": "new_input"}
    connection_manager.send_message(message)
    connection_manager.initialize_connection()

    # Get the values from the server needed to initialize the client
    init_vals = connection_manager.get_message()[0]
    client_id = init_vals["CLIENT_ID"]
    num_players = init_vals["NUM_PLAYERS"]

    # Now, create and show the main window
    window = MainWindow(connection_manager, num_players, client_id)
    window.show()

    # Start the event loop
    app.exec()