# NIELIT Anonymous Chat

NIELIT Anonymous Chat is a real-time chat application with message storage, abusive language filtering, and automatic chat clearing at midnight. The app is built using Flask, Flask-SocketIO, MongoDB, and WebSockets.

## Features
- **Real-time chat** using WebSockets.
- **Anonymous messaging** with user-defined nicknames.
- **Abusive language detection** with automatic 24-hour bans.
- **Message storage** using MongoDB.
- **Automatic chat clearance** every midnight (IST).
- **Ban system** with remaining time notifications.
- **Fully responsive UI** with Bootstrap.

## Tech Stack
- **Backend:** Flask, Flask-SocketIO, Gevent
- **Database:** MongoDB
- **Frontend:** HTML, CSS (Bootstrap, FontAwesome, Animate.css), JavaScript (jQuery, Socket.IO)
- **Hosting:** Can be deployed on any server supporting Python & MongoDB

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- MongoDB (or use a cloud MongoDB service like MongoDB Atlas)

### Steps to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/lovnishverma/realtimechatroom.git
   cd realtimechatroom
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up MongoDB:
   - Update the `MONGO_URI` in `app.py` with your MongoDB connection string.
4. Run the Flask app:
   ```bash
   python app.py
   ```
   OR using SocketIO's recommended method:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
5. Open `http://localhost:5000` in your browser.

## Configuration
Modify the following in `app.py` as needed:
- **MongoDB Connection:** Update `MONGO_URI` with your database details.
- **Abusive Words Filter:** Edit `ABUSIVE_WORDS` in `app.py` to add/remove restricted words.
- **Ban Duration:** Change `timedelta(hours=24)` in the `ban_user` function.
- **Chat Clearing Time:** Chat history clears at midnight IST; modify `clear_chat_at_midnight` function if needed.

## Deployment
- Can be deployed on **PythonAnywhere, AWS, Google Cloud, or any Flask-compatible hosting.**
- If deploying with **Gunicorn**, use:
  ```bash
  gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
  ```
- Use **NGINX and Supervisor** for production.

## API Endpoints
| Endpoint       | Method | Description |
|---------------|--------|-------------|
| `/`           | GET    | Renders chat UI |
| `/socket.io`  | WS     | Handles WebSocket communication |

## Issues & Contributions
Feel free to report issues or contribute by creating pull requests!

## License
MIT License

