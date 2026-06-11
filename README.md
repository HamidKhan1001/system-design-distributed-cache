# system-design-distributed-cache

Distributed in-memory key-value cache with LRU and LFU eviction, cache stampede prevention via per-key async locks, and horizontal scaling via consistent-hash sharding.

## Components

### LRUCache — O(1) eviction via `OrderedDict`

Moves accessed keys to the tail; pops the head on eviction. Tracks hit rate via `CacheStats`.

### LFUCache — O(1) eviction via frequency buckets

Maintains a `min_freq` pointer and per-frequency `OrderedDict` buckets. On access, promotes key to next bucket. Evicts the LRU key within the minimum-frequency bucket.

### StampedeShield — cache stampede / thundering herd prevention

```
Cache miss for key K
       │
  acquire per-key asyncio.Lock
       │
  double-check (another waiter may have filled it)
       │
  compute() if still missing ← only ONE coroutine reaches here
       │
  store result → release lock
       │
  all other waiters return cached result
```

### ShardedCache — horizontal scaling

Consistent-hash sharding across N LRU shards. Each key maps to exactly one shard via MD5; shards are independent, eliminating a single lock bottleneck.

## Eviction comparison

| Strategy | Evicts    | Best for                        |
|----------|-----------|---------------------------------|
| LRU      | Least recently used  | Temporal locality (recent = hot) |
| LFU      | Least frequently used | Stable hot-set (frequency = hot) |

## Usage

```python
from cache import LRUCache, LFUCache, StampedeShield, ShardedCache

lru = LRUCache(capacity=1000)
lru.put("k", "v")
lru.get("k")           # → "v"
lru.stats.hit_rate     # → 1.0

shield = StampedeShield()
val = await shield.get_or_compute("key", expensive_fetch, ttl_seconds=60)

sharded = ShardedCache(num_shards=16, shard_capacity=256)
sharded.put("user:42", {...})
```

## Running tests

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v   # 36 tests
```
