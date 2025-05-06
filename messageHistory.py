from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# MongoDB connection using encoded password
uri = "mongodb+srv://admin:%40password123@cluster0.jpynuym.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Access the database and collection
db = client.chat_app
collection = db.messages

# Save a message to MongoDB
def log_message(username, text):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc = {
        "timestamp": stamp,
        "username": username,
        "message": text
    }
    collection.insert_one(doc)

# Get all messages for a given user
def get_history(username):
    messages = collection.find({'username': username}).sort("timestamp", 1)
    return [f"[{msg['timestamp']}] {msg['username']}: {msg['message']}" for msg in messages]
