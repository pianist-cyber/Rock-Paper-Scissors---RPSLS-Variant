import csv
from pathlib import Path
from typing import TextIO

from simulation.simulator import MatchSummary


class MatchLogger:
    """
    Writes completed MatchSummary objects to matches.csv.

    Responsibility:
        MatchSummary
            ↓
        matches.csv

    This class does not run simulations and does not perform analysis.
    It only handles persistent storage of completed-match summaries.
    """

    FIELDNAMES = (
        "match_id",
        "bot_a",
        "bot_b",
        "winner",
        "total_rounds",
        "final_score_a",
        "final_score_b",
        "momentum_uses_a",
        "momentum_uses_b",
        "feints_used_a",
        "feints_used_b",
    )

    def __init__(
        self,
        output_directory: str = "data",
        filename: str = "matches.csv",
    ) -> None:
        if not isinstance(output_directory, str) or not output_directory.strip():
            raise ValueError(
                "output_directory must be a non-empty string"
            )

        if not isinstance(filename, str) or not filename.strip():
            raise ValueError(
                "filename must be a non-empty string"
            )

        self._output_directory = Path(output_directory)
        self._output_directory.mkdir(parents=True, exist_ok=True)

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

        If the file does not exist, the CSV header is written first.
        Existing data is preserved.
        """

        if self._file is not None:
            raise RuntimeError("MatchLogger is already open")

        file_exists = self._file_path.exists()
        file_has_data = file_exists and self._file_path.stat().st_size > 0

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

    def log(self, summary: MatchSummary) -> None:
        """
        Write one completed MatchSummary as one CSV row.
        """

        if not isinstance(summary, MatchSummary):
            raise TypeError(
                f"Expected MatchSummary, got {type(summary).__name__}"
            )

        if self._writer is None or self._file is None:
            raise RuntimeError(
                "MatchLogger must be opened before logging"
            )

        self._writer.writerow(
            {
                "match_id": summary.match_id,
                "bot_a": summary.bot_a,
                "bot_b": summary.bot_b,
                "winner": summary.winner,
                "total_rounds": summary.total_rounds,
                "final_score_a": summary.final_score_a,
                "final_score_b": summary.final_score_b,
                "momentum_uses_a": summary.momentum_uses_a,
                "momentum_uses_b": summary.momentum_uses_b,
                "feints_used_a": summary.feints_used_a,
                "feints_used_b": summary.feints_used_b,
            }
        )

        # Flush immediately so the row is actually written to disk
        # instead of remaining only in Python's file buffer.
        self._file.flush()

    def close(self) -> None:
        """Close the CSV file if it is currently open."""

        if self._file is not None:
            self._file.close()

        self._file = None
        self._writer = None

    def __enter__(self) -> "MatchLogger":
        """Allow usage with a 'with' statement."""
        self.open()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """Automatically close the file when leaving the 'with' block."""
        self.close()