from app.game_state.schemas import Direction, Mole


class BoardState:
    def modify(self, mole: Mole, direction: Direction) -> None:
        pass

    @property
    def moves(self) -> int:
        return 0

    def finish_state(self) -> bool:
        return False

    def flush(self) -> None:
        pass

    def clear(self) -> None:
        pass

    def revert(self) -> None:
        pass
