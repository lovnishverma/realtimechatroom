from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import threading
import time
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kartik_super_secret_key'
socketio = SocketIO(app, async_mode='gevent')

MONGO_URI = "mongodb+srv://test:test@cluster0.sxci1.mongodb.net/chatDB?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['kartikdarkchatDB']
messages_collection = db['messages']
banned_users_collection = db['banned_users']

IST = pytz.timezone('Asia/Kolkata')

ABUSIVE_WORDS = ['fudu', 'makelode', 'chutiye', 'gandu', 'maderchod', 'fuck']
ABUSIVE_PATTERN = re.compile(r'\b(' + '|'.join(ABUSIVE_WORDS) + r')\b', re.IGNORECASE)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    client_ip = request.remote_addr
    if is_user_banned(client_ip):
        emit('ban_notification', {'message': 'You are temporarily banned.', 'remaining': get_ban_remaining_time(client_ip)})
        return
    
    past_messages = list(messages_collection.find({}).sort('timestamp', 1))
    
    for msg in past_messages:
        msg['_id'] = str(msg['_id'])
        
        if 'timestamp' in msg:
            try:
                if isinstance(msg['timestamp'], str):
                    msg['timestamp'] = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')

                # If it's still naive, make it UTC aware
                if msg['timestamp'].tzinfo is None:
                    msg['timestamp'] = pytz.utc.localize(msg['timestamp'])

                # Convert to IST
                ist_time = msg['timestamp'].astimezone(IST)
                msg['timestamp'] = ist_time.strftime("%d-%m-%Y %I:%M:%S %p")
            except Exception as e:
                print("Error parsing timestamp:", e)
                msg['timestamp'] = "Unknown"
    
    emit('load_messages', past_messages)


@socketio.on('message')
def handle_message(data):
    client_ip = request.remote_addr
    if is_user_banned(client_ip):
        emit('ban_notification', {'message': 'You are temporarily banned.', 'remaining': get_ban_remaining_time(client_ip)})
        return
    
    nickname = data.get('nickname', 'Anonymous')
    message_text = data.get('message', '')
    
    if contains_abusive_words(message_text):
        ban_user(client_ip, nickname)
        emit('ban_notification', {'message': 'You have been banned for 24 hours.'})
        return
    
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    ist_now = utc_now.astimezone(IST)
    message_doc = {'nickname': nickname, 'message': message_text, 'timestamp': utc_now, 'ip': client_ip}
    inserted_doc = messages_collection.insert_one(message_doc)
    broadcast_doc = {'_id': str(inserted_doc.inserted_id), 'nickname': nickname, 'message': message_text, 'timestamp': ist_now.strftime("%d-%m-%Y %I:%M:%S %p")}
    emit('message', broadcast_doc, broadcast=True)

def contains_abusive_words(message):
    return bool(ABUSIVE_PATTERN.search(message))

def ban_user(ip, nickname):
    ban_until = datetime.utcnow() + timedelta(hours=24)
    banned_users_collection.insert_one({'ip': ip, 'nickname': nickname, 'banned_at': datetime.utcnow(), 'ban_until': ban_until, 'reason': 'Abusive language'})
    print("User banned:", nickname, "IP:", ip, "until", ban_until)

def is_user_banned(ip):
    now = datetime.utcnow()
    return bool(banned_users_collection.find_one({'ip': ip, 'ban_until': {'$gt': now}}))

def get_ban_remaining_time(ip):
    now = datetime.utcnow()
    ban_record = banned_users_collection.find_one({'ip': ip, 'ban_until': {'$gt': now}})
    if ban_record:
        remaining = ban_record['ban_until'] - now
        hours, minutes = divmod(int(remaining.total_seconds() / 60), 60)
        return "{} hours and {} minutes".format(hours, minutes)
    return None

def clear_chat_at_midnight():
    while True:
        now = datetime.now(IST)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.time() >= midnight.time():
            midnight += timedelta(days=1)
        seconds_to_midnight = (midnight - now).total_seconds()
        print("Next chat cleanup scheduled in {:.2f} hours".format(seconds_to_midnight / 3600))
        time.sleep(seconds_to_midnight)
        try:
            result = messages_collection.delete_many({})
            print("Chat cleared at", datetime.now(IST), "Deleted", result.deleted_count, "messages.")
            socketio.emit('chat_cleared', {'message': 'Chat has been cleared for the day.'}, broadcast=True)
        except Exception as e:
            print("Error clearing chat:", e)

if __name__ == '__main__':
    chat_clear_thread = threading.Thread(target=clear_chat_at_midnight)
    chat_clear_thread.daemon = True  # Set the thread as daemon
    chat_clear_thread.start()

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
