# 🚀 NIELIT Anonymous Chat

[Live Demo 🔗](https://realtimechatroom-nqgq.onrender.com/)

A real-time anonymous chat application built with **Flask, Socket.IO, Gevent, and MongoDB**, supporting anonymous nicknames, ban system, message history, and automatic chat clearing at midnight (IST).

---

## ✨ Features

✅ **Real-Time Messaging** via WebSockets (Socket.IO)
✅ **Anonymous Chatting** with user-defined nicknames
✅ **Abusive Language Detection & 24-Hour Ban**
✅ **Message Persistence** via MongoDB
✅ **Auto Chat Clearing** every day at midnight IST
✅ **Ban Notifications** with remaining time alerts
✅ **Responsive UI** using Bootstrap, Animate.css, Font Awesome
✅ **Dark/Light Theme Toggle**
✅ **Emoji Picker** for quick reactions

---

## 🛠️ Tech Stack

| Layer        | Technology                                                                                              |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| **Backend**  | Flask, Flask-SocketIO (gevent mode), Python 2.7                                                         |
| **Database** | MongoDB Atlas / Local MongoDB                                                                           |
| **Frontend** | HTML5, CSS3 (Bootstrap 5, Animate.css, FontAwesome), JavaScript (jQuery, Socket.IO 2.1.1)               |
| **Hosting**  | Render.com ([https://realtimechatroom-nqgq.onrender.com/](https://realtimechatroom-nqgq.onrender.com/)) |

---

## 📥 Installation

### 🔧 Prerequisites

* Python 2.7 (as per this deployment)
* MongoDB (local or Atlas cloud instance)

---

### 🚀 Steps to Run Locally

```bash
# Clone the repository
git clone https://github.com/lovnishverma/realtimechatroom.git
cd realtimechatroom

# (Optional but recommended) Create a virtual environment
python2.7 -m virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### 🔑 Configuration

Edit **`app.py`** to update:

```python
MONGO_URI = "your-mongodb-connection-string"
```

---

### ▶️ Running the App Locally

```bash
python app.py
# OR (if configured for flask CLI)
flask run --host=0.0.0.0 --port=5000
```

Then open in browser:

```
http://localhost:5000/
```

---

## 🚀 Deployment Instructions (Render.com)

> This project is live at:
> **[https://realtimechatroom-nqgq.onrender.com/](https://realtimechatroom-nqgq.onrender.com/)**

If deploying yourself:

1. Push code to GitHub.
2. Connect GitHub repo to Render.com.
3. Use Docker deployment.
4. Expose port `5000`.
5. Set environment variables if needed.

---

### 🐳 Docker Build (Optional)

```dockerfile
# Dockerfile
FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python2.7 python2.7-dev build-essential libssl-dev libffi-dev zlib1g-dev wget && \
    wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && \
    python2.7 get-pip.py && \
    rm get-pip.py && \
    pip install --upgrade "pip<21.0" setuptools wheel

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

CMD ["python2.7", "app.py"]
```

---

## 📃 API Endpoints

| Endpoint     | Method | Purpose                      |
| ------------ | ------ | ---------------------------- |
| `/`          | GET    | Renders the Chat UI          |
| `/socket.io` | WS     | WebSocket for real-time chat |

---

## ⚙️ Configuration Options

You can adjust in **`app.py`**:

| Option                   | Purpose                              |
| ------------------------ | ------------------------------------ |
| `ABUSIVE_WORDS`          | Add/remove words to filter           |
| `BAN_DURATION`           | Set `timedelta(hours=24)` as desired |
| `clear_chat_at_midnight` | Adjust schedule as needed            |

---

## 📸 Screenshots

> <img width="1918" height="957" alt="image" src="https://github.com/user-attachments/assets/73d2c682-7b10-44bc-ae46-a030d59b90f0" />


---

## 📎 Useful Commands for Production

If deploying with Gunicorn:

```bash
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
```

Or with Flask-SocketIO:

```bash
python app.py
```

---

## 🚩 Known Limitations

* **Python 2.7 is deprecated.** Migration to Python 3 is recommended.
* Render free plan may sleep after inactivity.

---

## 🙌 Contributions

Feel free to fork this repo, improve features, fix bugs, and open a Pull Request.

---

## 📜 License

MIT License

---

## 🔗 Live Project

**[https://realtimechatroom-nqgq.onrender.com/](https://realtimechatroom-nqgq.onrender.com/)**


