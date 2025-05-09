from datetime import datetime
import socket
from threading import Thread
import os
import sys
from messageHistory import show_history, log_message

class UserEntry:
    id_seed = 1

    def __init__(self, email, name, password):
        self.id = UserEntry.id_seed
        UserEntry.id_seed += 1
        self.email = email
        self.name = name
        self.password = password

    # format user entry for users.txt
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

        # load existing users from users.txt
        self.users = self.load_users()
        self.name = None

        # start the login or registration prompt
        self.start_login_or_register()


    # load existing users from users.txt
    def load_users(self):
        users = []
        if os.path.exists("users.txt"):
            with open("users.txt", "r") as f:
                for line in f:
                    user = UserEntry.from_line(line)
                    if user:
                        users.append(user)
        return users


    # save a new user to users.txt
    def save_user(self, user):
        with open("users.txt", "a") as f:
            f.write(user.to_line())


    # prompt user to register or login
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


    # grab email, name, and password from user input, save it to users.txt, and enter the chat
    def register(self):
        email = input("Enter email: ").strip()
        name = input("Enter name: ").strip()
        password = input("Enter password: ").strip()

        if not email or not name or not password:
            print("All fields are required. Registration failed.")
            sys.exit(0)

        if any(u.email == email for u in self.users):
            print("User already exists. Try logging in.")
            sys.exit(0)

        new_user = UserEntry(email, name, password)
        self.users.append(new_user)
        self.save_user(new_user)
        self.name = name
   
        with open("users.txt", "a") as f:
            f.write(new_user.to_line())

        print("Registration successful. You are now logged in as", self.name)
        show_history(self.name)
        self.talk_to_server()


    # grab email and password from user input, check if it exists in users.txt, and enter the chat
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
        show_history(self.name)
        self.talk_to_server()
    

    # after login or register, start the chat with the server
    def talk_to_server(self):
        self.socket.send(self.name.encode()) # send name to server

        # different threads for sending and receiving messages
        Thread(target=self.receive_message).start() # start a new thread to listen to messages from server
        self.send_message() # send messages to server from main thread


    # running on main thread which reads user input and sends messages to the server with a timestamp
    # also handles exiting the chat with /quit
    def send_message(self):
        while True:
            client_input = input("")

            # /quit to exit as client
            if client_input.lower() == "/quit":
                stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                quit_msg = f"[{stamp}] {self.name}: bye"
                self.socket.send(quit_msg.encode())
                print("You have left the chat.")
                self.socket.close()
                sys.exit(0)

            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            packet = f"[{stamp}] {self.name}: {client_input}"
            self.socket.send(packet.encode())
            log_message(self.name, client_input)


    # running on seperate thread which listens for messages from the server
    def receive_message(self):
        while True:
            try:
                server_message = self.socket.recv(1024).decode()
            except (ConnectionAbortedError, ConnectionResetError, OSError):
                # socket closed so stop listening
                return

            # if the server message is empty then close the connection
            if not server_message.strip():
                return

            try:
                # parse “[timestamp] user: text”
                stamp, rest = server_message.split("] ", 1)
                user, text = rest.split(": ", 1)

                # skip reprint of your own messages
                if user == self.name:
                    continue

                # print everyone else's messages
                print(f"{stamp}] \033[1;31;40m{user}\033[0m: {text}")
            except ValueError:
                # fallback for system messages
                print("\033[1;31;40m" + server_message + "\033[0m")


if __name__ == "__main__":
    Client('127.0.0.1', 5155)
