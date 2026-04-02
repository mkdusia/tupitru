from uuid import UUID


class Player:
    def __init__(self, id: UUID, nickname: str) -> None:
        self.nickname: str = nickname
        self.id: UUID = id
        self.answer: int = -1
