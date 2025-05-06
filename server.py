import socket
from threading import Thread, Lock
from messageHistory import log_message, get_history

class Server:
    Clients = []
    ClientsLock = Lock()

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print("Server waiting for connection...")

    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from:" + str(address))

            client_name = client_socket.recv(1024).decode()
            client = {'client_name': client_name, 'client_socket': client_socket}

            self.broadcast_message("Server", f"*** {client_name} has joined the chat! ***")

            with Server.ClientsLock:
                Server.Clients.append(client)

            Thread(target=self.handle_new_client, args=(client,)).start()

    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']

        while True:
            try:
                raw = client_socket.recv(1024).decode().strip()
            except (ConnectionResetError, ConnectionAbortedError):
                self.disconnect_client(client)
                break

            if not raw:
                self.disconnect_client(client)
                break

            if raw.lower() == "/history":
                self.send_history_to_client(client)
            else:
                log_message(client_name, raw)
                self.broadcast_message(client_name, raw)

    def send_history_to_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        history = get_history(client_name)

        if not history:
            client_socket.send("No history found.\n".encode())
        else:
            client_socket.send("Your message history:\n".encode())
            for msg in history:
                client_socket.send((msg + "\n").encode())

    def disconnect_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        self.broadcast_message("Server", f"*** {client_name} has left the chat. ***")

        with Server.ClientsLock:
            if client in Server.Clients:
                Server.Clients.remove(client)
        client_socket.close()

    def broadcast_message(self, sender_name, message):
        dead_clients = []
        with Server.ClientsLock:
            for client in list(Server.Clients):
                try:
                    client['client_socket'].send(f"[{sender_name}] {message}".encode())
                except:
                    dead_clients.append(client)

            for dc in dead_clients:
                Server.Clients.remove(dc)

if __name__ == "__main__":
    server = Server('127.0.0.1', 5155) 
    server.listen()
