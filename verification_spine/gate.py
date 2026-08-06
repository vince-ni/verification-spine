"""Held-out promotion gate: the part of a self-improving loop that says no.

Verdict logic extracted from a production personal agent system. The premise:
an optimizer measured only on the data it optimizes against will report
improvement forever. Verdicts here are decided by a held-out split the
optimizer never sees, filtered through a noise floor. Promotion to production
is a separate, human-anchored step (see log.py).
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


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


def estimate_noise(repeated_scores: Sequence[float]) -> float:
    """Noise floor from repeatedly scoring the SAME artifact on the SAME split.

    Score deltas smaller than the floor are silence, not signal. Sample
    standard deviation is a starting point; be conservative — probe several
    artifacts and take the largest floor you observe.
    """
    scores = list(repeated_scores)
    if len(scores) < 2:
        raise ValueError("need at least two repeated scores to estimate noise")
    for value in scores:
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"scores must be finite numbers in [0, 1], got {value!r}")
    return statistics.stdev(scores)


def _validate(scores: Scores, name: str) -> None:
    for field in ("train", "heldout"):
        value = getattr(scores, field)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{name}.{field} must be a finite number in [0, 1], got {value!r}")


def evaluate(baseline: Scores, candidate: Scores, epsilon: float) -> Decision:
    """Decide a candidate's fate against a baseline, through the noise floor.

    Only the held-out delta decides. Train fitness is carried for diagnosis —
    the over-fit signature is train up while held-out falls — but a train gain
    never earns a pass on its own.

    Invalid inputs raise instead of judging: a gate that fails open on NaN,
    infinity, or out-of-range scores would let corrupted scoring promote.
    """
    if not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError(f"epsilon must be a finite non-negative number, got {epsilon!r}")
    _validate(baseline, "baseline")
    _validate(candidate, "candidate")
    train_delta = candidate.train - baseline.train
    heldout_delta = candidate.heldout - baseline.heldout

    if heldout_delta > epsilon:
        verdict = Verdict.KEEP_ADVANCE
        reason = f"held-out {heldout_delta:+.3f} clears the noise floor ({epsilon:.3f})"
    elif heldout_delta < -epsilon:
        verdict = Verdict.DISCARD_OVERFIT
        reason = f"held-out {heldout_delta:+.3f} regresses beyond the noise floor ({epsilon:.3f})"
        if train_delta > 0:
            reason += f"; train {train_delta:+.3f} — the over-fit signature"
    else:
        verdict = Verdict.KEEP_PARETO
        reason = (
            f"held-out {heldout_delta:+.3f} is inside the noise floor ({epsilon:.3f}): "
            "no signal, no promotion"
        )
    return Decision(verdict, train_delta, heldout_delta, epsilon, reason)
