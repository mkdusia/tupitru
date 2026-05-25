from uuid import UUID
from typing import Optional


class Player:
    def __init__(self, id: UUID, nickname: str) -> None:
        self.nickname: str = nickname
        self.id: UUID = id
        self.answer: int = 0
        self.answer_time: Optional[float] = None
        self.points = 0
