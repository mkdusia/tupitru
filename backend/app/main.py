from uuid import UUID
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
async def user_endpoint(socket: WebSocket) -> None:
    user_id = socket.query_params.get("user_id")

    if user_id is None:
        id = await con_manager.connect(socket)
    else:
        try:
            id = UUID(user_id)
            lock = con_manager.get_lock(id)
            if lock is None:
                raise ValueError
            async with lock:
                good = await con_manager.reconnect(id, socket)
            if not good:
                return
        except ValueError:
            await socket.close()
            return
        data = game_manager.get_state(id)
        data["type"] = "success"
        data["info"] = "reconnect"
        await socket.send_json(data)

    try:
        while True:
            data = await socket.receive_json()
            data["id"] = id
            await event_handler.handle(data, "external")
    except WebSocketDisconnect:
        await event_handler.handle({"type": "disconnect", "id": id}, "internal")
