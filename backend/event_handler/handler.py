from typing import Any
from ConnectionManager import ConnectionManager
from GameManager import GameManager
from event_handler.router import external_registry, internal_registry

class EventHandler:
    def __init__(self, con_manager: ConnectionManager, game_manager: GameManager) -> None:
        self.con_manager = con_manager
        self.game_manager = game_manager

    async def handle(self, event: dict[str,Any], source: str):
        tp = event.get("type")
        if tp is None:
            return
        if source=="external":
            if tp in external_registry:
                await external_registry[tp](self, event)
        elif tp in internal_registry:
            await internal_registry[tp](self, event)
