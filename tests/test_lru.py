import pytest
from cache import LRUCache


def test_put_and_get(lru):
    lru.put("a", 1)
    assert lru.get("a") == 1


def test_miss_returns_none(lru):
    assert lru.get("missing") is None


def test_evicts_least_recently_used():
    c = LRUCache(capacity=2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1


def test_update_promotes(lru):
    lru.put("a", 1)
    lru.put("b", 2)
    lru.put("c", 3)
    lru.put("a", 99)
    lru.put("d", 4)
    assert lru.get("a") == 99
    assert lru.get("b") is None


def test_hit_rate(lru):
    lru.put("x", 1)
    lru.get("x")
    lru.get("missing")
    assert lru.stats.hit_rate == pytest.approx(0.5)


def test_eviction_counted():
    c = LRUCache(capacity=2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.stats.evictions == 1


def test_delete(lru):
    lru.put("a", 1)
    assert lru.delete("a") is True
    assert lru.get("a") is None


def test_delete_missing(lru):
    assert lru.delete("no") is False


def test_capacity_invalid():
    with pytest.raises(ValueError):
        LRUCache(capacity=0)


def test_len(lru):
    lru.put("a", 1)
    lru.put("b", 2)
    assert len(lru) == 2
