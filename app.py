from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import threading
import time
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'superduper_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# MongoDB setup
MONGO_URI = "mongodb+srv://test:test@cluster0.sxci1.mongodb.net/chatDB?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['realtimechatDB']
messages_collection = db['messages']
banned_users_collection = db['banned_users']

# Timezone setup
IST = pytz.timezone('Asia/Kolkata')

# Abusive words list
ABUSIVE_WORDS = ['motherfucker', 'fuck', 'shit', 'damn', 'bitch']
ABUSIVE_PATTERN = re.compile(r'\b(' + '|'.join(re.escape(word) for word in ABUSIVE_WORDS) + r')\b', re.IGNORECASE)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    session_id = request.sid
    print(f"User connected: {session_id}")

    if is_user_banned(session_id):
        remaining_time = get_ban_remaining_time(session_id)
        print(f"User {session_id} is banned. Emitting ban_notification...")
        emit('ban_notification', {
            'message': 'You are temporarily banned.',
            'remaining': remaining_time
        })
        return

    try:
        past_messages = list(messages_collection.find({}).sort('timestamp', 1).limit(100))
        for msg in past_messages:
            msg['_id'] = str(msg['_id'])
            if 'timestamp' in msg:
                try:
                    if isinstance(msg['timestamp'], str):
                        msg['timestamp'] = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if msg['timestamp'].tzinfo is None:
                        msg['timestamp'] = pytz.utc.localize(msg['timestamp'])
                    msg['timestamp'] = msg['timestamp'].astimezone(IST).strftime("%d-%m-%Y %I:%M:%S %p")
                except Exception as e:
                    print(f"Error parsing timestamp: {e}")
                    msg['timestamp'] = "Unknown"
        emit('load_messages', past_messages)
    except Exception as e:
        print(f"Error loading messages: {e}")
        emit('load_messages', [])

@socketio.on('message')
def handle_message(data):
    session_id = request.sid
    
    if is_user_banned(session_id):
        print(f"User {session_id} is banned. Sending notification...")
        remaining_time = get_ban_remaining_time(session_id)
        emit('ban_notification', {
            'message': 'You are temporarily banned.',
            'remaining': remaining_time
        })
        return
    
    nickname = data.get('nickname', 'Anonymous')
    message_text = data.get('message', '').strip()
    
    # Validate message
    if not message_text:
        return
    
    if len(message_text) > 1000:  # Limit message length
        emit('error', {'message': 'Message too long. Maximum 1000 characters.'})
        return
    
    if contains_abusive_words(message_text):
        ban_user(session_id, nickname)
        return
    
    try:
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        ist_now = utc_now.astimezone(IST)
        
        message_doc = {
            'nickname': nickname,
            'message': message_text,
            'timestamp': utc_now,
            'session_id': session_id
        }
        
        inserted_doc = messages_collection.insert_one(message_doc)
        
        broadcast_doc = {
            '_id': str(inserted_doc.inserted_id),
            'nickname': nickname,
            'message': message_text,
            'timestamp': ist_now.strftime("%d-%m-%Y %I:%M:%S %p")
        }
        
        emit('message', broadcast_doc, broadcast=True)
        
    except Exception as e:
        print(f"Error handling message: {e}")
        emit('error', {'message': 'Failed to send message.'})

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    print(f"User disconnected: {session_id}")

def contains_abusive_words(message):
    return bool(ABUSIVE_PATTERN.search(message))

def ban_user(session_id, nickname):
    try:
        ban_until = datetime.utcnow() + timedelta(hours=24)
        banned_users_collection.insert_one({
            'session_id': session_id,
            'nickname': nickname,
            'banned_at': datetime.utcnow(),
            'ban_until': ban_until,
            'reason': 'Abusive language'
        })
        print(f"User banned: {nickname}, Session ID: {session_id}, until {ban_until}")

        # Emit the ban notification to the specific user
        socketio.emit("ban_notification", {
            "message": "You have been banned for 24 hours due to abusive language.",
            "remaining": "24 hours"
        }, room=session_id)

        print(f"Ban notification emitted to session {session_id}")
        
    except Exception as e:
        print(f"Error banning user: {e}")

def is_user_banned(session_id):
    try:
        now = datetime.utcnow()
        return bool(banned_users_collection.find_one({
            'session_id': session_id, 
            'ban_until': {'$gt': now}
        }))
    except Exception as e:
        print(f"Error checking ban status: {e}")
        return False

def get_ban_remaining_time(session_id):
    try:
        now = datetime.utcnow()
        ban_record = banned_users_collection.find_one({
            'session_id': session_id, 
            'ban_until': {'$gt': now}
        })
        if ban_record:
            remaining = ban_record['ban_until'] - now
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours} hours and {minutes} minutes"
        return None
    except Exception as e:
        print(f"Error getting ban remaining time: {e}")
        return None

def cleanup_expired_bans():
    """Clean up expired bans from the database"""
    try:
        now = datetime.utcnow()
        result = banned_users_collection.delete_many({'ban_until': {'$lt': now}})
        if result.deleted_count > 0:
            print(f"Cleaned up {result.deleted_count} expired bans")
    except Exception as e:
        print(f"Error cleaning up expired bans: {e}")

def clear_chat_at_midnight():
    """Clear chat messages at midnight IST"""
    while True:
        try:
            now = datetime.now(IST)
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            seconds_to_midnight = (midnight - now).total_seconds()
            
            print(f"Next chat cleanup scheduled in {seconds_to_midnight / 3600:.2f} hours")
            time.sleep(seconds_to_midnight)
            
            # Clear messages
            result = messages_collection.delete_many({})
            print(f"Chat cleared at {datetime.now(IST)}, Deleted {result.deleted_count} messages.")
            
            # Clean up expired bans
            cleanup_expired_bans()
            
            # Notify all users
            socketio.emit('chat_cleared', {
                'message': 'Chat has been cleared for the day.'
            }, broadcast=True)
            
        except Exception as e:
            print(f"Error in chat cleanup: {e}")
            time.sleep(3600)  # Wait 1 hour before retrying

if __name__ == '__main__':
    # Start the chat cleanup thread
    chat_clear_thread = threading.Thread(target=clear_chat_at_midnight)
    chat_clear_thread.daemon = True
    chat_clear_thread.start()

    # Run the application
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
