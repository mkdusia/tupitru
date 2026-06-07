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

        # Interior edges as (x, y, direction) — only "up" (0) and "left" (3) half-edges
        # to avoid duplicates.
        edges: list[tuple[int, int, int]] = []
        for y in range(self.size):
            for x in range(self.size):
                if y > 0:
                    edges.append((x, y, 0))  # wall on top of (x, y) == bottom of (x, y-1)
                if x > 0:
                    edges.append((x, y, 3))  # wall on left of (x, y) == right of (x-1, y)
        rng.shuffle(edges)

        placed = 0
        for x, y, d in edges:
            if placed == n_walls:
                break
            # Mirror onto neighbour
            if d == 0:
                nx, ny, nd = x, y - 1, 2
            else:  # d == 3
                nx, ny, nd = x - 1, y, 1
            new_a = _with_wall(grid[y][x], d)
            new_b = _with_wall(grid[ny][nx], nd)
            grid[y][x] = new_a
            grid[ny][nx] = new_b
            placed += 1

        cells = [(x, y) for y in range(self.size) for x in range(self.size)]
        rng.shuffle(cells)
        mole_positions = tuple(Position(x=x, y=y) for x, y in cells[:5])

        return BoardData(
            width=self.size,
            height=self.size,
            grid=grid,
            mole_position=mole_positions,  # type: ignore[arg-type]
            moves=0,
        )


def _with_wall(cell: Cell, direction: int) -> Cell:
    walls = list(cell.wall)
    walls[direction] = True
    return Cell(wall=tuple(walls))  # type: ignore[arg-type]
