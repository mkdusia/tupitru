from app.event_handler.router import external_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.external import ChangeStateEvent, HostEvent


@external_event("host", HostEvent)
async def handle_host(handler: EventHandlerProtocol, event: HostEvent) -> None:
    room_id = handler.game_manager.host(event.id)
    await handler.con_manager.send(
        event.id, {"type": "success", "message": "host", "room_id": room_id}
    )


@external_event("change_state", ChangeStateEvent)
async def handle_game_start(handler: EventHandlerProtocol, event: ChangeStateEvent) -> None:
    await handler.game_manager.change_game_state(event.id)
