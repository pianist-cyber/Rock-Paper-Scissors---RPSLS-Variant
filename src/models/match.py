from typing import Callable, Optional, Tuple

from core.gestures import Gesture
from core.round import RoundResolver, RoundThrow
from models.player import Player
from models.scoreboard import RoundLogEntry, Scoreboard

PlayerController = Callable[[Player], Tuple[Gesture, bool]]


class Match:
    """Runs a full match: repeatedly resolves rounds until one player reaches the target score."""

    def __init__(
        self,
        player_a: Player,
        player_b: Player,
        target_score: int,
        controller_a: PlayerController,
        controller_b: PlayerController,
    ) -> None:
        if not isinstance(player_a, Player) or not isinstance(player_b, Player):
            raise TypeError("player_a and player_b must be Player instances")
        if not callable(controller_a) or not callable(controller_b):
            raise TypeError("controller_a and controller_b must be callable")

        self._player_a = player_a
        self._player_b = player_b
        self._controller_a = controller_a
        self._controller_b = controller_b
        self._scoreboard = Scoreboard(player_a.name, player_b.name, target_score)

    @property
    def scoreboard(self) -> Scoreboard:
        return self._scoreboard

    @property
    def player_a(self) -> Player:
        return self._player_a

    @property
    def player_b(self) -> Player:
        return self._player_b

    def is_over(self) -> bool:
        return self._scoreboard.is_match_over()

    def winner(self) -> Optional[str]:
        return self._scoreboard.match_winner()

    def play_round(self) -> RoundLogEntry:
        """Resolve a single round: gather choices, spend tokens, score it, update momentum."""
        if self.is_over():
            raise RuntimeError("Match already has a winner; no further rounds can be played")

        gesture_a, spend_a = self._controller_a(self._player_a)
        gesture_b, spend_b = self._controller_b(self._player_b)

        if not isinstance(gesture_a, Gesture) or not isinstance(gesture_b, Gesture):
            raise TypeError("controllers must return a Gesture as the first element")
        if not isinstance(spend_a, bool) or not isinstance(spend_b, bool):
            raise TypeError("controllers must return a bool as the second element")

        token_spent_a = spend_a and self._player_a.feint.can_spend()
        if token_spent_a:
            self._player_a.feint.spend()

        token_spent_b = spend_b and self._player_b.feint.can_spend()
        if token_spent_b:
            self._player_b.feint.spend()

        had_momentum_a = self._player_a.momentum.has_bonus_for(gesture_a)
        had_momentum_b = self._player_b.momentum.has_bonus_for(gesture_b)

        throw_a = RoundThrow(
            gesture=gesture_a, playstyle=self._player_a.playstyle,
            token_spent=token_spent_a, had_momentum_bonus=had_momentum_a,
        )
        throw_b = RoundThrow(
            gesture=gesture_b, playstyle=self._player_b.playstyle,
            token_spent=token_spent_b, had_momentum_bonus=had_momentum_b,
        )

        result = RoundResolver.resolve(throw_a, throw_b, self._scoreboard.target_score)

        entry = self._scoreboard.record_round(
            gesture_a, gesture_b, self._player_a.playstyle, self._player_b.playstyle, result
        )

        self._player_a.momentum.register_throw(gesture_a)
        self._player_b.momentum.register_throw(gesture_b)

        return entry

    def play_to_completion(self, max_rounds: int = 1000) -> str:
        """Play rounds until someone wins. Returns the winner's name."""
        rounds_played = 0
        while not self.is_over():
            if rounds_played >= max_rounds:
                raise RuntimeError(f"Match exceeded {max_rounds} rounds without a winner")
            self.play_round()
            rounds_played += 1

        winner = self.winner()
        assert winner is not None, "Game finished without a winner"
        return winner