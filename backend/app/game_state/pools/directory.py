import random
from pathlib import Path

from app.game_state.BoardState import BoardData

from .base import Pool


class DirectoryPool(Pool):
    def __init__(self, directory: str, absolute: bool = False) -> None:
        """
        `directory`: path resolved relative to `backend/app/game_state/` unless `absolute=True`.
        `absolute=True` is intended for tests (and not used by catalog entries).
        """
        if absolute:
            base = Path(directory)
        else:
            base = Path(__file__).parent.parent / directory
        self.files = sorted(base.glob("*.json"))
        if not self.files:
            raise ValueError(f"DirectoryPool: no JSON files in {base}")

    def generate(self, seed: int) -> BoardData:
        rng = random.Random(seed)
        path = rng.choice(self.files)
        json_string = path.read_text()
        return BoardData.model_validate_json(json_string)
