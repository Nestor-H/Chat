import socket
from threading import Thread

class Server:
    Clients = [] # list of connected clients

    # create a TCP socket over IPv4 and accept up to 5 connections
    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT)) # bind socket to localhost and port
        self.socket.listen(5) # accept up to 5 connections
        print("Server waiting for connection...")


    # listen for connections on the main thread and create a new thread for each client connection
    # as well as add them to the list of clients
    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from:" + str(address))

            # will ask client for their name
            client_name = client_socket.recv(1024).decode()
            client = {'client_name': client_name, 'client_socket': client_socket} # client dictionary with name and socket

            # broadcast message that a new client has joined
            self.broadcast_message(client_name, client_name + " has joined the chat!")

            # append to list of clients and create and start a new thread to handle the client
            Server.Clients.append(client)
            Thread(target = self.handle_new_client, args = (client,)).start()


    # handle_new_client method will be run in a new thread for each client
    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']

        while True:
            try:
                raw = client_socket.recv(1024).decode().strip()
            except (ConnectionResetError, ConnectionAbortedError):
                # client died unexpectedly
                self.broadcast_message(client_name, f"{client_name} has left the chat!")
                if client in Server.Clients:
                    Server.Clients.remove(client)
                client_socket.close()
                break

            # Only treat a truly closed socket as “left”
            if not raw:
                self.broadcast_message(client_name, f"{client_name} has left the chat!")
                if client in Server.Clients:
                    Server.Clients.remove(client)
                client_socket.close()
                break

            # Otherwise broadcast exactly what was sent
            self.broadcast_message(client_name, raw)


    # 
    def broadcast_message(self, sender_name, message):
        dead_clients = []
        for client in Server.Clients:
            sock = client['client_socket']
            try:
                sock.send(message.encode())
            except (ConnectionResetError, ConnectionAbortedError):
                # that client is gone—schedule removal
                dead_clients.append(client)

        # remove any dead clients so future broadcasts don’t error
        for dc in dead_clients:
            Server.Clients.remove(dc)

if __name__ == "__main__":
    server = Server('127.0.0.1', 5155)
    server.listen()
