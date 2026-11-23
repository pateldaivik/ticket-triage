# ticket-triage

An LLM labels each customer support ticket with a queue, a priority and a one-line summary.

## Week 1: first run

50 tickets from `data/test.csv`, zero-shot prompt, run file `data/run_001.jsonl`.
Reproduce the numbers with `uv run python scripts/analyze.py`.

| metric | value |
|---|---|
| queue accuracy | 34% (17/50) |
| priority accuracy | 50% (25/50) |
| both correct | 20% (10/50) |
| cost per ticket | $0.000165 |

### 3 most common errors

All 40 misses are tagged in [errors.md](errors.md).

1. **Definitions disagree with the gold labels (11).** The prompt defines every queue, but the dataset uses them differently: advice and info requests are Customer Service in the gold labels, while the model follows the definitions to Product Support or Sales.
2. **Support queues overlap (9).** The model can't separate Technical, Product and IT Support, and defaults to Technical.
3. **Label noise (9).** The gold label looks wrong (e.g. marketing advice labelled Billing, agent replies stored as tickets). This caps reachable accuracy on this set.

Priority misses are almost all off by one level, leaning toward higher urgency (14 up, 10 down).

**Next:** add a few labelled examples from `train.csv` to the prompt (few-shot) so the model learns how the dataset actually uses each queue, then re-run and compare against run_001.
