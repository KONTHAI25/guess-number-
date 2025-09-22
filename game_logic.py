from typing import Dict, List, Any, Optional, TypedDict, cast
import random
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from models import Game as GameModel


class GameMode(TypedDict):
    max_n: int
    max_attempts: int
    base_per_turn_penalty: int
    base_hint_penalty: int


MODES: Dict[str, GameMode] = {
    "easy": {"max_n": 100, "max_attempts": 10, "base_per_turn_penalty": 600, "base_hint_penalty": 300},
    "medium": {"max_n": 1000, "max_attempts": 14, "base_per_turn_penalty": 429, "base_hint_penalty": 250},
    "hard": {"max_n": 10000, "max_attempts": 18, "base_per_turn_penalty": 333, "base_hint_penalty": 150},
}


class GameState(TypedDict):
    mode: str
    secret: int
    max_n: int
    max_attempts: int
    attempts_left: int
    attempts_used: int
    base_per_turn_penalty: int
    base_hint_penalty: int
    score: int
    used_hints: int
    hints_in_turn: int
    hints: List[str]
    guesses: List[int]
    status: str


def start_new_game(mode_key: str) -> GameState:
    """Initialize and return a new game state for the requested mode."""
    mode = MODES.get(mode_key, MODES["easy"])
    secret = random.randint(1, mode["max_n"])
    state: GameState = {
        "mode": mode_key,
        "secret": secret,
        "max_n": mode["max_n"],
        "max_attempts": mode["max_attempts"],
        "attempts_left": mode["max_attempts"],
        "attempts_used": 0,
        "base_per_turn_penalty": mode["base_per_turn_penalty"],
        "base_hint_penalty": mode["base_hint_penalty"],
        "score": 10000,  # Starting score
        "used_hints": 0,
        "hints_in_turn": 0,
        "hints": [],
        "guesses": [],
        "status": "playing",
    }
    return cast(GameState, state)


def update_score_for_guess(game: GameState) -> None:
    """Update game state after a guess attempt."""
    # decrement attempts_left but keep at >= 0
    game["attempts_left"] = max(0, game["attempts_left"] - 1)
    game["attempts_used"] += 1
    game["score"] = max(0, game["score"] - game["base_per_turn_penalty"])
    game["hints_in_turn"] = 0  # Reset hints-per-turn after each guess


def apply_hint_penalty(game: GameState) -> int:
    """Apply penalty for using a hint and return the cost."""
    hint_num = game["used_hints"] + 1
    hint_cost = game["base_hint_penalty"] * hint_num
    game["used_hints"] = hint_num
    game["hints_in_turn"] += 1
    game["score"] = max(0, game["score"] - hint_cost)
    return hint_cost


def record_game_result(
    db: SQLAlchemy,
    game: GameState,
    won: bool,
    user_id: Optional[int] = None,
    guest_name: Optional[str] = None,
) -> None:
    """
    Persist a finished game's summary to the database.

    Note: pass the SQLAlchemy instance (usually `db`) — this function uses db.session.
    """
    # Ensure the state has a final status
    game["status"] = "won" if won else "lost"

    # Create model instance. Use a datetime object for played_at.
    game_record = GameModel(
        user_id=user_id,
        guest_name=guest_name,
        mode=game["mode"],
        secret=game["secret"],
        attempts_used=game["attempts_used"],
        max_attempts=game["max_attempts"],
        used_hints=game["used_hints"],
        score=max(0, int(game["score"])),
        won=won,
        played_at=datetime.utcnow(),  # prefer a datetime, not an ISO string
    )

    # Persist via the SQLAlchemy session
    db.session.add(game_record)
    db.session.commit()
