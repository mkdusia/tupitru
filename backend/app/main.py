from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .ConnectionManager import ConnectionManager
from .event_handler import EventHandler
from .game_state.GameManager import GameManager

app = FastAPI()


con_manager = ConnectionManager()
game_manager = GameManager()
event_handler = EventHandler(con_manager, game_manager)
game_manager.set_emitter(lambda event: event_handler.handle(event, "internal"))


@app.websocket("/ws")
async def host_endpoint(socket: WebSocket) -> None:
    id = await con_manager.connect(socket)
    try:
        while True:
            data = await socket.receive_json()
            data["id"] = id
            await event_handler.handle(data, "external")
    except WebSocketDisconnect:
        await event_handler.handle({"type": "disconnect", "id": id}, "internal")
