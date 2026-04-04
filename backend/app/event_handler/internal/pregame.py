from app.event_handler.router import internal_event
from app.event_handler.schemas.internal import InternalGameStartEvent, PlayerJoinedEvent
from app.event_handler.schemas.protocol import EventHandlerProtocol


@internal_event("game_start", InternalGameStartEvent)
async def internal_game_start(handler: EventHandlerProtocol, event: InternalGameStartEvent) -> None:
    await handler.con_manager.broadcast(event.notify, {"type": "info", "message": "game_start"})


@internal_event("player_joined", PlayerJoinedEvent)
async def internal_player_joined(handler: EventHandlerProtocol, event: PlayerJoinedEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify, {"type": "info", "message": "player_joined", "nickname": event.nickname}
    )
    await handler.con_manager.send(
        event.player_id, {"type": "success", "message": "join", "room_id": event.room_id}
    )
