import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.cli import main as run_cli  # noqa: E402


def main() -> None:
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nMatch interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()