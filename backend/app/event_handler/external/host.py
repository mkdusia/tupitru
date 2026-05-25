from app.event_handler.router import external_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.external import (
    ChangeStateEvent,
    CloseRoomEvent,
    HostEvent,
    KickEvent,
    SkipEvent,
)


@external_event("host", HostEvent)
async def handle_host(handler: EventHandlerProtocol, event: HostEvent) -> None:
    room_id = await handler.game_manager.host(event.id)
    await handler.con_manager.send(
        event.id, {"type": "success", "message": "host", "room_id": room_id}
    )


@external_event("change_state", ChangeStateEvent)
async def handle_game_start(handler: EventHandlerProtocol, event: ChangeStateEvent) -> None:
    await handler.game_manager.change_game_state(event.id, event.round_time)


@external_event("skip_round", SkipEvent)
async def handle_skip(handler: EventHandlerProtocol, event: SkipEvent) -> None:
    await handler.game_manager.skip(event.id)


@external_event("kick", KickEvent)
async def handle_kick(handler: EventHandlerProtocol, event: KickEvent) -> None:
    await handler.game_manager.kick(event.id, event.nickname)


@external_event("close", CloseRoomEvent)
async def handle_close(handler: EventHandlerProtocol, event: CloseRoomEvent) -> None:
    v = await handler.game_manager.close_room(event.id)
    if v:
        await handler.con_manager.send(event.id, {"type": "success", "message": "close"})
