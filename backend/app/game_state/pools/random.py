import random

from app.game_state.BoardState import BoardData, Cell, Position

from .base import Pool

MAX_ATTEMPTS = 200


class RandomPool(Pool):
    def __init__(self, size: int, min_walls: int, max_walls: int) -> None:
        self.size = size
        self.min_walls = min_walls
        self.max_walls = max_walls

    def generate(self, seed: int) -> BoardData:
        rng = random.Random(seed)
        board = self._candidate(rng)
        attempts = 1

        while not board.is_connected() and attempts < MAX_ATTEMPTS:
            board = self._candidate(rng)
            attempts += 1
        return board

    def _candidate(self, rng: random.Random) -> BoardData:
        n_walls = rng.randint(self.min_walls, self.max_walls)
        grid = [[Cell() for _ in range(self.size)] for _ in range(self.size)]

        # We generate walls in L-shapes
        # Each L-shape is represented as (x, y, type) — type is 0,1,2,3
        edges: list[tuple[int, int, int]] = []
        for y in range(self.size):
            for x in range(self.size):
                edges.append((x, y, rng.randint(0, 3)))
        rng.shuffle(edges)

        placed = 0
        target_positions: list[tuple[int, int]] = []
        for x, y, t in edges:
            if placed == n_walls:
                break
            grid[y][x] = _with_walls(grid[y][x], t)
            if y > 0 and (t == 0 or t == 3):
                grid[y - 1][x] = _with_wall(grid[y - 1][x], 2)
            if y < self.size - 1 and (t == 1 or t == 2):
                grid[y + 1][x] = _with_wall(grid[y + 1][x], 0)
            if x > 0 and (t == 2 or t == 3):
                grid[y][x - 1] = _with_wall(grid[y][x - 1], 1)
            if x < self.size - 1 and (t == 0 or t == 1):
                grid[y][x + 1] = _with_wall(grid[y][x + 1], 3)
            placed += 1
            target_positions.append((x, y))

        cells = [(x, y) for y in range(self.size) for x in range(self.size)]
        rng.shuffle(cells)
        mole_positions = tuple(Position(x=x, y=y) for x, y in cells[:5])

        return BoardData(
            width=self.size,
            height=self.size,
            grid=grid,
            mole_position=mole_positions,  # type: ignore[arg-type]
            target_positions=list(Position(x=x, y=y) for x, y in target_positions),
            moves=0,
        )


def _with_wall(cell: Cell, direction: int) -> Cell:
    walls = list(cell.wall)
    walls[direction] = True
    return Cell(wall=tuple(walls))  # type: ignore[arg-type]


def _with_walls(cell: Cell, direction: int) -> Cell:
    walls = list(cell.wall)
    walls[direction] = True
    walls[(direction + 1) % 4] = True
    return Cell(wall=tuple(walls))  # type: ignore[arg-type]
