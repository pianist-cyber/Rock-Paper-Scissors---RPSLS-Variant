import csv
from pathlib import Path
from typing import TextIO

from simulation.simulator import DecisionRecord


class DecisionLogger:
    """
    Writes DecisionRecord objects to decisions.csv.

    Responsibility:
        DecisionRecord
            ↓
        decisions.csv

    One DecisionRecord represents one bot's decision in one round.

    Therefore:
        1 round  →  2 DecisionRecords
        1 match   →  multiple DecisionRecords
        N matches →  potentially millions of rows

    The logger writes each record immediately instead of accumulating
    records in memory.
    """

    FIELDNAMES = (
        "match_id",
        "round_number",
        "acting_bot",
        "opponent_bot",
        "previous_own_move",
        "previous_opponent_move",
        "own_momentum",
        "opponent_momentum",
        "own_feints_remaining",
        "opponent_feints_remaining",
        "own_score",
        "opponent_score",
        "own_playstyle",
        "opponent_playstyle",
        "selected_move",
        "round_result",
    )

    def __init__(
        self,
        output_directory: str = "data",
        filename: str = "decisions.csv",
    ) -> None:
        """
        Create a DecisionLogger.

        Parameters
        ----------
        output_directory:
            Directory where the CSV file will be stored.

        filename:
            Name of the CSV file.
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

        # Create the directory if it does not already exist.
        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._file_path = self._output_directory / filename

        self._file: TextIO | None = None
        self._writer: csv.DictWriter | None = None

    @property
    def file_path(self) -> Path:
        """Return the path of the CSV file being written."""
        return self._file_path

    def open(self) -> None:
        """
        Open the CSV file for appending.

        Existing data is preserved.

        If the file does not exist, or exists but is empty,
        the CSV header is written.
        """

        if self._file is not None:
            raise RuntimeError(
                "DecisionLogger is already open"
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

    def log(self, record: DecisionRecord) -> None:
        """
        Write one DecisionRecord as one row in decisions.csv.
        """

        if not isinstance(record, DecisionRecord):
            raise TypeError(
                f"Expected DecisionRecord, "
                f"got {type(record).__name__}"
            )

        if self._writer is None or self._file is None:
            raise RuntimeError(
                "DecisionLogger must be opened before logging"
            )

        self._writer.writerow(
            {
                "match_id": record.match_id,
                "round_number": record.round_number,
                "acting_bot": record.acting_bot,
                "opponent_bot": record.opponent_bot,
                "previous_own_move": record.previous_own_move,
                "previous_opponent_move": (
                    record.previous_opponent_move
                ),
                "own_momentum": record.own_momentum,
                "opponent_momentum": record.opponent_momentum,
                "own_feints_remaining": (
                    record.own_feints_remaining
                ),
                "opponent_feints_remaining": (
                    record.opponent_feints_remaining
                ),
                "own_score": record.own_score,
                "opponent_score": record.opponent_score,
                "own_playstyle": record.own_playstyle,
                "opponent_playstyle": (
                    record.opponent_playstyle
                ),
                "selected_move": record.selected_move,
                "round_result": record.round_result,
            }
        )

        # Immediately push the row to the file buffer.
        self._file.flush()

    def close(self) -> None:
        """
        Close the CSV file.

        Safe to call even if the logger is already closed.
        """

        if self._file is not None:
            self._file.close()

        self._file = None
        self._writer = None

    def __enter__(self) -> "DecisionLogger":
        """
        Open the logger when entering a 'with' block.
        """

        self.open()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """
        Automatically close the logger when leaving a 'with' block.
        """

        self.close()