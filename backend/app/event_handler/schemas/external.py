from pydantic import BaseModel
from typing import Literal
from uuid import UUID
from app.game_state.schemas import Mole, Direction


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


class RespondEvent(ExternalEvent):
    type: Literal["respond"]
    mole: Mole
    direction: Direction


class GiveUpEvent(ExternalEvent):
    type: Literal["give_up"]


class RevertEvent(ExternalEvent):
    type: Literal["revert"]


class SkipEvent(ExternalEvent):
    type: Literal["skip_round"]
