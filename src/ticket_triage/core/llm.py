from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field

from ticket_triage.config import Settings

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


def classify_ticket(subject: str | None, body: str) -> TicketLabel:
    """Ask the model to label one ticket with a queue, priority and summary."""
    settings = Settings()
    client = OpenAI(api_key=settings.openai_api_key)

    ticket_text = f"Subject: {subject or '(no subject)'}\n\nBody:\n{body}"

    response = client.responses.parse(
        model=settings.model,
        instructions=SYSTEM_PROMPT,
        input=ticket_text,
        text_format=TicketLabel,
    )

    label = response.output_parsed
    if label is None:
        raise RuntimeError(
            f"Model returned no parsed TicketLabel (response id {response.id}, "
            f"status {response.status!r}); it may have refused or been cut off."
        )
    return label
