import random
from typing import Literal, cast

from pydantic import BaseModel

from app.game_state.schemas import Direction, Mole

# Probability that a round's target accepts any mole (universal) rather than a specific one.
UNIVERSAL_TARGET_PROB = 0.2
# Default number of rounds when the host doesn't specify one.
DEFAULT_ROUNDS = 5


class Cell(BaseModel):
    wall: tuple[bool, bool, bool, bool] = (False, False, False, False)


class Position(BaseModel):
    x: int
    y: int


class BoardData(BaseModel):
    model_config = {"validate_assignment": True}
    width: int
    height: int
    grid: list[list[Cell]]
    mole_position: tuple[Position, Position, Position, Position, Position]
    target_positions: list[Position]
    moves: int
    finish: Position | None = None
    finish_mole: Mole | Literal[-1] = -1

    def is_connected(self) -> bool:
        """
        Whether every cell is reachable from every other one (walls as barriers).
        A disconnected board can strand moles in a region with no usable target.
        """
        seen = {(0, 0)}
        stack = [(0, 0)]
        deltas = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        while stack:
            x, y = stack.pop()
            walls = self.grid[y][x].wall
            for d, (dx, dy) in enumerate(deltas):
                if walls[d]:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    stack.append((nx, ny))
        return len(seen) == self.width * self.height

    def blocked_by_wall(self, pos: Position, direction: Direction) -> bool:
        """
        Check whether a move from a given position in a given direction is blocked by a wall
        """
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][direction]
        cell = self.grid[pos.y][pos.x]
        return (
            cell.wall[direction]
            or pos.x + dx < 0
            or pos.x + dx >= self.width
            or pos.y + dy < 0
            or pos.y + dy >= self.height
        )

    def contains_mole(self, pos: Position) -> bool:
        """
        Check whether a given position contains a mole
        """
        return any([mole == pos for mole in self.mole_position])


class BoardState:
    board: BoardData
    move_stack: list[tuple[Mole, Position]]

    def __init__(self, board: BoardData, seed: int, rounds: int) -> None:
        self.move_stack = []
        self.board = board
        self._rng = random.Random(seed)
        self.rounds_left = rounds
        self.next_round()

    def _roll_target(self) -> None:
        """
        Pick this round's target: a uniformly random cell not currently occupied by a
        mole (so it can never start the round already blocked), for a specific mole or
        any mole (universal).
        """
        free = [p for p in self.board.target_positions if not self.board.contains_mole(p)]
        self.board.finish = self._rng.choice(free)
        if self._rng.random() < UNIVERSAL_TARGET_PROB:
            self.board.finish_mole = -1
        else:
            self.board.finish_mole = cast(Mole, self._rng.randint(0, 4))

    def _get_move(self, pos: Position, direction: Direction) -> Position:
        """
        Get the ending position of a move from a given position in a given direction
        """
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][direction]
        while True:
            next_pos = Position(x=pos.x + dx, y=pos.y + dy)
            if self.board.blocked_by_wall(pos, direction) or self.board.contains_mole(next_pos):
                break
            pos = next_pos
        return pos

    def finish_state(self) -> bool:
        """
        Check whether the current state is the finish state for the round
        """
        if self.board.finish is None:
            return False
        mole = self.board.finish_mole
        if mole == -1:
            return any([self.board.finish == pos for pos in self.board.mole_position])
        else:
            pos = self.board.mole_position[mole]
            return pos == self.board.finish

    def next_round(self) -> bool:
        """
        Prepare the board for the next round, returns False if there is no next round
        """
        if self.rounds_left <= 0:
            return False
        self.rounds_left -= 1
        self._roll_target()
        return True

    def modify(self, mole_id: Mole, direction: Direction) -> None:
        """
        Perform a single move
        """
        self.move_stack.append((mole_id, self.board.mole_position[mole_id].model_copy()))
        curr_pos = self.board.mole_position[mole_id]
        next_pos = self._get_move(curr_pos, direction)
        self.board.mole_position[mole_id].x = next_pos.x
        self.board.mole_position[mole_id].y = next_pos.y

    def revert(self) -> None:
        if len(self.move_stack) > 0:
            mole, pos = self.move_stack.pop()
            self.board.mole_position[mole].x = pos.x
            self.board.mole_position[mole].y = pos.y

    def clear(self) -> None:
        while len(self.move_stack) > 0:
            self.revert()

    def flush(self) -> None:
        self.move_stack = []

    @property
    def moves(self) -> int:
        return len(self.move_stack)

    @property
    def data(self) -> BoardData:
        self.board.moves = self.moves
        return self.board.model_copy()
