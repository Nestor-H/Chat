import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(msg)
        except:
            break

def main():
    name = input("Enter your name: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5155))  # Change to server IP if running on a network

    sock.send(name.encode())

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input()
        if msg.lower() == "/quit":
            break
        sock.send(msg.encode())

    sock.close()

if __name__ == "__main__":
    main()
