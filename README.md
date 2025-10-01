# ADC — AI Dream Chat

**ADC (AI Dream Chat)** is an intelligent assistant that interprets dreams using AI, transforming your subconscious thoughts into meaningful insights. Built with Flask and a modular backend, ADC features a fully documented API and a structured database design, making it easy to explore, extend, and integrate.

Ask about your dreams, get real-time AI-powered interpretations, and see how each endpoint connects to the system  all while reviewing a clean, professional backend showcase.


## 🌍 Live Demo
[View Live Website](https://your-live-app-link.com)

---
## 📖 Documentation
- [API Docs](ADC-documentation.json)
- [WebSocket Docs](docs/websocket.md)

## 🌟 Features

- User authentication (sign up, login, JWT tokens)  
- Post dreams & add comments  
- Create chat groups, invite via unique link, add/remove users  
- Real-time messaging with WebSockets  
- Time-based edit restrictions (e.g., you can edit a post only within 3 hours)  
- Anonymous by design — no profile photo or personal bios collected  

---

## 🧰 Tech Stack

| Component        | Technology / Library      |
|------------------|---------------------------|
| Backend          | Python, Flask             |
| DB & Migrations  | SQLAlchemy, Flask-Migrate |
| Real-time        | Flask-SocketIO            |
| Authentication   | JWT, Flask-HTTPAuth        |
| Dev / Production DB | SQLite (dev), Postgres (prod) |

---

## 🚀 Installation & Setup

# bash
git clone https://github.com/Syntax-Queen/ADC-Backend.git

cd ADC-Backend

python -m venv .venv

.venv/bin/activate         # or Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Setup your config (e.g. SECRET_KEY, database URI) in `config.py` or via env vars

flask db migrate -m "Initial migration"
flask db upgrade

# Run with WebSocket support
python app.py               # or flask run if you wire socketio.run in your entry


---

## 📸 Screenshots

### 🔑 Authentication
![Signup](docs/screenshots/signup.png)
![Login](docs/screenshots/login.png)

### 👥 Group Management
![Create-Group](docs/screenshots/create-group.png)
![delete-Group](docs/screenshots/delete-group.png)
![join-Group](docs/screenshots/join-group.png)

### 💬 Messaging
![group-message](docs/screenshots/message.png)
![Post](docs/screenshots/post.png)
![view-all-messages](docs/screenshots/view-all-messages.png)
![view-posts-comments](docs/screenshots/view-post-comments.png)

---
# Project Layout

├── app.py
├── auth.py
├── config.py
├── models.py
├── routes/
│   └── user.py
├── migrations/
├── requirements.txt
└── docs/
    └── screenshots/
