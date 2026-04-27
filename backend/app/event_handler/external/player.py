from app.event_handler.router import external_event
from app.event_handler.schemas.external import (
    AnswerEvent,
    GiveUpEvent,
    JoinEvent,
    RespondEvent,
    RevertEvent,
)
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.game_state.schemas import Direction


@external_event("join", JoinEvent)
async def handle_join(handler: EventHandlerProtocol, event: JoinEvent) -> None:
    await handler.game_manager.join(event.id, event.room_id, event.nickname)


@external_event("answer", AnswerEvent)
async def handle_answer(handler: EventHandlerProtocol, event: AnswerEvent) -> None:
    await handler.game_manager.answer(event.id, event.answer)


@external_event("respond", RespondEvent)
async def handle_respond(handler: EventHandlerProtocol, event: RespondEvent) -> None:
    change: dict[str, Direction] = {"U": 0, "R": 1, "D": 2, "L": 3}
    await handler.game_manager.respond(event.id, event.mole, change[event.direction])


@external_event("give_up", GiveUpEvent)
async def handle_give_up(handler: EventHandlerProtocol, event: GiveUpEvent) -> None:
    await handler.game_manager.give_up(event.id)


@external_event("revert", RevertEvent)
async def handle_revert(handler: EventHandlerProtocol, event: RevertEvent) -> None:
    await handler.game_manager.revert_move(event.id)
