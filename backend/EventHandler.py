from typing import Any, Awaitable, Callable
from ConnectionManager import ConnectionManager
from GameManager import GameManager

class EventHandler:
    CLIENT_EVENTS = {"host", "game_start", "join"}

    async def handle_host(self, event: dict[str,Any]):
        id = event.get("id")
        if id is None:
            return
        room_id = self.game_manager.host(id)
        await self.con_manager.send(id, {"type": "success", "room_id": room_id})

    async def handle_join(self, event: dict[str,Any]):
        id = event.get("id")
        room_id = event.get("room_id")
        nickname = event.get("nickname")
        
        if not all([id, room_id, nickname]):
            await self.con_manager.send(id, {"type": "error", "message": "Brakuje danych (room_id lub nickname)"})
            return
            
        success = await self.game_manager.join(id, room_id, nickname)
        if success:
            await self.con_manager.send(id, {"type": "success", "message": "joined", "room_id": room_id})
        else:
            await self.con_manager.send(id, {"type": "error", "message": "Nie znaleziono pokoju o tym kodzie"})

    async def handle_game_start(self, event: dict[str,Any]):
        id = event.get("id")
        room_id = event.get("room_id")
        if id is None or room_id is None:
            return
        await self.game_manager.game_start(id,room_id)

    async def internal_game_start(self, event: dict[str,Any]):
        await self.con_manager.broadcast(event["notify"], {"type": "info", "message": "Game start"})

    async def internal_player_joined(self, event: dict[str,Any]):
        await self.con_manager.broadcast(
            event["notify"], 
            {"type": "info", "message": "player_joined", "nickname": event["nickname"]}
        )

    async def internal_disconnect(self, event: dict[str,Any]):
        await self.game_manager.player_disconnect(event["id"])
        self.con_manager.disconnect(event["id"])

    async def internal_player_disconnected(self, event: dict[str,Any]):
        await self.con_manager.broadcast(event["notify"], {"type": "info", "message": "player_disconnected", "nickname": event["nickname"]})

    async def internal_room_destroyed(self, event: dict[str,Any]):
        await self.con_manager.broadcast(event["notify"], {"type": "info", "message": "room_destroyed"})
        

    def __init__(self, con_manager: ConnectionManager, game_manager: GameManager) -> None:
        self.con_manager = con_manager
        self.game_manager = game_manager
        self.external_handlers: dict[str, Callable[[dict], Awaitable[None]]] = {}
        self.internal_handlers: dict[str, Callable[[dict], Awaitable[None]]] = {}
        
        self.external_handlers["host"] = self.handle_host
        self.external_handlers["game_start"] = self.handle_game_start
        self.external_handlers["join"] = self.handle_join
        
        self.internal_handlers["game_start"] = self.internal_game_start
        self.internal_handlers["disconnect"] = self.internal_disconnect
        self.internal_handlers["player_joined"] = self.internal_player_joined
        self.internal_handlers["player_disconnected"] = self.internal_player_disconnected
        self.internal_handlers["room_destroyed"] = self.internal_room_destroyed

    async def handle(self, event: dict[str,Any], source: str):
        tp = event.get("type")
        if tp is None:
            return
        if source=="external":
            if tp not in EventHandler.CLIENT_EVENTS:
                return
            if tp in self.external_handlers:
                await self.external_handlers[tp](event)
        elif tp in self.internal_handlers:
            await self.internal_handlers[tp](event)
