from enum import Enum


class Category(str, Enum):
    AGGRESSIVE = "Aggressive"
    DEFENSIVE = "Defensive"
    NEUTRAL = "Neutral"


class Gesture(str, Enum):
    ROCK = "Rock"
    PAPER = "Paper"
    SCISSORS = "Scissors"
    LIZARD = "Lizard"
    SPOCK = "Spock"


class RoundOutcome(str, Enum):
    WIN = "Win"
    LOSE = "Lose"
    DRAW = "Draw"


GESTURE_CATEGORY = {
    Gesture.ROCK: Category.AGGRESSIVE,
    Gesture.SCISSORS: Category.AGGRESSIVE,
    Gesture.PAPER: Category.DEFENSIVE,
    Gesture.SPOCK: Category.DEFENSIVE,
    Gesture.LIZARD: Category.NEUTRAL,
}


class GestureRules:
    """Each gesture owns its own win-condition function (Section 2)."""

    @staticmethod
    def rock_beats(other: Gesture) -> bool:
        return other in (Gesture.SCISSORS, Gesture.LIZARD)

    @staticmethod
    def paper_beats(other: Gesture) -> bool:
        return other in (Gesture.ROCK, Gesture.SPOCK)

    @staticmethod
    def scissors_beats(other: Gesture) -> bool:
        return other in (Gesture.PAPER, Gesture.LIZARD)

    @staticmethod
    def lizard_beats(other: Gesture) -> bool:
        return other in (Gesture.SPOCK, Gesture.PAPER)

    @staticmethod
    def spock_beats(other: Gesture) -> bool:
        return other in (Gesture.SCISSORS, Gesture.ROCK)

    @classmethod
    def beats(cls, gesture: Gesture, other: Gesture) -> bool:
        if not isinstance(gesture, Gesture) or not isinstance(other, Gesture):
            raise TypeError("beats() requires two Gesture values")
        checker = getattr(cls, f"{gesture.name.lower()}_beats")
        return checker(other)

    @classmethod
    def category_of(cls, gesture: Gesture) -> Category:
        if not isinstance(gesture, Gesture):
            raise TypeError(f"Expected Gesture, got {type(gesture).__name__}")
        return GESTURE_CATEGORY[gesture]

    @classmethod
    def resolve(cls, a: Gesture, b: Gesture) -> RoundOutcome:
        """Resolve gesture `a` against gesture `b` from a's perspective."""
        if a == b:
            return RoundOutcome.DRAW
        if cls.beats(a, b):
            return RoundOutcome.WIN
        return RoundOutcome.LOSE