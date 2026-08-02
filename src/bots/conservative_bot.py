import random
from typing import List, Tuple

from bots.base_bot import BaseBot
from core.gestures import Gesture, GestureRules
from core.nerf import NerfRules
from core.playstyles import Playstyle
from models.player import Player


def _nerf_exposure(gesture: Gesture, playstyle: Playstyle) -> int:
    """
    How many of `gesture`'s two counters would trigger `playstyle`'s Nerf
    penalty if they won this round. 0 = safe even on a loss, 2 = a loss is
    guaranteed to trigger the Nerf (Rock for Rogue, Lizard for Defensive --
    Calm never hits above 0).
    """
    return sum(
        1
        for beater in Gesture
        if GestureRules.beats(beater, gesture)
        and NerfRules.triggers(playstyle, GestureRules.category_of(beater))
    )


class ConservativeBot(BaseBot):
    """
    Resource-management bot. Avoids the one gesture (if any) that would
    guarantee a Nerf penalty on a loss for its playstyle this match, then
    picks randomly among the rest. Spends a Feint Token only when the
    gesture it ends up throwing still carries real residual Nerf exposure
    -- and never spends its last token, always keeping one in reserve.
    """

    name = "ConservativeBot"

    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        candidates: List[Gesture] = [
            g for g in Gesture if _nerf_exposure(g, player.playstyle) < 2
        ]
        if not candidates:
            candidates = list(Gesture)  # safety net; never actually needed

        gesture = random.choice(candidates)
        exposure = _nerf_exposure(gesture, player.playstyle)
        spend = exposure > 0 and player.feint.tokens >= 2

        return gesture, spend