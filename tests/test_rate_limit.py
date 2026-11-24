import asyncio

from ticket_triage.core.rate_limit import TokenBucket


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_starts_full():
    bucket = TokenBucket(capacity=5, refill_per_s=1.0, clock=FakeClock())
    assert bucket.tokens == 5


def test_refill_adds_elapsed_times_rate():
    clock = FakeClock()
    bucket = TokenBucket(capacity=5, refill_per_s=2.0, clock=clock)
    bucket.tokens = 0
    clock.t = 1.5
    bucket._refill()
    assert bucket.tokens == 3.0


def test_refill_caps_at_capacity():
    clock = FakeClock()
    bucket = TokenBucket(capacity=5, refill_per_s=1.0, clock=clock)
    clock.t = 100
    bucket._refill()
    assert bucket.tokens == 5


def test_per_minute_converts_rpm_to_per_second():
    bucket = TokenBucket.per_minute(rpm=120, burst=3)
    assert bucket.refill_per_s == 2.0
    assert bucket.capacity == 3


def test_acquire_waits_when_empty():
    clock = FakeClock()
    bucket = TokenBucket(capacity=2, refill_per_s=1.0, clock=clock)
    slept = []

    async def fake_sleep(s):  # advance fake time instead of really waiting
        slept.append(s)
        clock.t += s

    async def run():
        for _ in range(3):
            await bucket.acquire(sleep=fake_sleep)

    asyncio.run(run())
    assert slept == [1.0]  # burst of 2 is free, 3rd waits exactly 1s


def test_rejects_zero_rate():
    import pytest

    with pytest.raises(ValueError):
        TokenBucket(capacity=5, refill_per_s=0)
