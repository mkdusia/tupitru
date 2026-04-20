import asyncio
from app.event_handler.router import internal_event
from app.event_handler.schemas.internal import (
    DisconnectEvent,
    PlayerDisconnectEvent,
    RoomDestroyedEvent,
)
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.config import DISCONNECT_TIME


@internal_event("disconnect", DisconnectEvent)
async def internal_disconnect(handler: EventHandlerProtocol, event: DisconnectEvent) -> None:
    lock = handler.con_manager.get_lock(event.id)
    if lock is None:
        return
    async with lock:
        handler.con_manager.disconnect(event.id)
    await asyncio.sleep(DISCONNECT_TIME)
    async with lock:
        if not handler.con_manager.is_connected(event.id):
            handler.con_manager.remove(event.id)
        else:
            return
    await handler.game_manager.player_disconnect(event.id)


@internal_event("player_disconnected", PlayerDisconnectEvent)
async def internal_player_disconnected(
    handler: EventHandlerProtocol, event: PlayerDisconnectEvent
) -> None:
    await handler.con_manager.broadcast(
        event.notify, {"type": "info", "message": "player_disconnected", "nickname": event.nickname}
    )


@internal_event("room_destroyed", RoomDestroyedEvent)
async def internal_room_destroyed(handler: EventHandlerProtocol, event: RoomDestroyedEvent) -> None:
    await handler.con_manager.broadcast(event.notify, {"type": "info", "message": "room_destroyed"})
