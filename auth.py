# auth.py
import random
from functools import wraps
from flask import session, flash, redirect, url_for

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
