from .gestures import Category
from .playstyles import Playstyle, PlaystyleRules


class NerfRules:
    """Each playstyle owns its own penalty-trigger function (Section 5)."""

    PENALTY = 1

    @staticmethod
    def rogue_takes_penalty(winning_category: Category) -> bool:
        return winning_category == Category.DEFENSIVE

    @staticmethod
    def defensive_takes_penalty(winning_category: Category) -> bool:
        return winning_category == Category.AGGRESSIVE

    @staticmethod
    def calm_takes_penalty(winning_category: Category) -> bool:
        return False

    @classmethod
    def triggers(cls, loser_playstyle: Playstyle, winning_category: Category) -> bool:
        """
        Whether the Section 5 penalty applies to the losing player this round.
        `winning_category` is the category of the gesture that WON the round.
        """
        if not isinstance(loser_playstyle, Playstyle):
            raise TypeError(f"Expected Playstyle, got {type(loser_playstyle).__name__}")
        if not isinstance(winning_category, Category):
            raise TypeError(f"Expected Category, got {type(winning_category).__name__}")
        checker = getattr(cls, f"{loser_playstyle.name.lower()}_takes_penalty")
        return checker(winning_category)

    @classmethod
    def apply_penalty(cls, current_score: int) -> int:
        """Deduct the penalty from the loser's score, clamped at 0."""
        if current_score < 0:
            raise ValueError(f"current_score cannot be negative, got {current_score}")
        return max(0, current_score - cls.PENALTY)

    @classmethod
    def plain_win_score(cls, winner_playstyle: Playstyle, beaten_category: Category) -> int:
        """
        Winner's score on a nerf round: base playstyle points only.
        No Affinity Clash, no Momentum — the Section 5 bonus lockout.
        """
        return PlaystyleRules.base_win_score(winner_playstyle, beaten_category)