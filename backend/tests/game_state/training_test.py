import uuid
from typing import Any

import pytest

from app.ConnectionManager import ConnectionManager
from app.event_handler import EventHandler
from app.game_state.BoardState import BoardData, Cell, Position
from app.game_state.GameManager import GameManager
from app.game_state.Training import TrainingManager, TrainingSession


# A 3x3 open board. The four edge midpoints stay free, the centre and corners hold moles.
def _open_board() -> BoardData:
    return BoardData(
        width=3,
        height=3,
        grid=[[Cell() for _ in range(3)] for _ in range(3)],
        mole_position=(
            Position(x=0, y=0),
            Position(x=2, y=0),
            Position(x=0, y=2),
            Position(x=2, y=2),
            Position(x=1, y=1),
        ),
        moves=0,
    )


def _session_with_target(finish: Position, finish_mole: int) -> TrainingSession:
    session = TrainingSession(_open_board(), pool_id="test", seed=0)
    session.board_state.board.finish = finish
    session.board_state.board.finish_mole = finish_mole  # type: ignore[assignment]
    return session


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []
        self.closed = False

    async def accept(self) -> None:
        pass

    async def send_json(self, data: dict[str, Any]) -> None:
        self.sent.append(data)

    async def close(self) -> None:
        self.closed = True


# --- TrainingSession unit behaviour. ---


def test_effective_move_increments_counter() -> None:
    # Mole 0 at (0,0) slides right (direction 1) until it hits mole 1 at (2,0),
    # stopping at (1,0): an effective move.
    session = _session_with_target(Position(x=2, y=1), finish_mole=0)
    assert session.moves == 0
    session.move(0, 1)
    assert session.moves == 1
    assert session.board.mole_position[0] == Position(x=1, y=0)


def test_blocked_move_does_not_count() -> None:
    # Mole 0 at (0,0) cannot move up (direction 0): board edge, so no move is counted.
    session = _session_with_target(Position(x=2, y=1), finish_mole=0)
    finished = session.move(0, 0)
    assert session.moves == 0
    assert finished is False
    assert session.board.mole_position[0] == Position(x=0, y=0)


def test_reset_restores_initial_layout_and_counter() -> None:
    session = _session_with_target(Position(x=2, y=1), finish_mole=0)
    # Mole 0 slides right (0,0)->(1,0); mole 3 slides up (2,2)->(2,1): two real moves.
    session.move(0, 1)
    session.move(3, 0)
    assert session.moves == 2
    assert session.board.mole_position[0] == Position(x=1, y=0)
    assert session.board.mole_position[3] == Position(x=2, y=1)
    session.reset()
    assert session.moves == 0
    assert session.board.mole_position[0] == Position(x=0, y=0)
    assert session.board.mole_position[3] == Position(x=2, y=2)


def test_reaching_target_reports_finished() -> None:
    # Mole 0 at (0,0) slides down (direction 2) to (0,1)? No: it slides until it hits
    # mole 2 at (0,2), stopping at (0,1). Target is (0,1) for mole 0.
    session = _session_with_target(Position(x=0, y=1), finish_mole=0)
    finished = session.move(0, 2)
    assert finished is True
    assert session.is_finished() is True


def test_universal_target_finishes_with_any_mole() -> None:
    # Universal target (-1) at (1,0): mole 0 slides right and stops at (1,0).
    session = _session_with_target(Position(x=1, y=0), finish_mole=-1)
    finished = session.move(0, 1)
    assert finished is True


# --- TrainingManager orchestration. ---


def test_manager_start_creates_session_per_user() -> None:
    manager = TrainingManager()
    user = uuid.uuid4()
    session = manager.start(user, pool_id="dummy_3x3", seed=1)
    assert session is not None
    assert manager.get_session(user) is session
    assert session.pool_id == "dummy_3x3"


def test_manager_start_is_deterministic_for_same_seed() -> None:
    manager = TrainingManager()
    a = manager.start(uuid.uuid4(), pool_id="random_7x7", seed=99)
    b = manager.start(uuid.uuid4(), pool_id="random_7x7", seed=99)
    assert a is not None and b is not None
    assert a.board.mole_position == b.board.mole_position
    assert (a.board.finish, a.board.finish_mole) == (b.board.finish, b.board.finish_mole)


def test_manager_rejects_unknown_pool() -> None:
    manager = TrainingManager()
    assert manager.start(uuid.uuid4(), pool_id="does_not_exist", seed=0) is None


def test_manager_move_and_reset_without_session() -> None:
    manager = TrainingManager()
    user = uuid.uuid4()
    assert manager.move(user, 0, 1) is None
    assert manager.reset(user) is None


def test_manager_new_board_keeps_pool_by_default() -> None:
    manager = TrainingManager()
    user = uuid.uuid4()
    manager.start(user, pool_id="random_7x7", seed=1)
    session = manager.new_board(user, seed=2)
    assert session is not None
    assert session.pool_id == "random_7x7"
    assert session.seed == 2


def test_manager_stop_drops_session() -> None:
    manager = TrainingManager()
    user = uuid.uuid4()
    manager.start(user, seed=0)
    manager.stop(user)
    assert manager.get_session(user) is None
    manager.stop(user)  # idempotent


# --- End-to-end through the event handler stack. ---


def _build_stack() -> tuple[EventHandler, ConnectionManager, TrainingManager]:
    con = ConnectionManager()
    game = GameManager()
    training = TrainingManager()
    handler = EventHandler(con, game, training)
    game.set_emitter(lambda event: handler.handle(event, "internal"))
    return handler, con, training


@pytest.mark.asyncio
async def test_train_start_returns_board_and_pools() -> None:
    handler, con, _ = _build_stack()
    socket = FakeWebSocket()
    user = await con.connect(socket)  # type: ignore[arg-type]
    socket.sent.clear()

    await handler.handle(
        {"type": "train_start", "id": user, "pool_id": "dummy_3x3", "seed": 3}, "external"
    )

    msg = socket.sent[-1]
    assert msg["type"] == "success"
    assert msg["message"] == "train_start"
    assert "board" in msg
    assert msg["pool_id"] == "dummy_3x3"
    assert isinstance(msg["pools"], list) and len(msg["pools"]) >= 1


@pytest.mark.asyncio
async def test_train_move_reports_board_and_finished_flag() -> None:
    handler, con, training = _build_stack()
    socket = FakeWebSocket()
    user = await con.connect(socket)  # type: ignore[arg-type]
    await handler.handle({"type": "train_start", "id": user, "seed": 3}, "external")

    # Pin a target reachable in one move regardless of the generated board.
    session = training.get_session(user)
    assert session is not None
    session.board_state.board.finish = Position(x=0, y=1)
    session.board_state.board.finish_mole = 0
    session.board_state.board.mole_position[0].x = 0
    session.board_state.board.mole_position[0].y = 0
    session.board_state.board.mole_position[2].x = 0
    session.board_state.board.mole_position[2].y = 2

    socket.sent.clear()
    await handler.handle(
        {"type": "train_move", "id": user, "mole": 0, "direction": "D"}, "external"
    )

    msg = socket.sent[-1]
    assert msg["type"] == "success"
    assert msg["message"] == "train_move"
    assert msg["finished"] is True
    assert msg["board"]["moves"] == 1


@pytest.mark.asyncio
async def test_train_move_without_session_errors() -> None:
    handler, con, _ = _build_stack()
    socket = FakeWebSocket()
    user = await con.connect(socket)  # type: ignore[arg-type]
    socket.sent.clear()

    await handler.handle(
        {"type": "train_move", "id": user, "mole": 0, "direction": "U"}, "external"
    )

    assert socket.sent[-1]["type"] == "error"


@pytest.mark.asyncio
async def test_train_reset_returns_unfinished_board() -> None:
    handler, con, _ = _build_stack()
    socket = FakeWebSocket()
    user = await con.connect(socket)  # type: ignore[arg-type]
    await handler.handle({"type": "train_start", "id": user, "seed": 3}, "external")
    socket.sent.clear()

    await handler.handle({"type": "train_reset", "id": user}, "external")

    msg = socket.sent[-1]
    assert msg["message"] == "train_reset"
    assert msg["finished"] is False
    assert msg["board"]["moves"] == 0


@pytest.mark.asyncio
async def test_train_exit_drops_session() -> None:
    handler, con, training = _build_stack()
    socket = FakeWebSocket()
    user = await con.connect(socket)  # type: ignore[arg-type]
    await handler.handle({"type": "train_start", "id": user, "seed": 3}, "external")
    assert training.get_session(user) is not None

    await handler.handle({"type": "train_exit", "id": user}, "external")

    assert training.get_session(user) is None
    assert socket.sent[-1]["message"] == "train_exit"
