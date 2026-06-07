import uuid
from typing import Any

import pytest
from pydantic import ValidationError

from app.event_handler.schemas.external import ChangeStateEvent, HostEvent, StartGameEvent
from app.game_state.GameManager import GameManager
from app.game_state.pools import CATALOG


def _manager_with_capture() -> tuple[GameManager, list[dict[str, Any]]]:
    manager = GameManager()
    events: list[dict[str, Any]] = []

    async def emitter(event: dict[str, Any]) -> None:
        events.append(event)

    manager.set_emitter(emitter)
    return manager, events


@pytest.mark.asyncio
async def test_host_creates_room_with_default_pool() -> None:
    manager, _ = _manager_with_capture()
    room_id = await manager.host(uuid.uuid4())
    assert isinstance(room_id, str)
    room = manager.rooms[room_id]
    assert room.pool_id == CATALOG[0].id
    assert isinstance(room.seed, int)


@pytest.mark.asyncio
async def test_start_game_applies_config_and_starts() -> None:
    manager, _ = _manager_with_capture()
    host_id = uuid.uuid4()
    room_id = await manager.host(host_id)
    await manager.start_game(host_id, pool_id="random_7x7", seed=42, rounds=3)
    room = manager.rooms[room_id]
    assert room.pool_id == "random_7x7"
    assert room.seed == 42
    assert room.state == "awaiting_answers"


@pytest.mark.asyncio
async def test_start_game_rejects_unknown_pool() -> None:
    manager, events = _manager_with_capture()
    host_id = uuid.uuid4()
    room_id = await manager.host(host_id)
    await manager.start_game(host_id, pool_id="does_not_exist", seed=0, rounds=3)
    room = manager.rooms[room_id]
    assert room.state == "awaiting_start"
    assert any(e.get("type") == "propagate_error" for e in events)


@pytest.mark.asyncio
async def test_change_state_refuses_to_start_from_lobby() -> None:
    manager, events = _manager_with_capture()
    host_id = uuid.uuid4()
    room_id = await manager.host(host_id)
    await manager.change_game_state(host_id)
    room = manager.rooms[room_id]
    assert room.state == "awaiting_start"
    assert any(e.get("type") == "propagate_error" for e in events)


def test_host_event_parses_without_config() -> None:
    event = HostEvent(type="host", id=uuid.uuid4())
    assert event.type == "host"


def test_change_state_event_parses_bare() -> None:
    event = ChangeStateEvent(type="change_state", id=uuid.uuid4())
    assert event.type == "change_state"


def test_start_game_event_accepts_config_range() -> None:
    StartGameEvent(type="start_game", id=uuid.uuid4(), pool_id="random_7x7", seed=0, rounds=1)
    StartGameEvent(
        type="start_game",
        id=uuid.uuid4(),
        pool_id="random_7x7",
        seed=2**32 - 1,
        rounds=50,
        round_time=30,
    )


def test_start_game_event_requires_config() -> None:
    with pytest.raises(ValidationError):
        StartGameEvent(type="start_game", id=uuid.uuid4())  # type: ignore[call-arg]


def test_start_game_event_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        StartGameEvent(type="start_game", id=uuid.uuid4(), pool_id="random_7x7", seed=-1, rounds=3)
    with pytest.raises(ValidationError):
        StartGameEvent(
            type="start_game", id=uuid.uuid4(), pool_id="random_7x7", seed=2**32, rounds=3
        )
    with pytest.raises(ValidationError):
        StartGameEvent(type="start_game", id=uuid.uuid4(), pool_id="random_7x7", seed=0, rounds=0)
    with pytest.raises(ValidationError):
        StartGameEvent(
            type="start_game",
            id=uuid.uuid4(),
            pool_id="random_7x7",
            seed=0,
            rounds=3,
            round_time=0,
        )
