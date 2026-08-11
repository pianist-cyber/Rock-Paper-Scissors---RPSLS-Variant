import csv
from pathlib import Path
from typing import TextIO

from simulation.config import SimulationConfig


class ExperimentLogger:
    """
    Writes information about a simulation experiment to experiments.csv.

    Responsibility:
        SimulationConfig
            ↓
        experiments.csv

    Unlike MatchLogger and DecisionLogger, this logger records
    information about the experiment itself rather than individual
    matches or rounds.

    One experiment configuration produces one row.
    """

    FIELDNAMES = (
        "experiment_name",
        "bot_a",
        "bot_b",
        "target_score",
        "num_matches",
        "seed",
        "output_directory",
    )

    def __init__(
        self,
        output_directory: str = "data",
        filename: str = "experiments.csv",
    ) -> None:
        """
        Create an ExperimentLogger.

        Parameters
        ----------
        output_directory:
            Directory where experiments.csv will be stored.

        filename:
            Name of the experiment metadata CSV file.
        """

        if not isinstance(output_directory, str):
            raise TypeError(
                "output_directory must be a string"
            )

        if not output_directory.strip():
            raise ValueError(
                "output_directory must be a non-empty string"
            )

        if not isinstance(filename, str):
            raise TypeError(
                "filename must be a string"
            )

        if not filename.strip():
            raise ValueError(
                "filename must be a non-empty string"
            )

        self._output_directory = Path(output_directory)

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._file_path = self._output_directory / filename

        self._file: TextIO | None = None
        self._writer: csv.DictWriter | None = None

    @property
    def file_path(self) -> Path:
        """Return the path of the experiment CSV file."""
        return self._file_path

    def open(self) -> None:
        """
        Open experiments.csv for appending.

        Existing experiment records are preserved.

        If the file does not exist, or exists but is empty,
        the CSV header is written.
        """

        if self._file is not None:
            raise RuntimeError(
                "ExperimentLogger is already open"
            )

        file_exists = self._file_path.exists()

        file_has_data = (
            file_exists
            and self._file_path.stat().st_size > 0
        )

        self._file = self._file_path.open(
            mode="a",
            newline="",
            encoding="utf-8",
        )

        self._writer = csv.DictWriter(
            self._file,
            fieldnames=self.FIELDNAMES,
        )

        if not file_has_data:
            self._writer.writeheader()
            self._file.flush()

    def log(self, config: SimulationConfig) -> None:
        """
        Write one SimulationConfig as one experiment record.
        """

        if not isinstance(config, SimulationConfig):
            raise TypeError(
                f"Expected SimulationConfig, "
                f"got {type(config).__name__}"
            )

        if self._writer is None or self._file is None:
            raise RuntimeError(
                "ExperimentLogger must be opened before logging"
            )

        self._writer.writerow(
            {
                "experiment_name": config.experiment_name,
                "bot_a": config.bot_a.name,
                "bot_b": config.bot_b.name,
                "target_score": config.target_score,
                "num_matches": config.num_matches,
                "seed": config.seed,
                "output_directory": config.output_directory,
            }
        )

        self._file.flush()

    def close(self) -> None:
        """Close the CSV file if it is currently open."""

        if self._file is not None:
            self._file.close()

        self._file = None
        self._writer = None

    def __enter__(self) -> "ExperimentLogger":
        """Open the logger when entering a 'with' block."""

        self.open()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """Automatically close the logger when leaving the 'with' block."""

        self.close()