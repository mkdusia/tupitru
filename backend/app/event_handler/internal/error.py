from app.event_handler.router import internal_event
from app.event_handler.schemas.internal import PropagateError
from app.event_handler.schemas.protocol import EventHandlerProtocol


@internal_event("propagate_error", PropagateError)
async def internal_game_start(handler: EventHandlerProtocol, event: PropagateError) -> None:
    await handler.con_manager.send(event.recipient, {"type": "error", "message": event.message})
