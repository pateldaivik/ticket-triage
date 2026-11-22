import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import httpx
import openai
from openai import OpenAI
from pydantic import BaseModel, Field

from ticket_triage.config import Settings

log = logging.getLogger(__name__)

Priority = Literal["high", "medium", "low"]
Queue = Literal[
    "Technical Support",
    "Product Support",
    "Customer Service",
    "IT Support",
    "Billing and Payments",
    "Returns and Exchanges",
    "Service Outages and Maintenance",
    "Sales and Pre-Sales",
]

SYSTEM_PROMPT = """\
You are a support ticket triage assistant for a software and IT services company.

Each message contains one customer ticket with a subject and a body. The subject may be missing.

For every ticket, choose the queue that should handle it, assign a priority, and write a short \
summary. Base every decision only on what the ticket says; do not invent details.

If a ticket could fit more than one queue, pick the one that matches the customer's main problem \
or request. Always return exactly one queue and one priority.
"""


class TicketLabel(BaseModel):
    queue: Queue = Field(
        description=(
            "The team that should handle the ticket. "
            "Technical Support: the software product is not working as expected "
            "(bugs, errors, slow performance, failing integrations or APIs). "
            "IT Support: infrastructure and hardware (devices, networks, servers, "
            "accounts and access, installing or upgrading systems). "
            "Product Support: how to use or configure product features, "
            "or a feature behaving confusingly rather than breaking. "
            "Customer Service: general questions, complaints and account requests "
            "that need no technical fix. "
            "Billing and Payments: invoices, charges, refunds of payments, "
            "subscriptions and payment errors. "
            "Returns and Exchanges: sending back, replacing or exchanging a "
            "purchased product. "
            "Service Outages and Maintenance: a service that is down or unreachable "
            "for many users, network disruptions, or planned maintenance. "
            "Sales and Pre-Sales: questions from prospective buyers about features, "
            "pricing, plans or compatibility before purchase."
        )
    )
    priority: Priority = Field(
        description=(
            "How urgently the ticket needs attention, judged by its impact. "
            "high: a system is down, data or security is at risk, "
            "or the customer's work is blocked. "
            "medium: something is degraded or broken but a workaround exists. "
            "low: a question, information request or feature suggestion. "
            "Medium is the most common level. "
            "Words like 'urgent' or 'critical' alone do not make a ticket high; "
            "judge by the actual impact described."
        )
    )
    summary: str = Field(
        description=(
            "One English sentence of at most 20 words stating the customer's "
            "actual problem or request, with no greeting."
        )
    )


@dataclass
class CallResult:
    label: TicketLabel
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_s: float


def cost_usd(input_tokens: int, output_tokens: int, in_per_1m: float, out_per_1m: float) -> float:
    """Pure cost maths: tokens x price per million."""
    return (input_tokens * in_per_1m + output_tokens * out_per_1m) / 1_000_000


MAX_ATTEMPTS = 4


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 20.0, rand=random.random) -> float:
    """Full jitter: uniform in [0, min(cap, base * 2**attempt)]. attempt starts at 0."""
    return rand() * min(cap, base * 2**attempt)


def is_retryable(exc: Exception) -> bool:
    """429, timeouts, connection drops and 5xx are worth retrying; other 4xx are our bug."""
    if isinstance(exc, openai.RateLimitError | openai.APITimeoutError | openai.APIConnectionError):
        return True
    return isinstance(exc, openai.APIStatusError) and exc.status_code >= 500


def with_retry[T](fn: Callable[[], T], max_attempts: int = MAX_ATTEMPTS, sleep=time.sleep) -> T:
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            if not is_retryable(exc) or attempt == max_attempts - 1:
                raise
            delay = backoff_delay(attempt)
            if isinstance(exc, openai.RateLimitError):
                retry_after = exc.response.headers.get("retry-after")
                if retry_after:
                    delay = float(retry_after)
            log.warning(
                "llm_retry attempt=%d/%d err=%s sleep=%.2fs",
                attempt + 1,
                max_attempts,
                type(exc).__name__,
                delay,
            )
            sleep(delay)

    raise AssertionError("unreachable")


def classify_ticket(subject: str | None, body: str) -> CallResult:
    """Ask the model to label one ticket with a queue, priority and summary."""
    settings = Settings()
    # max_retries=0: we own the retry policy, so the SDK must not retry underneath us.
    # timeout: a hung request raises APITimeoutError, which with_retry treats as retryable.
    client = OpenAI(
        api_key=settings.openai_api_key,
        max_retries=0,
        timeout=httpx.Timeout(settings.request_timeout_s, connect=5.0),
    )

    ticket_text = f"Subject: {subject or '(no subject)'}\n\nBody:\n{body}"

    start = time.perf_counter()
    response = with_retry(
        lambda: client.responses.parse(
            model=settings.model,
            instructions=SYSTEM_PROMPT,
            input=ticket_text,
            text_format=TicketLabel,
        )
    )
    latency_s = time.perf_counter() - start

    label = response.output_parsed
    if label is None:
        raise RuntimeError(
            f"Model returned no parsed TicketLabel (response id {response.id}, "
            f"status {response.status!r}); it may have refused or been cut off."
        )

    usage = response.usage
    if usage is None:
        raise RuntimeError(
            f"Model returned no usage details (response id {response.id}, "
            f"status {response.status!r}); it may have refused or been cut off."
        )
    in_tok, out_tok = usage.input_tokens, usage.output_tokens
    cost = cost_usd(in_tok, out_tok, settings.price_input_per_1m, settings.price_output_per_1m)
    log.info("llm_call in=%d out=%d cost=$%.6f latency=%.2fs", in_tok, out_tok, cost, latency_s)
    return CallResult(label, in_tok, out_tok, cost, latency_s)
