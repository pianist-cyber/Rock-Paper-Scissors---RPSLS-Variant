import random
from dataclasses import dataclass
from typing import Callable, Optional, Iterator 

from bots.base_bot import BaseBot
from core.playstyles import Playstyle
from core.feint import FeintTracker
from models.match import Match
from models.player import Player
from models.scoreboard import RoundLogEntry
from simulation.config import SimulationConfig


# Cache once instead of rebuilding list(Playstyle) every match.
_PLAYSTYLES: tuple[Playstyle, ...] = tuple(Playstyle)


@dataclass(frozen=True)
class MatchSummary:
    """
    One completed match.

    This maps directly to one row of matches.csv.
    """

    match_id: str

    bot_a: str
    bot_b: str

    winner: str

    total_rounds: int

    final_score_a: int
    final_score_b: int

    momentum_uses_a: int
    momentum_uses_b: int

    feints_used_a: int
    feints_used_b: int


@dataclass(frozen=True)
class DecisionRecord:
    """
    One player's decision during one round.

    This maps directly to one row of decisions.csv.
    Every round therefore produces exactly two DecisionRecords.
    """

    match_id: str
    round_number: int

    acting_bot: str
    opponent_bot: str

    previous_own_move: Optional[str]
    previous_opponent_move: Optional[str]

    own_momentum: int
    opponent_momentum: int

    own_feints_remaining: int
    opponent_feints_remaining: int

    own_score: int
    opponent_score: int

    own_playstyle: str
    opponent_playstyle: str

    selected_move: str

    # Win / Lose / Draw
    round_result: str


class Simulator:
    """
    Executes large batches of matches between two bots.

    Design goals
    ------------
    • Random playstyles every match.
    • Deterministic experiments when a seed is supplied.
    • Constant memory usage.
    • Independent bot memory per match.
    • Completely independent of CSV/logging implementation.
    """

    def __init__(self, config: SimulationConfig) -> None:

        if not isinstance(config, SimulationConfig):
            raise TypeError(
                f"Expected SimulationConfig, got {type(config).__name__}"
            )

        self._config = config

        # Keeps experiment IDs deterministic.
        self._match_counter = 0

        # Dedicated RNG.
        #
        # Never seed or use the global random module.
        # This keeps simulations reproducible without affecting
        # randomness elsewhere in the project.
        self._rng = random.Random(config.seed)

    @property
    def config(self) -> SimulationConfig:
        return self._config

    def _next_match_id(self) -> str:
        """Return the next unique match identifier."""

        self._match_counter += 1

        return (
            f"{self._config.experiment_name}"
            f"-{self._match_counter:06d}"
        )

    def _random_playstyle(self) -> Playstyle:
        """
        Choose a playstyle uniformly at random.

        Called once per player, per match.
        """

        return self._rng.choice(_PLAYSTYLES)

    @staticmethod
    def _outcome_for(
        entry: RoundLogEntry,
        *,
        is_player_a: bool,
    ) -> str:
        """
        Convert the round winner into the acting player's perspective.

        Returns:
            "Win"
            "Lose"
            "Draw"
        """

        own_name = entry.name_a if is_player_a else entry.name_b

        if entry.winner_name is None:
            return "Draw"

        return "Win" if entry.winner_name == own_name else "Lose"

    @staticmethod
    def _make_decision_record(
        *,
        match_id: str,
        entry: RoundLogEntry,
        acting_bot: BaseBot,
        opponent_bot: BaseBot,
        own_previous_move,
        opponent_previous_move,
        own_momentum: int,
        opponent_momentum: int,
        own_feints: int,
        opponent_feints: int,
        own_score: int,
        opponent_score: int,
        own_playstyle: Playstyle,
        opponent_playstyle: Playstyle,
        selected_move,
        is_player_a: bool,
    ) -> DecisionRecord:
        """
        Build one DecisionRecord.

        Centralising this avoids maintaining two almost-identical
        constructors for Player A and Player B.
        """

        return DecisionRecord(
            match_id=match_id,
            round_number=entry.round_number,

            acting_bot=acting_bot.name,
            opponent_bot=opponent_bot.name,

            previous_own_move=(
                own_previous_move.value
                if own_previous_move is not None
                else None
            ),

            previous_opponent_move=(
                opponent_previous_move.value
                if opponent_previous_move is not None
                else None
            ),

            own_momentum=own_momentum,
            opponent_momentum=opponent_momentum,

            own_feints_remaining=own_feints,
            opponent_feints_remaining=opponent_feints,

            own_score=own_score,
            opponent_score=opponent_score,

            own_playstyle=own_playstyle.value,
            opponent_playstyle=opponent_playstyle.value,

            selected_move=selected_move.value,

            round_result=Simulator._outcome_for(
                entry,
                is_player_a=is_player_a,
            ),
        )
    def run_match(
        self,
        on_decision: Optional[Callable[[DecisionRecord], None]] = None,
    ) -> MatchSummary:
        """
        Run one complete match.

        DecisionRecord objects are streamed immediately through the
        callback as each round completes. Only the MatchSummary is kept
        until the end of the match.
        """

        bot_a = self._config.bot_a
        bot_b = self._config.bot_b

        # Reset per-match bot memory.
        bot_a.reset()
        bot_b.reset()

        playstyle_a = self._random_playstyle()
        playstyle_b = self._random_playstyle()

        # Scoreboard requires distinct player names.
        player_a = Player(
            name=f"{bot_a.name}_A",
            playstyle=playstyle_a,
        )

        player_b = Player(
            name=f"{bot_b.name}_B",
            playstyle=playstyle_b,
        )

        match = Match(
            player_a=player_a,
            player_b=player_b,
            target_score=self._config.target_score,
            controller_a=bot_a,
            controller_b=bot_b,
        )

        match_id = self._next_match_id()

        momentum_uses_a = 0
        momentum_uses_b = 0

        while not match.is_over():

            # -----------------------------
            # Snapshot state BEFORE round.
            # This is exactly the information
            # the acting bot had available
            # when making its decision.
            # -----------------------------

            previous_move_a = player_a.momentum.last_gesture
            previous_move_b = player_b.momentum.last_gesture

            momentum_a = player_a.momentum.stacks
            momentum_b = player_b.momentum.stacks

            feints_a = player_a.feint.tokens
            feints_b = player_b.feint.tokens

            score_a = match.scoreboard.score_of(player_a.name)
            score_b = match.scoreboard.score_of(player_b.name)

            entry = match.play_round()

            # Track actual Momentum bonus usage.
            if entry.momentum_applied:

                if entry.winner_name == player_a.name:
                    momentum_uses_a += 1

                elif entry.winner_name == player_b.name:
                    momentum_uses_b += 1

            if on_decision is not None:

                decision_a = self._make_decision_record(
                    match_id=match_id,
                    entry=entry,
                    acting_bot=bot_a,
                    opponent_bot=bot_b,
                    own_previous_move=previous_move_a,
                    opponent_previous_move=previous_move_b,
                    own_momentum=momentum_a,
                    opponent_momentum=momentum_b,
                    own_feints=feints_a,
                    opponent_feints=feints_b,
                    own_score=score_a,
                    opponent_score=score_b,
                    own_playstyle=playstyle_a,
                    opponent_playstyle=playstyle_b,
                    selected_move=entry.gesture_a,
                    is_player_a=True,
                )

                decision_b = self._make_decision_record(
                    match_id=match_id,
                    entry=entry,
                    acting_bot=bot_b,
                    opponent_bot=bot_a,
                    own_previous_move=previous_move_b,
                    opponent_previous_move=previous_move_a,
                    own_momentum=momentum_b,
                    opponent_momentum=momentum_a,
                    own_feints=feints_b,
                    opponent_feints=feints_a,
                    own_score=score_b,
                    opponent_score=score_a,
                    own_playstyle=playstyle_b,
                    opponent_playstyle=playstyle_a,
                    selected_move=entry.gesture_b,
                    is_player_a=False,
                )

                on_decision(decision_a)
                on_decision(decision_b)

                # Allow both bots to observe the completed round and update
                # any internal memory they maintain (frequency counts,
                # opponent modelling, etc.).
                bot_a.observe_result(entry, is_player_a=True)
                bot_b.observe_result(entry, is_player_a=False)

            # ---------------------------------------------------------
            # Match complete.
            # Build the final summary returned to the caller.
            # ---------------------------------------------------------

            winner_name = match.winner()

            if winner_name == player_a.name:
                winner = bot_a.name
            elif winner_name == player_b.name:
                winner = bot_b.name
            else:
                raise RuntimeError(
                    "Match finished without a valid winner."
                )

            feints_used_a = (
                FeintTracker.STARTING_TOKENS
                - player_a.feint.tokens
            )

            feints_used_b = (
                FeintTracker.STARTING_TOKENS
                - player_b.feint.tokens
            )

            summary = MatchSummary(
                match_id=match_id,

                bot_a=bot_a.name,
                bot_b=bot_b.name,

                winner=winner,

                total_rounds=len(match.scoreboard.history),

                final_score_a=match.scoreboard.score_of(player_a.name),
                final_score_b=match.scoreboard.score_of(player_b.name),

                momentum_uses_a=momentum_uses_a,
                momentum_uses_b=momentum_uses_b,

                feints_used_a=feints_used_a,
                feints_used_b=feints_used_b,
            )

            return summary

    def run_batch(
        self,
        on_match: Optional[Callable[[MatchSummary], None]] = None,
        on_decision: Optional[Callable[[DecisionRecord], None]] = None,
    ) -> Iterator[MatchSummary]:
        """
        Run the configured number of matches.

        This method is intentionally a generator.

        Instead of creating a large list containing every MatchSummary,
        it yields one summary at a time. This allows a future recorder
        to write each match to disk and immediately discard it from
        memory.

        DecisionRecords are already streamed through on_decision and
        are never accumulated by the simulator.

        Parameters
        ----------
        on_match:
            Optional callback called once after each match completes.

        on_decision:
            Optional callback called twice per round:
            once for Player A and once for Player B.

        Yields
        ------
        MatchSummary
            The summary of each completed match.
        """

        for _ in range(self._config.num_matches):

            summary = self.run_match(
                on_decision=on_decision
            )

            if on_match is not None:
                on_match(summary)

            yield summary