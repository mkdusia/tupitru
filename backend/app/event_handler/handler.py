from typing import Any

from pydantic import ValidationError
from app.ConnectionManager import ConnectionManager
from app.game_state.GameManager import GameManager
from app.event_handler.router import external_registry, internal_registry


class EventHandler:
    def __init__(self, con_manager: ConnectionManager, game_manager: GameManager) -> None:
        self.con_manager = con_manager
        self.game_manager = game_manager

    async def handle(self, event: dict[str, Any], source: str) -> None:
        tp = event.get("type")

        try:
            if source == "external" and tp in external_registry:
                schema, fn = external_registry[tp]
                parsed = schema(**event)
                await fn(self, parsed)
            elif source == "internal" and tp in internal_registry:
                schema, fn = internal_registry[tp]
                parsed = schema(**event)
                await fn(self, parsed)
            else:
                # TODO: Add logging here!
                if source == "external" and "id" in event:
                    await self.con_manager.send(
                        event["id"], {"type": "error", "message": "Invalid event type"}
                    )
        except ValidationError:
            if source == "external" and "id" in event:
                await self.con_manager.send(
                    event["id"], {"type": "error", "message": "Invalid event format"}
                )
