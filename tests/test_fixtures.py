"""The receipts are executable: replay the sanitized originating-run fixtures.

``docs/fixtures/originating-runs.jsonl`` carries the numeric records of three
real evolution runs from the originating system (instruction text redacted —
see docs/fixtures/README.md for provenance). This test recomputes every
non-baseline round's verdict from its parent round's scores and asserts it
matches the verdict the originating system recorded at the time.
"""
import json
from pathlib import Path

from verification_spine import Scores, evaluate

FIXTURE = Path(__file__).resolve().parent.parent / "docs" / "fixtures" / "originating-runs.jsonl"


def load_runs():
    rows = [json.loads(line) for line in FIXTURE.read_text().splitlines() if line.strip()]
    runs = {}
    for row in rows:
        runs.setdefault(row["run"], {})[row["round"]] = row
    return runs


def test_fixture_covers_three_runs():
    assert len(load_runs()) == 3


def test_every_recorded_verdict_reproduces():
    replayed = 0
    for rounds in load_runs().values():
        for row in rounds.values():
            if row["status"] == "baseline":
                continue
            parent = rounds[row["parent_round"]]
            decision = evaluate(
                Scores(train=parent["train_fitness"], heldout=parent["heldout_fitness"]),
                Scores(train=row["train_fitness"], heldout=row["heldout_fitness"]),
                row["epsilon"],
            )
            assert decision.verdict.value == row["status"], (row["run"], row["round"])
            replayed += 1
    # keep-advance x2 (June 9 r1, July 4), discard-overfit (June 9 r2), keep-pareto (July 5)
    assert replayed == 4
