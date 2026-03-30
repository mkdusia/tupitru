from pydantic import BaseModel
from typing import Literal
from uuid import UUID


class HostEvent(BaseModel):
    type: Literal["host"]
    id: UUID


class JoinEvent(BaseModel):
    type: Literal["join"]
    id: UUID
    room_id: str
    nickname: str


class GameStartEvent(BaseModel):
    type: Literal["game_start"]
    id: UUID
    room_id: str
