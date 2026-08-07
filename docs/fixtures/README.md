# Fixture provenance

`originating-runs.jsonl` is a sanitized export of three real evolution runs
from the originating system's run logs (June 9, July 4, and July 5, 2026 —
the incidents documented in [heldout-gate.md](../heldout-gate.md)).

**What was kept:** every numeric field verbatim at full float precision
(`train_fitness`, `heldout_fitness`, `epsilon`, `samples`), round structure
(`parent_round`), recorded verdicts (`status`), and the one-line edit
summaries.

**What was removed:** the full instruction text of each candidate (the
private prompt content of a running business), and internal run-id suffixes.

**What this buys you:** `tests/test_fixtures.py` recomputes every
non-baseline verdict from the parent round's scores and asserts it matches
what the originating system recorded. That makes the README's receipts
*mechanically reproducible* from a shipped artifact — it demonstrates the
verdict logic against the recorded values. It does not, and cannot,
independently attest that the underlying production events occurred; that
claim rests on the author.
