from typing import Protocol
from app.ConnectionManager import ConnectionManager
from app.game_state.GameManager import GameManager
from app.game_state.Training import TrainingManager


class EventHandlerProtocol(Protocol):
    con_manager: ConnectionManager
    game_manager: GameManager
    training_manager: TrainingManager
