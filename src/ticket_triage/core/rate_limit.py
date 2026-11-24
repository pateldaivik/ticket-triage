"""Token bucket: caps requests per unit time (throughput), unlike a semaphore (concurrency)."""

import asyncio
import time
from collections.abc import Callable


class TokenBucket:
    def __init__(
        self, capacity: float, refill_per_s: float, clock: Callable[[], float] = time.monotonic
    ) -> None:
        if capacity < 1 or refill_per_s <= 0:  # acquire() divides by the rate
            raise ValueError("need capacity >= 1 and refill_per_s > 0")
        self.capacity = capacity  # max burst size
        self.refill_per_s = refill_per_s  # steady-state rate, e.g. 60 RPM -> 1.0
        self.clock = clock  # injectable so tests can fake time
        self.tokens = capacity  # start full: allow an initial burst
        self.last = clock()
        self._lock = asyncio.Lock()  # one waiter at a time, so two tasks can't grab one token

    @classmethod
    def per_minute(cls, rpm: float, burst: float = 5) -> "TokenBucket":
        """Build from a provider's RPM limit: 60 RPM -> 1 token/s, bursts up to `burst`."""
        return cls(capacity=burst, refill_per_s=rpm / 60)

    def _refill(self) -> None:
        """Add tokens for the time elapsed since the last refill, never above capacity."""
        now = self.clock()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_s)
        self.last = now

    async def acquire(self, sleep=asyncio.sleep) -> None:
        """Take one token, sleeping until one has refilled if the bucket is empty."""
        async with self._lock:
            self._refill()
            if self.tokens < 1:
                wait_s = (1 - self.tokens) / self.refill_per_s  # time until 1 full token
                await sleep(wait_s)
                self._refill()
            self.tokens -= 1
