import random
from collections import Counter
from typing import Optional, Tuple

from src.bots.base_bot import BaseBot
from src.bots.conservative_bot import _nerf_exposure
from src.core.gestures import Gesture, GestureRules, RoundOutcome
from src.models.player import Player
from src.models.scoreboard import RoundLogEntry

WIN_WEIGHT = 2.0
LOSE_WEIGHT = -2.0
MOMENTUM_BONUS_WEIGHT = 1.0
MOMENTUM_BUILDING_WEIGHT = 0.5
BASE_RISK_WEIGHT = 1.0
POSITION_AHEAD_MULTIPLIER = 1.5
POSITION_BEHIND_MULTIPLIER = 0.5
FEINT_AVAILABLE_DISCOUNT = 0.5


class BalancedBot(BaseBot):
    """
    Strongest handcrafted bot. Scores every legal gesture on a weighted
    function combining:
      - predicted winning chance, from the opponent's most frequent
        revealed move so far,
      - Momentum (repeating a 2-stack charged gesture, or building toward
        one),
      - Nerf risk for its own playstyle this match (reuses
        ConservativeBot's exposure metric),
      - how far ahead/behind it is on score (plays safer when ahead,
        gambles more when behind),
      - Feint Token availability (a token in reserve discounts risk,
        since a bad round can be insured against).

    Picks the highest-scoring gesture; ties broken randomly. Unlike
    ConservativeBot, it will spend its LAST token too if the chosen
    gesture still carries residual risk -- it optimizes for expected
    value rather than hoarding tokens.
    """

    name = "BalancedBot"

    def __init__(self) -> None:
        self._opponent_counts: Counter = Counter()
        self._own_score: int = 0
        self._opponent_score: int = 0

    def _predicted_opponent_move(self) -> Optional[Gesture]:
        if not self._opponent_counts:
            return None
        gesture, _ = self._opponent_counts.most_common(1)[0]
        return gesture

    def _score_candidate(self, candidate: Gesture, player: Player) -> float:
        score = 0.0

        predicted = self._predicted_opponent_move()
        if predicted is not None:
            outcome = GestureRules.resolve(candidate, predicted)
            if outcome == RoundOutcome.WIN:
                score += WIN_WEIGHT
            elif outcome == RoundOutcome.LOSE:
                score += LOSE_WEIGHT

        if player.momentum.has_bonus_for(candidate):
            score += MOMENTUM_BONUS_WEIGHT
        elif player.momentum.last_gesture == candidate:
            score += MOMENTUM_BUILDING_WEIGHT

        exposure = _nerf_exposure(candidate, player.playstyle)
        if exposure > 0:
            score_diff = self._own_score - self._opponent_score
            if score_diff > 0:
                position_multiplier = POSITION_AHEAD_MULTIPLIER
            elif score_diff < 0:
                position_multiplier = POSITION_BEHIND_MULTIPLIER
            else:
                position_multiplier = 1.0

            feint_multiplier = FEINT_AVAILABLE_DISCOUNT if player.feint.tokens > 0 else 1.0
            risk_penalty = exposure * BASE_RISK_WEIGHT * position_multiplier * feint_multiplier
            score -= risk_penalty

        return score

    def choose_move(self, player: Player) -> Tuple[Gesture, bool]:
        scores = {g: self._score_candidate(g, player) for g in Gesture}
        best_score = max(scores.values())
        best_candidates = [g for g, s in scores.items() if s == best_score]
        gesture = random.choice(best_candidates)

        exposure = _nerf_exposure(gesture, player.playstyle)
        spend = exposure > 0 and player.feint.tokens > 0

        return gesture, spend

    def observe_result(self, entry: RoundLogEntry, is_player_a: bool) -> None:
        opponent_gesture = entry.gesture_b if is_player_a else entry.gesture_a
        self._opponent_counts[opponent_gesture] += 1
        self._own_score = entry.total_a if is_player_a else entry.total_b
        self._opponent_score = entry.total_b if is_player_a else entry.total_a

    def reset(self) -> None:
        self._opponent_counts = Counter()
        self._own_score = 0
        self._opponent_score = 0