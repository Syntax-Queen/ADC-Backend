# ADC Backend

A Flask-powered backend for a group messaging and collaboration system.  
Users can create groups, send messages in real time using **WebSockets**, join groups through invite links, and manage group membership (add/remove members, delete groups, or leave on their own).

---

## 🚀 Features

- 🔑 **User Authentication** – Secure login system with `Flask-HTTPAuth`.
- 👥 **Group Management**
  - Create groups.
  - Add/remove members.
  - Delete groups.
  - Leave groups independently.
- 💬 **Messaging**
  - Send and view messages inside groups.
  - Real-time messaging powered by **Flask-SocketIO**.
  - Join/leave notifications with WebSockets.
- 🔗 **Invite System** – Users can join via a unique invite link.
- 📜 **Database Integration** – SQLAlchemy + Flask-Migrate for schema handling.

---

## 🛠 Tech Stack

- **Backend:** Flask, Flask-SocketIO, Flask-Migrate, Flask-SQLAlchemy
- **Auth:** Flask-HTTPAuth
- **Database:** SQLite / PostgreSQL
- **Realtime:** WebSockets (Socket.IO)

---

## 📸 Screenshots

### 🔑 Authentication
![Signup](screenshots/signup.png)
![Login](screenshots/login.png)

### 👥 Group Management
![Group](screenshots/group.png)

### 💬 Messaging
![Chat](screenshots/chat.png)

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Syntax-Queen/ADC-Backend.git
   cd ADC-Backend
