import uuid

import pytest
from app.game_state.GameManager import GameManager


class DummyEmitter:
    def __init__(self) -> None:
        self.events = []

    async def __call__(self, event) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_host_closes_previous_room_when_rehosting() -> None:
    manager = GameManager()
    emitter = DummyEmitter()
    manager.set_emitter(emitter)

    host_id = uuid.uuid4()
    old_room_id = await manager.host(host_id)
    assert old_room_id in manager.rooms

    new_room_id = await manager.host(host_id)
    assert new_room_id in manager.rooms
    assert old_room_id not in manager.rooms


@pytest.mark.asyncio
async def test_join_removes_player_from_previous_room() -> None:
    manager = GameManager()
    emitter = DummyEmitter()
    manager.set_emitter(emitter)

    host_a = uuid.uuid4()
    room_a = await manager.host(host_a)

    host_b = uuid.uuid4()
    room_b = await manager.host(host_b)

    player = uuid.uuid4()
    await manager.join(player, room_a, "player")
    assert manager.player_room[player] == room_a
    assert player in manager.rooms[room_a].players

    await manager.join(player, room_b, "player")
    assert manager.player_room[player] == room_b
    assert player in manager.rooms[room_b].players
    assert player not in manager.rooms[room_a].players


@pytest.mark.asyncio
async def test_disconnect_current_respondent_advances_round() -> None:
    manager = GameManager()
    emitter = DummyEmitter()
    manager.set_emitter(emitter)

    host_id = uuid.uuid4()
    room_id = await manager.host(host_id)
    room = manager.rooms[room_id]

    player_a = uuid.uuid4()
    player_b = uuid.uuid4()
    await manager.join(player_a, room_id, "A")
    await manager.join(player_b, room_id, "B")

    await room.start_game(emitter)
    room.set_answer(player_a, 3)
    room.set_answer(player_b, 2)
    await room.settle_round(emitter)

    current = room.current_respondent.id
    await manager.player_disconnect(current)

    assert room.state == "settling_round"
    assert room.current_respondent.id != current
    assert any(event["type"] == "player_disconnected" for event in emitter.events)
