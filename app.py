from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from hints import get_hint
import random
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# SQLite setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'game.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(6), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)
    is_guest = db.Column(db.Boolean, default=False)

    def highest_score(self):
        return max([s.value for s in self.scores], default=0)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

MODES = {
    'easy': {'range': (1, 1000), 'name': 'Easy'},
    'medium': {'range': (1, 10000), 'name': 'Medium'},
    'hard': {'range': (1, 500000), 'name': 'Hard'}
}

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', modes=MODES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            session['is_guest'] = user.is_guest
            return redirect(url_for('home'))
        else:
            flash("Invalid login.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username taken.")
        elif len(username) > 20 or len(password) != 6 or not password.isdigit():
            flash("Invalid format.")
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            session['is_guest'] = False
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/guest')
def guest_mode():
    import string
    while True:
        guest_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not User.query.filter_by(username=guest_id).first():
            break
    user = User(username=guest_id, password='', is_guest=True)
    db.session.add(user)
    db.session.commit()
    session['username'] = guest_id
    session['is_guest'] = True
    return redirect(url_for('start_game', mode='easy'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(username=session['username']).first()
    scores = [s.value for s in user.scores]
    highest = user.highest_score()

    all_users = User.query.filter_by(is_guest=False).all()
    leaderboard = sorted(all_users, key=lambda u: u.highest_score(), reverse=True)
    position = next((i + 1 for i, u in enumerate(leaderboard) if u.username == user.username), -1)

    return render_template('profile.html', scores=scores, highest=highest, position=position)

@app.route('/start/<mode>')
def start_game(mode):
    if mode not in MODES:
        flash("Invalid mode.")
        return redirect(url_for('home'))
    session['mode'] = mode
    session['secret'] = random.randint(*MODES[mode]['range'])
    session['guesses_left'] = 4
    session['hint_used'] = False
    session['score'] = 0
    session['game_over'] = False
    return redirect(url_for('play'))

@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'secret' not in session:
        return redirect(url_for('home'))
    if session['game_over']:
        return redirect(url_for('home'))

    feedback = ''
    show_hint = False

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'guess':
            guess = request.form.get('guess', type=int)
            if guess is None:
                feedback = "Enter a number."
            else:
                secret = session['secret']
                guesses_left = session['guesses_left']
                if guess == secret:
                    round_points = [100, 80, 60, 40][4 - guesses_left]
                    hint_penalty = 10 if session['hint_used'] else 0
                    session['score'] = round_points - hint_penalty
                    session['game_over'] = True
                    user = User.query.filter_by(username=session['username']).first()
                    score_entry = Score(value=session['score'], user=user)
                    db.session.add(score_entry)
                    db.session.commit()
                    flash(f"🎉 Correct! You scored {session['score']}.")
                    return redirect(url_for('play'))
                else:
                    session['guesses_left'] -= 1
                    if session['guesses_left'] == 0:
                        session['game_over'] = True
                        flash("❌ Out of guesses!")
                        return redirect(url_for('play'))
                    feedback = "Too high!" if guess > secret else "Too low!"
        elif action == 'hint':
            show_hint = True
            session['hint_used'] = True

    return render_template(
        'play.html',
        mode=MODES[session['mode']]['name'],
        range_limit=MODES[session['mode']]['range'],
        guesses_left=session['guesses_left'],
        hint=get_hint(session['secret']) if show_hint else None,
        feedback=feedback,
        game_over=session['game_over']
    )

@app.route('/leaderboard')
def leaderboard_page():
    users = User.query.filter_by(is_guest=False).all()
    scores = [{'name': u.username, 'score': u.highest_score()} for u in users]
    scores.sort(key=lambda x: x['score'], reverse=True)
    return render_template('leaderboard.html', scores=scores)

if __name__ == '__main__':
    app.run(debug=True)