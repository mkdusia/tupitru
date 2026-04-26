from typing import Awaitable, Callable, Any
from uuid import UUID

from .BoardState import BoardState
from .schemas import Direction, Mole, RoomStatus
from .Player import Player
from app.schemas import Emitter


class Room:
    def __init__(self, host: UUID) -> None:
        self.host = host

        self.players: dict[UUID, Player] = {}
        self.state: RoomStatus = "awaiting_start"
        self.ranking: list[Player] = []
        self.current_respondent: Player
        self.change_state: dict[RoomStatus, Callable[[Emitter], Awaitable[None]]] = {
            "awaiting_start": self.start_game,
            "awaiting_answers": self.settle_round,
            "settling_round": self.next_player,
            "game_ended": self.restart_game,
        }
        self.board_state = BoardState()

    def add_player(self, player: UUID, nickname: str) -> None:
        """
        Add a player to the room.
        """
        self.players[player] = Player(player, nickname)

    def remove_player(self, player: UUID) -> None:
        """
        Remove a player from the room.
        """
        if player in self.players:
            self.players.pop(player)

    def get_player(self, player: UUID) -> Player:
        """
        Get player object with the given id.
        """
        return self.players[player]

    def can_change_state(self, host: UUID) -> bool:
        """
        Check whether a given user can change the state of this room.
        """
        return self.host == host

    def can_skip_round(self, host: UUID) -> bool:
        """
        Check whether a given user can skip a round in this room.
        """
        return self.host == host and self.state == "settling_round"

    def can_answer(self, id: UUID) -> bool:
        """
        Check whether a given user can provide an answer in this room.
        """
        return not (self.state != "awaiting_answers" or self.players.get(id) is None)

    def set_answer(self, player: UUID, answer: int) -> None:
        """
        Set a players answer.
        """
        self.players[player].answer = answer

    async def start_game(self, emitter: Emitter) -> None:
        """
        Handle the start of the game.
        """
        self.state = "awaiting_answers"
        for player in self.players.values():
            player.answer = 0
        to_notify = list(self.players.keys())
        to_notify.append(self.host)
        await emitter({"type": "game_start", "notify": to_notify, "board": self.board_state.data})

    async def settle_round(self, emitter: Emitter) -> None:
        """
        Move into the phase of showing solutions.
        """
        self.state = "settling_round"
        self.ranking = list(self.players.values())
        self.ranking = list(filter(lambda player: player.answer > 0, self.ranking))
        self.ranking.sort(key=lambda player: player.answer, reverse=True)
        await self.next_player(emitter)

    async def next_player(self, emitter: Emitter) -> None:
        """
        Allow the next player to show their solution.
        """
        to_notify = list(self.players.keys())
        to_notify.append(self.host)
        if len(self.ranking) == 0:
            if not self.board_state.next_round():
                self.state = "game_ended"
                players = [(player.points, player.nickname) for player in self.players.values()]
                players.sort(key=lambda pr: pr[0])
                await emitter({"type": "game_end", "notify": to_notify, "ranking": players})
            else:
                await self.start_game(emitter)
            return

        self.current_respondent = self.ranking.pop()
        to_notify.remove(self.current_respondent.id)
        await emitter(
            {
                "type": "awaiting_response",
                "notify": to_notify,
                "respondent": self.current_respondent.nickname,
            }
        )
        await emitter(
            {
                "type": "respond",
                "notify": self.current_respondent.id,
                "board": self.board_state.data,
            }
        )

    async def restart_game(self, emitter: Emitter) -> None:
        """
        Start the ended game with a new board
        """
        self.board_state = BoardState()
        await self.start_game(emitter)

    async def next_stage(self, emitter: Emitter) -> None:
        """
        Change the state of the game
        """
        await self.change_state[self.state](emitter)

    def respond(self, player: UUID, mole: Mole, direction: Direction) -> bool:
        """
        Accept a response from a player.
        """
        if self.state != "settling_round" or player != self.current_respondent.id:
            return False
        pl = self.players[player]
        if self.board_state.moves < pl.answer:
            self.board_state.modify(mole, direction)
        return True

    def is_response_full(self) -> bool:
        """
        Check whether a solution is complete.
        """
        return self.state == "settling_round" and self.board_state.finish_state()

    async def win_round(self, emitter: Emitter) -> None:
        """
        Handle the end of a round.
        """
        if self.state == "settling_round":
            self.current_respondent.points += 1
            await emitter(
                {
                    "type": "announce_winner",
                    "notify": [self.host],
                    "player_id": self.current_respondent.id,
                    "nickname": self.current_respondent.nickname,
                }
            )
            self.board_state.flush()
            self.ranking = []
            await self.next_stage(emitter)

    def end_settling(self) -> None:
        """
        End a round before the players provide their solutions.
        """
        if self.state == "settling_round":
            self.board_state.clear()
            self.ranking = []

    def give_up(self, player: UUID) -> bool:
        """
        Allow a player to give up providing a solution.
        """
        if self.state != "settling_round" or player != self.current_respondent.id:
            return False
        self.board_state.clear()
        return True

    def revert_move(self, player: UUID) -> bool:
        """
        Revert the last move of a player.
        """
        if self.state != "settling_round" or player != self.current_respondent.id:
            return False
        self.board_state.revert()
        return True

    def get_state(self, id: UUID) -> dict[str, Any]:
        """
        Get the current game state for a given player.
        """
        res: dict[str, Any] = {}
        res["game_state"] = self.state
        res["host"] = id == self.host
        if not res["host"]:
            player = self.get_player(id)
            res["nickname"] = player.nickname
            if res["game_state"] == "awaiting_answers" or res["game_state"] == "settling_round":
                res["answer"] = player.answer
            if res["game_state"] == "settling_round":
                res["respond"] = self.current_respondent.id == id
                if res["respond"]:
                    res["board"] = self.board_state.data.model_dump()
        else:
            if res["game_state"] == "awaiting_answers" or res["game_state"] == "settling_round":
                res["board"] = self.board_state.data.model_dump()
            if res["game_state"] == "settling_round":
                res["respondent"] = self.current_respondent.nickname
                res["answer"] = self.current_respondent.answer
            if res["game_state"] == "game_ended":
                res["ranking"] = sorted(
                    [(player.points, player.nickname) for player in self.players.values()],
                    key=lambda pr: pr[0],
                )
        return res
