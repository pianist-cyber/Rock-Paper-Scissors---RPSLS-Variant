from pathlib import Path

from src.simulation.config import SimulationConfig
from src.simulation.experiment_runner import ExperimentRunner

from src.bots.random_bot import RandomBot
from src.bots.counter_bot import CounterBot

# Project root:
# Rock-Paper-Scissors---RPSLS-Variant/
PROJECT_ROOT = Path(__file__).resolve().parent

# The project's actual data directory.
DATA_DIRECTORY = PROJECT_ROOT / "data"  

def main() -> None:
    """
    Entry point for running a simulation experiment.

    This first experiment is intentionally tiny.
    We are testing the complete simulation pipeline before
    generating large amounts of data.
    """

    config = SimulationConfig(
        experiment_name="random_vs_counter_test",
        bot_a=RandomBot(),
        bot_b=CounterBot(),
        target_score=10,
        num_matches=5,
        seed=12345,
        output_directory=str(DATA_DIRECTORY)  # Use the actual data directory,
    )

    runner = ExperimentRunner(config)

    runner.run()

    print("Experiment completed successfully.")
    print(f"Experiment: {config.experiment_name}")
    print(f"Matches simulated: {config.num_matches}")
    print(f"Output directory: {config.output_directory}")


if __name__ == "__main__":
    main()