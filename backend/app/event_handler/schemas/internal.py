from uuid import UUID
from pydantic import BaseModel
from typing import Literal
from app.game_state.BoardState import BoardData


class InternalGameStartEvent(BaseModel):
    type: Literal["game_start"]
    notify: list[UUID]
    board: BoardData


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
    respondent: str


class RespondEvent(BaseModel):
    type: Literal["respond"]
    notify: UUID


class AnswerEvent(BaseModel):
    type: Literal["answer"]
    notify: list[UUID]
    player_id: UUID
    nickname: str
    answer: int


class PropagateError(BaseModel):
    type: Literal["propagate_error"]
    message: str
    recipient: UUID


class ResponseReceivedEvent(BaseModel):
    type: Literal["response_received"]
    notify: list[UUID]
    player_id: UUID
    board: BoardData


class GiveUpEvent(BaseModel):
    type: Literal["give_up"]
    notify: list[UUID]
    player_id: UUID
    board: BoardData


class RevertEvent(BaseModel):
    type: Literal["revert"]
    notify: list[UUID]
    player_id: UUID
    board: BoardData
