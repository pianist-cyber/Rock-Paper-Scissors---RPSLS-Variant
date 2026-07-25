from dataclasses import dataclass
from typing import Optional

from .affinity import AffinityRules, AFFINITY_BONUS
from .feint import FeintTracker
from .gestures import Gesture, GestureRules, RoundOutcome
from .momentum import MomentumTracker
from .nerf import NerfRules
from .playstyles import Playstyle, PlaystyleRules

VALID_TARGET_SCORES = {5, 10, 25}


@dataclass(frozen=True)
class RoundThrow:
    """One player's inputs for a single round."""

    gesture: Gesture
    playstyle: Playstyle
    token_spent: bool = False
    had_momentum_bonus: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.gesture, Gesture):
            raise TypeError(f"Expected Gesture, got {type(self.gesture).__name__}")
        if not isinstance(self.playstyle, Playstyle):
            raise TypeError(f"Expected Playstyle, got {type(self.playstyle).__name__}")
        if not isinstance(self.token_spent, bool):
            raise TypeError(f"Expected bool for token_spent, got {type(self.token_spent).__name__}")
        if not isinstance(self.had_momentum_bonus, bool):
            raise TypeError(
                f"Expected bool for had_momentum_bonus, got {type(self.had_momentum_bonus).__name__}"
            )


@dataclass(frozen=True)
class RoundResult:
    """
    Outcome of a resolved round.

    winner_points / loser_penalty are the raw deltas to apply to each side's
    score (the caller is responsible for clamping via NerfRules.apply_penalty
    or Scoreboard's own clamp, and for updating Momentum stacks afterward).
    """

    winner: Optional[str]  # 'a', 'b', or None for a draw
    winner_points: int
    loser_penalty: int
    nerf_triggered: bool
    token_saved: bool
    affinity_applied: bool
    momentum_applied: bool


class RoundResolver:
    """Resolves a single round per Section 8's step order (steps 1-7 here; 8-9 are the caller's job)."""

    @staticmethod
    def resolve(throw_a: RoundThrow, throw_b: RoundThrow, target_score: int) -> RoundResult:
        if target_score not in VALID_TARGET_SCORES:
            raise ValueError(f"target_score must be one of {VALID_TARGET_SCORES}, got {target_score}")

        # Step 3: determine win / lose / draw from A's perspective
        outcome_a = GestureRules.resolve(throw_a.gesture, throw_b.gesture)

        # Step 4: draw ends the round immediately
        if outcome_a == RoundOutcome.DRAW:
            return RoundResult(
                winner=None, winner_points=0, loser_penalty=0,
                nerf_triggered=False, token_saved=False,
                affinity_applied=False, momentum_applied=False,
            )

        if outcome_a == RoundOutcome.WIN:
            winner_key, loser_key = "a", "b"
            winner_throw, loser_throw = throw_a, throw_b
        else:
            winner_key, loser_key = "b", "a"
            winner_throw, loser_throw = throw_b, throw_a

        # Step 5: feint-saved loss downgrades to a draw
        adjusted = FeintTracker.apply_outcome(RoundOutcome.LOSE, loser_throw.token_spent)
        if adjusted == RoundOutcome.DRAW:
            return RoundResult(
                winner=None, winner_points=0, loser_penalty=0,
                nerf_triggered=False, token_saved=True,
                affinity_applied=False, momentum_applied=False,
            )

        winning_category = GestureRules.category_of(winner_throw.gesture)
        beaten_category = GestureRules.category_of(loser_throw.gesture)

        # Step 6: Playstyle Nerf check (bonus lockout — no Affinity, no Momentum)
        if NerfRules.triggers(loser_throw.playstyle, winning_category):
            plain_points = NerfRules.plain_win_score(winner_throw.playstyle, beaten_category)
            return RoundResult(
                winner=winner_key, winner_points=plain_points,
                loser_penalty=NerfRules.PENALTY, nerf_triggered=True,
                token_saved=False, affinity_applied=False, momentum_applied=False,
            )

        # Step 7: full win scoring
        base = PlaystyleRules.base_win_score(winner_throw.playstyle, beaten_category)
        affinity = AffinityRules.has_affinity(winner_throw.gesture, loser_throw.gesture)
        momentum = winner_throw.had_momentum_bonus

        affinity_bonus = AFFINITY_BONUS if affinity else 0
        momentum_bonus = MomentumTracker.BONUS if momentum else 0

        if target_score == 5:
            total_bonus = max(affinity_bonus, momentum_bonus)
        else:
            total_bonus = affinity_bonus + momentum_bonus

        return RoundResult(
            winner=winner_key, winner_points=base + total_bonus, loser_penalty=0,
            nerf_triggered=False, token_saved=False,
            affinity_applied=affinity, momentum_applied=momentum,
        )