import json
import logging
from pathlib import Path

import pandas as pd
import typer

from ticket_triage.config import Settings
from ticket_triage.core.llm import classify_ticket

app = typer.Typer()


@app.callback()
def main():
    """Ticket triage tools."""  # a callback keeps `classify` a named subcommand


@app.command()
def classify(n: int = 50, out: Path = Path("data/run_001.jsonl")):
    """Classify the first n test tickets and write one JSON line per ticket."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    budget = Settings().max_budget_usd
    df = pd.read_csv("data/test.csv").head(n)
    total = 0.0
    with out.open("w") as f:
        for i, row in enumerate(df.itertuples()):
            subject = row.subject if isinstance(row.subject, str) else None
            r = classify_ticket(subject, row.body)
            total += r.cost_usd
            record = {"i": i, "gold_queue": row.queue, "gold_priority": row.priority,
                      **r.label.model_dump(), "input_tokens": r.input_tokens,
                      "output_tokens": r.output_tokens, "cost_usd": r.cost_usd,
                      "latency_s": round(r.latency_s, 3)}  # fmt: skip
            f.write(json.dumps(record) + "\n")
            if total > budget:
                typer.echo(f"Budget ${budget} exceeded after {i + 1} tickets, stopping.")
                break
    typer.echo(f"Wrote {out}  total cost: ${total:.4f}")
