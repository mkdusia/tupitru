from app.event_handler.router import external_event
from app.event_handler.types.external import JoinEvent
from app.event_handler.types.protocol import EventHandlerProtocol


@external_event("join", JoinEvent)
async def handle_join(handler: EventHandlerProtocol, event: JoinEvent) -> None:
    success = await handler.game_manager.join(event.id, event.room_id, event.nickname)
    if success:
        await handler.con_manager.send(
            event.id, {"type": "success", "message": "joined", "room_id": event.room_id}
        )
    else:
        await handler.con_manager.send(
            event.id, {"type": "error", "message": "No room with this PIN"}
        )
