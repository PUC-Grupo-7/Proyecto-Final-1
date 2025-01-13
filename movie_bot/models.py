# movie_bot/models.py
from .db import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    favorite_genre = db.Column(db.String(50), nullable=True)
    disliked_genre = db.Column(db.String(50), nullable=True)
    messages = db.relationship('Message', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)  # 'user' o 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Message {self.id} by {self.author} at {self.timestamp}>"
