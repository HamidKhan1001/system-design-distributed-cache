# system-design-distributed-cache

[![CI](https://github.com/HamidKhan1001/system-design-distributed-cache/actions/workflows/ci.yml/badge.svg)](https://github.com/HamidKhan1001/system-design-distributed-cache/actions/workflows/ci.yml)

An in-process key-value cache library in Python. It implements LRU and LFU eviction with O(1) operations, a stampede shield that collapses concurrent recomputation of the same key, and a sharded wrapper that spreads keys across independent LRU instances.

Despite the repository name, this is a single-process library. There is no network layer, replication, or cluster membership. It is a study of the data structures and concurrency patterns that sit inside a distributed cache node, not a deployable cache server.

## Problem

A cache needs to answer three questions well:

1. What do we evict when full, and can we decide in constant time?
2. When many requests miss on the same hot key at once, how do we avoid sending all of them to the backing store?
3. How do we split the key space so no single structure becomes the bottleneck?

## Design

### LRUCache (`cache/lru.py`)

A single `OrderedDict`. A hit moves the key to the tail, and eviction pops the head. `get`, `put`, and `delete` are O(1).

### LFUCache (`cache/lfu.py`)

Three structures: a `key -> value` dict, a `key -> frequency` dict, and a `frequency -> OrderedDict` bucket map, plus a `min_freq` pointer. A hit moves the key from bucket `f` to `f+1`. Eviction pops the oldest key from the `min_freq` bucket, so ties are broken by recency. All operations are O(1).

### StampedeShield (`cache/stampede.py`)

On a miss, the caller takes a per-key `asyncio.Lock` and re-checks the cache inside the lock. Only the first coroutine runs `compute()`. The others wait on the lock, then find the fresh value on their re-check. Entries carry a TTL based on `time.monotonic()`.

### ShardedCache (`cache/shard.py`)

Routes each key to one of N `LRUCache` shards using the first 4 bytes of its MD5 digest modulo N. Stats from all shards are merged on read.

## Tradeoffs and known limitations

- **Not thread-safe.** `LRUCache` and `LFUCache` have no locking. The stampede shield is safe across coroutines on one event loop, not across threads.
- **Sharding is modulo hashing, not consistent hashing.** Changing `num_shards` remaps most keys. A real distributed deployment would need a hash ring with virtual nodes to limit key movement on resize.
- **Sharding here does not reduce lock contention in practice.** There are no locks, and under the GIL the shards still share one interpreter. The split models how a multi-node cache partitions keys.
- **StampedeShield state is unbounded.** Its lock and value dictionaries grow with the number of distinct keys, and expired entries are only replaced, not removed. A production version needs a size bound or a sweep.
- **No TTL on `LRUCache` or `LFUCache`.** Only the stampede shield expires entries.
- **LFU frequency never decays.** Keys that were hot long ago can outlive newer hot keys.
- **MD5 is used for distribution, not security.**

## Usage

```python
from cache import LRUCache, LFUCache, StampedeShield, ShardedCache

lru = LRUCache(capacity=1000)
lru.put("k", "v")
lru.get("k")        # "v"
lru.stats.hit_rate  # 1.0

shield = StampedeShield()
value = await shield.get_or_compute("key", fetch_from_db, ttl_seconds=60)

sharded = ShardedCache(num_shards=16, shard_capacity=256)
sharded.put("user:42", {"name": "example"})
```

## Running the tests

Tested on Python 3.13.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests -v
```

The suite has 36 tests covering eviction order and capacity limits for both caches, hit and miss accounting, shard routing and stats merging, and the stampede shield (including a test that many concurrent callers trigger exactly one computation).

## Layout

```
cache/
  lru.py        LRU cache
  lfu.py        LFU cache
  stampede.py   per-key lock, TTL, single recompute
  shard.py      modulo-hash sharded LRU
  stats.py      hit, miss, eviction counters
tests/          pytest suite
```
