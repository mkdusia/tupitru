from typing import Any, Awaitable, Callable
from uuid import UUID
from secrets import randbelow
from .Room import Room
from app.schemas import Emitter


class GameManager:
    def __init__(self) -> None:
        self.emit_event: Emitter
        self.rooms: dict[str, Room]
        self.rooms = {}
        self.player_room: dict[UUID, str]
        self.player_room = {}

    def set_emitter(self, emitter: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        self.emit_event = emitter

    async def no_action_error(self, id: UUID) -> None:
        await self.emit_event(
            {
                "type": "propagate_error",
                "message": "The room does not exist or you do not have permission to access it.",
                "recipient": id,
            }
        )

    def host(self, host_id: UUID) -> str:
        room_id = f"{randbelow(10**10):010}"
        self.rooms[room_id] = Room(host_id)
        self.player_room[host_id] = room_id
        return room_id

    async def join(self, player_id: UUID, room_id: str, nickname: str) -> None:
        room = self.rooms.get(room_id)
        if room is None:
            await self.no_action_error(player_id)
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
        room_id = self.player_room.get(host_id)
        if room_id is None:
            await self.no_action_error(host_id)
            return
        room = self.rooms.get(room_id)
        if room is None or not room.can_change_state(host_id):
            await self.no_action_error(host_id)
            return
        await room.next_stage(self.emit_event)

    async def player_disconnect(self, player_id: UUID) -> None:
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
            name = room.players[player_id]
            room.remove_player(player_id)
            to_notify = list(room.players.keys())
            to_notify.append(room.host)
            await self.emit_event(
                {"type": "player_disconnected", "nickname": name, "notify": to_notify}
            )

    async def answer(self, player_id: UUID, answer: int) -> None:
        room_id = self.player_room.get(player_id)
        if room_id is None:
            await self.no_action_error(player_id)
            return
        room = self.rooms.get(room_id)
        if room is None or not room.can_answer(player_id):
            await self.no_action_error(player_id)
            return
        room.set_answer(player_id, answer)
