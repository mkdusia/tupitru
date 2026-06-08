from app.game_state.BoardState import BoardData, BoardState, Cell, Position


def _board() -> BoardData:
    # 3x3 board; 5 moles leave exactly the 4 edge-midpoints free.
    # No finish/finish_mole passed — BoardState rolls them.
    return BoardData(
        width=3,
        height=3,
        grid=[[Cell() for _ in range(3)] for _ in range(3)],
        mole_position=(
            Position(x=0, y=0),
            Position(x=2, y=0),
            Position(x=0, y=2),
            Position(x=2, y=2),
            Position(x=1, y=1),
        ),
        target_positions=list(Position(x=x, y=y) for x in range(3) for y in range(3)),
        moves=0,
    )


def _assert_target_free(state: BoardState) -> None:
    finish = state.board.finish
    assert finish is not None
    assert not state.board.contains_mole(finish)


def test_init_rolls_target_on_a_free_cell() -> None:
    state = BoardState(_board(), seed=1, rounds=3)
    _assert_target_free(state)


def test_target_never_on_a_mole_across_rounds() -> None:
    state = BoardState(_board(), seed=7, rounds=4)
    rounds_seen = 1
    _assert_target_free(state)
    while state.next_round():
        _assert_target_free(state)
        rounds_seen += 1
    assert rounds_seen == 4


def test_next_round_respects_round_count() -> None:
    state = BoardState(_board(), seed=0, rounds=2)
    assert state.next_round() is True
    assert state.next_round() is False


def test_single_round_has_no_next() -> None:
    state = BoardState(_board(), seed=0, rounds=1)
    assert state.next_round() is False


def test_targets_deterministic_for_same_seed() -> None:
    a = BoardState(_board(), seed=42, rounds=3)
    b = BoardState(_board(), seed=42, rounds=3)
    assert (a.board.finish, a.board.finish_mole) == (b.board.finish, b.board.finish_mole)
