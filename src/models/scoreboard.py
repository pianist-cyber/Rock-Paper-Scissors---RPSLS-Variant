from dataclasses import dataclass
from typing import Dict, List, Optional

from core.gestures import Gesture
from core.playstyles import Playstyle
from core.round import VALID_TARGET_SCORES, RoundResult


@dataclass(frozen=True)
class RoundLogEntry:
    """One row of match history — everything a display layer needs for one round."""

    round_number: int
    name_a: str
    name_b: str
    gesture_a: Gesture
    gesture_b: Gesture
    playstyle_a: Playstyle
    playstyle_b: Playstyle
    points_a: int
    points_b: int
    total_a: int
    total_b: int
    winner_name: Optional[str]  # None for a draw
    affinity_applied: bool
    momentum_applied: bool
    nerf_triggered: bool
    token_saved: bool


class Scoreboard:
    """Owns running scores and the round-by-round log for a match between two players."""

    def __init__(self, name_a: str, name_b: str, target_score: int) -> None:
        if not isinstance(name_a, str) or not name_a.strip():
            raise ValueError("name_a must be a non-empty string")
        if not isinstance(name_b, str) or not name_b.strip():
            raise ValueError("name_b must be a non-empty string")
        if name_a == name_b:
            raise ValueError("name_a and name_b must be distinct")
        if target_score not in VALID_TARGET_SCORES:
            raise ValueError(f"target_score must be one of {VALID_TARGET_SCORES}, got {target_score}")

        self._name_a = name_a
        self._name_b = name_b
        self._target_score = target_score
        self._scores: Dict[str, int] = {name_a: 0, name_b: 0}
        self._history: List[RoundLogEntry] = []

    @property
    def target_score(self) -> int:
        return self._target_score

    @property
    def name_a(self) -> str:
        return self._name_a

    @property
    def name_b(self) -> str:
        return self._name_b

    @property
    def history(self) -> List[RoundLogEntry]:
        return list(self._history)

    def score_of(self, name: str) -> int:
        if name not in self._scores:
            raise ValueError(f"Unknown player name: {name!r}")
        return self._scores[name]

    def record_round(
        self,
        gesture_a: Gesture,
        gesture_b: Gesture,
        playstyle_a: Playstyle,
        playstyle_b: Playstyle,
        result: RoundResult,
    ) -> RoundLogEntry:
        """Apply a resolved round's deltas to running scores (clamped at 0) and log it."""
        if not isinstance(gesture_a, Gesture) or not isinstance(gesture_b, Gesture):
            raise TypeError("gesture_a and gesture_b must be Gesture values")
        if not isinstance(playstyle_a, Playstyle) or not isinstance(playstyle_b, Playstyle):
            raise TypeError("playstyle_a and playstyle_b must be Playstyle values")
        if not isinstance(result, RoundResult):
            raise TypeError(f"Expected RoundResult, got {type(result).__name__}")

        points_a, points_b = 0, 0
        winner_name: Optional[str] = None

        if result.winner == "a":
            points_a = result.winner_points
            points_b = -result.loser_penalty
            winner_name = self._name_a
        elif result.winner == "b":
            points_b = result.winner_points
            points_a = -result.loser_penalty
            winner_name = self._name_b

        self._scores[self._name_a] = max(0, self._scores[self._name_a] + points_a)
        self._scores[self._name_b] = max(0, self._scores[self._name_b] + points_b)

        entry = RoundLogEntry(
            round_number=len(self._history) + 1,
            name_a=self._name_a,
            name_b=self._name_b,
            gesture_a=gesture_a,
            gesture_b=gesture_b,
            playstyle_a=playstyle_a,
            playstyle_b=playstyle_b,
            points_a=points_a,
            points_b=points_b,
            total_a=self._scores[self._name_a],
            total_b=self._scores[self._name_b],
            winner_name=winner_name,
            affinity_applied=result.affinity_applied,
            momentum_applied=result.momentum_applied,
            nerf_triggered=result.nerf_triggered,
            token_saved=result.token_saved,
        )
        self._history.append(entry)
        return entry

    def match_winner(self) -> Optional[str]:
        """Name of the player who has reached the target score, or None if the match continues."""
        if self._scores[self._name_a] >= self._target_score:
            return self._name_a
        if self._scores[self._name_b] >= self._target_score:
            return self._name_b
        return None

    def is_match_over(self) -> bool:
        return self.match_winner() is not None