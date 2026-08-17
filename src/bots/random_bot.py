import random
from typing import Tuple

from src.bots.base_bot import BaseBot
from src.core.gestures import Gesture
from src.models.player import Player


class RandomBot(BaseBot):
    """
    Baseline bot. Picks one of the 5 gestures with equal probability every
    round. No memory, no prediction, never spends Feint Tokens.
    """

    name = "RandomBot"

    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        return random.choice(list(Gesture)), False