from typing import Optional

from .gestures import Gesture


class MomentumTracker:
    """
    Tracks one player's Momentum charge stacks across rounds (Section 7).

    Usage per round (matches Section 8's resolution order):
      1. Call has_bonus_for(gesture) BEFORE scoring, using stacks built up
         from previous rounds.
      2. Call register_throw(gesture) AFTER scoring, to update stacks for
         the next round.
    """

    MAX_STACKS = 2
    BONUS = 1

    def __init__(self) -> None:
        self._last_gesture: Optional[Gesture] = None
        self._stacks: int = 0

    @property
    def stacks(self) -> int:
        return self._stacks

    @property
    def last_gesture(self) -> Optional[Gesture]:
        return self._last_gesture

    def has_bonus_for(self, gesture: Gesture) -> bool:
        """Whether a win with `gesture` this round earns the +1 Momentum bonus."""
        if not isinstance(gesture, Gesture):
            raise TypeError(f"Expected Gesture, got {type(gesture).__name__}")
        return self._stacks >= self.MAX_STACKS and self._last_gesture == gesture

    def register_throw(self, gesture: Gesture) -> None:
        """Update stack state after `gesture` is played this round."""
        if not isinstance(gesture, Gesture):
            raise TypeError(f"Expected Gesture, got {type(gesture).__name__}")
        if gesture == self._last_gesture:
            self._stacks = min(self.MAX_STACKS, self._stacks + 1)
        else:
            self._stacks = 0
        self._last_gesture = gesture

    def reset(self) -> None:
        """Clear all state — e.g. at the start of a new match."""
        self._last_gesture = None
        self._stacks = 0