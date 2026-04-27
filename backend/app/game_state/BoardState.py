import json
from pydantic import BaseModel
from app.game_state.schemas import Direction, Mole
from typing import Literal, cast
from pathlib import Path
from random import shuffle


class Cell(BaseModel):
    wall: tuple[bool, bool, bool, bool] = (False, False, False, False)


class Position(BaseModel):
    x: int
    y: int


class BoardData(BaseModel):
    width: int
    height: int
    grid: list[list[Cell]]
    mole_position: tuple[Position, Position, Position, Position, Position]
    moves: int
    finish: Position
    finish_mole: Mole | Literal[-1]

    def blocked_by_wall(self, pos: Position, direction: Direction) -> bool:
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][direction]
        cell = self.grid[pos.x][pos.y]
        return (
            cell.wall[direction]
            or pos.x + dx < 0
            or pos.x + dx >= self.width
            or pos.y + dy < 0
            or pos.y + dy >= self.height
        )

    def contains_mole(self, pos: Position) -> bool:
        return any([mole == pos for mole in self.mole_position])


class BoardState:
    board: BoardData
    move_stack: list[tuple[Mole, Direction]] = []
    finish_positions: list[tuple[Position, Mole | Literal[-1]]]

    def __init__(self, file: Path = Path(__file__).parent.resolve() / "static/board1.json"):
        with open(file) as f:
            data = json.load(f)
            self.finish_positions = data["finish_positions"]
            shuffle(self.finish_positions)
            del data["finish_positions"]
            pos, mole = self.finish_positions.pop()
            data["finish"] = pos
            data["finish_mole"] = mole
        self.board = BoardData.model_validate(data)

    def _get_move(self, pos: Position, direction: Direction) -> Position:
        dx, dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][direction]
        while True:
            next_pos = Position(x=pos.x + dx, y=pos.y + dy)
            if self.board.blocked_by_wall(pos, direction) or self.board.contains_mole(next_pos):
                break
            pos = next_pos
        return pos

    def finish_state(self) -> bool:
        mole = self.board.finish_mole
        if mole == -1:
            return any([self.board.finish == pos for pos in self.board.mole_position])
        else:
            pos = self.board.mole_position[mole]
            return pos == self.board.finish

    def next_round(self) -> bool:
        if len(self.finish_positions) == 0:
            return False
        pos, mole = self.finish_positions.pop()
        self.board.finish = pos
        self.board.finish_mole = mole
        return True

    def modify(self, mole_id: Mole, direction: Direction) -> None:
        self.move_stack.append((mole_id, direction))
        curr_pos = self.board.mole_position[mole_id]
        next_pos = self._get_move(curr_pos, direction)
        self.board.mole_position[mole_id].x = next_pos.x
        self.board.mole_position[mole_id].y = next_pos.y

    def revert(self) -> None:
        if len(self.move_stack) > 0:
            mole, direction = self.move_stack.pop()
            curr_pos = self.board.mole_position[mole]
            next_pos = self._get_move(curr_pos, cast(Literal[0, 1, 2, 3], (direction + 2) % 4))
            self.board.mole_position[mole].x = next_pos.x
            self.board.mole_position[mole].y = next_pos.y

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
