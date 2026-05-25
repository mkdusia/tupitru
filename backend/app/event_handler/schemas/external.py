from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from app.game_state.schemas import Mole


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
    round_time: int | None = Field(default=None, gt=0)


class AnswerEvent(ExternalEvent):
    type: Literal["answer"]
    answer: int


class RespondEvent(ExternalEvent):
    type: Literal["respond"]
    mole: Mole
    direction: Literal["U", "R", "D", "L"]


class GiveUpEvent(ExternalEvent):
    type: Literal["give_up"]


class RevertEvent(ExternalEvent):
    type: Literal["revert"]


class SkipEvent(ExternalEvent):
    type: Literal["skip_round"]


class KickEvent(ExternalEvent):
    type: Literal["kick"]
    nickname: str


class CloseRoomEvent(ExternalEvent):
    type: Literal["close"]
