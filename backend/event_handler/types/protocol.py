from typing import Protocol
from ConnectionManager import ConnectionManager
from GameManager import GameManager

class EventHandlerProtocol(Protocol):
    con_manager: ConnectionManager
    game_manager: GameManager
