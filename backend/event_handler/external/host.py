from event_handler.router import external_event
from event_handler.types.protocol import EventHandlerProtocol
from event_handler.types.external import HostEvent, GameStartEvent

@external_event("host", HostEvent)
async def handle_host(handler: EventHandlerProtocol, event: HostEvent):
    room_id = handler.game_manager.host(event.id)
    await handler.con_manager.send(event.id, {"type": "success", "room_id": room_id})

@external_event("game_start", GameStartEvent)
async def handle_game_start(handler: EventHandlerProtocol, event: GameStartEvent):
    await handler.game_manager.game_start(event.id,event.room_id)

