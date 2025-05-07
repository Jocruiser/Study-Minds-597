# apps/models.py
from .db import db  # Import db from the current package
from flask_login import UserMixin

# Define the models

class User(db.Model, UserMixin):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    #email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # Add this line
    decks = db.relationship('Deck', backref='user', lazy=True)

class Flashcard(db.Model):
    __tablename__ = 'flashcard' 
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    answer = db.Column(db.String)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)  # ForeignKey to Deck
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Deck(db.Model):
    __tablename__ = 'deck' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='decks', lazy=True)
    created_at = db.Column(db.DateTime)
    flashcards = db.relationship('Flashcard', backref='deck', lazy=True)

    def get_id(self):
        return str(self.id)
    def __repr__(self):
        return f'<User {self.username}>'
