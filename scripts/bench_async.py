"""Time 10 tickets one-at-a-time vs all at once with asyncio.gather."""

import asyncio
import time

import pandas as pd

from ticket_triage.config import Settings
from ticket_triage.core.llm import classify_many, classify_ticket_async, make_async_client


async def main(n: int = 10) -> None:
    settings = Settings()
    client = make_async_client(settings)
    df = pd.read_csv("data/test.csv").head(n)
    tickets = [
        (s if isinstance(s, str) else None, b) for s, b in zip(df.subject, df.body, strict=True)
    ]

    start = time.perf_counter()
    for subject, body in tickets:  # await each call before starting the next
        await classify_ticket_async(client, settings, subject, body)
    seq_s = time.perf_counter() - start

    start = time.perf_counter()
    results = await classify_many(client, settings, tickets, 2)
    conc_s = time.perf_counter() - start

    slowest = max(r.latency_s for r in results)
    print(f"sequential: {seq_s:.2f}s")
    print(f"gather:     {conc_s:.2f}s  (slowest single call {slowest:.2f}s)")
    print(f"speedup:    {seq_s / conc_s:.1f}x")


if __name__ == "__main__":
    asyncio.run(main())
