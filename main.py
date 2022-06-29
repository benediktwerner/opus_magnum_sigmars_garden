import sys
from time import sleep

from detection import detect_board
from setup import perform_setup
from solver import Solver
from utils import mouseDown, mouseUp, moveTo

args = sys.argv
if len(args) > 2 or len(args) == 2 and not args[1].isnumeric():
    print("Usage:", args[0], "[optional: games to play]")
    exit(1)

if len(args) == 2:
    games_to_play = int(args[1])
else:
    games_to_play = 1


# Sleep at the start to allow focusing the game
for i in range(3, 0, -1):
    print(i)
    sleep(1)


setup = perform_setup()
cell_pos = setup.generate_cell_positions()

for _ in range(games_to_play):
    board = detect_board(setup)
    print("Starting solve")
    sol = Solver(board).solve()

    if not sol:
        print("No solution found")
    else:
        for x, y in reversed(sol):
            p = cell_pos[y][x]
            moveTo(p)
            sleep(0.02)
            mouseDown()
            sleep(0.02)
            mouseUp()

    sleep(0.1)
    moveTo(setup.new_game_btn_pos)
    sleep(0.1)
    mouseDown()
    sleep(0.1)
    mouseUp()
    sleep(5)
