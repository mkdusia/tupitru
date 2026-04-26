from fastapi import WebSocket
from uuid import uuid4, UUID
from typing import Any
from asyncio import Lock

Data = dict[str, Any]


class ConnectionManager:
    def __init__(self) -> None:
        self.sockets: dict[UUID, WebSocket] = {}
        self.connected: dict[UUID, bool] = {}
        self.locks: dict[UUID, Lock] = {}

    def get_lock(self, id: UUID) -> Lock | None:
        """
        Return the lock associated with a user. Used to synchronize reconnect/disconnect clean-up logic.
        """
        return self.locks.get(id)

    def is_connected(self, id: UUID) -> bool:
        """
        Check whether a user is currently connected.
        """
        return id in self.connected and self.connected[id]

    async def connect(self, socket: WebSocket) -> UUID:
        """
        Accept a brand new WebSocket connection.
        """
        await socket.accept()
        id = uuid4()
        self.sockets[id] = socket
        self.connected[id] = True
        self.locks[id] = Lock()
        await socket.send_json({"type": "success", "message": "connect", "user_id": str(id)})
        return id

    async def reconnect(self, id: UUID, socket: WebSocket) -> bool:
        """
        Restore a previously disconnected user connection.
        """
        if id not in self.sockets or self.is_connected(id):
            await socket.close()
            return False
        await socket.accept()
        self.sockets[id] = socket
        self.connected[id] = True
        return True

    def disconnect(self, id: UUID) -> None:
        """
        Mark a user as disconnected without removing them.
        """
        self.connected[id] = False

    def remove(self, id: UUID) -> None:
        """
        Permanently remove a user.
        """
        self.sockets.pop(id)
        self.connected.pop(id)
        self.locks.pop(id)

    async def send(self, id: UUID, data: Data) -> None:
        """
        Send a JSON message to a specific connected user.
        """
        if id in self.sockets and self.connected[id]:
            await self.sockets[id].send_json(data)

    async def broadcast(self, ids: list[UUID], data: Data) -> None:
        """
        Send a JSON message to multiple users.
        """
        for id in ids:
            try:
                await self.send(id, data)
            except Exception:
                pass
