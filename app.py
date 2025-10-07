from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # allow all origins for testing

from flask_socketio import SocketIO, join_room, leave_room


app.config.from_object(Config)

# bind socketio to flask app
socketio = SocketIO( app, cors_allowed_origins="*") #allow cors for frontend

db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)

import models

from routes import user

with app.app_context():
    db.create_all()

@socketio.on("join")
def on_join(data):
    group_id = data.get("group_id")
    username = data.get("username")
    room = f'group_{group_id}'
    join_room(room)
    socketio.emit("status", {'msg': f"{username} has joined the group"}, room=room)
    
    
    
@socketio.on("leave")
def on_leave(data):
    group_id = data.get('group_id')
    username = data.get("username")
    room = f'group_{group_id}'
    leave_room(room)
    socketio.emit('status', {'msg': f'{username} has left the group'}, room=room)