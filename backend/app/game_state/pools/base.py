from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.game_state.BoardState import BoardData


class Pool(ABC):
    @abstractmethod
    def generate(self, seed: int) -> BoardData:
        """Return a board (walls + initial mole positions) deterministically from
        the seed. Round targets are rolled dynamically by BoardState."""
        ...


@dataclass(frozen=True)
class PoolEntry:
    id: str
    display_name: str
    pool: Pool
