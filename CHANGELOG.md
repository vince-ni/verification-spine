# Changelog

## v0.2.0 — 2026-08-07

Hardening and completeness after two cross-vendor adversarial review rounds
(every finding hand-reproduced before fixing; each fix ships with its
regression test).

**Breaking**
- `PromotionLog.promote()` now requires a gate `Decision` and refuses any
  verdict other than `keep-advance` — the log can no longer record candidates
  the gate rejected.
- Promotion log format moved from delimited text to JSON Lines: field content
  (separators, unicode) is inert data; malformed lines are reported with
  their line number.

**Fixed**
- Gate fails closed on NaN/±inf/out-of-range scores and non-finite epsilon
  (previously NaN could earn `keep-pareto` and +inf could earn `keep-advance`).
- `promote()` validates `heldout` (finite, in [0, 1]) before writing.
- Acks made of zero-width characters, and control characters in ack or
  candidate id, are refused.
- The "over-fit signature" annotation now requires train to actually rise.
- `estimate_noise()` validates inputs and accepts any sequence.

**Added**
- Sanitized primary-log fixtures (`docs/fixtures/`) plus a replay test that
  recomputes every recorded verdict from the fixture.
- Runnable `examples/`.
- `py.typed`, CI across Python 3.10–3.13 with least-privilege permissions,
  test extra (`pip install -e '.[test]'`), CONTRIBUTING, SECURITY, Dependabot.

## v0.1.0 — 2026-08-06

Initial release: three-verdict held-out gate (`keep-advance` / `keep-pareto` /
`discard-overfit`) with a noise floor, append-only promotion log with a
mandatory acknowledgment, targeted full-width folding, 18 tests replaying the
originating incidents.
