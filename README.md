# Opus Magnum Sigmar's Garden Mini Game Solver

Solver to automatically play the *Sigmar's Garden* mini game in the *Opus Magnum* game.

## Video

[![YouTube Video of the solver in action](http://img.youtube.com/vi/mLaJSjhnD54/0.jpg)](http://www.youtube.com/watch?v=mLaJSjhnD54 "Automated Sigmar's Garden (Opus Magnum Minigame) Solver")

## Usage

1. Make sure you have a recent installation of Python. Probably 3.6+ should work, 3.8+ definitely works.
2. Install requirements: `pip install -r requirements.txt`
3. Run `python main.py`
   - You can pass a number to play that many games at once (otherwise it only plays one): `python main.py 25`
4. The solver will wait 3 seconds at the start to give you time to focus the game window
5. On the first run, you need to have a cleared board to take a calibration image. The sovler will then ask you to place your mouse on a few key locations. To confirm a position, focus the message dialog that opens, move your mouse to the correct position, and confirm the dialog using the <kbd>Enter</kbd> key. After the first run, these values will be saved and won't be required on subsequent runs. If anything about your display resolution changes, you can delete the generated `positions.json` and `empty.png` files to clear the values.

## How it works

### Detection

To detect the board, the solver utilizes the fact that the game highlights matching elements when clicking on an element in the bottom bar. It takes a screenshot at the start, then clicks on each elements, compares the two images, and everywhere something changed the clicked on element is present.

Unfortunately, the dark and light elements don't appear in the bottom bar so for those, we first do a differnece with the empty calibration board taken at the start. This, together with the already identified elements allows us to figure out where the leftover dark and light elements are. We then just take the average color in the center of those cells to figure out which one it is.

### Solver

The solver is just a very simple brute-force backtracking solver. The only optimization is aborting the search when the number of cardinal elements and salts makes it unsolvable, i.e. when the number of cardinal elements with an odd amount left is greated than the number of salts left.

The game is simple enough that even this very basic and inefficient implementation in Python is quick enough to solve most boards. For difficult boards, the solver just restarts after visiting 1M nodes.
