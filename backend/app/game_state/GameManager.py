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

    async def host(self, host_id: UUID) -> str:
        """
        Create a new room.
        """
        if host_id in self.player_room:
            await self.player_disconnect(host_id)
        room_id = f"{randbelow(10**10):010}"
        self.rooms[room_id] = Room(host_id, self.emit_event)
        self.player_room[host_id] = room_id
        return room_id

    async def join(self, player_id: UUID, room_id: str, nickname: str) -> None:
        """
        Join a player to a room.
        """
        if player_id in self.player_room:
            await self.player_disconnect(player_id)
        room = self.rooms.get(room_id)
        if room is None:
            await self._error(player_id, "The room does not exist.")
            return

        if room.state != "awaiting_start":
            await self._error(player_id, "The game has already started or ended.")
            return

        for player in room.players.values():
            if player.nickname == nickname:
                await self._error(
                    player_id, f"The nickname '{nickname}' is already taken in this room."
                )
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
        await room.next_stage()

    async def close_room(self, host: UUID) -> bool:
        room_id = self.player_room.get(host)
        if room_id is None:
            await self._error(host, "You cannot close this room now.")
            return False
        room = self.rooms[room_id]
        if not room.is_host(host):
            await self._error(host, "You cannot close this room now.")
            return False
        self.player_room.pop(host)
        abandoned_players = list(room.players.keys())
        for player in abandoned_players:
            self.player_room.pop(player)
        self.rooms.pop(room_id)
        await self.emit_event({"type": "room_destroyed", "notify": abandoned_players})
        return True

    async def player_disconnect(self, player_id: UUID) -> None:
        """
        Remove a player from the game.
        """
        room_id = self.player_room.get(player_id)
        if room_id is None:
            return
        room = self.rooms[room_id]
        if room.host == player_id:
            await self.close_room(player_id)
            return

        player = room.get_player(player_id)
        self.player_room.pop(player_id)
        await room.remove_player(player_id)
        name = player.nickname
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
            await room.win_round()

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
        await room.next_stage()

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
        await room.end_settling()

    async def kick(self, host_id: UUID, nickname: str) -> None:
        """
        Kick a player out of the room.
        """
        room = self.get_room(host_id)
        if room is None or not room.is_host(host_id):
            await self._error(host_id, "You cannot kick this player out.")
            return
        ii = await room.kick(nickname)
        if ii is not None:
            del self.player_room[ii]
            await self.emit_event(
                {"type": "kick", "notify": [host_id], "nickname": nickname, "player_id": ii}
            )

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
