import uuid
from typing import Any

import pytest

from app.game_state.BoardState import DEFAULT_ROUNDS
from app.game_state.pools import CATALOG
from app.game_state.Room import Room
from app.schemas import Emitter


async def _collect_emitter(events: list[dict[str, Any]]) -> Any:
    async def emitter(data: dict[str, Any]) -> None:
        events.append(data)

    return emitter


def _make_room(emitter: Emitter) -> Room:
    entry = CATALOG[0]
    board = entry.pool.generate(0)
    return Room(uuid.uuid4(), emitter, board, entry.id, 0, DEFAULT_ROUNDS)


@pytest.mark.asyncio
async def test_timeout_answers_noop_if_state_changed() -> None:
    events: list[dict[str, Any]] = []
    emitter = await _collect_emitter(events)

    room = _make_room(emitter)
    room.state = "settling_round"

    await room._timeout_answers()

    assert room.state == "settling_round"
    assert events == []


@pytest.mark.asyncio
async def test_cancel_timer_stops_pending_task() -> None:
    events: list[dict[str, Any]] = []
    emitter = await _collect_emitter(events)

    room = _make_room(emitter)
    room.round_time = 60
    room.state = "awaiting_answers"
    room._start_timer(room._timeout_answers)

    assert room.timer_task is not None
    room.cancel_timer()
    assert room.timer_task is None
    assert room.state == "awaiting_answers"
