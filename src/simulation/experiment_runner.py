from simulation.config import SimulationConfig
from simulation.simulator import Simulator
from recorders.experiment_logger import ExperimentLogger
from recorders.match_logger import MatchLogger
from recorders.decision_logger import DecisionLogger


class ExperimentRunner:
    """
    Orchestrates a complete simulation experiment.

    Responsibilities
    ----------------
    - Accept a SimulationConfig.
    - Create the Simulator.
    - Create and connect all recorders.
    - Record experiment metadata.
    - Run the configured batch of matches.
    - Stream match and decision data directly to disk.

    This class contains no game logic and no bot logic.
    It only connects the existing components together.
    """

    def __init__(self, config: SimulationConfig) -> None:
        if not isinstance(config, SimulationConfig):
            raise TypeError(
                f"Expected SimulationConfig, got {type(config).__name__}"
            )

        self._config = config
        self._simulator = Simulator(config)

    @property
    def config(self) -> SimulationConfig:
        """Return the configuration used by this experiment."""
        return self._config

    @property
    def simulator(self) -> Simulator:
        """Return the simulator used by this experiment."""
        return self._simulator

    def run(self) -> None:
        """
        Run the complete experiment.

        Data flow:

            SimulationConfig
                    |
                    v
            ExperimentLogger
                    |
                    v
                Simulator
                 /     \
                /       \
               v         v
        MatchLogger   DecisionLogger
               |         |
               v         v
          matches.csv decisions.csv

        All records are streamed directly to their respective files.
        The runner does not accumulate the generated data in memory.
        """

        output_directory = self._config.output_directory

        experiment_logger = ExperimentLogger(
            output_directory=output_directory
        )

        match_logger = MatchLogger(
            output_directory=output_directory
        )

        decision_logger = DecisionLogger(
            output_directory=output_directory
        )

        try:
            # -------------------------------------------------
            # 1. Record the experiment configuration.
            # -------------------------------------------------

            experiment_logger.open()
            experiment_logger.log(self._config)
            print("Experiment logger wrote:", experiment_logger.file_path)

            # -------------------------------------------------
            # 2. Open the match and decision recorders.
            # -------------------------------------------------

            match_logger.open()
            decision_logger.open()
            print("Match logger:", match_logger.file_path)
            print("Decision logger:", decision_logger.file_path)

            # -------------------------------------------------
            # 3. Run the simulation.
            #
            # The callbacks stream records directly into
            # the appropriate logger.
            # -------------------------------------------------

            for _summary in self._simulator.run_batch(
                on_match=match_logger.log,
                on_decision=decision_logger.log,
            ):
                print("MATCH:", _summary.match_id)
                pass

        finally:
            # -------------------------------------------------
            # 4. Always close all files.
            #
            # The finally block ensures files are closed even
            # if an exception occurs during the experiment.
            # -------------------------------------------------

            decision_logger.close()
            match_logger.close()
            experiment_logger.close()