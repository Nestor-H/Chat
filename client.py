import socket
from threading import Thread
import os
import sys

class UserEntry:
    id_seed = 1

    def __init__(self, email, name, password):
        self.id = UserEntry.id_seed
        UserEntry.id_seed += 1
        self.email = email
        self.name = name
        self.password = password

    def to_line(self):
        return f"{self.email},{self.name},{self.password}\n"

    @staticmethod
    def from_line(line):
        parts = line.strip().split(",")
        if len(parts) == 3:
            return UserEntry(parts[0], parts[1], parts[2])
        return None

class Client:

    def __init__(self, HOST, PORT):
        self.socket = socket.socket() # create a TCP socket
        self.socket.connect((HOST, PORT)) # attempt to connect to server
        #self.name = input("Enter your name: ") # ask user for their name

        #self.talk_to_server() # can now talk to server
        
        self.users = self.load_users()
        self.name = None

        self.start_login_or_register()

    def load_users(self):
        users = []
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                for line in f:
                    user = UserEntry.from_line(line)
                    if user:
                        users.append(user)
        return users

    def save_user(self, user):
        with open("users.txt", "a") as f:
            f.write(user.to_line())

    def start_login_or_register(self):
        print("Welcome! Choose an option:")
        print("1. Register")
        print("2. Login")
        choice = input("Enter 1 or 2: ")

        if choice == "1":
            self.register()
        elif choice == "2":
            self.login()
        else:
            print("Invalid choice, exiting.")
            sys.exit(0)

    def register(self):
        email = input("Enter email: ").strip()
        name = input("Enter name: ").strip()
        password = input("Enter password: ").strip()

        if not email or not name or not password:
            print("All fields are required. Registration failed.")
            sys.exit(0)

        # Check if user already exists
        existing = next((u for u in self.users if u.email == email), None)
        if existing:
            print("User already exists. Try logging in.")
            sys.exit(0)

        new_user = UserEntry(email, name, password)
        self.users.append(new_user)
        self.name = name

        with open("users.txt", "a") as f:
            f.write(new_user.to_line())

        print("Registration successful. You are now logged in as", self.name)
        self.talk_to_server()

    def login(self):
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()

        if not email or not password:
            print("All fields are required. Login failed.")
            sys.exit(0)

        existing = next((u for u in self.users if u.email == email), None)
        if not existing:
            print("User not found. Please register first.")
            sys.exit(0)

        if existing.password != password:
            print("Email and Password do not match. Login failed.")
            sys.exit(0)

        self.name = existing.name
        print("Login successful. You are now logged in as", self.name)
        self.talk_to_server()
    
    def talk_to_server(self):
        self.socket.send(self.name.encode()) # send name to server

        # different threads for sending and receiving messages
        Thread(target=self.receive_message).start() # start a new thread to listen to messages from server
        self.send_message() # send messages to server from main thread

    def send_message(self):
        while True:
            client_input = input("") # keep asking for input
            client_message = self.name + ": " + client_input # append client's name to the message
            self.socket.send(client_message.encode()) # send message to socket

    
    def receive_message(self):
        while True:
            server_message = self.socket.recv(1024).decode() # constantly listening for messages from server
            if not server_message.strip(): # exit if server message is empty
                os._exit(0)

            print("\033[1;31;40m" + server_message + "\033[0m")  # print message in red

if __name__ == "__main__":
    Client('127.0.0.1', 5155)
