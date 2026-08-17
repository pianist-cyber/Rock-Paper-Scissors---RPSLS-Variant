import random
from typing import Tuple

from src.bots.base_bot import BaseBot
from src.core.gestures import Gesture
from src.models.player import Player
from src.models.scoreboard import RoundLogEntry


class MomentumBot(BaseBot):
    """
    Tests the Momentum mechanic. Repeats its last gesture round after round
    to build and hold Momentum stacks (drawing doesn't interrupt this, since
    stacks still build through a draw). Switches to a fresh random gesture
    only after an actual loss — repeating a gesture that just lost would be
    self-defeating. Never spends Feint Tokens.
    """

    name = "MomentumBot"

    def __init__(self) -> None:
        self._lost_last_round: bool = False

    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        last_gesture = player.momentum.last_gesture
        if last_gesture is None or self._lost_last_round:
            return random.choice(list(Gesture)), False
        return last_gesture, False

    def observe_result(self, entry: RoundLogEntry, is_player_a: bool) -> None:
        own_name = entry.name_a if is_player_a else entry.name_b
        self._lost_last_round = entry.winner_name is not None and entry.winner_name != own_name

    def reset(self) -> None:
        self._lost_last_round = False