import asyncio
import time
from typing import Any, Callable, Awaitable


class StampedeShield:
    """
    Prevents cache stampede using per-key async locks.
    Only one coroutine recomputes; others wait and share the result.
    """

    def __init__(self):
        self._locks: dict = {}
        self._cache: dict = {}
        self._recompute_count = 0

    async def get_or_compute(
        self,
        key: str,
        compute: Callable[[], Awaitable[Any]],
        ttl_seconds: float = 60.0,
    ) -> Any:
        now = time.monotonic()
        entry = self._cache.get(key)
        if entry is not None:
            value, exp = entry
            if now < exp:
                return value

        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            entry = self._cache.get(key)
            if entry is not None:
                value, exp = entry
                if time.monotonic() < exp:
                    return value

            value = await compute()
            self._recompute_count += 1
            self._cache[key] = (value, time.monotonic() + ttl_seconds)
            return value

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    @property
    def recompute_count(self) -> int:
        return self._recompute_count
