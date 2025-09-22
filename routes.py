from flask import render_template, request, redirect, url_for, session, flash, Response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# after
from auth import login_required, create_guest
from models import db, User, Game
from game_logic import MODES, start_new_game, update_score_for_guess, apply_hint_penalty, record_game_result
from hints import get_hint


def index():
    return render_template("index.html", modes=MODES)


def register() -> Response | str:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Input validation
        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("register"))
            
        if len(username) < 3 or len(username) > 20:
            flash("Username must be 3-20 characters long.", "danger")
            return redirect(url_for("register"))
            
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("register"))

        try:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                created_at=datetime.utcnow().isoformat(timespec="seconds")
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e):
                flash("Username already exists.", "danger")
            elif "Data too long" in str(e):
                flash("Username is too long.", "danger")
            else:
                flash("Registration failed. Please try again.", "danger")
                # Log the full error for debugging
                app.logger.error(f"Registration error: {str(e)}", exc_info=True)
                
    return render_template("register.html")


def login() -> Response | str:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Input validation
        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("login"))

        # Basic rate limiting using session
        failed_attempts = session.get('failed_login_attempts', 0)
        if failed_attempts >= 5:
            flash("Too many failed attempts. Please try again later.", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Successful login - reset failed attempts
            session.clear()
            session["user_id"] = user.id
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("index"))
        else:
            # Failed login - increment counter
            session['failed_login_attempts'] = failed_attempts + 1
            flash("Invalid username or password.", "danger")
            app.logger.warning(f"Failed login attempt for username: {username}")
            
    return render_template("login.html")


def logout() -> Response:
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


def guest():
    session.clear()
    create_guest()
    flash(f"You are playing as {session['guest_name']}", "info")
    return redirect(url_for("index"))


def new_game() -> Response:
    # Accept mode from query (GET) or form (POST)
    mode = request.values.get("mode", "easy")
    if "user_id" not in session and not session.get("is_guest"):
        create_guest()
    session["game"] = start_new_game(mode)
    return redirect(url_for("play"))


def play():
    # Migrate old game sessions to new format
    if session.get("game") and "base_per_turn_penalty" not in session["game"]:
        try:
            mode_key = session["game"]["mode"]
            old_game = session["game"]
            new_game = start_new_game(mode_key)

            # Preserve existing game state
            for key in ["secret", "max_n", "max_attempts", "attempts_left",
                        "attempts_used", "score", "used_hints", "hints",
                        "guesses", "status"]:
                if key in old_game:
                    new_game[key] = old_game[key]

            # Adjust score if needed
            new_game["score"] = min(new_game["score"], 10000)
            session["game"] = new_game
            flash("Your game has been migrated to the new scoring system", "info")
        except Exception as e:
            print(f"Migration error: {e}")
            session.pop("game", None)
            return redirect(url_for("index"))

    game = session.get("game")

    if request.method == "POST":
        if not game:
            flash("No active game. Start a new game.", "warning")
            return redirect(url_for("index"))

        action = request.form.get("action")
        if action == "hint":
            if game["status"] != "playing":
                flash("Game is over.", "warning")
                return redirect(url_for("play"))
            # Enforce 2 hints per turn limit
            if game["hints_in_turn"] >= 2:
                flash("You have reached the limit of 2 hints per turn", "warning")
                return redirect(url_for("play"))
            hint_cost = apply_hint_penalty(game)
            hint_text = get_hint(game)
            if hint_text:
                game["hints"].append(hint_text)
                session["game"] = game
                flash(f"Hint used! -{hint_cost} points", "info")

        if action == "guess":
            if not game or game["status"] != "playing":
                flash("No active game or game is already over.", "warning")
                return redirect(url_for("play"))
                
            try:
                guess = int(request.form.get("guess", "").strip())
                if guess < 1 or guess > game["max_n"]:
                    raise ValueError("Guess out of range")
            except ValueError as e:
                if "out of range" in str(e):
                    flash(f"Your guess must be between 1 and {game['max_n']}.", "warning")
                else:
                    flash("Please enter a valid number.", "danger")
                app.logger.info(f"Invalid guess attempt: {request.form.get('guess')}")
                return redirect(url_for("play"))

            update_score_for_guess(game)
            game["guesses"].append(guess)

            if guess == game["secret"]:
                game["status"] = "won"
                session["game"] = game
                record_game_result(db.session, game, True, session.get("user_id"), session.get("guest_name"))
                flash(f"Correct! The number was {game['secret']}.", "success")
            else:
                if game["attempts_left"] <= 0:
                    game["status"] = "lost"
                    session["game"] = game
                    record_game_result(db.session, game, False, session.get("user_id"), session.get("guest_name"))
                    flash(f"Out of attempts. The number was {game['secret']}.", "danger")
                else:
                    if guess < game["secret"]:
                        flash("Too low! Try higher.", "info")
                    else:
                        flash("Too high! Try lower.", "info")
            session["game"] = game
            return redirect(url_for("play"))

    return render_template("play.html", game=game, modes=MODES)


@login_required
def profile() -> str:
    try:
        if session.get("user_id"):
            user = User.query.get(session["user_id"])
            if not user:
                flash("User not found", "danger")
                return redirect(url_for("index"))
                
            games = Game.query.filter_by(user_id=session["user_id"]).order_by(Game.played_at.desc()).limit(100).all()
            stats_query = db.session.query(
                db.func.count(Game.id).label('total_games'),
                db.func.sum(Game.won).label('wins'),
                db.func.max(Game.score).label('best_score'),
                db.func.avg(Game.score).label('avg_score')
            ).filter(Game.user_id == session["user_id"]).first()
            username = session.get("username")
        else:
            guest_name = session.get("guest_name")
            if not guest_name:
                flash("Guest session invalid", "danger")
                return redirect(url_for("index"))
                
            games = Game.query.filter_by(guest_name=guest_name).order_by(Game.played_at.desc()).limit(100).all()
            stats_query = db.session.query(
                db.func.count(Game.id).label('total_games'),
                db.func.sum(Game.won).label('wins'),
                db.func.max(Game.score).label('best_score'),
                db.func.avg(Game.score).label('avg_score')
            ).filter(Game.guest_name == guest_name).first()
            username = guest_name

        # Convert stats to dict with proper null handling
        stats = {
            'total_games': stats_query.total_games if stats_query and stats_query.total_games else 0,
            'wins': stats_query.wins if stats_query and stats_query.wins else 0,
            'best_score': stats_query.best_score if stats_query and stats_query.best_score else 0,
            'avg_score': float(stats_query.avg_score) if stats_query and stats_query.avg_score else 0.0
        }

        return render_template("profile.html", username=username, games=games, stats=stats)
        
    except Exception as e:
        app.logger.error(f"Profile error: {str(e)}", exc_info=True)
        flash("Error loading profile data", "danger")
        return redirect(url_for("index"))


def leaderboard() -> str:
    try:
        # Best single-game score per user or guest
        best_subquery = db.session.query(
            db.func.coalesce(User.username, Game.guest_name).label('name'),
            db.func.max(Game.score).label('best_score')
        ).outerjoin(User, User.id == Game.user_id).group_by(
            db.func.coalesce(User.username, Game.guest_name)
        ).subquery()

        best = db.session.query(best_subquery).order_by(best_subquery.c.best_score.desc()).limit(20).all()

        # Top 20 wins
        wins_subquery = db.session.query(
            db.func.coalesce(User.username, Game.guest_name).label('name'),
            db.func.sum(Game.won).label('wins')
        ).outerjoin(User, User.id == Game.user_id).group_by(
            db.func.coalesce(User.username, Game.guest_name)
        ).subquery()

        wins = db.session.query(wins_subquery).order_by(wins_subquery.c.wins.desc(), wins_subquery.c.name.asc()).limit(20).all()

        return render_template("leaderboard.html", best=best, wins=wins)
        
    except Exception as e:
        app.logger.error(f"Leaderboard error: {str(e)}", exc_info=True)
        flash("Error loading leaderboard", "danger")
        return render_template("leaderboard.html", best=[], wins=[])


def api_leaderboard():
    best_subquery = db.session.query(
        db.func.coalesce(User.username, Game.guest_name).label('name'),
        db.func.max(Game.score).label('best_score')
    ).outerjoin(User, User.id == Game.user_id).group_by(
        db.func.coalesce(User.username, Game.guest_name)
    ).subquery()

    best = db.session.query(best_subquery).order_by(best_subquery.c.best_score.desc()).limit(50).all()
    from flask import jsonify
    return jsonify([{"name": row.name, "best_score": row.best_score} for row in best])


def chat():
    """Render the chat interface"""
    return render_template("chat.html")


def api_chat():
    """Handle chat messages and return responses"""
    from flask import jsonify, request
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Simple echo response for now - you can replace this with your AI logic
    response = f"Echo: {message}"
    
    return jsonify({
        'message': message,
        'response': response,
        'timestamp': datetime.utcnow().isoformat()
    })