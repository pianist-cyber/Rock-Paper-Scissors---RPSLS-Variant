from abc import ABC, abstractmethod
from typing import Tuple

from core.gestures import Gesture
from models.player import Player
from models.scoreboard import RoundLogEntry


class BaseBot(ABC):
    """
    Shared interface every v2 bot implements.

    A BaseBot instance IS a valid PlayerController (models.match.PlayerController):
    it can be passed directly as controller_a/controller_b to Match, since
    __call__ matches Callable[[Player], Tuple[Gesture, bool]] exactly.
    No changes to core/ or models/ are required for this to work.

    Two extra hooks exist purely inside this bot framework (the simulator
    drives them, not Match):
      - observe_result(): called after each round with that round's
        RoundLogEntry, so stateful bots can remember what the opponent
        revealed (their move, playstyle, score) without needing any
        engine changes.
      - reset(): called before a new match starts, so per-match memory
        (e.g. "opponent's last move") doesn't leak between matches.
    """

    name: str = "BaseBot"

    def __call__(self, player: Player) -> Tuple[Gesture, bool]:
        return self.choose_move(player)

    @abstractmethod
    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        """
        Decide this round's (gesture, spend_feint_token).

        Must rely only on `player`'s own state (playstyle, feint tokens,
        momentum) plus whatever this bot has legitimately learned via
        observe_result() — never on directly reaching into the opponent's
        live Player object.
        """
        raise NotImplementedError

    def observe_result(self, entry: RoundLogEntry, is_player_a: bool) -> None:
        """
        Called once per round, after it's resolved, with the full
        RoundLogEntry. `is_player_a` tells this bot which side it played,
        so it can tell its own gesture/score from the opponent's.

        Default: no-op. Override in bots that need memory (Counter,
        Frequency, Balanced, ...).
        """
        return None

    def reset(self) -> None:
        """Clear any per-match memory. Default: no-op."""
        return None

    def __repr__(self) -> str:
        return f"{self.name}()"