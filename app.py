from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kartik_secret_key'

socketio = SocketIO(app, async_mode='threading')

# Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://test:test@cluster0.sxci1.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['kartikchatDB']
messages_collection = db['messages']

# Define Indian Timezone (IST)
IST = pytz.timezone('Asia/Kolkata')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Send past messages when a user connects."""
    past_messages = list(messages_collection.find({}))

    for msg in past_messages:
        msg['_id'] = str(msg['_id'])  # Convert ObjectId to string
        
        if 'timestamp' in msg:
            try:
                # Convert timestamp string to datetime if stored as string
                if isinstance(msg['timestamp'], str):
                    msg['timestamp'] = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
                
                # If timestamp is stored as ISO format string, handle it
                elif isinstance(msg['timestamp'], unicode):  # Handle Unicode issue
                    msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])

                # Ensure datetime is timezone-aware
                if msg['timestamp'].tzinfo is None:
                    msg['timestamp'] = pytz.utc.localize(msg['timestamp'])

                # Convert to IST and format
                ist_time = msg['timestamp'].astimezone(IST)
                msg['timestamp'] = ist_time.strftime("%d-%m-%Y %I:%M %p")  # Requested format
            except Exception as e:
                print("Error parsing timestamp:", e)
                msg['timestamp'] = "Unknown"

    emit('load_messages', past_messages)

@socketio.on('message')
def handle_message(data):
    """Store messages in MongoDB and broadcast."""
    utc_now = datetime.utcnow()

    # Make UTC timezone-aware
    utc_now = pytz.utc.localize(utc_now)

    ist_now = utc_now.astimezone(IST)  # Convert to IST

    message_doc = {
        'message': data,
        'timestamp': utc_now.isoformat()  # Store timestamp as ISO format string
    }
    inserted_doc = messages_collection.insert_one(message_doc)

    # Convert for frontend display with requested format
    message_doc['_id'] = str(inserted_doc.inserted_id)
    message_doc['timestamp'] = ist_now.strftime("%d-%m-%Y %I:%M %p")  # Requested format

    emit('message', message_doc, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
