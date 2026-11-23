"""Score a run file against gold labels."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path


def load(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/run_001.jsonl")
    rows = load(path)
    n = len(rows)

    queue_ok = sum(r["queue"] == r["gold_queue"] for r in rows)
    prio_ok = sum(r["priority"] == r["gold_priority"] for r in rows)
    both_ok = sum(
        r["priority"] == r["gold_priority"] and r["queue"] == r["gold_queue"] for r in rows
    )
    cost = sum(r["cost_usd"] for r in rows)

    print(f"tickets:        {n}")
    print(f"queue accuracy: {queue_ok / n:.0%} ({queue_ok}/{n})")
    print(f"prio accuracy:  {prio_ok / n:.0%} ({prio_ok}/{n})")
    print(f"both accuracy:  {both_ok / n:.0%} ({both_ok}/{n})")
    print(f"cost/ticket:    ${cost / n:.6f}")

    print("\nqueue confusions (gold -> predicted):")
    misses = Counter((r["gold_queue"], r["queue"]) for r in rows if r["queue"] != r["gold_queue"])
    for (gold, pred), count in misses.most_common(5):
        print(f"  {count:>2}  {gold} -> {pred}")

    print("\npriority confusions (gold -> predicted):")
    priority_misses = Counter(
        (r["gold_priority"], r["priority"]) for r in rows if r["priority"] != r["gold_priority"]
    )
    for (gold, pred), count in priority_misses.most_common(5):
        print(f"  {count:>2}  {gold} -> {pred}")

    write_errors(rows, Path("errors.md"))


def write_errors(rows: list[dict], out: Path) -> None:
    """One table row per ticket with a wrong queue or priority; 'why' is filled by hand."""
    with Path("data/test.csv").open() as f:
        subjects = [row["subject"] for row in csv.DictReader(f)]

    lines = [
        "# Errors: run_001",
        "",
        "| # | subject | gold queue / prio | predicted queue / prio | why |",
        "|---|---|---|---|---|",
    ]
    wrong = 0
    for r in rows:
        if r["queue"] == r["gold_queue"] and r["priority"] == r["gold_priority"]:
            continue
        wrong += 1
        subject = (subjects[r["i"]] or "").replace("|", "/")
        gold = f"{r['gold_queue']} / {r['gold_priority']}"
        pred = f"{r['queue']} / {r['priority']}"
        lines.append(f"| {r['i']} | {subject} | {gold} | {pred} |  |")

    out.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {wrong} rows to {out}")


if __name__ == "__main__":
    main()
