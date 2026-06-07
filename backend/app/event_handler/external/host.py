from app.event_handler.router import external_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.external import (
    ChangeStateEvent,
    CloseRoomEvent,
    HostEvent,
    KickEvent,
    SkipEvent,
    StartGameEvent,
)
from app.game_state.pools import CATALOG


@external_event("host", HostEvent)
async def handle_host(handler: EventHandlerProtocol, event: HostEvent) -> None:
    room_id = await handler.game_manager.host(event.id)
    await handler.con_manager.send(
        event.id,
        {
            "type": "success",
            "message": "host",
            "room_id": room_id,
            "pools": [{"id": e.id, "display_name": e.display_name} for e in CATALOG],
        },
    )


@external_event("start_game", StartGameEvent)
async def handle_start_game(handler: EventHandlerProtocol, event: StartGameEvent) -> None:
    await handler.game_manager.start_game(
        event.id, event.pool_id, event.seed, event.rounds, event.round_time
    )


@external_event("change_state", ChangeStateEvent)
async def handle_change_state(handler: EventHandlerProtocol, event: ChangeStateEvent) -> None:
    await handler.game_manager.change_game_state(event.id)


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
