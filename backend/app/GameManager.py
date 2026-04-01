from typing import Any, Awaitable, Callable
from uuid import UUID
from secrets import randbelow


class GameManager:
    class Room:
        def __init__(self, host: UUID) -> None:
            self.host = host
            self.players: dict[UUID, str]
            self.players = {}

        def add_player(self, player: UUID, nickname: str) -> None:
            self.players[player] = nickname

        def remove_player(self, player: UUID) -> None:
            if player in self.players:
                self.players.pop(player)

    def __init__(self) -> None:
        self.emit_event: Callable[[dict[str, Any]], Awaitable[None]]
        self.rooms: dict[str, GameManager.Room]
        self.rooms = {}
        self.player_room: dict[UUID, str]
        self.player_room = {}

    def set_emitter(self, emitter: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        self.emit_event = emitter

    def host(self, host_id: UUID) -> str:
        room_id = f"{randbelow(10**10):010}"
        self.rooms[room_id] = self.Room(host_id)
        self.player_room[host_id] = room_id
        return room_id

    async def join(self, player_id: UUID, room_id: str, nickname: str) -> bool:
        room = self.rooms.get(room_id)
        if room is None:
            return False

        to_notify = list(room.players.keys())
        to_notify.append(room.host)

        room.add_player(player_id, nickname)
        self.player_room[player_id] = room_id

        await self.emit_event({"type": "player_joined", "notify": to_notify, "nickname": nickname})
        return True

    async def game_start(self, host_id: UUID, room_id: str) -> None:
        room = self.rooms.get(room_id)
        if room is None:
            return
        if room.host != host_id:
            return
        to_notify = list(room.players.keys())
        to_notify.append(room.host)
        await self.emit_event({"type": "game_start", "notify": to_notify})

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
