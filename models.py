# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    # store a hashed password (use werkzeug.security or passlib to create/verify)
    password_hash = db.Column(db.String(128), nullable=False)
    # store an actual datetime (UTC) rather than a string
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # cascade so when a user is deleted, related games are cleaned up (optional)
    games = db.relationship(
        "Game",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    guest_name = db.Column(db.String(80), nullable=True)
    mode = db.Column(db.String(20), nullable=False)
    secret = db.Column(db.Integer, nullable=False)
    attempts_used = db.Column(db.Integer, nullable=False)
    max_attempts = db.Column(db.Integer, nullable=False)
    used_hints = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Boolean, nullable=False)
    # store played_at as a DateTime (UTC)
    played_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Game id={self.id} mode={self.mode} score={self.score} won={self.won}>"
