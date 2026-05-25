import uuid
import pytest
from typing import Any

from app.game_state.Room import Room


async def _collect_emitter(events: list[dict[str, Any]]) -> Any:
    async def emitter(data: dict[str, Any]) -> None:
        events.append(data)

    return emitter


@pytest.mark.asyncio
async def test_timeout_answers_noop_if_state_changed() -> None:
    events: list[dict[str, Any]] = []
    emitter = await _collect_emitter(events)

    room = Room(uuid.uuid4(), emitter)
    room.state = "settling_round"  # already advanced

    await room._timeout_answers()

    assert room.state == "settling_round"
    assert events == []


@pytest.mark.asyncio
async def test_cancel_timer_stops_pending_task() -> None:
    events: list[dict[str, Any]] = []
    emitter = await _collect_emitter(events)

    room = Room(uuid.uuid4(), emitter)
    room.round_time = 60
    room.state = "awaiting_answers"
    room._start_timer(room._timeout_answers)

    assert room.timer_task is not None
    room.cancel_timer()
    assert room.timer_task is None
    # state unchanged — timer was cancelled before firing
    assert room.state == "awaiting_answers"
