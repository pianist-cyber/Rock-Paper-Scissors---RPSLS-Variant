import random
from typing import List

from core.gestures import Gesture, GestureRules


def counters_of(gesture: Gesture) -> List[Gesture]:
    """All gestures that beat the given gesture (always exactly 2 in RPSLS)."""
    if not isinstance(gesture, Gesture):
        raise TypeError(f"Expected Gesture, got {type(gesture).__name__}")
    return [candidate for candidate in Gesture if GestureRules.beats(candidate, gesture)]


def pick_counter(gesture: Gesture) -> Gesture:
    """Pick one gesture, at random, that beats the given gesture."""
    return random.choice(counters_of(gesture))