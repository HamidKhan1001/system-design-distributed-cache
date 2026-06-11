import asyncio
import pytest
from cache import StampedeShield


@pytest.mark.asyncio
async def test_get_or_compute_basic(shield):
    call_count = [0]

    async def compute():
        call_count[0] += 1
        return "result"

    val = await shield.get_or_compute("k", compute, ttl_seconds=60)
    assert val == "result"
    assert call_count[0] == 1


@pytest.mark.asyncio
async def test_concurrent_only_one_compute(shield):
    compute_count = [0]

    async def compute():
        compute_count[0] += 1
        await asyncio.sleep(0.05)
        return "value"

    results = await asyncio.gather(*[
        shield.get_or_compute("key", compute, ttl_seconds=60)
        for _ in range(10)
    ])
    assert all(r == "value" for r in results)
    assert compute_count[0] == 1
    assert shield.recompute_count == 1


@pytest.mark.asyncio
async def test_cache_hit_no_recompute(shield):
    async def first():
        return "v"

    await shield.get_or_compute("k", first, ttl_seconds=60)
    count_before = shield.recompute_count

    async def should_not_run():
        raise AssertionError("should not be called")

    val = await shield.get_or_compute("k", should_not_run, ttl_seconds=60)
    assert val == "v"
    assert shield.recompute_count == count_before


@pytest.mark.asyncio
async def test_invalidate_forces_recompute(shield):
    async def compute():
        return "fresh"

    await shield.get_or_compute("k", compute, ttl_seconds=60)
    shield.invalidate("k")
    val = await shield.get_or_compute("k", compute, ttl_seconds=60)
    assert val == "fresh"
    assert shield.recompute_count == 2


@pytest.mark.asyncio
async def test_different_keys_independent(shield):
    calls = {"a": 0, "b": 0}

    async def compute_a():
        calls["a"] += 1
        return "a"

    async def compute_b():
        calls["b"] += 1
        return "b"

    await asyncio.gather(
        shield.get_or_compute("a", compute_a, ttl_seconds=60),
        shield.get_or_compute("b", compute_b, ttl_seconds=60),
    )
    assert calls["a"] == 1
    assert calls["b"] == 1
