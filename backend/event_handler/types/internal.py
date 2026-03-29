from uuid import UUID
from pydantic import BaseModel
from typing import Literal


class InternalGameStartEvent(BaseModel):
    type: Literal["game_start"]
    notify: list[UUID]


class PlayerJoinedEvent(BaseModel):
    type: Literal["player_joined"]
    notify: list[UUID]
    nickname: str


class DisconnectEvent(BaseModel):
    type: Literal["disconnect"]
    id: UUID


class PlayerDisconnectEvent(BaseModel):
    type: Literal["player_disconnected"]
    notify: list[UUID]
    nickname: str


class RoomDestroyedEvent(BaseModel):
    type: Literal["room_destroyed"]
    notify: list[UUID]
