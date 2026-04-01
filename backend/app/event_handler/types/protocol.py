from typing import Protocol
from app.ConnectionManager import ConnectionManager
from app.GameManager import GameManager


class EventHandlerProtocol(Protocol):
    con_manager: ConnectionManager
    game_manager: GameManager
