from uuid import UUID
from secrets import randbelow
from typing import Any
from .Room import Room
from app.schemas import Emitter
from .schemas import Mole, Direction


class GameManager:
    def __init__(self) -> None:
        self.emit_event: Emitter
        self.rooms: dict[str, Room]
        self.rooms = {}
        self.player_room: dict[UUID, str]
        self.player_room = {}

    def set_emitter(self, emitter: Emitter) -> None:
        """
        Set the emitter that broadcasts events.
        """
        self.emit_event = emitter

    async def _error(self, id: UUID, message: str) -> None:
        """
        Broadcast an error.
        """
        await self.emit_event(
            {
                "type": "propagate_error",
                "message": message,
                "recipient": id,
            }
        )

    def get_room(self, player_id: UUID) -> None | Room:
        """
        Get the room object of a player.
        """
        room_id = self.player_room.get(player_id)
        if room_id is None:
            return None
        return self.rooms.get(room_id)

    def host(self, host_id: UUID) -> str:
        """
        Create a new room.
        """
        room_id = f"{randbelow(10**10):010}"
        self.rooms[room_id] = Room(host_id)
        self.player_room[host_id] = room_id
        return room_id

    async def join(self, player_id: UUID, room_id: str, nickname: str) -> None:
        """
        Join a player to a room.
        """
        room = self.rooms.get(room_id)
        if room is None:
            await self._error(player_id, "The room does not exist.")
            return

        to_notify = list(room.players.keys())
        to_notify.append(room.host)
        room.add_player(player_id, nickname)
        self.player_room[player_id] = room_id
        await self.emit_event(
            {
                "type": "player_joined",
                "notify": to_notify,
                "nickname": nickname,
                "player_id": player_id,
                "room_id": room_id,
            }
        )

    async def change_game_state(self, host_id: UUID) -> None:
        """
        Change the state of the game in the room with the given host.
        """
        room = self.get_room(host_id)
        if room is None or not room.can_change_state(host_id):
            await self._error(host_id, "You do not have permission to perform this action.")
            return
        await room.next_stage(self.emit_event)

    async def player_disconnect(self, player_id: UUID) -> None:
        """
        Remove a player from the game.
        """
        room_id = self.player_room.get(player_id)
        if room_id is None:
            return
        room = self.rooms[room_id]
        self.player_room.pop(player_id)
        if room.host == player_id:
            abandoned_players = list(room.players.keys())
            for player in abandoned_players:
                self.player_room.pop(player)
            self.rooms.pop(room_id)
            await self.emit_event({"type": "room_destroyed", "notify": abandoned_players})
        else:
            name = room.players[player_id].nickname
            room.remove_player(player_id)
            to_notify = list(room.players.keys())
            to_notify.append(room.host)
            await self.emit_event(
                {"type": "player_disconnected", "nickname": name, "notify": to_notify}
            )

    async def answer(self, player_id: UUID, answer: int) -> None:
        """
        Save the answer of a player.
        """
        room = self.get_room(player_id)
        if room is None or not room.can_answer(player_id):
            await self._error(player_id, "You cannot give your answer now.")
            return
        room.set_answer(player_id, answer)
        nickname = room.get_player(player_id).nickname
        await self.emit_event(
            {
                "type": "answer",
                "notify": [room.host],
                "player_id": player_id,
                "nickname": nickname,
                "answer": answer,
            }
        )

    async def respond(self, player_id: UUID, mole: Mole, direction: Direction) -> None:
        """
        Accept a move in a solution from a player.
        """
        room = self.get_room(player_id)
        if room is None or not room.respond(player_id, mole, direction):
            await self._error(player_id, "You cannot give your response now.")
            return
        await self.emit_event(
            {
                "type": "response_received",
                "notify": [room.host],
                "player_id": player_id,
                "board": room.board_state.data,
            }
        )
        if room.is_response_full():
            await room.win_round(self.emit_event)

    async def give_up(self, player_id: UUID) -> None:
        """
        Allow a player to give up providing their solution.
        """
        room = self.get_room(player_id)
        if room is None or not room.give_up(player_id):
            await self._error(player_id, "You cannot end your response now.")
            return
        await self.emit_event(
            {
                "type": "give_up",
                "notify": [room.host],
                "player_id": player_id,
                "board": room.board_state.data,
            }
        )
        await room.next_stage(self.emit_event)

    async def revert_move(self, player_id: UUID) -> None:
        """
        Revert the last move a player made.
        """
        room = self.get_room(player_id)
        if room is None or not room.revert_move(player_id):
            await self._error(player_id, "You cannot revert your move.")
            return
        await self.emit_event(
            {
                "type": "revert",
                "notify": [room.host],
                "player_id": player_id,
                "board": room.board_state.data,
            }
        )

    async def skip(self, host_id: UUID) -> None:
        """
        End a round before the players provide their solutions.
        """
        room = self.get_room(host_id)
        if room is None or not room.can_skip_round(host_id):
            await self._error(host_id, "You do not have permission to perform this action.")
            return
        room.end_settling()
        await room.next_stage(self.emit_event)

    def get_state(self, id: UUID) -> dict[str, Any]:
        """
        Get the current state of the game a given user is in.
        """
        room = self.get_room(id)
        if room is None:
            return {"game_state": "no_game"}
        data = room.get_state(id)
        if data["host"]:
            data["room_id"] = self.player_room[id]
        return data
