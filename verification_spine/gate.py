"""Held-out promotion gate: the part of a self-improving loop that says no.

Verdict logic extracted from a production personal agent system. The premise:
an optimizer measured only on the data it optimizes against will report
improvement forever. Verdicts here are decided by a held-out split the
optimizer never sees, filtered through a noise floor. Promotion to production
is a separate, human-anchored step (see log.py).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    KEEP_ADVANCE = "keep-advance"
    KEEP_PARETO = "keep-pareto"
    DISCARD_OVERFIT = "discard-overfit"


@dataclass(frozen=True)
class Scores:
    """Fitness of one artifact on the two disjoint splits, each in [0, 1]."""

    train: float
    heldout: float


@dataclass(frozen=True)
class Decision:
    verdict: Verdict
    train_delta: float
    heldout_delta: float
    epsilon: float
    reason: str


def estimate_noise(repeated_scores: list[float]) -> float:
    """Noise floor from repeatedly scoring the SAME artifact on the SAME split.

    Score deltas smaller than the floor are silence, not signal. Sample
    standard deviation is a starting point; be conservative — probe several
    artifacts and take the largest floor you observe.
    """
    if len(repeated_scores) < 2:
        raise ValueError("need at least two repeated scores to estimate noise")
    return statistics.stdev(repeated_scores)


def evaluate(baseline: Scores, candidate: Scores, epsilon: float) -> Decision:
    """Decide a candidate's fate against a baseline, through the noise floor.

    Only the held-out delta decides. Train fitness is carried for diagnosis —
    the over-fit signature is train up while held-out falls — but a train gain
    never earns a pass on its own.
    """
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative")
    train_delta = candidate.train - baseline.train
    heldout_delta = candidate.heldout - baseline.heldout

    if heldout_delta > epsilon:
        verdict = Verdict.KEEP_ADVANCE
        reason = f"held-out {heldout_delta:+.3f} clears the noise floor ({epsilon:.3f})"
    elif heldout_delta < -epsilon:
        verdict = Verdict.DISCARD_OVERFIT
        reason = f"held-out {heldout_delta:+.3f} regresses beyond the noise floor ({epsilon:.3f})"
        if train_delta > -epsilon:
            reason += f"; train {train_delta:+.3f} — the over-fit signature"
    else:
        verdict = Verdict.KEEP_PARETO
        reason = (
            f"held-out {heldout_delta:+.3f} is inside the noise floor ({epsilon:.3f}): "
            "no signal, no promotion"
        )
    return Decision(verdict, train_delta, heldout_delta, epsilon, reason)
