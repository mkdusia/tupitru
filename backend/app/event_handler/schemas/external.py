from pydantic import BaseModel
from typing import Literal
from uuid import UUID


class ExternalEvent(BaseModel):
    id: UUID


class HostEvent(ExternalEvent):
    type: Literal["host"]


class JoinEvent(ExternalEvent):
    type: Literal["join"]
    room_id: str
    nickname: str


class GameStartEvent(ExternalEvent):
    type: Literal["game_start"]
    room_id: str


class AnswerEvent(ExternalEvent):
    type: Literal["answer"]
    answer: int


class TimeUpEvent(ExternalEvent):
    type: Literal["time_up"]
