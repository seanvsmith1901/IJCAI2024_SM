import json
import socket
import queue
import time

def start_client():
    global client_socket
    host = '127.0.0.1'  # Localhost
    port = 12345  # The port number to connect to
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))
    # Send initial data to the server
    message = {
        "MESSAGE": "Hello from the client!"
    }
    client_socket.send(json.dumps(message).encode())
    q = queue.Queue()
    receive_data(q)

def receive_data(q):
    global client_socket
    while True:
        try:
            data = client_socket.recv(4096)  # Buffer size of 1024 bytes
            if not data:
                break
            message = json.loads(data.decode())
            q.put(message)  # Send the message to the queue
        except Exception as e:
            print("Error receiving data:", e)
            break
        time.sleep(2)


if __name__ == '__main__':
    start_client()