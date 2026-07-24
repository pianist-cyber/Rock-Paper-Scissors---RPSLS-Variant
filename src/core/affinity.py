from .gestures import Gesture

AFFINITY_BONUS = 1


class AffinityRules:
    """Each gesture owns the one opponent it gets a +1 Affinity Clash bonus against (Section 6)."""

    @staticmethod
    def rock_affinity_target() -> Gesture:
        return Gesture.LIZARD

    @staticmethod
    def paper_affinity_target() -> Gesture:
        return Gesture.ROCK

    @staticmethod
    def scissors_affinity_target() -> Gesture:
        return Gesture.PAPER

    @staticmethod
    def lizard_affinity_target() -> Gesture:
        return Gesture.SPOCK

    @staticmethod
    def spock_affinity_target() -> Gesture:
        return Gesture.SCISSORS

    @classmethod
    def has_affinity(cls, winning_move: Gesture, beaten_move: Gesture) -> bool:
        if not isinstance(winning_move, Gesture) or not isinstance(beaten_move, Gesture):
            raise TypeError("has_affinity() requires two Gesture values")
        checker = getattr(cls, f"{winning_move.name.lower()}_affinity_target")
        return checker() == beaten_move