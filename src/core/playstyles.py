from enum import Enum

from .gestures import Category


class Playstyle(str, Enum):
    ROGUE = "Rogue"
    DEFENSIVE = "Defensive"
    CALM = "Calm"


class PlaystyleRules:
    """Each playstyle owns its own base win-scoring function (Section 4)."""

    @staticmethod
    def rogue_score(beaten_category: Category) -> int:
        scores = {Category.AGGRESSIVE: 2, Category.DEFENSIVE: 0, Category.NEUTRAL: 1}
        return scores[beaten_category]

    @staticmethod
    def defensive_score(beaten_category: Category) -> int:
        scores = {Category.AGGRESSIVE: 0, Category.DEFENSIVE: 2, Category.NEUTRAL: 1}
        return scores[beaten_category]

    @staticmethod
    def calm_score(beaten_category: Category) -> int:
        scores = {Category.AGGRESSIVE: 1, Category.DEFENSIVE: 1, Category.NEUTRAL: 1}
        return scores[beaten_category]

    @classmethod
    def base_win_score(cls, playstyle: Playstyle, beaten_category: Category) -> int:
        if not isinstance(playstyle, Playstyle):
            raise TypeError(f"Expected Playstyle, got {type(playstyle).__name__}")
        if not isinstance(beaten_category, Category):
            raise TypeError(f"Expected Category, got {type(beaten_category).__name__}")
        checker = getattr(cls, f"{playstyle.name.lower()}_score")
        return checker(beaten_category)