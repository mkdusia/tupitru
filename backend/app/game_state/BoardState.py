import json

from pydantic import BaseModel, model_validator
from app.game_state.schemas import Direction, Mole
from typing import Dict, List, Optional


class Cell(BaseModel):
    wall_top: bool = False
    wall_right: bool = False
    wall_bottom: bool = False
    wall_left: bool = False

    is_finish: bool = False
    can_spawn_mole: bool = True


class Position(BaseModel):
    x: int
    y: int


class FinishField(BaseModel):
    pos: Position
    color: str


class BoardData(BaseModel):
    width: int
    height: int
    grid: List[List[Cell]]
    moles: Dict[int, Position]
    moves: int
    finish: FinishField


class Board(BaseModel):
    width: int
    height: int
    grid: List[List[Cell]]
    mole_spawn_points: List[Position]
    finish: FinishField

    @classmethod
    def from_json_file(cls, file_path: str) -> "Board":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    @model_validator(mode="after")
    def setup_board_logic(self) -> "Board":
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                if y == 0:
                    cell.wall_top = True
                if y == self.height - 1:
                    cell.wall_bottom = True
                if x == 0:
                    cell.wall_left = True
                if x == self.width - 1:
                    cell.wall_right = True

                if x == self.finish.pos.x and y == self.finish.pos.y:
                    cell.is_finish = True
                    cell.can_spawn_mole = False
                else:
                    cell.is_finish = False

        return self


class BoardState:
    # def __init__(self, board: Board):
    #    self.board = board
    #    self.moles: Dict[int, Position] = {
    #        i: pos.model_copy() for i, pos in enumerate(self.board.mole_spawn_points)
    #    }
    #    self._moves: int = 0
    #    self._history: List[Dict[int, Position]] = []
    def __init__(self, file_path: str = "static/board1.json"):
        self.board = Board.from_json_file(file_path)
        self.moles: Dict[int, Position] = {
            i: pos.model_copy() for i, pos in enumerate(self.board.mole_spawn_points)
        }
        self._moves: int = 0
        self._history: List[Dict[int, Position]] = []

    def finish_state(self) -> bool:
        # Zakładamy, że kret, którego trzeba doprowadzić do mety, ma ID = 0.
        target_mole = self.moles.get(0)
        if target_mole:
            return (
                target_mole.x == self.board.finish.pos.x
                and target_mole.y == self.board.finish.pos.y
            )
        return False

    def modify(self, mole_id: Mole, direction: Direction) -> None:
        if mole_id not in self.moles:
            return

        self._history.append(self.moles.copy())

        dx, dy = self._get_delta(direction)
        curr_pos = self.moles[mole_id]

        while True:
            if self._is_blocked_by_wall(curr_pos, direction):
                break

            next_x, next_y = curr_pos.x + dx, curr_pos.y + dy

            if self._is_occupied_by_other_mole(next_x, next_y, mole_id):
                break

            curr_pos = Position(x=next_x, y=next_y)

        if self.moles[mole_id] != curr_pos:
            self.moles[mole_id] = curr_pos
            self._moves += 1

    def _get_delta(self, direction: Direction) -> tuple[int, int]:
        if direction == 0:
            return (0, -1)
        if direction == 1:
            return (1, 0)
        if direction == 2:
            return (0, 1)
        if direction == 3:
            return (-1, 0)
        return (0, 0)

    def _is_blocked_by_wall(self, pos: Position, direction: Direction) -> bool:
        cell = self.board.grid[pos.y][pos.x]
        if direction == 0:
            return bool(cell.wall_top)
        if direction == 1:
            return bool(cell.wall_right)
        if direction == 2:
            return bool(cell.wall_bottom)
        if direction == 3:
            return bool(cell.wall_left)
        return False

    def _is_occupied_by_other_mole(self, x: int, y: int, moving_mole_id: int) -> bool:
        for mid, pos in self.moles.items():
            if mid == moving_mole_id:
                continue
            if pos.x == x and pos.y == y:
                return True
        return False

    def revert(self) -> None:
        if self._history:
            self.moles = self._history.pop()
            self._moves -= 1

    def clear(self) -> None:
        self.moles = {i: p.model_copy() for i, p in enumerate(self.board.mole_spawn_points)}
        self._moves = 0
        self._history = []

    def flush(self) -> None:
        self._history = []

    @property
    def moves(self) -> int:
        return self._moves

    @property
    def data(self) -> BoardData:
        return BoardData(
            width=self.board.width,
            height=self.board.height,
            grid=self.board.grid,
            moles=self.moles,
            moves=self._moves,
            finish=self.board.finish,
        )
