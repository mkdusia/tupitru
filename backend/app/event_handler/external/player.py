from app.event_handler.router import external_event
from app.event_handler.schemas.external import AnswerEvent, JoinEvent
from app.event_handler.schemas.protocol import EventHandlerProtocol


@external_event("join", JoinEvent)
async def handle_join(handler: EventHandlerProtocol, event: JoinEvent) -> None:
    await handler.game_manager.join(event.id, event.room_id, event.nickname)


@external_event("answer", AnswerEvent)
async def handle_answer(handler: EventHandlerProtocol, event: AnswerEvent) -> None:
    await handler.game_manager.answer(event.id, event.answer)
