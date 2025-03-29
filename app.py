from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime
import pytz
import gevent
import gevent.monkey
gevent.monkey.patch_all()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'btechkartik_secret_key'

socketio = SocketIO(app, async_mode='gevent')

# Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://test:test@cluster0.sxci1.mongodb.net/chatDB?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['kartikchatDB']
messages_collection = db['messages']

IST = pytz.timezone('Asia/Kolkata')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Send past messages when a user connects."""
    try:
        past_messages = list(messages_collection.find({}))
        for msg in past_messages:
            msg['_id'] = str(msg['_id'])  # Convert ObjectId to string

            if 'timestamp' in msg:
                try:
                    if isinstance(msg['timestamp'], str):
                        msg['timestamp'] = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
                    
                    if msg['timestamp'].tzinfo is None:
                        msg['timestamp'] = pytz.utc.localize(msg['timestamp'])

                    ist_time = msg['timestamp'].astimezone(IST)
                    msg['timestamp'] = ist_time.strftime("%d-%m-%Y %I:%M %p")  # Requested format
                except Exception as e:
                    print("Error parsing timestamp:", e)
                    msg['timestamp'] = "Unknown"
        
        emit('load_messages', past_messages)
    except Exception as e:
        print("MongoDB Connection Error:", e)

@socketio.on('message')
def handle_message(data):
    """Store messages in MongoDB and broadcast."""
    utc_now = datetime.utcnow()
    utc_now = pytz.utc.localize(utc_now)
    ist_now = utc_now.astimezone(IST)

    message_doc = {
        'message': data,
        'timestamp': utc_now  # Store in UTC
    }
    inserted_doc = messages_collection.insert_one(message_doc)

    message_doc['_id'] = str(inserted_doc.inserted_id)
    message_doc['timestamp'] = ist_now.strftime("%d-%m-%Y %I:%M %p")

    emit('message', message_doc, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
