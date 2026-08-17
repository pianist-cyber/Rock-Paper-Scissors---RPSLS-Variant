import random
from typing import Optional, Tuple

from src.bots.gesture_selection import pick_counter
from src.bots.base_bot import BaseBot
from src.core.gestures import Gesture
from src.models.player import Player
from src.models.scoreboard import RoundLogEntry


class CounterBot(BaseBot):
    """
    Simple prediction bot. Remembers only the opponent's last revealed
    gesture, assumes they'll repeat it, and plays a gesture that beats that
    prediction (there are always two valid counters; one is picked at
    random). With no history yet, picks randomly. Never spends Feint
    Tokens.
    """

    name = "CounterBot"

    def __init__(self) -> None:
        self._opponent_last_gesture: Optional[Gesture] = None

    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        if self._opponent_last_gesture is None:
            return random.choice(list(Gesture)), False
        return pick_counter(self._opponent_last_gesture), False

    def observe_result(self, entry: RoundLogEntry, is_player_a: bool) -> None:
        self._opponent_last_gesture = entry.gesture_b if is_player_a else entry.gesture_a

    def reset(self) -> None:
        self._opponent_last_gesture = None