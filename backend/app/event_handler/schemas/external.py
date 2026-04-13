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


class ChangeStateEvent(ExternalEvent):
    type: Literal["change_state"]


class AnswerEvent(ExternalEvent):
    type: Literal["answer"]
    answer: int
