import pytest
from cache import LRUCache, LFUCache, StampedeShield, ShardedCache


@pytest.fixture
def lru():
    return LRUCache(capacity=3)


@pytest.fixture
def lfu():
    return LFUCache(capacity=3)


@pytest.fixture
def shield():
    return StampedeShield()


@pytest.fixture
def sharded():
    return ShardedCache(num_shards=4, shard_capacity=10)
