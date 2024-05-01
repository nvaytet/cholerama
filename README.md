![cholerama_banner](https://github.com/nvaytet/cholerama/assets/39047984/4c57c612-069b-4ebc-9a20-c23e568cd007)

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

- Bacterial evolution is governed by **Conway’s Game of Life**
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
- Starting positions are randomized

<img src="https://github.com/nvaytet/cholerama/assets/39047984/a98198e6-bec5-49ed-90e9-edf8e6d6f20b" width="200" />

```Py
import numpy as np
from cholerama import helpers, Positions

AUTHOR = "YeastieBoys"  # This is your team name

class Bot:
    def __init__(self, number: int, name: str, x: int, y: int):
        self.number = number  # Mandatory: this is your number on the board
        self.name = name  # Mandatory: player name
        self.color = None  # Optional

        # If we make the pattern too sparse, it just dies quickly
        self.pattern = np.random.randint(0, 2, (12, 12))
        # The pattern can also be just an image (0=white, 1=black)
        # self.pattern = "mypattern.png"
```

### During iterations:

#### You are provided with

- Iteration number (int)
- Current board: numpy array with integer values. 0 means empty, other values correspond to players (`self.number`)

#### Spawning new cells

- You can return a set of (x, y) positions corresponding to new alive cells to be placed on the board (integers)
- 1 cell costs 1 token
- The locations for new cells on the board must be empty
- The order in which bots apply their new cells cycles every round
- The total number of additional tokens you'll receive during a round is 200

```Py
class Bot:
    ...

    def iterate(self, iteration: int, board: np.ndarray, tokens: int):
        if tokens >= 5:
            # Pick a random empty patch of size 3x3
            empty_patches = helpers.find_empty_patches(board, (3, 3))
            npatches = len(empty_patches)
            if npatches == 0:
                return None
            # Make a glider
            ind = np.random.randint(0, npatches)
            x = np.array([1, 2, 0, 1, 2]) + empty_patches[ind, 1]
            y = np.array([2, 1, 0, 0, 0]) + empty_patches[ind, 0]
            return Positions(x=x, y=y)
```

## Tips

- This is more about exploring the world of the Game of Life, rather than hardcore programming for 4 hours
- Spend time reading up about gliders, spaceships, guns, puffers, eaters, spacefillers...

#### To speed up your runs, you can

- Change the `fps`
- Change the `nthreads` (doesn’t seem to always work?)
- Run in `headless` mode

