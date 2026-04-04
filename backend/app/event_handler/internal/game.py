from app.event_handler.router import internal_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.internal import (
    AwaitingResponseEvent,
    InternalGameEndEvent,
    RespondEvent,
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
