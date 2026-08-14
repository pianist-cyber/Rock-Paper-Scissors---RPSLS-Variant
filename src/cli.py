from typing import Tuple

import utils
from src.core.gestures import Gesture
from src.core.playstyles import Playstyle
from src.models.match import Match
from src.models.player import Player

COMPUTER_NAME = "Computer"
COMPUTER_PLAYSTYLE = Playstyle.CALM  # v1: computer plays randomly/neutrally


def human_controller(player: Player) -> Tuple[Gesture, bool]:
    while True:
        raw = input(f"{player.name}, choose your gesture (Rock/Paper/Scissors/Lizard/Spock): ")
        try:
            gesture = utils.parse_gesture(raw)
            break
        except (TypeError, ValueError) as exc:
            print(exc)

    spend = False
    if player.feint.can_spend():
        raw_spend = input(f"Spend a Feint Token? ({player.feint.tokens} left) [y/N]: ").strip().lower()
        spend = raw_spend in ("y", "yes")

    return gesture, spend


def computer_controller(player: Player) -> Tuple[Gesture, bool]:
    return utils.random_gesture(), False


def prompt_playstyle(label: str) -> Playstyle:
    while True:
        raw = input(f"{label}, choose your playstyle (Rogue/Defensive/Calm): ")
        try:
            return utils.parse_playstyle(raw)
        except (TypeError, ValueError) as exc:
            print(exc)


def prompt_target_score() -> int:
    while True:
        raw = input("Choose target score (5, 10, or 25): ")
        try:
            return utils.parse_target_score(raw)
        except (TypeError, ValueError) as exc:
            print(exc)


def main() -> None:
    print("=== Rock Paper Scissors Lizard Spock — Custom Variant ===\n")

    human_name = input("Enter your name: ").strip() or "Player"
    human_playstyle = prompt_playstyle(human_name)
    target_score = prompt_target_score()

    human = Player(human_name, human_playstyle)
    computer = Player(COMPUTER_NAME, COMPUTER_PLAYSTYLE)

    match = Match(human, computer, target_score, human_controller, computer_controller)

    print()
    print(utils.render_table_header(human.name, computer.name))

    while not match.is_over():
        entry = match.play_round()
        print(utils.render_table_row(entry))

    print(utils.render_match_summary(match.scoreboard))


if __name__ == "__main__":
    main()