import json
from pathlib import Path

import pytest

from app.game_state.pools import CATALOG, CATALOG_BY_ID, Pool, PoolEntry
from app.game_state.pools.directory import DirectoryPool
from app.game_state.pools.random import RandomPool


def test_pool_package_exports() -> None:
    assert Pool is not None
    assert PoolEntry is not None
    assert isinstance(CATALOG, list)
    assert isinstance(CATALOG_BY_ID, dict)


def test_random_pool_deterministic() -> None:
    pool = RandomPool(size=7, min_walls=6, max_walls=16)
    assert pool.generate(seed=42).model_dump() == pool.generate(seed=42).model_dump()


def test_random_pool_different_seeds_differ() -> None:
    pool = RandomPool(size=7, min_walls=6, max_walls=16)
    assert pool.generate(seed=1).model_dump() != pool.generate(seed=2).model_dump()


def test_random_pool_well_formed() -> None:
    pool = RandomPool(size=7, min_walls=6, max_walls=16)
    for seed in (1, 7, 42, 999, 12345):
        board = pool.generate(seed=seed)
        # Dimensions
        assert board.width == 7 and board.height == 7
        assert len(board.grid) == 7 and all(len(row) == 7 for row in board.grid)
        # 5 distinct moles
        positions = [(p.x, p.y) for p in board.mole_position]
        assert len(positions) == 5
        assert len(set(positions)) == 5
        # No fully-walled cell
        for row in board.grid:
            for cell in row:
                assert not all(cell.wall)
        # Wall mirroring
        for y in range(7):
            for x in range(7):
                cell = board.grid[y][x]
                if y > 0:
                    assert cell.wall[0] == board.grid[y - 1][x].wall[2]
                if x > 0:
                    assert cell.wall[3] == board.grid[y][x - 1].wall[1]
        # Single connected component
        assert board.is_connected()


@pytest.fixture
def board_dir(tmp_path: Path) -> Path:
    data = {
        "width": 3,
        "height": 3,
        "mole_position": [
            {"x": 0, "y": 0},
            {"x": 2, "y": 0},
            {"x": 0, "y": 2},
            {"x": 2, "y": 2},
            {"x": 1, "y": 1},
        ],
        "target_positions": [
            {"x": 0, "y": 0},
            {"x": 1, "y": 0},
            {"x": 2, "y": 0},
            {"x": 0, "y": 1},
            {"x": 1, "y": 1},
            {"x": 2, "y": 1},
            {"x": 0, "y": 2},
            {"x": 1, "y": 2},
            {"x": 2, "y": 2},
        ],
        "moves": 0,
        "grid": [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]],
        # Present but ignored — targets are rolled dynamically by BoardState.
        "finish_positions": [[{"x": 1, "y": 0}, 0]],
    }
    (tmp_path / "a.json").write_text(json.dumps(data))
    return tmp_path


def test_directory_pool_deterministic(board_dir: Path) -> None:
    pool = DirectoryPool(directory=str(board_dir), absolute=True)
    assert pool.generate(seed=5).model_dump() == pool.generate(seed=5).model_dump()


def test_directory_pool_loads_layout_and_ignores_finishes(board_dir: Path) -> None:
    pool = DirectoryPool(directory=str(board_dir), absolute=True)
    board = pool.generate(seed=0)
    assert board.width == 3 and board.height == 3
    assert len(board.mole_position) == 5


def test_catalog_has_expected_entries() -> None:
    ids = {entry.id for entry in CATALOG}
    assert "random_7x7" in ids
    assert "dummy_3x3" in ids

    for entry in CATALOG:
        assert isinstance(entry, PoolEntry)
        assert isinstance(entry.pool, Pool)
        assert entry.display_name
        assert CATALOG_BY_ID[entry.id] is entry

    assert len({e.id for e in CATALOG}) == len(CATALOG)


def test_catalog_pools_generate() -> None:
    for entry in CATALOG:
        board = entry.pool.generate(seed=1)
        assert board.width >= 3
        assert board.height >= 3
        assert len(board.mole_position) == 5
