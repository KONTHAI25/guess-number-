import os
import random
from functools import wraps

from flask import Flask, session, flash, redirect, url_for

from models import db
from routes import (
    index,
    register,
    login,
    logout,
    guest,
    new_game,
    play,
    profile,
    leaderboard,
    api_leaderboard,
    chat,
    api_chat,
)

APP_SECRET = os.environ.get("APP_SECRET", "dev-secret-change-me")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "game.db")

app = Flask(__name__)
app.secret_key = APP_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# -------------------- Database helpers --------------------
def init_db():
    with app.app_context():
        db.create_all()


# -------------------- Auth utils --------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session and not session.get("is_guest"):
            flash("Please login to access your profile.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def create_guest():
    # Only create if not already guest or user
    if "user_id" in session or session.get("is_guest"):
        return
    suffix = random.randint(1000, 9999)
    session["is_guest"] = True
    session["guest_name"] = f"Guest-{suffix}"


# -------------------- Routes --------------------
app.add_url_rule("/", "index", index)
app.add_url_rule("/register", "register", register, methods=["GET", "POST"])
app.add_url_rule("/login", "login", login, methods=["GET", "POST"])
app.add_url_rule("/logout", "logout", logout)
app.add_url_rule("/guest", "guest", guest)
app.add_url_rule("/new_game", "new_game", new_game, methods=["GET", "POST"])
app.add_url_rule("/play", "play", play, methods=["GET", "POST"])
app.add_url_rule("/profile", "profile", profile)
app.add_url_rule("/leaderboard", "leaderboard", leaderboard)
app.add_url_rule("/api/leaderboard", "api_leaderboard", api_leaderboard)
app.add_url_rule("/chat", "chat", chat)
app.add_url_rule("/api/chat", "api_chat", api_chat, methods=["POST"])


if __name__ == "__main__":
    init_db()
    # For local dev
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
