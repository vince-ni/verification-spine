"""Replay the sanitized originating-run fixtures and print the verdict table.

Every verdict below is recomputed from the shipped numbers — compare the
`recorded` and `recomputed` columns. See docs/fixtures/README.md.
"""
import json
from pathlib import Path

from verification_spine import Scores, evaluate

fixture = Path(__file__).resolve().parent.parent / "docs" / "fixtures" / "originating-runs.jsonl"
rows = [json.loads(line) for line in fixture.read_text().splitlines() if line.strip()]

runs: dict = {}
for row in rows:
    runs.setdefault(row["run"], {})[row["round"]] = row

print(f"{'run':<18} {'round':>5} {'recorded':<16} {'recomputed':<16}")
for run, rounds in runs.items():
    for rnd in sorted(rounds):
        row = rounds[rnd]
        if row["status"] == "baseline":
            continue
        parent = rounds[row["parent_round"]]
        decision = evaluate(
            Scores(parent["train_fitness"], parent["heldout_fitness"]),
            Scores(row["train_fitness"], row["heldout_fitness"]),
            row["epsilon"],
        )
        match = "✓" if decision.verdict.value == row["status"] else "✗ MISMATCH"
        print(f"{run:<18} {rnd:>5} {row['status']:<16} {decision.verdict.value:<16} {match}")
