from typing import Any

from event_handler.handler import EventHandler
from event_handler.router import internal_event

@internal_event("disconnect")
async def internal_disconnect(handler: EventHandler, event: dict[str,Any]):
    await handler.game_manager.player_disconnect(event["id"])
    handler.con_manager.disconnect(event["id"])

@internal_event("player_disconnected")
async def internal_player_disconnected(handler: EventHandler, event: dict[str,Any]):
    await handler.con_manager.broadcast(event["notify"], {"type": "info", "message": "player_disconnected", "nickname": event["nickname"]})

@internal_event("room_destroyed")
async def internal_room_destroyed(handler: EventHandler, event: dict[str,Any]):
    await handler.con_manager.broadcast(event["notify"], {"type": "info", "message": "room_destroyed"})
