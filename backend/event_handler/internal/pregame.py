from typing import Any

from event_handler.router import internal_event

@internal_event("game_start")
async def internal_game_start(handler, event: dict[str,Any]):
    await handler.con_manager.broadcast(event["notify"], {"type": "info", "message": "Game start"})

@internal_event("player_joined")
async def internal_player_joined(handler, event: dict[str,Any]):
    await handler.con_manager.broadcast(
        event["notify"], 
        {"type": "info", "message": "player_joined", "nickname": event["nickname"]}
    )
