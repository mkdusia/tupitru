from typing import Literal

RoomStatus = (
    Literal["awaiting_start"]
    | Literal["awaiting_answers"]
    | Literal["settling_round"]
    | Literal["game_ended"]
)

Mole = Literal[0, 1, 2, 3, 4, 5]

Direction = Literal[0, 1, 2, 3]
