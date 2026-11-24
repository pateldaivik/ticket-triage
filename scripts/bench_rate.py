"""Run N tickets through classify_many with a semaphore + token bucket; count 429 retries."""

import asyncio
import logging
import sys
import time

import pandas as pd

from ticket_triage.config import Settings
from ticket_triage.core.llm import classify_many, make_async_client
from ticket_triage.core.rate_limit import TokenBucket


class RetryCounter(logging.Handler):
    """Counts llm_retry log lines, split into 429s vs other retryable errors."""

    def __init__(self) -> None:
        super().__init__()
        self.rate_limited = 0
        self.other = 0

    def emit(self, record: logging.LogRecord) -> None:
        if "RateLimitError" in record.getMessage():
            self.rate_limited += 1
        else:
            self.other += 1


async def main(n: int, rpm: float, concurrency: int) -> None:
    settings = Settings()
    client = make_async_client(settings)
    df = pd.read_csv("data/test.csv").head(n)
    tickets = [
        (s if isinstance(s, str) else None, b) for s, b in zip(df.subject, df.body, strict=True)
    ]
    counter = RetryCounter()
    logging.getLogger("ticket_triage.core.llm").addHandler(counter)

    bucket = TokenBucket.per_minute(rpm, burst=concurrency)
    start = time.perf_counter()
    results = await classify_many(client, settings, tickets, concurrency, bucket=bucket)
    elapsed = time.perf_counter() - start

    print(f"tickets:   {len(results)}  (rpm={rpm:g}, concurrency={concurrency})")
    print(f"elapsed:   {elapsed:.1f}s  -> {len(results) / elapsed * 60:.0f} req/min actual")
    print(f"429s:      {counter.rate_limited}")
    print(f"other retries: {counter.other}")
    print(f"cost:      ${sum(r.cost_usd for r in results):.4f}")


if __name__ == "__main__":
    # usage: uv run python scripts/bench_rate.py [n] [rpm] [concurrency]
    args = sys.argv[1:]
    n = int(args[0]) if len(args) > 0 else 100
    rpm = float(args[1]) if len(args) > 1 else 300
    conc = int(args[2]) if len(args) > 2 else 10
    asyncio.run(main(n, rpm, conc))
