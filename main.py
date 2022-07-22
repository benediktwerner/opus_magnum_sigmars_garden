import argparse
from time import sleep

from detection import detect_board
from setup import perform_setup
from solver import Solver, TimeoutException
from utils import is_invalid_board, mouseDown, mouseUp, moveTo


parser = argparse.ArgumentParser()
parser.add_argument(
    "games", help="number of games to play", type=int, default=1, nargs="?"
)
parser.add_argument(
    "-d",
    "--click-delay",
    dest="click_delay",
    help="delay between clicks",
    type=float,
    default=0.2,
    metavar="DELAY",
)
parser.add_argument(
    "--show-detection",
    help="display detected board state and exit",
    action="store_true",
)
args = parser.parse_args()

click_delay = args.click_delay
slow_click_delay = min(max(0.1, click_delay), 1)


# Sleep at the start to allow focusing the game
for i in range(3, 0, -1):
    print(i)
    sleep(1)


setup = perform_setup()
cell_pos = setup.generate_cell_positions()

for _ in range(max(1, args.games)):
    board = detect_board(setup, click_delay, args.show_detection)

    error = is_invalid_board(board)
    if error is not None:
        print()
        print("Detected board is invalid or unsolvable")
        print()
        print(error)
        print()
        print("Troubleshooting steps:")
        print("- Make sure the calibration is correct:")
        print("  - Check that empty.png shows an empty board without any elements on it")
        print("  - If the shown board isn't completely empty, delete the empty.png file, clear the board (i.e. solve it manually, if it's not already empty) and try again.")
        print("  - If the board isn't shown properly, i.e. a part of the playing area is cut off or it just doesn't show the board at all,")
        print("    delete the empty.png AND positions.json files and try again. Make sure to properly follow the instructions at the start.")
        print("- Try a higher click delay. It's possible the current delay is too fast for the game to keep up.")
        print("  The default click delay is 0.2. Try passing '-d 1' as a command line argument to the solver to use a one second delay instead.")
        print("- You can pass '--show-detection' as a command line argument to the solver to show the detected board.")
        print()
        exit(5)

    print("Starting solve")
    try:
        sol = Solver(board).solve()
        if not sol:
            print("No solution found")
    except TimeoutException:
        print("Timed out. Took too long to find a solution. Moving on.")
        sol = None

    if sol:
        for x, y in reversed(sol):
            p = cell_pos[y][x]
            moveTo(p)
            sleep(click_delay)
            mouseDown()
            sleep(click_delay)
            mouseUp()

    sleep(slow_click_delay)
    moveTo(setup.new_game_btn_pos)
    sleep(slow_click_delay)
    mouseDown()
    sleep(slow_click_delay)
    mouseUp()
    sleep(5)
