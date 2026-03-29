from typing import Any

from event_handler.handler import EventHandler
from event_handler.router import external_event

@external_event("join")
async def handle_join(handler: EventHandler, event: dict[str,Any]):
    id = event.get("id")
    room_id = event.get("room_id")
    nickname = event.get("nickname")
    
    if not all([id, room_id, nickname]):
        await handler.con_manager.send(id, {"type": "error", "message": "Brakuje danych (room_id lub nickname)"})
        return
        
    success = await handler.game_manager.join(id, room_id, nickname)
    if success:
        await handler.con_manager.send(id, {"type": "success", "message": "joined", "room_id": room_id})
    else:
        await handler.con_manager.send(id, {"type": "error", "message": "Nie znaleziono pokoju o tym kodzie"})
