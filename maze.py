"""Grid helpers and DFS (recursive-backtracker) maze generation."""
import random
from config import *
from ds import Stack


def empty_grid(rows=ROWS, cols=COLS, fill=NORMAL):
    """2D array (list of lists). Border cells are walls, inside is `fill`."""
    g = [[fill] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r in (0, rows - 1) or c in (0, cols - 1):
                g[r][c] = WALL
    return g


def generate_maze_steps(grid, rng=random):
    """DFS maze generation with BACKTRACKING. Starts with all walls, carves passages.
    Generator: yields each newly opened cell so the UI can animate it."""
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = WALL
    grid[1][1] = NORMAL
    stack = Stack()                                   # explicit stack = recursion made visible
    stack.push((1, 1))
    yield (1, 1)
    while not stack.is_empty():
        r, c = stack.peek()
        options = [(r + dr, c + dc, dr, dc) for dr, dc in ((-2, 0), (0, 2), (2, 0), (0, -2))
                   if 0 < r + dr < rows - 1 and 0 < c + dc < cols - 1 and grid[r + dr][c + dc] == WALL]
        if options:                                   # go deeper: carve wall between + next cell
            nr, nc, dr, dc = rng.choice(options)
            grid[r + dr // 2][c + dc // 2] = NORMAL
            grid[nr][nc] = NORMAL
            yield (r + dr // 2, c + dc // 2)
            yield (nr, nc)
            stack.push((nr, nc))
        else:                                         # dead end: BACKTRACK
            stack.pop()


def finish_maze(grid, with_terrain=True, rng=random):
    """Make the perfect maze more interesting: add loops (so paths differ) and terrain (weights)."""
    rows, cols = len(grid), len(grid[0])
    for _ in range(rows * cols // 25):                # knock down some walls -> multiple routes
        r, c = rng.randrange(1, rows - 1), rng.randrange(1, cols - 1)
        if grid[r][c] == WALL and ((grid[r - 1][c] != WALL and grid[r + 1][c] != WALL) or
                                   (grid[r][c - 1] != WALL and grid[r][c + 1] != WALL)):
            grid[r][c] = NORMAL
    if with_terrain:
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] == NORMAL and rng.random() < 0.18:
                    grid[r][c] = rng.choices([MUD, WATER, MOUNTAIN], [5, 3, 2])[0]
    grid[1][1] = grid[rows - 2][cols - 2] = NORMAL
    return (1, 1), (rows - 2, cols - 2)               # default Start and End
