from bots.base_bot import BaseBot
from core.playstyles import Playstyle


class SimulationConfig:
    """
    Configuration for a simulation experiment.

    Defines:
        - experiment name
        - the two bots that will compete
        - their playstyles
        - target score
        - number of matches to simulate
        - random seed (optional)
        - output directory for generated data
    """

    def __init__(
        self,
        experiment_name: str,
        bot_a: BaseBot,
        bot_b: BaseBot,
        playstyle_a: Playstyle,
        playstyle_b: Playstyle,
        target_score: int,
        num_matches: int,
        seed: int | None = None,
        output_directory: str = "data",
    ) -> None:

        if not isinstance(experiment_name, str) or not experiment_name.strip():
            raise ValueError("experiment_name must be a non-empty string")

        if not isinstance(bot_a, BaseBot):
            raise TypeError(f"Expected BaseBot, got {type(bot_a).__name__}")

        if not isinstance(bot_b, BaseBot):
            raise TypeError(f"Expected BaseBot, got {type(bot_b).__name__}")

        if not isinstance(playstyle_a, Playstyle):
            raise TypeError(
                f"Expected Playstyle, got {type(playstyle_a).__name__}"
            )

        if not isinstance(playstyle_b, Playstyle):
            raise TypeError(
                f"Expected Playstyle, got {type(playstyle_b).__name__}"
            )

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
        self._playstyle_a = playstyle_a
        self._playstyle_b = playstyle_b
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
    def playstyle_a(self) -> Playstyle:
        return self._playstyle_a

    @property
    def playstyle_b(self) -> Playstyle:
        return self._playstyle_b

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
            f"playstyle_a={self._playstyle_a.value}, "
            f"playstyle_b={self._playstyle_b.value}, "
            f"target_score={self._target_score}, "
            f"num_matches={self._num_matches}, "
            f"seed={self._seed}, "
            f"output_directory={self._output_directory!r})"
        )