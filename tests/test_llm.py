import asyncio

import httpx
import openai
import pytest

from ticket_triage.core.llm import backoff_delay, cost_usd, with_retry, with_retry_async

REQ = httpx.Request("POST", "https://api.openai.com/v1/responses")


def test_cost_usd_maths():
    assert cost_usd(1000, 200, 0.20, 1.25) == pytest.approx(0.00045)
    assert cost_usd(1_000_000, 0, 0.20, 1.25) == pytest.approx(0.20)
    assert cost_usd(0, 0, 0.20, 1.25) == 0


def test_backoff_doubles_then_caps():
    max_delays = [backoff_delay(a, rand=lambda: 1.0) for a in range(6)]
    assert max_delays == [1, 2, 4, 8, 16, 20]  # cap=20
    assert backoff_delay(3, rand=lambda: 0.0) == 0  # full jitter can go to zero


def test_retries_timeouts_then_succeeds():
    calls, sleeps = [], []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise openai.APITimeoutError(request=REQ)
        return "ok"

    assert with_retry(flaky, sleep=sleeps.append) == "ok"
    assert len(calls) == 3 and len(sleeps) == 2


def test_async_retries_timeouts_then_succeeds():
    calls, sleeps = [], []

    async def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise openai.APITimeoutError(request=REQ)
        return "ok"

    async def fake_sleep(s):
        sleeps.append(s)

    assert asyncio.run(with_retry_async(flaky, sleep=fake_sleep)) == "ok"
    assert len(calls) == 3 and len(sleeps) == 2


def test_gives_up_after_max_attempts():
    calls = []

    def always_429():
        calls.append(1)
        raise openai.RateLimitError(
            "slow down", response=httpx.Response(429, request=REQ), body=None
        )

    with pytest.raises(openai.RateLimitError):
        with_retry(always_429, sleep=lambda s: None)
    assert len(calls) == 4


def test_non_retryable_raises_immediately():
    calls = []

    def bad_request():
        calls.append(1)
        resp = httpx.Response(400, request=REQ)
        raise openai.BadRequestError("bad", response=resp, body=None)

    with pytest.raises(openai.BadRequestError):
        with_retry(bad_request, sleep=lambda s: None)
    assert len(calls) == 1


def test_retry_after_header_overrides_jitter():
    sleeps = []

    def always_429():
        resp = httpx.Response(429, request=REQ, headers={"retry-after": "7"})
        raise openai.RateLimitError("slow down", response=resp, body=None)

    with pytest.raises(openai.RateLimitError):
        with_retry(always_429, sleep=sleeps.append)
    assert sleeps == [7.0, 7.0, 7.0]  # 4 attempts -> 3 waits, all from the header


def test_classify_many_caps_concurrency(monkeypatch):
    import ticket_triage.core.llm as llm

    in_flight, peak = 0, 0

    async def fake_classify(client, settings, subject, body):
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return body

    monkeypatch.setattr(llm, "classify_ticket_async", fake_classify)
    tickets = [(None, f"t{i}") for i in range(10)]
    results = asyncio.run(llm.classify_many(None, None, tickets, max_concurrency=3))
    assert results == [f"t{i}" for i in range(10)]  # order preserved
    assert peak == 3
