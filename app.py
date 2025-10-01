from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
socketio = SocketIO(cors_allowed_origins="*") #allow cors for frontend

db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)

import models

from routes import user