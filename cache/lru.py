from collections import OrderedDict
from typing import Any
from .stats import CacheStats


class LRUCache:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._store: OrderedDict = OrderedDict()
        self.stats = CacheStats()

    def get(self, key: str) -> Any:
        if key not in self._store:
            self.stats.record_miss()
            return None
        self._store.move_to_end(key)
        self.stats.record_hit()
        return self._store[key]

    def put(self, key: str, value: Any) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        else:
            if len(self._store) >= self.capacity:
                self._store.popitem(last=False)
                self.stats.record_eviction()
        self._store[key] = value

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: str) -> bool:
        return key in self._store
