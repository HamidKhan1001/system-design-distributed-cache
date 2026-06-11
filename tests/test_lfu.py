import pytest
from cache import LFUCache


def test_put_and_get(lfu):
    lfu.put("a", 10)
    assert lfu.get("a") == 10


def test_miss_returns_none(lfu):
    assert lfu.get("z") is None


def test_evicts_least_frequently_used():
    c = LFUCache(capacity=2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1


def test_update_existing_key(lfu):
    lfu.put("a", 1)
    lfu.put("a", 99)
    assert lfu.get("a") == 99


def test_stats_hit_miss(lfu):
    lfu.put("k", "v")
    lfu.get("k")
    lfu.get("missing")
    assert lfu.stats.hits == 1
    assert lfu.stats.misses == 1


def test_eviction_counted():
    c = LFUCache(capacity=2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.stats.evictions == 1


def test_delete(lfu):
    lfu.put("a", 1)
    assert lfu.delete("a") is True
    assert lfu.get("a") is None


def test_capacity_invalid():
    with pytest.raises(ValueError):
        LFUCache(capacity=0)


def test_len(lfu):
    lfu.put("a", 1)
    lfu.put("b", 2)
    assert len(lfu) == 2
