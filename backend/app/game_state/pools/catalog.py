from .base import PoolEntry
from .directory import DirectoryPool
from .random import RandomPool

CATALOG: list[PoolEntry] = [
    PoolEntry(
        id="dummy_3x3",
        display_name="Dummy 3×3",
        pool=DirectoryPool(directory="static/dummy_3x3"),
    ),
    PoolEntry(
        id="random_7x7",
        display_name="Random 7×7",
        pool=RandomPool(size=7, min_walls=6, max_walls=16),
    ),
]

CATALOG_BY_ID: dict[str, PoolEntry] = {e.id: e for e in CATALOG}
