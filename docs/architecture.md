# Zen Ω — A Personal Agent System Built Around a Verification Spine

*The evaluation architecture this library was extracted from. The implementation is private; the methodology is not.*

## The premise

Agent output compounds only as fast as you can trust your judge. Most agent systems scale generation and leave verification to vibes; then every gain is provisional and every regression is silent. So this system is organized around the opposite priority: **the first question of every task is "how will we know it's right?"** Model choice is just a performance parameter; trust lives in the judging assets — test suites, held-out evals, promotion gates, and human sign-off boundaries.

## The self-improvement ratchet

The system's skills (prompt + scaffold bundles) improve through a reflective-evolution loop in the spirit of GEPA (Agrawal et al., 2025): candidates are mutated from execution feedback, then scored on a **disjoint held-out set** they never trained against, with a Pareto noise-floor gate on top. What I added is promotion governance:

- **A machine gate that can say no.** Candidates that improve on the feedback objective but fail to beat the held-out baseline are discarded, not shipped.
- **A human gate above the machine gate.** Passing held-out earns "keep-advance" status only. A formal promotion additionally requires explicit human acknowledgment, recorded in an append-only log. The machine has never self-promoted — zero auto-promotions to date.
- **Anti-gaming ACL.** The eval assets are held-out in the organizational sense too: the executing agent is forbidden from editing them. A judge the optimizer can touch is not a judge.

## Receipts (every number traces to a primary log)

- **The gate caught a real over-fit.** Furizen's SEO-writing skill's round-1 candidate passed held-out (0.318 → 0.727, train 0.349 → 0.821) and earned keep-advance; the round-2 candidate nudged the training objective up (+0.004, inside the noise floor) but regressed held-out by 0.045 — 2.7× the noise floor — and was **discarded by the gate** (verdict: discard-overfit). [Full incident report →](heldout-gate.md)
- **Generalization across subjects.** Five held-out gate passes across three unrelated skill domains (structuring, verification, SEO), including a verification skill lifted 0.750 → 1.000 in two independent runs.
- **One formal promotion, human-acknowledged.** Held-out 0.8247 → 0.9336, promoted only after explicit human sign-off.
- **The gate also refuses.** A later candidate scored 0.9520 against a promoted baseline of 0.9563 — inside the noise floor — and the machine declined to promote. Restraint is a feature.
- **234 tests** on the kernel (as of Aug 2026).

## Memory with an expiry date

Agent memory here is plain Markdown with temporal governance, converging on the bi-temporal design Zep/Graphiti pioneered for knowledge graphs (Rasmussen et al., 2025):

- Superseded facts are **invalidated, never deleted** (`invalid_at` + `superseded_by`), so the system can answer "what was believed when" and never serves a stale fact as current.
- Every substantive claim carries a **three-tier provenance tag** — extracted (verbatim from a source), inferred (model synthesis), or ambiguous (insufficient evidence) — and agents may never upgrade their own claims to verified status; only the human can.
- Memories carry **staleness domains** (vendor facts rot in ~30 days; historical facts don't), swept weekly by a scheduled job that queues re-verification instead of trusting recall.

## Autonomy that fails closed

Unattended runs operate under layered constraints: OS-sandboxed egress, hard-denied send actions, and a versioned constitution the agents cannot edit (enforced by protected hooks). When an autonomous task hits a decision that belongs to the human, it doesn't guess — it writes a one-line **pending-approval slip** and stops. Publish authority never leaves the human.

## Cross-vendor adversarial review

Builder and reviewer are models from different labs, and the trust is asymmetric: a reviewer's refutation is weighted far above its endorsement, because LLM judges share failure modes — agreement is not correctness. This pairing caught a real regression that self-review had passed — in the judge itself: a "fix" to a brand-canon lint script used Unicode NFKC normalization to defeat full-width evasion, and as a side effect folded ™ into TM, silently degrading the very rules the judge was meant to enforce (correct names false-flagged; a hard FAIL downgraded to WARN). The cross-vendor reviewer re-ran the patched judge against evasion and regression sets and caught it; the repair was redone with targeted character folding. When the judge regresses, only someone outside your model family is likely to notice. [Full incident report →](cross-vendor-review.md)

## Where this sits relative to the field

The components rhyme with the current frontier: three-tier/file-based memory (Letta's lineage), bi-temporal fact invalidation (Zep/Graphiti), reflective prompt evolution with held-out validation (GEPA, ICLR 2026). I built on those ideas rather than claiming them. What I'd argue is genuinely uncommon is the **governance composition at production scale-of-one**: executor-forbidden evals, human-anchored promotion, provenance-typed memory, and fail-closed autonomy, all running daily against real stakes — my own money, customers, and reputation — rather than a benchmark.

## What's deliberately not here

The private implementation, the personal-life integration, and the business-specific strategy layers are omitted. If you want to go deep on the architecture, ask — that conversation is the point of this page.
