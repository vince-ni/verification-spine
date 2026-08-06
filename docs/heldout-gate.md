# Prompt Evolution Overfits: An Incident Report

*How a held-out gate stopped my optimizer from shipping a regression that looked like progress.*

> **TL;DR** — On June 9, 2026, the prompt-evolution loop in my personal agent system produced a candidate that scored *higher* on its training objective and *worse* on a held-out set it had never seen. The gate discarded it automatically. This post walks through the actual run log, the mechanism that made the catch possible, and what I'd tell anyone optimizing prompts without a held-out split: you are almost certainly shipping over-fit, and you have no way to know.

## The incident

My agent system improves its own skills through reflective prompt evolution, in the spirit of GEPA (Agrawal et al., 2025): execute, collect feedback, mutate the instruction, re-score. The subject here was an SEO-writing skill for [Furizen](https://furizen.com), the DTC pet brand I run — real copy, real customers, not a benchmark.

Three rounds from the run log, verbatim fitness values:

| Round | Verdict | Train fitness | Held-out fitness |
|---|---|---|---|
| 0 (baseline) | — | 0.349 | 0.318 |
| 1 | keep-advance | 0.821 | 0.727 |
| 2 | **discard-overfit** | 0.825 | **0.682** |

Round 1 was a genuine improvement: the mutation embedded the brand canon and a structural checklist directly into the instruction, and both splits agreed — train +0.47, held-out +0.41. Advance.

Round 2 is the interesting one. Its edit summary read like exactly what a diligent engineer would do next: *"fix forbidden terms, size format, citation domain restrictions, Sources enforcement."* More rules, tighter constraints, every one of them individually defensible. Train fitness ticked up to 0.825.

And held-out fitness fell from 0.727 to 0.682.

The system's noise floor for this slot was ε = 0.017 (estimated from repeated sampling). Against that: the round-2 training "gain" was +0.004 — **inside the noise**. The held-out regression was −0.045 — **2.7× the noise floor**. The verdict logic reads exactly one way: this candidate learned the test, not the job. Status: `discard-overfit`. The candidate never shipped.

## Why round 2 fooled the training set

The round-2 mutation piled instruction mass onto the specific failure cases in the feedback set — forbidden-term fixes, formatting minutiae, citation-domain rules. Each added constraint bought a fraction of a point on the cases that had prompted it, and collectively they made the instruction more brittle on anything else. That is the textbook over-fit signature, and it is invisible if your only scoreboard is the data you optimized against.

This is worth stating bluntly because prompt work has quietly regressed to pre-ML hygiene. Nobody with ML training would evaluate a model on its training set — yet that is precisely how most teams iterate on prompts: tweak, re-run the same examples, watch the score go up, ship. The score always goes up. That's what optimizing against a fixed set *does*. GEPA's authors handle this with disjoint feedback and validation sets; most production prompt pipelines I've seen handle it with optimism.

## The mechanism

Four design decisions made this catch automatic rather than lucky:

**1. The splits are disjoint, and the optimizer only ever sees one.** Mutations are driven by feedback-set failures; held-out cases never appear in the mutation context. A judge the optimizer can study is a training set with a title.

**2. Scores become decisions only through a noise floor.** Fitness deltas smaller than ε are treated as silence, not signal. Without this, round 2's +0.004 train delta reads as "improvement"; with it, the delta is correctly worthless — and the −0.045 held-out drop is correctly damning.

**3. Verdicts, not scores.** Each round resolves to a category — `keep-advance`, `keep-pareto`, `discard-overfit` — with the comparison logic fixed in code. The human reviews verdicts; the machine never gets to argue that 0.825 > 0.821 means progress.

**4. Passing the gate still isn't shipping.** Held-out survival earns advancement inside the loop. Formal promotion — the instruction actually taking over production — additionally requires explicit human acknowledgment, recorded in an append-only log. In this system's entire history there has been exactly one formal promotion (held-out 0.825 → 0.934, human-acked) and zero auto-promotions. The eval assets themselves sit behind an ACL the executing agent cannot write to: the optimizer does not own the judge.

## What happened after

The thin spot in this story is honest to name: at the time of the incident, this slot's held-out split was a **single rubric-scored case** (the set was 3 train / 1 held-out). The mechanism worked, but one case is a tripwire, not a test suite. The set has since been expanded — to 8 train / 4 held-out in early July, and 13 / 7 as of this writing — and two subsequent runs under the larger set are what give me confidence the gate generalizes:

- **July 4:** a candidate beat the expanded held-out baseline 0.825 → 0.934, and became the system's single formal, human-acknowledged promotion.
- **July 5:** the next candidate scored 0.952 on held-out against the promoted baseline's 0.956 — inside the noise floor, alongside a clear train-side regression (0.946 → 0.836) — and the machine **declined to promote**. (Each run re-scores its baseline from fresh samples, which is why the promoted instruction reads 0.956 here and 0.934 the day before: scores are measurements, not stored constants.) A gate that can only say yes is decoration.

## Limitations

This is an n-of-1 system run by its own author. Fitness here is rubric pass-rate on deterministic checks (brand canon, structure, evidence density, citation grounding), not human quality judgment — the rubric can itself be gamed, which is exactly why promotion keeps a human in the loop. Held-out sets this small demonstrate the mechanism, not statistical power; rotation and set-hardening are ongoing work. I'd expect the same architecture at team scale to need adversarial case generation and periodic held-out refresh to stay honest.

## Takeaways

- **If your prompts improve every iteration, you are measuring the wrong thing.** Optimizing against your evaluation set guarantees the number goes up. Hold cases out or you're flying blind.
- **A noise floor turns scores into decisions.** Estimate variance from repeated sampling and refuse to interpret deltas beneath it. Most "improvements" I've measured were noise.
- **Emit verdicts, not dashboards.** Fixed comparison logic (`discard-overfit` as a first-class outcome) removes the human temptation to rationalize a favorable score.
- **Separate "passed the gate" from "shipped."** Machine gates filter; humans promote. The append-only promotion log costs nothing and makes the whole history auditable.
- **The optimizer must not own the judge.** Whatever process mutates prompts should have no write access to what evaluates them. This is an org-chart principle as much as a technical one.

## References

- Agrawal et al., *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning* (ICLR 2026), [arXiv:2507.19457](https://arxiv.org/abs/2507.19457) — the disjoint feedback/Pareto-validation design this loop follows.
- Khattab et al., *DSPy* — programmatic prompt optimization that popularized treating prompts as learned parameters (the regime where held-out discipline becomes non-optional).
- Husain, H., *Your AI Product Needs Evals* — the practitioner case for error analysis and eval-first iteration.
