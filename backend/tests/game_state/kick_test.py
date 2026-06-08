import uuid
from typing import Any

import pytest

from app.ConnectionManager import ConnectionManager
from app.event_handler import EventHandler
from app.game_state.GameManager import GameManager
from app.game_state.Training import TrainingManager


class FakeWebSocket:
    """Minimal stand-in for a Starlette WebSocket used by ConnectionManager."""

    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []
        self.closed = False

    async def accept(self) -> None:
        pass

    async def send_json(self, data: dict[str, Any]) -> None:
        self.sent.append(data)

    async def close(self) -> None:
        self.closed = True


def _build_stack() -> tuple[EventHandler, ConnectionManager, GameManager]:
    con = ConnectionManager()
    game = GameManager()
    training = TrainingManager()
    handler = EventHandler(con, game, training)
    game.set_emitter(lambda event: handler.handle(event, "internal"))
    return handler, con, game


async def _connect(con: ConnectionManager) -> tuple[uuid.UUID, FakeWebSocket]:
    socket = FakeWebSocket()
    user_id = await con.connect(socket)  # type: ignore[arg-type]
    return user_id, socket


# --- GameManager data layer: the nickname must be free right after a kick. ---


@pytest.mark.asyncio
async def test_kick_frees_nickname_for_a_new_player() -> None:
    manager = GameManager()
    events: list[dict[str, Any]] = []

    async def emitter(event: dict[str, Any]) -> None:
        events.append(event)

    manager.set_emitter(emitter)

    host_id = uuid.uuid4()
    room_id = await manager.host(host_id)

    bob = uuid.uuid4()
    await manager.join(bob, room_id, "Bob")
    await manager.kick(host_id, "Bob")

    assert bob not in manager.rooms[room_id].players
    assert bob not in manager.player_room

    events.clear()
    newcomer = uuid.uuid4()
    await manager.join(newcomer, room_id, "Bob")

    assert newcomer in manager.rooms[room_id].players
    assert manager.rooms[room_id].players[newcomer].nickname == "Bob"
    assert not any(e.get("type") == "propagate_error" for e in events)


@pytest.mark.asyncio
async def test_kicked_player_can_rejoin_with_same_nickname() -> None:
    manager = GameManager()

    async def emitter(event: dict[str, Any]) -> None:
        pass

    manager.set_emitter(emitter)

    host_id = uuid.uuid4()
    room_id = await manager.host(host_id)

    bob = uuid.uuid4()
    await manager.join(bob, room_id, "Bob")
    await manager.kick(host_id, "Bob")
    await manager.join(bob, room_id, "Bob")

    assert bob in manager.rooms[room_id].players


# --- Connection layer: a kicked player must be fully disconnected. ---


@pytest.mark.asyncio
async def test_kick_closes_and_removes_kicked_connection() -> None:
    handler, con, game = _build_stack()

    host_id, _ = await _connect(con)
    bob_id, bob_socket = await _connect(con)

    await handler.handle({"type": "host", "id": host_id}, "external")
    room_id = game.player_room[host_id]
    await handler.handle(
        {"type": "join", "id": bob_id, "room_id": room_id, "nickname": "Bob"}, "external"
    )
    assert bob_id in game.rooms[room_id].players

    await handler.handle({"type": "kick", "id": host_id, "nickname": "Bob"}, "external")

    # The kicked player got notified, their socket was closed and all of their
    # connection bookkeeping was dropped (so their user_id is now invalid).
    assert {"type": "info", "message": "kick"} in bob_socket.sent
    assert bob_socket.closed is True
    assert bob_id not in con.sockets
    assert con.get_lock(bob_id) is None
    assert bob_id not in game.player_room
    assert bob_id not in game.rooms[room_id].players


@pytest.mark.asyncio
async def test_new_player_takes_nickname_through_full_handler_stack() -> None:
    handler, con, game = _build_stack()

    host_id, _ = await _connect(con)
    bob_id, _ = await _connect(con)

    await handler.handle({"type": "host", "id": host_id}, "external")
    room_id = game.player_room[host_id]
    await handler.handle(
        {"type": "join", "id": bob_id, "room_id": room_id, "nickname": "Bob"}, "external"
    )
    await handler.handle({"type": "kick", "id": host_id, "nickname": "Bob"}, "external")

    charlie_id, charlie_socket = await _connect(con)
    await handler.handle(
        {"type": "join", "id": charlie_id, "room_id": room_id, "nickname": "Bob"}, "external"
    )

    assert charlie_id in game.rooms[room_id].players
    assert game.rooms[room_id].players[charlie_id].nickname == "Bob"
    assert not any(msg.get("type") == "error" for msg in charlie_socket.sent)


@pytest.mark.asyncio
async def test_kicking_unknown_nickname_is_noop() -> None:
    handler, con, game = _build_stack()

    host_id, host_socket = await _connect(con)
    await handler.handle({"type": "host", "id": host_id}, "external")
    room_id = game.player_room[host_id]

    host_socket.sent.clear()
    await handler.handle({"type": "kick", "id": host_id, "nickname": "Nobody"}, "external")

    assert not any(msg.get("message") == "kick" for msg in host_socket.sent)
    assert game.rooms[room_id].players == {}
