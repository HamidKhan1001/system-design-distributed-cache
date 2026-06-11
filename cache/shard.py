import hashlib
from .lru import LRUCache
from .stats import CacheStats


class ShardedCache:
    """Distributes keys across N LRU shards via consistent hashing."""

    def __init__(self, num_shards: int = 8, shard_capacity: int = 128):
        if num_shards < 1:
            raise ValueError("num_shards must be >= 1")
        self._shards = [LRUCache(shard_capacity) for _ in range(num_shards)]
        self.num_shards = num_shards

    def _shard(self, key: str) -> LRUCache:
        digest = hashlib.md5(key.encode()).digest()
        idx = int.from_bytes(digest[:4], "big") % self.num_shards
        return self._shards[idx]

    def get(self, key: str):
        return self._shard(key).get(key)

    def put(self, key: str, value) -> None:
        self._shard(key).put(key, value)

    def delete(self, key: str) -> bool:
        return self._shard(key).delete(key)

    def __contains__(self, key: str) -> bool:
        return key in self._shard(key)

    @property
    def stats(self) -> CacheStats:
        merged = CacheStats()
        for s in self._shards:
            merged.hits += s.stats.hits
            merged.misses += s.stats.misses
            merged.evictions += s.stats.evictions
        return merged

    @property
    def total_items(self) -> int:
        return sum(len(s) for s in self._shards)
