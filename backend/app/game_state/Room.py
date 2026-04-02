from uuid import UUID
from .Player import Player


class Room:
    def __init__(self, host: UUID) -> None:
        self.host = host
        self.players: dict[UUID, Player] = {}
        self.started: bool = False

    def add_player(self, player: UUID, nickname: str) -> None:
        self.players[player] = Player(player, nickname)

    def remove_player(self, player: UUID) -> None:
        if player in self.players:
            self.players.pop(player)

    def set_answer(self, player: UUID, answer: int) -> None:
        self.players[player].answer = answer
        print("Setting answer")

    def settle_round(self) -> list[Player]:
        players: list[Player] = list(self.players.values()).copy()
        players.sort(key=lambda player: player.answer, reverse=True)
        return players
