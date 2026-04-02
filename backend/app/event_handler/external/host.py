from app.event_handler.router import external_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.external import HostEvent, GameStartEvent, TimeUpEvent


@external_event("host", HostEvent)
async def handle_host(handler: EventHandlerProtocol, event: HostEvent) -> None:
    room_id = handler.game_manager.host(event.id)
    await handler.con_manager.send(
        event.id, {"type": "success", "message": "host", "room_id": room_id}
    )


@external_event("game_start", GameStartEvent)
async def handle_game_start(handler: EventHandlerProtocol, event: GameStartEvent) -> None:
    await handler.game_manager.game_start(event.id, event.room_id)


@external_event("time_up", TimeUpEvent)
async def handle_time_up(handler: EventHandlerProtocol, event: TimeUpEvent) -> None:
    await handler.game_manager.time_up(event.id)
