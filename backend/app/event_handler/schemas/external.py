from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.game_state.schemas import Mole


class ExternalEvent(BaseModel):
    id: UUID


class HostEvent(ExternalEvent):
    type: Literal["host"]


class JoinEvent(ExternalEvent):
    type: Literal["join"]
    room_id: str
    nickname: str


class StartGameEvent(ExternalEvent):
    type: Literal["start_game"]
    pool_id: str
    seed: int = Field(ge=0, lt=2**32)
    rounds: int = Field(ge=1, le=50)
    round_time: int | None = Field(default=None, gt=0)


class ChangeStateEvent(ExternalEvent):
    type: Literal["change_state"]


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


class TrainStartEvent(ExternalEvent):
    type: Literal["train_start"]
    pool_id: str | None = None
    seed: int | None = Field(default=None, ge=0, lt=2**32)


class TrainMoveEvent(ExternalEvent):
    type: Literal["train_move"]
    mole: Mole
    direction: Literal["U", "R", "D", "L"]


class TrainResetEvent(ExternalEvent):
    type: Literal["train_reset"]


class TrainNewEvent(ExternalEvent):
    type: Literal["train_new"]
    pool_id: str | None = None
    seed: int | None = Field(default=None, ge=0, lt=2**32)


class TrainExitEvent(ExternalEvent):
    type: Literal["train_exit"]
