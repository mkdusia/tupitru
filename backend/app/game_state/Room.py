import asyncio
from typing import Awaitable, Callable, Any
from uuid import UUID

from .BoardState import BoardState
from .schemas import Direction, Mole, RoomStatus
from .Player import Player
from app.schemas import Emitter
import time

_TimerAction = Callable[[], Awaitable[None]]


class Room:
    def __init__(self, host: UUID, emitter: Emitter) -> None:
        self.host: UUID = host
        self.emitter: Emitter = emitter

        self.players: dict[UUID, Player] = {}
        self.state: RoomStatus = "awaiting_start"
        self.announced_winner: bool = False
        self.ranking: list[Player] = []
        self.current_respondent: Player | None = None
        self.change_state: dict[RoomStatus, Callable[[], Awaitable[None]]] = {
            "awaiting_start": self.start_game,
            "awaiting_answers": self.settle_round,
            "settling_round": self.next_player,
            "game_ended": self.restart_game,
        }
        self.board_state = BoardState()
        self.round_time: int | None = None
        self.timer_task: asyncio.Task[None] | None = None

    def cancel_timer(self) -> None:
        if self.timer_task is not None:
            self.timer_task.cancel()
            self.timer_task = None

    def _start_timer(self, action: _TimerAction) -> None:
        self.cancel_timer()
        round_time = self.round_time
        if round_time is None:
            return
        self.timer_task = asyncio.create_task(self._run_timer(action, round_time))

    async def _run_timer(self, action: _TimerAction, delay: int) -> None:
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            return
        self.timer_task = None
        await action()

    async def _timeout_answers(self) -> None:
        if self.state == "awaiting_answers":
            await self.settle_round()

    async def _timeout_response(self) -> None:
        if self.state == "settling_round":
            self.board_state.clear()
            await self.next_player()

    def add_player(self, player: UUID, nickname: str) -> None:
        """
        Add a player to the room.
        """
        self.players[player] = Player(player, nickname)

    async def remove_player(self, player: UUID) -> None:
        """
        Remove a player from the room. Needs to be async in case we need to move to the next player.
        """
        if player in self.players:
            player_obj = self.players.pop(player)
            if player_obj in self.ranking:
                self.ranking.remove(player_obj)
            if self.current_respondent is not None and player == self.current_respondent.id:
                await self.next_player()

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

    def is_host(self, host: UUID) -> bool:
        """
        Check whether a given user is the host.
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
        pl = self.players[player]
        pl.answer = answer
        if answer > 0:
            pl.answer_time = time.time()
        else:
            pl.answer_time = None

    async def kick(self, nickname: str) -> UUID | None:
        """
        Kick a player out of the room.
        """
        for key, player in list(self.players.items()):
            if player.nickname == nickname:
                await self.remove_player(key)
                return key
        return None

    async def start_game(self) -> None:
        """
        Handle the start of the game.
        """
        self.state = "awaiting_answers"
        self.announced_winner = False
        for player in self.players.values():
            player.answer = 0
        to_notify = list(self.players.keys())
        to_notify.append(self.host)
        await self.emitter(
            {"type": "game_start", "notify": to_notify, "board": self.board_state.data}
        )
        self._start_timer(self._timeout_answers)

    async def settle_round(self) -> None:
        """
        Move into the phase of showing solutions.
        """
        self.state = "settling_round"
        self.ranking = list(self.players.values())
        self.ranking = list(filter(lambda player: player.answer > 0, self.ranking))
        self.ranking.sort(
            key=lambda player: (
                player.answer,
                player.answer_time if player.answer_time is not None else float("inf"),
            ),
            reverse=True,
        )
        await self.next_player()

    async def next_player(self) -> None:
        """
        Allow the next player to show their solution.
        """
        self.cancel_timer()
        to_notify = list(self.players.keys())
        to_notify.append(self.host)
        if len(self.ranking) == 0:
            if not self.announced_winner:
                self.announced_winner = True
                await self.emitter(
                    {
                        "type": "announce_winner",
                        "notify": to_notify,
                        "player_id": None,
                        "nickname": None,
                    }
                )
                return
            if not self.board_state.next_round():
                self.state = "game_ended"
                players = [
                    (player.points, player.nickname, player.id) for player in self.players.values()
                ]
                players.sort(key=lambda pr: pr[0], reverse=True)
                await self.emitter({"type": "game_end", "host": self.host, "ranking": players})
            else:
                await self.start_game()
            return

        self.current_respondent = self.ranking.pop()

        to_notify.remove(self.current_respondent.id)
        await self.emitter(
            {
                "type": "awaiting_response",
                "notify": to_notify,
                "respondent": self.current_respondent.nickname,
            }
        )
        await self.emitter(
            {
                "type": "respond",
                "notify": self.current_respondent.id,
                "board": self.board_state.data,
            }
        )
        self._start_timer(self._timeout_response)

    async def restart_game(self) -> None:
        """
        Start the ended game with a new board
        """
        self.board_state = BoardState()
        await self.start_game()

    async def next_stage(self) -> None:
        """
        Change the state of the game
        """
        await self.change_state[self.state]()

    def respond(self, player: UUID, mole: Mole, direction: Direction) -> bool:
        """
        Accept a response from a player.
        """
        if self.current_respondent is None or player != self.current_respondent.id:
            return False
        pl = self.players[player]
        if self.board_state.moves < pl.answer:
            self.board_state.modify(mole, direction)
        return True

    def is_response_full(self) -> bool:
        """
        Check whether a solution is complete.
        """
        return self.current_respondent is not None and self.board_state.finish_state()

    async def win_round(self) -> None:
        """
        Handle the end of a round.
        """
        if self.state == "settling_round" and self.current_respondent is not None:
            self.announced_winner = True
            self.current_respondent.points += 1
            to_notify = list(self.players.keys())
            to_notify.append(self.host)
            to_notify.remove(self.current_respondent.id)
            await self.emitter(
                {
                    "type": "announce_winner",
                    "notify": to_notify,
                    "player_id": self.current_respondent.id,
                    "nickname": self.current_respondent.nickname,
                }
            )
            self.current_respondent = None
            self.board_state.flush()
            self.ranking = []

    async def end_settling(self) -> None:
        """
        End a round before the players provide their solutions.
        """
        if self.state == "settling_round":
            self.board_state.clear()
            self.ranking = []
            await self.next_stage()

    def give_up(self, player: UUID) -> bool:
        """
        Allow a player to give up providing a solution.
        """
        if self.current_respondent is None or player != self.current_respondent.id:
            return False
        self.board_state.clear()
        return True

    def revert_move(self, player: UUID) -> bool:
        """
        Revert the last move of a player.
        """
        if (
            self.state != "settling_round"
            or self.current_respondent is None
            or player != self.current_respondent.id
        ):
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
        if res["game_state"] == "settling_round" and self.current_respondent is not None:
            res["respondent"] = self.current_respondent.nickname

        ranking = sorted(
            [(player.points, player.nickname) for player in self.players.values()],
            key=lambda pr: pr[0],
        )

        if not res["host"]:
            player = self.get_player(id)
            res["nickname"] = player.nickname
            if res["game_state"] == "awaiting_answers" or res["game_state"] == "settling_round":
                res["answer"] = player.answer
            if res["game_state"] == "settling_round" and self.current_respondent is not None:
                res["respond"] = self.current_respondent.id == id
                if res["respond"]:
                    res["board"] = self.board_state.data.model_dump()
            if res["game_state"] == "game_ended":
                nick = self.get_player(id).nickname
                for i, (pt, nc) in enumerate(ranking):
                    if nick == nc:
                        res["score"] = pt
                        res["position"] = i
                        break
        else:
            if res["game_state"] == "awaiting_start":
                res["nicknames"] = [player.nickname for player in self.players.values()]
            if res["game_state"] == "awaiting_answers":
                answers_sorted = sorted(
                    self.players.values(),
                    key=lambda p: (
                        p.answer,
                        p.answer_time if p.answer_time is not None else float("inf"),
                    ),
                )
                res["answers"] = [(p.answer, p.nickname) for p in answers_sorted]
            if res["game_state"] == "awaiting_answers" or res["game_state"] == "settling_round":
                res["board"] = self.board_state.data.model_dump()
            if res["game_state"] == "settling_round" and self.current_respondent is not None:
                res["answer"] = self.current_respondent.answer
            if res["game_state"] == "game_ended":
                res["ranking"] = ranking
        return res
