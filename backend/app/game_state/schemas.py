from typing import Literal

RoomStatus = (
    Literal["awaiting_start"]
    | Literal["awaiting_answers"]
    | Literal["settling_round"]
    | Literal["game_ended"]
)
