guessing-game-flask/
│
├── app.py
├── hints.py
├── game.db (auto-created)
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── play.html
│   ├── profile.html
│   └── leaderboard.html
│
├── static/
│   └── style.css
│
├── requirements.txt
├── README.md
└── .gitignore

# 🔢 Number Guessing Game with Flask

A web-based guessing number game with multiple modes, login, leaderboard, and hints.

## Features

- 🔐 User authentication and profiles
- 🎟 Guest mode (auto-generated username)
- 🎯 3 game modes (Easy, Medium, Hard)
- 🧠 Hint system (-10 pts)
- 🏆 Leaderboard with SQLite backend
- 📊 User profiles with score history

## Installation

1. Clone the repo
2. Create a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt