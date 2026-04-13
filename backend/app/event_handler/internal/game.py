from app.event_handler.router import internal_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.internal import (
    AwaitingResponseEvent,
    InternalGameEndEvent,
    RespondEvent,
    AnswerSavedEvent
)


@internal_event("game_end", InternalGameEndEvent)
async def internal_game_end(handler: EventHandlerProtocol, event: InternalGameEndEvent) -> None:
    await handler.con_manager.broadcast(event.notify, {"type": "info", "message": "game_end"})


@internal_event("awaiting_response", AwaitingResponseEvent)
async def awaiting_response_event(
    handler: EventHandlerProtocol, event: AwaitingResponseEvent
) -> None:
    await handler.con_manager.broadcast(
        event.notify, {"type": "info", "message": "awaiting_response"}
    )


@internal_event("respond", RespondEvent)
async def respond_event(handler: EventHandlerProtocol, event: RespondEvent) -> None:
    await handler.con_manager.send(event.notify, {"type": "info", "message": "respond"})


@internal_event("answer_saved", AnswerSavedEvent)
async def handle_answer_saved(handler: EventHandlerProtocol, event: AnswerSavedEvent) -> None:
    for uid in event.notify:
        await handler.con_manager.send(
            uid, 
            {
                "type": "answer_confirmed", 
                "player_id": str(event.player_id)
            }
        )