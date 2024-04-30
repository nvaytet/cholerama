![cholerama](https://github.com/nvaytet/cholerama/assets/39047984/dca39008-ae9d-47c7-8965-ac463bbb2cb5)

# cholerama

Competitive multiplayer game of life

## TL;DR

- [Create a new repository from the template](https://github.com/new?template_name=germ_bot&template_owner=nvaytet).
- `conda create -n <NAME> -c conda-forge python=3.10.*`
- `conda activate <NAME>`
- `git clone https://github.com/nvaytet/cholerama`
- `git clone https://github.com/<USERNAME>/<MYBOTNAME>_bot.git`
- `cd cholerama/`
- `python -m pip install -e .`
- `cd run/`
- `ln -s ../../<MYBOTNAME>_bot .`
- `python play.py`

## Game rules

### Goal

Conquer the largest surface on the board

### During a round:

- Bacterial evolution is governed by Conway’s Game of Life
- Begin on a small patch of board (36x36) with 100 cells
- Run 4000 iterations
- Winner is the one with most alive cells at the end

### Conway's Game of Life rules:

1. Any live cell with fewer than two live neighbors dies (underpopulation)
1. Any live cell with two or three live neighbors lives
1. Any live cell with more than three live neighbors dies (overpopulation)
1. Any dead cell with exactly three live neighbors spontaneously comes to life
1. **Multiplayer**: the cell that comes to life takes the value of most common neighbor

### Tokens:

- You start the game with 100 tokens
- 1 token = 1 cell
- Populate your 36x36 patch as you wish
- You get to keep the extra tokens
- Every iteration, you are free to place any number of tokens on an empty space on the board (you must still be alive)
- Every 20 iterations, you receive an additional token (if you are still alive)
- This equates to 200 additional tokens during a round

### Scoring:

- Points given at the end of a round are the number of alive cells a player still has
- Bonus prize for peak board coverage reached over the course of the tournament

### Tournament:

- Run as many rounds as there are players

## The Bot

### At the start of the game

- Pick a name
- Pick a color (optional)
- Create a pattern with your 100 tokens: numpy array of 0s and 1s (at most 36x36 in size) or a path to an image (white = 0, black = 1)

<img src="https://github.com/nvaytet/cholerama/assets/39047984/a98198e6-bec5-49ed-90e9-edf8e6d6f20b" width="200" />

### During iterations:

#### You are provided with

- Iteration number (int)
- Current board: numpy array with integer values. 0 means empty, other values correspond to players (`self.number`)

#### Spawning new cells

- You can return a set of (x, y) positions corresponding to new alive cells to be placed on the board (integers)
- The locations for new cells on the board must be empty
- The order in which bots apply their new cells cycles every round

## Tips

- This is more about exploring the world of the Game of Life, rather than hardcore programming for 4 hours
- Spend time reading up about gliders, spaceships, guns, puffers, eaters, spacefillers...

#### To speed up your runs, you can

- Change the `fps`
- Change the `nthreads` (doesn’t seem to always work?)
- Run in `headless` mode

