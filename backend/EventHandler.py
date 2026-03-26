from typing import Any, Awaitable, Callable
from ConnectionManager import ConnectionManager
from GameManager import GameManager

class EventHandler:
    CLIENT_EVENTS = {"host", "game_start"}

    async def handle_host(self, event: dict[str,Any]):
        id = event.get("id")
        if id is None:
            return
        room_id = self.game_manager.host(id)
        await self.con_manager.send(id, {"type": "success", "room_id": room_id})

    async def handle_game_start(self, event: dict[str,Any]):
        id = event.get("id")
        room_id = event.get("room_id")
        if id is None or room_id is None:
            return
        await self.game_manager.game_start(id,room_id)

    async def internal_game_start(self, event: dict[str,Any]):
        await self.con_manager.broadcast(event["notify"], {"type": "info", "message": "Game start"})

    async def internal_disconnect(self, event: dict[str,Any]):
        await self.game_manager.player_disconnect(event["id"])
        self.con_manager.disconnect(event["id"])


    def __init__(self, con_manager: ConnectionManager, game_manager: GameManager) -> None:
        self.con_manager = con_manager
        self.game_manager = game_manager
        self.external_handlers: dict[str, Callable[[dict], Awaitable[None]]]
        self.internal_handlers: dict[str, Callable[[dict], Awaitable[None]]]
        self.external_handlers = {}
        self.internal_handlers = {}
        self.external_handlers["host"] = self.handle_host
        self.external_handlers["game_start"] = self.handle_game_start
        self.internal_handlers["game_start"] = self.internal_game_start
        self.internal_handlers["disconnect"] = self.internal_disconnect

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
