import uuid
import pytest
from app.GameManager import GameManager


@pytest.mark.asyncio
async def test_host() -> None:
    manager = GameManager()
    room_id = manager.host(uuid.uuid4())
    assert room_id is not None
    assert type(room_id) is str
