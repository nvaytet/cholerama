# cholerama

Competitive multiplayer game of life

## TL;DR

- Create a new repository from the [template](https://github.com/new?template_name=germ_bot&template_owner=nvaytet).
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
1. Multiplayer: the cell that comes to life takes the value of most common neighbor

### Tokens:

- You start the game with 100 tokens
- 1 token = 1 cell
- Populate your 36x36 patch as you wish
- You get to keep the extra tokens
- Every iteration, you are free to place any number of tokens on an empty space on the board (you must still be alive)
- Every 5 iterations, you receive an additional token (if you are still alive)
