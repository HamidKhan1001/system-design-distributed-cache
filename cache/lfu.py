from collections import defaultdict, OrderedDict
from typing import Any
from .stats import CacheStats


class LFUCache:
    """O(1) LFU using frequency buckets."""

    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._values: dict = {}
        self._freq: dict = {}
        self._buckets: dict = defaultdict(OrderedDict)
        self._min_freq = 0
        self.stats = CacheStats()

    def get(self, key: str) -> Any:
        if key not in self._values:
            self.stats.record_miss()
            return None
        self._bump(key)
        self.stats.record_hit()
        return self._values[key]

    def put(self, key: str, value: Any) -> None:
        if key in self._values:
            self._values[key] = value
            self._bump(key)
            return
        if len(self._values) >= self.capacity:
            self._evict()
        self._values[key] = value
        self._freq[key] = 1
        self._buckets[1][key] = None
        self._min_freq = 1

    def delete(self, key: str) -> bool:
        if key not in self._values:
            return False
        freq = self._freq.pop(key)
        del self._values[key]
        self._buckets[freq].pop(key, None)
        return True

    def __len__(self) -> int:
        return len(self._values)

    def __contains__(self, key: str) -> bool:
        return key in self._values

    def _bump(self, key: str) -> None:
        f = self._freq[key]
        self._freq[key] = f + 1
        self._buckets[f].pop(key)
        if not self._buckets[f] and f == self._min_freq:
            self._min_freq = f + 1
        self._buckets[f + 1][key] = None

    def _evict(self) -> None:
        bucket = self._buckets[self._min_freq]
        evicted_key, _ = bucket.popitem(last=False)
        del self._values[evicted_key]
        del self._freq[evicted_key]
        self.stats.record_eviction()
