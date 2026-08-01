import random
from collections import Counter
from typing import Tuple

from bots.base_bot import BaseBot
from bots.gesture_selection import pick_counter
from core.gestures import Gesture
from models.player import Player
from models.scoreboard import RoundLogEntry


class FrequencyBot(BaseBot):
    """
    Statistical prediction bot. Tracks how often the opponent has played
    each gesture so far this match, predicts they'll play their most
    frequent gesture again, and plays a counter to it. With no history yet,
    picks randomly. Never spends Feint Tokens.
    """

    name = "FrequencyBot"

    def __init__(self) -> None:
        self._opponent_counts: Counter = Counter()

    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        if not self._opponent_counts:
            return random.choice(list(Gesture)), False
        most_common_gesture, _ = self._opponent_counts.most_common(1)[0]
        return pick_counter(most_common_gesture), False

    def observe_result(self, entry: RoundLogEntry, is_player_a: bool) -> None:
        opponent_gesture = entry.gesture_b if is_player_a else entry.gesture_a
        self._opponent_counts[opponent_gesture] += 1

    def reset(self) -> None:
        self._opponent_counts = Counter()