# Contributing

## Setup

```bash
git clone https://github.com/vince-ni/verification-spine.git
cd verification-spine
pip install -e '.[test]'
pytest -q
```

Standard library only — no runtime dependencies, and PRs that add one need a
strong reason.

## Ground rules

1. **Fail closed.** Invalid input raises; it never earns a verdict or a log
   entry. If your change introduces a path where corrupted data passes
   silently, it will be rejected.
2. **Every bugfix ships its regression test.** The test suite doubles as this
   project's incident history — tests are named for the behavior they pin,
   not the implementation.
3. **Don't weaken the receipts.** `docs/fixtures/` numbers are verbatim from
   the originating system's logs and are not edited to make tests pass. If a
   logic change breaks fixture replay, the change is wrong or the semantics
   changed — say which, explicitly, in the PR.
4. **Judging logic gets adversarial review.** Changes to verdict logic,
   validation, or the log format go through an adversarial review by a
   reviewer (human or model) from outside the author's family before merge —
   executing the code against evasion *and* regression suites, not reading
   the diff. This repo exists because that discipline catches what
   self-review cannot (see docs/cross-vendor-review.md).

## Pull requests

Keep them small and single-purpose. State what breaks (API, log format) in
the first line. CI must be green across the Python matrix.
