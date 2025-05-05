import os
from datetime import datetime

HISTORY_FILE = "messages.txt"


# show every past message in the messages.txt file
def show_history(username = None):
    if not os.path.exists(HISTORY_FILE):
        return

    with open(HISTORY_FILE, "r") as f:
        for line in f:
            ts, user, text = line.strip().split(",", 2)
            # UNCONDITIONAL: print every message
            print(f"[{ts}] {user}: {text}", flush=True)


# append a new message to the messages.txt file
def log_message(username, text):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{stamp},{username},{text}\n")
