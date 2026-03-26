from fastapi import WebSocket
from uuid import uuid4, UUID

class ConnectionManager:
    def __init__(self) -> None:
        self.user_id: dict[UUID, WebSocket]
        self.user_id = {}

    async def connect(self, socket: WebSocket) -> UUID:
        await socket.accept();
        id = uuid4()
        self.user_id[id] = socket
        return id

    def disconnect(self, id: UUID):
        self.user_id.pop(id)

    async def send(self, id: UUID, data: dict):
        if id in self.user_id:
            await self.user_id[id].send_json(data)

    async def broadcast(self, ids: list[UUID], data: dict):
        for id in ids:
            try:
                await self.send(id,data)
            except:
                pass
