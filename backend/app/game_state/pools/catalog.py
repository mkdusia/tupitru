from .base import PoolEntry
from .directory import DirectoryPool
from .random import RandomPool

CATALOG: list[PoolEntry] = [
    PoolEntry(
        id="dummy_3x3",
        display_name="Trivial 3x3",
        pool=DirectoryPool(directory="static/dummy_3x3"),
    ),
    PoolEntry(
        id="random_5x5",
        display_name="Easy 5x5",
        pool=RandomPool(size=5, min_walls=3, max_walls=7),
    ),
    PoolEntry(
        id="random_7x7",
        display_name="Medium 7x7",
        pool=RandomPool(size=7, min_walls=7, max_walls=13),
    ),
    PoolEntry(
        id="random_10x10",
        display_name="Hard 10x10",
        pool=RandomPool(size=10, min_walls=15, max_walls=25),
    ),
    PoolEntry(
        id="random_13x13",
        display_name="Extreme 13x13",
        pool=RandomPool(size=13, min_walls=25, max_walls=40),
    ),
]

CATALOG_BY_ID: dict[str, PoolEntry] = {e.id: e for e in CATALOG}
