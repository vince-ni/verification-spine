# The originating system (context)

*This library was extracted from a personal agent system that has run the
author's daily work — and [Furizen](https://furizen.com), a US
direct-to-consumer pet brand — on Claude Code since 2024. This page gives
just enough context to read the incident reports; the full system
documentation lives at [vince-ni.github.io/zen.html](https://vince-ni.github.io/zen.html).*

The system's organizing premise is that agent output compounds only as fast
as its judge can be trusted, so trust is placed in judging assets rather
than in models: test suites, held-out evals, promotion gates, and human
sign-off boundaries. Model choice is treated as a performance parameter.

Four properties of that system matter for the reports in this directory:

1. **Skills improve through reflective evolution** (in the spirit of GEPA),
   scored on a held-out split the optimizer never sees — the loop this
   library's verdicts were extracted from.
2. **Promotion is human-anchored.** Held-out survival earns advancement
   only; production promotion requires an explicit human acknowledgment in
   an append-only log. History to date: one formal promotion, zero
   auto-promotions.
3. **Eval assets sit behind an ACL** the executing agent cannot write to.
4. **Judging assets are cross-vendor reviewed** — builder and reviewer
   models come from different labs, refutations are weighted above
   endorsements, and every refutation is human-reproduced before acceptance
   (see [cross-vendor-review.md](cross-vendor-review.md) for the incident
   that made this a rule).

Scale note: the originating system's kernel carries 234 tests as of
Aug 2026 — that is the private system, not this repository; this repo's own
suite is smaller, public, and replays the incidents in
[fixtures/](fixtures/).
