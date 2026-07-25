from .gestures import RoundOutcome


class FeintTracker:
    """
    Tracks one player's Feint Token count and applies the downgrade-to-draw
    rule (Section 7).

    Usage per round:
      1. Player decides whether to spend a token (call spend() if so) BEFORE
         gestures are revealed.
      2. After the round is resolved, call apply_outcome() with the raw
         outcome and whether a token was spent this round.
    """

    STARTING_TOKENS = 2

    def __init__(self) -> None:
        self._tokens: int = self.STARTING_TOKENS

    @property
    def tokens(self) -> int:
        return self._tokens

    def can_spend(self) -> bool:
        return self._tokens > 0

    def spend(self) -> None:
        """Spend one token. Tokens don't refund, win, lose, or draw."""
        if self._tokens <= 0:
            raise ValueError("No feint tokens remaining")
        self._tokens -= 1

    @staticmethod
    def apply_outcome(outcome: RoundOutcome, token_spent: bool) -> RoundOutcome:
        """
        A spent token only ever affects a LOSS, downgrading it to a DRAW
        (0 points, no bonuses, no nerf penalty). WIN and DRAW are returned
        unchanged regardless of token spend.
        """
        if not isinstance(outcome, RoundOutcome):
            raise TypeError(f"Expected RoundOutcome, got {type(outcome).__name__}")
        if token_spent and outcome == RoundOutcome.LOSE:
            return RoundOutcome.DRAW
        return outcome

    def reset(self) -> None:
        """Reset to starting tokens — e.g. at the start of a new match."""
        self._tokens = self.STARTING_TOKENS