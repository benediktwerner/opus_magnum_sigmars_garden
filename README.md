# Opus Magnum Sigmar's Garden Mini Game Solver

Solver to automatically play *Sigmar's Garden*, the puzzle mini game innside *Opus Magnum*.

## Video

[![YouTube Video of the solver in action](http://img.youtube.com/vi/mLaJSjhnD54/0.jpg)](http://www.youtube.com/watch?v=mLaJSjhnD54 "Automated Sigmar's Garden (Opus Magnum Minigame) Solver")

## Usage

1. Make sure you have a recent installation of Python. Probably 3.6+ should work, 3.8+ definitely works.
2. Install requirements: `pip install -r requirements.txt`
3. Run `python main.py`
   - Pass a number to play that many games at once (otherwise it only plays one): `python main.py 25`
   - Pass `-d 0.1` (or replace `0.1` with any other number) to change the delay between clicks: `python main.py -d 0.1`. The default is `0.02` (seconds). If you are getting bad detection across the board or the board doesn't get cleared properly when it starts to solve, chances are the delay is too small for your PC and the game can't keep up.
   - Pass `--show-detection` to detect the board, display what it detected, and then exit without trying to solve: `python main.py --show-detection`. The window showing the detected board may open in the background i.e. you may have to Alt+Tab to see it.
   - You can also combine multiple options, e.g. `python main.py -d 0.1 --show-detection` or `python main.py 25 -d 0.1`
4. The solver will wait 3 seconds at the start to give you time to focus the game window
5. On the first run, you need to have a cleared board (i.e. you need to solve it manually and have no more elements on the board) to take a calibration image. The sovler will then ask you to place your mouse on a few key locations. To confirm a position, focus the message dialog that opens, move your mouse to the correct position, and confirm the dialog using the <kbd>Enter</kbd> key. After the first run, these values will be saved and won't be required on subsequent runs. If anything about your display resolution changes, you can delete the generated `positions.json` and `empty.png` files to clear the values.

If it goes out of control (i.e. clicks outside the game), you can move the mouse into the top left corner of the screen to abort it.

## How it works

### Detection

To detect the board, the solver utilizes the fact that the game highlights matching elements when clicking on an element in the bottom bar. It takes a screenshot at the start, then clicks on each elements, compares the two images, and everywhere something changed the clicked on element is present.

Credit to that idea goes to [Doublevil/SigmarsBoredom](https://github.com/Doublevil/SigmarsBoredom).

Unfortunately, the dark and light elements don't appear in the bottom bar so for those, we first do a differnece with the empty calibration board taken at the start. This, together with the already identified elements allows us to figure out where the leftover dark and light elements are. We then just take the average color in the center of those cells to figure out which one it is.

### Solver

The solver is a fairly simple brute-force backtracking solver i.e. it just tries every possible order of valid element combination until it finds one that clears the board. The only optimizations are ignoring moves which lead to situations where the number of cardinal elements and salts makes it unsolvable (i.e. when the number of cardinal elements with an odd amount left is greater than the number of salts left) or which have already been seen before (and therefore aren't solvable since we otherwise would have returned a solution and aborted when exploring them).

## License

All the code in this repository is in the public domain. Or if you prefer, you may also use it under the [MIT license](LICENSE-MIT) or [CC0 license](LICENSE-CC0).
