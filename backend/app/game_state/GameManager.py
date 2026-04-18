from uuid import UUID
from secrets import randbelow
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
        self.emit_event = emitter

    async def error(self, id: UUID, message: str) -> None:
        await self.emit_event(
            {
                "type": "propagate_error",
                "message": message,
                "recipient": id,
            }
        )

    def get_room(self, player_id: UUID) -> None | Room:
        room_id = self.player_room.get(player_id)
        if room_id is None:
            return None
        return self.rooms.get(room_id)

    def host(self, host_id: UUID) -> str:
        room_id = f"{randbelow(10**10):010}"
        self.rooms[room_id] = Room(host_id)
        self.player_room[host_id] = room_id
        return room_id

    async def join(self, player_id: UUID, room_id: str, nickname: str) -> None:
        room = self.rooms.get(room_id)
        if room is None:
            await self.error(player_id, "The room does not exist.")
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
        room = self.get_room(host_id)
        if room is None or not room.can_change_state(host_id):
            await self.error(host_id, "You do not have permission to perform this action.")
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
            name = room.players[player_id].nickname
            room.remove_player(player_id)
            to_notify = list(room.players.keys())
            to_notify.append(room.host)
            await self.emit_event(
                {"type": "player_disconnected", "nickname": name, "notify": to_notify}
            )

    async def answer(self, player_id: UUID, answer: int) -> None:
        room = self.get_room(player_id)
        if room is None or not room.can_answer(player_id):
            await self.error(player_id, "You cannot give your answer now.")
            return
        room.set_answer(player_id, answer)
        player = room.get_player(player_id)
        nickname = ""
        if player is not None:
            nickname = player.nickname
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
        room = self.get_room(player_id)
        if room is None or not room.respond(player_id, mole, direction):
            await self.error(player_id, "You cannot give your response now.")
            return
        await self.emit_event(
            {"type": "response_received", "notify": [room.host], "player_id": player_id}
        )
        if room.is_response_full():
            room.end_settling()
            await room.next_stage(self.emit_event)

    async def give_up(self, player_id: UUID) -> None:
        room = self.get_room(player_id)
        if room is None or not room.give_up(player_id):
            await self.error(player_id, "You cannot end your response now.")
            return
        await self.emit_event({"type": "give_up", "notify": [room.host], "player_id": player_id})
        await room.next_stage(self.emit_event)

    async def revert_move(self, player_id: UUID) -> None:
        room = self.get_room(player_id)
        if room is None or not room.revert_move(player_id):
            await self.error(player_id, "You cannot revert your move.")
            return
        await self.emit_event({"type": "revert", "notify": [room.host], "player_id": player_id})
