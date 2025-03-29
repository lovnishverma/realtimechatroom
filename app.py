from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kartik_secret_key'

socketio = SocketIO(app)

#Connect to MongoDB Atlas (Python 2.7 compatible)
MONGO_URI = "mongodb+srv://test:test@cluster0.sxci1.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['chatDB']
messages_collection = db['messages']

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Send past messages when a user connects."""
    past_messages = list(messages_collection.find({}, {'_id': 0}))
    emit('load_messages', past_messages)

@socketio.on('message')
def handle_message(data):
    """Store messages in MongoDB and broadcast."""
    message_doc = {
        'message': data,
        'timestamp': datetime.utcnow()
    }
    messages_collection.insert_one(message_doc)
    emit('message', message_doc, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
