from pathlib import Path

from src.bots.base_bot import BaseBot

class SimulationConfig:
    """
    Configuration for a simulation experiment.
    Defines:
        - experiment name
        - the two bots that will compete
        - target score
        - number of matches to simulate
        - random seed (optional)
        - output directory for generated data

    Playstyle is intentionally NOT configured here -- per Section 4, it's
    randomized independently per player, per match, by the simulator
    itself when each match is created. Fixing it here would mean every
    match in the batch uses the same playstyle pairing, which defeats the
    purpose of logging OwnPlaystyle/OpponentPlaystyle per decision row.
    """

    def __init__(
        self,
        experiment_name: str,
        bot_a: BaseBot,
        bot_b: BaseBot,
        target_score: int,
        num_matches: int,
        seed: int | None = None,
        output_directory: str = str(
            Path(__file__).resolve().parents[2] / "data"
        )
    ) -> None:
        if not isinstance(experiment_name, str) or not experiment_name.strip():
            raise ValueError("experiment_name must be a non-empty string")
        if not isinstance(bot_a, BaseBot):
            raise TypeError(f"Expected BaseBot, got {type(bot_a).__name__}")
        if not isinstance(bot_b, BaseBot):
            raise TypeError(f"Expected BaseBot, got {type(bot_b).__name__}")
        if target_score not in (5, 10, 25):
            raise ValueError("target_score must be one of: 5, 10 or 25")
        if not isinstance(num_matches, int):
            raise TypeError("num_matches must be an integer")
        if num_matches <= 0:
            raise ValueError("num_matches must be greater than zero")
        if seed is not None and not isinstance(seed, int):
            raise TypeError("seed must be an integer or None")
        if not isinstance(output_directory, str) or not output_directory.strip():
            raise ValueError("output_directory must be a non-empty string")

        self._experiment_name = experiment_name
        self._bot_a = bot_a
        self._bot_b = bot_b
        self._target_score = target_score
        self._num_matches = num_matches
        self._seed = seed
        self._output_directory = output_directory

    @property
    def experiment_name(self) -> str:
        return self._experiment_name

    @property
    def bot_a(self) -> BaseBot:
        return self._bot_a

    @property
    def bot_b(self) -> BaseBot:
        return self._bot_b

    @property
    def target_score(self) -> int:
        return self._target_score

    @property
    def num_matches(self) -> int:
        return self._num_matches

    @property
    def seed(self) -> int | None:
        return self._seed

    @property
    def output_directory(self) -> str:
        return self._output_directory

    def __repr__(self) -> str:
        return (
            f"SimulationConfig("
            f"experiment_name={self._experiment_name!r}, "
            f"bot_a={self._bot_a.name}, "
            f"bot_b={self._bot_b.name}, "
            f"target_score={self._target_score}, "
            f"num_matches={self._num_matches}, "
            f"seed={self._seed}, "
            f"output_directory={self._output_directory!r})"
        )