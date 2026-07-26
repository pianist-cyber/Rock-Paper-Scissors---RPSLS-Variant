import random
from typing import Dict

from core.gestures import Gesture
from core.playstyles import Playstyle
from core.round import VALID_TARGET_SCORES
from models.scoreboard import RoundLogEntry, Scoreboard

GESTURE_ALIASES: Dict[str, Gesture] = {
    "rock": Gesture.ROCK, "r": Gesture.ROCK,
    "paper": Gesture.PAPER, "p": Gesture.PAPER,
    "scissors": Gesture.SCISSORS, "sc": Gesture.SCISSORS,
    "lizard": Gesture.LIZARD, "l": Gesture.LIZARD,
    "spock": Gesture.SPOCK, "sp": Gesture.SPOCK,
}

PLAYSTYLE_ALIASES: Dict[str, Playstyle] = {
    "rogue": Playstyle.ROGUE,
    "defensive": Playstyle.DEFENSIVE,
    "calm": Playstyle.CALM,
}

COLUMN_WIDTHS = {"round": 6, "player": 24, "modifiers": 26, "points": 24, "total": 18}

def parse_gesture(raw: str) -> Gesture:
    if not isinstance(raw, str):
        raise TypeError(f"Expected str, got {type(raw).__name__}")
    key = raw.strip().lower()
    if key not in GESTURE_ALIASES:
        raise ValueError(f"Unrecognized gesture: {raw!r}. Try Rock, Paper, Scissors, Lizard, or Spock.")
    return GESTURE_ALIASES[key]


def parse_playstyle(raw: str) -> Playstyle:
    if not isinstance(raw, str):
        raise TypeError(f"Expected str, got {type(raw).__name__}")
    key = raw.strip().lower()
    if key not in PLAYSTYLE_ALIASES:
        raise ValueError(f"Unrecognized playstyle: {raw!r}. Try Rogue, Defensive, or Calm.")
    return PLAYSTYLE_ALIASES[key]


def parse_target_score(raw: str) -> int:
    if not isinstance(raw, str):
        raise TypeError(f"Expected str, got {type(raw).__name__}")
    try:
        value = int(raw.strip())
    except ValueError:
        raise ValueError(f"Target score must be a whole number, got {raw!r}")
    if value not in VALID_TARGET_SCORES:
        raise ValueError(f"Target score must be one of {sorted(VALID_TARGET_SCORES)}, got {value}")
    return value


def random_gesture() -> Gesture:
    return random.choice(list(Gesture))


def _format_gesture_cell(gesture: Gesture, playstyle: Playstyle) -> str:
    return f"{gesture.value} ({playstyle.value})"


def _format_modifiers(entry: RoundLogEntry) -> str:
    if entry.winner_name is None:
        return "Feint Save (Draw)" if entry.token_saved else "Draw"
    parts = []
    if entry.nerf_triggered:
        parts.append("Nerf! -1")
    if entry.affinity_applied:
        parts.append("Affinity +1")
    if entry.momentum_applied:
        parts.append("Momentum +1")
    return ", ".join(parts) if parts else "-"


def _format_points(entry: RoundLogEntry) -> str:
    def signed(n: int) -> str:
        return f"+{n}" if n > 0 else str(n)

    return f"{entry.name_a}: {signed(entry.points_a)}, {entry.name_b}: {signed(entry.points_b)}"

def _format_totals(entry: RoundLogEntry) -> str:
    return f"{entry.name_a}: {entry.total_a}, {entry.name_b}: {entry.total_b}"

def render_table_header(name_a: str, name_b: str) -> str:
    header = (
        f"{'Rnd':<{COLUMN_WIDTHS['round']}}"
        f"{name_a:<{COLUMN_WIDTHS['player']}}"
        f"{name_b:<{COLUMN_WIDTHS['player']}}"
        f"{'Modifiers':<{COLUMN_WIDTHS['modifiers']}}"
        f"{'Points':<{COLUMN_WIDTHS['points']}}"
        f"{'Total':<{COLUMN_WIDTHS['total']}}"
    )
    divider = "-" * sum(COLUMN_WIDTHS.values())
    return f"{header}\n{divider}"


def render_table_row(entry: RoundLogEntry) -> str:
    if not isinstance(entry, RoundLogEntry):
        raise TypeError(f"Expected RoundLogEntry, got {type(entry).__name__}")
    return (
        f"{entry.round_number:<{COLUMN_WIDTHS['round']}}"
        f"{_format_gesture_cell(entry.gesture_a, entry.playstyle_a):<{COLUMN_WIDTHS['player']}}"
        f"{_format_gesture_cell(entry.gesture_b, entry.playstyle_b):<{COLUMN_WIDTHS['player']}}"
        f"{_format_modifiers(entry):<{COLUMN_WIDTHS['modifiers']}}"
        f"{_format_points(entry):<{COLUMN_WIDTHS['points']}}"
        f"{_format_totals(entry):<{COLUMN_WIDTHS['total']}}"
    )


def render_match_summary(scoreboard: Scoreboard) -> str:
    if not isinstance(scoreboard, Scoreboard):
        raise TypeError(f"Expected Scoreboard, got {type(scoreboard).__name__}")
    divider = "=" * sum(COLUMN_WIDTHS.values())
    winner = scoreboard.match_winner()
    if winner is None:
        return f"{divider}\nMatch still in progress."
    score_a = scoreboard.score_of(scoreboard.name_a)
    score_b = scoreboard.score_of(scoreboard.name_b)
    return f"{divider}\nWON BY: {winner}   ({scoreboard.name_a}: {score_a} | {scoreboard.name_b}: {score_b})"