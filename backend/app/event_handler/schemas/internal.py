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
    player_id: UUID
    room_id: str


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


class PropagateErrorEvent(BaseModel):
    type: Literal["propagate_error"]
    message: str
    recipient: UUID


class InternalGameEndEvent(BaseModel):
    type: Literal["game_end"]
    notify: list[UUID]


class AwaitingResponseEvent(BaseModel):
    type: Literal["awaiting_response"]
    notify: list[UUID]


class RespondEvent(BaseModel):
    type: Literal["respond"]
    notify: UUID
