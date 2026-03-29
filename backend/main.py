from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from ConnectionManager import ConnectionManager
from EventHandler import EventHandler
from GameManager import GameManager

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

con_manager = ConnectionManager()
game_manager = GameManager()
event_handler = EventHandler(con_manager, game_manager)
game_manager.set_emitter(lambda event: event_handler.handle(event, "internal"))


@app.get("/")
async def get_index():
    return FileResponse('static/index.html')

@app.websocket("/ws")
async def host_endpoint(socket: WebSocket):
    id = await con_manager.connect(socket)
    try:
        while True:
            data = await socket.receive_json()
            data["id"] = id
            await event_handler.handle(data, "external")
    except WebSocketDisconnect:
        await event_handler.handle({"type": "disconnect", "id": id}, "internal")

@app.get("/room/{room_id}")
async def get_room(room_id: str):
    return FileResponse('static/index.html')