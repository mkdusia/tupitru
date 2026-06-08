from secrets import randbelow
from uuid import UUID

from .BoardState import BoardData, BoardState
from .schemas import Direction, Mole

# Training boards always have a single target to reach (no rounds, no bidding).
_TRAINING_ROUNDS = 1
_MAX_SEED = 2**32


class TrainingSession:
    def __init__(self, board: BoardData, pool_id: str, seed: int) -> None:
        self.pool_id = pool_id
        self.seed = seed
        self.board_state = BoardState(board, seed, _TRAINING_ROUNDS)

    def move(self, mole: Mole, direction: Direction) -> bool:

        before = self.board_state.board.mole_position[mole].model_copy()
        self.board_state.modify(mole, direction)
        after = self.board_state.board.mole_position[mole]
        if before.x == after.x and before.y == after.y:
            self.board_state.revert()
        return self.is_finished()

    def reset(self) -> None:

        self.board_state.clear()

    def is_finished(self) -> bool:

        return self.board_state.finish_state()

    @property
    def moves(self) -> int:
        return self.board_state.moves

    @property
    def board(self) -> BoardData:
        return self.board_state.data


class TrainingManager:
    def __init__(self) -> None:
        self.sessions: dict[UUID, TrainingSession] = {}

    def _build_session(self, pool_id: str | None, seed: int | None) -> TrainingSession | None:
        from .pools import CATALOG, CATALOG_BY_ID, PoolEntry  # local import avoids circular import

        entry: PoolEntry | None = CATALOG[0] if pool_id is None else CATALOG_BY_ID.get(pool_id)
        if entry is None:
            return None
        if seed is None:
            seed = randbelow(_MAX_SEED)
        board = entry.pool.generate(seed)
        return TrainingSession(board, entry.id, seed)

    def start(
        self, user_id: UUID, pool_id: str | None = None, seed: int | None = None
    ) -> TrainingSession | None:

        session = self._build_session(pool_id, seed)
        if session is None:
            return None
        self.sessions[user_id] = session
        return session

    def new_board(
        self, user_id: UUID, pool_id: str | None = None, seed: int | None = None
    ) -> TrainingSession | None:

        if pool_id is None:
            existing = self.sessions.get(user_id)
            if existing is not None:
                pool_id = existing.pool_id
        return self.start(user_id, pool_id, seed)

    def move(
        self, user_id: UUID, mole: Mole, direction: Direction
    ) -> tuple[BoardData, bool] | None:

        session = self.sessions.get(user_id)
        if session is None:
            return None
        finished = session.move(mole, direction)
        return session.board, finished

    def reset(self, user_id: UUID) -> BoardData | None:

        session = self.sessions.get(user_id)
        if session is None:
            return None
        session.reset()
        return session.board

    def stop(self, user_id: UUID) -> None:

        self.sessions.pop(user_id, None)

    def get_session(self, user_id: UUID) -> TrainingSession | None:
        return self.sessions.get(user_id)
