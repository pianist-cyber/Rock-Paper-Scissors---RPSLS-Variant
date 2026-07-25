from core.feint import FeintTracker
from core.momentum import MomentumTracker
from core.playstyles import Playstyle


class Player:
    """
    A player's identity for a match: name, chosen playstyle, Feint Tokens,
    and Momentum stacks. Does NOT hold score — that lives in Scoreboard.
    """

    def __init__(self, name: str, playstyle: Playstyle) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(playstyle, Playstyle):
            raise TypeError(f"Expected Playstyle, got {type(playstyle).__name__}")

        self._name = name
        self._playstyle = playstyle
        self._feint = FeintTracker()
        self._momentum = MomentumTracker()

    @property
    def name(self) -> str:
        return self._name

    @property
    def playstyle(self) -> Playstyle:
        return self._playstyle

    @property
    def feint(self) -> FeintTracker:
        return self._feint

    @property
    def momentum(self) -> MomentumTracker:
        return self._momentum

    def reset_for_new_match(self) -> None:
        """Reset per-match state (tokens, momentum stacks). Identity persists."""
        self._feint.reset()
        self._momentum.reset()

    def __repr__(self) -> str:
        return f"Player(name={self._name!r}, playstyle={self._playstyle.value})"