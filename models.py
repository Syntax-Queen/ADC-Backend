from datetime import datetime, timedelta
import os

import jwt
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author')
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def generate_auth_token(self):
        expiration_time = datetime.utcnow() + timedelta(days=10)
        payload ={
            'id': self.id,
            'exp': expiration_time,
        }
        
        token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            return token
    
    @staticmethod
    def verify_auth_token(token):
        if not token:
            return None
        try:
            active_token = StoredJwtToken.query.filter_by(token=token).first()
            if active_token:
                payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
                user = User.query.get(payload['id'])
                return user
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.DecodeError:
            print("Token is invalid")
            return None
       
       
class StoredJwtToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship("User", backref="tokens")
    
    
class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='password_reset_token', lazy=True)
    used = db.Column(db.Boolean, nullable=False, default=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    

# POST
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150),  nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    # Backrefs
    user = db.relationship('User', backref='comments', lazy=True)
    post = db.relationship('Post', backref='comments', lazy=True)    
        