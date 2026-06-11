import pytest
from cache import ShardedCache


def test_put_get(sharded):
    sharded.put("k", "v")
    assert sharded.get("k") == "v"


def test_miss(sharded):
    assert sharded.get("missing") is None


def test_contains(sharded):
    sharded.put("x", 1)
    assert "x" in sharded


def test_delete(sharded):
    sharded.put("d", "val")
    assert sharded.delete("d") is True
    assert sharded.get("d") is None


def test_distributes_across_shards():
    c = ShardedCache(num_shards=4, shard_capacity=100)
    for i in range(40):
        c.put(f"key-{i}", i)
    shard_sizes = [len(s) for s in c._shards]
    assert all(sz > 0 for sz in shard_sizes)


def test_total_items(sharded):
    for i in range(5):
        sharded.put(f"k{i}", i)
    assert sharded.total_items == 5


def test_stats_aggregated(sharded):
    sharded.put("a", 1)
    sharded.get("a")
    sharded.get("missing")
    stats = sharded.stats
    assert stats.hits == 1
    assert stats.misses == 1


def test_invalid_shards():
    with pytest.raises(ValueError):
        ShardedCache(num_shards=0)
