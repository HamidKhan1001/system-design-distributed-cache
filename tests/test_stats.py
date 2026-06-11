import pytest
from cache import CacheStats


def test_initial_zeros():
    s = CacheStats()
    assert s.hits == 0
    assert s.misses == 0
    assert s.evictions == 0


def test_hit_rate_zero_when_empty():
    assert CacheStats().hit_rate == 0.0


def test_hit_rate_calculation():
    s = CacheStats()
    s.record_hit()
    s.record_hit()
    s.record_miss()
    assert s.hit_rate == pytest.approx(2 / 3, abs=0.01)


def test_record_eviction():
    s = CacheStats()
    s.record_eviction()
    assert s.evictions == 1
