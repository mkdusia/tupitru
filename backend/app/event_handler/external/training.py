from app.event_handler.router import external_event
from app.event_handler.schemas.external import (
    TrainExitEvent,
    TrainMoveEvent,
    TrainNewEvent,
    TrainResetEvent,
    TrainStartEvent,
)
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.game_state.pools import CATALOG
from app.game_state.schemas import Direction

_DIRECTIONS: dict[str, Direction] = {"U": 0, "R": 1, "D": 2, "L": 3}

_NO_SESSION = "You are not in a training session."
_BAD_POOL = "The selected board pool does not exist."


def _pools() -> list[dict[str, str]]:
    return [{"id": e.id, "display_name": e.display_name} for e in CATALOG]


@external_event("train_start", TrainStartEvent)
async def handle_train_start(handler: EventHandlerProtocol, event: TrainStartEvent) -> None:
    session = handler.training_manager.start(event.id, event.pool_id, event.seed)
    if session is None:
        await handler.con_manager.send(event.id, {"type": "error", "message": _BAD_POOL})
        return
    await handler.con_manager.send(
        event.id,
        {
            "type": "success",
            "message": "train_start",
            "board": session.board.model_dump(),
            "pool_id": session.pool_id,
            "seed": session.seed,
            "pools": _pools(),
        },
    )


@external_event("train_move", TrainMoveEvent)
async def handle_train_move(handler: EventHandlerProtocol, event: TrainMoveEvent) -> None:
    result = handler.training_manager.move(event.id, event.mole, _DIRECTIONS[event.direction])
    if result is None:
        await handler.con_manager.send(event.id, {"type": "error", "message": _NO_SESSION})
        return
    board, finished = result
    await handler.con_manager.send(
        event.id,
        {
            "type": "success",
            "message": "train_move",
            "board": board.model_dump(),
            "finished": finished,
        },
    )


@external_event("train_reset", TrainResetEvent)
async def handle_train_reset(handler: EventHandlerProtocol, event: TrainResetEvent) -> None:
    board = handler.training_manager.reset(event.id)
    if board is None:
        await handler.con_manager.send(event.id, {"type": "error", "message": _NO_SESSION})
        return
    await handler.con_manager.send(
        event.id,
        {
            "type": "success",
            "message": "train_reset",
            "board": board.model_dump(),
            "finished": False,
        },
    )


@external_event("train_new", TrainNewEvent)
async def handle_train_new(handler: EventHandlerProtocol, event: TrainNewEvent) -> None:
    session = handler.training_manager.new_board(event.id, event.pool_id, event.seed)
    if session is None:
        await handler.con_manager.send(event.id, {"type": "error", "message": _BAD_POOL})
        return
    await handler.con_manager.send(
        event.id,
        {
            "type": "success",
            "message": "train_new",
            "board": session.board.model_dump(),
            "pool_id": session.pool_id,
            "seed": session.seed,
        },
    )


@external_event("train_exit", TrainExitEvent)
async def handle_train_exit(handler: EventHandlerProtocol, event: TrainExitEvent) -> None:
    handler.training_manager.stop(event.id)
    await handler.con_manager.send(event.id, {"type": "success", "message": "train_exit"})
