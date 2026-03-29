from typing import Any

from event_handler.router import external_event
from event_handler.handler import EventHandler

@external_event("host")
async def handle_host(handler: EventHandler, event: dict[str,Any]):
    id = event.get("id")
    if id is None:
        return
    room_id = handler.game_manager.host(id)
    await handler.con_manager.send(id, {"type": "success", "room_id": room_id})

@external_event("game_start")
async def handle_game_start(handler: EventHandler, event: dict[str,Any]):
    id = event.get("id")
    room_id = event.get("room_id")
    if id is None or room_id is None:
        return
    await handler.game_manager.game_start(id,room_id)

