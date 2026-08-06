"""The gate tests replay real production incidents, verbatim fitness values.

Sources: evolution run logs of the originating system, June–July 2026
(docs/heldout-gate.md walks through the June 9 incident in full).
"""
import pytest

from verification_spine import Scores, Verdict, estimate_noise, evaluate

EPSILON = 0.0167  # the originating slot's measured noise floor


def test_genuine_improvement_advances():
    # June 9, round 1: brand canon + structural checklist embedded — both splits agree.
    baseline = Scores(train=0.3491, heldout=0.3182)
    candidate = Scores(train=0.8213, heldout=0.7273)
    decision = evaluate(baseline, candidate, EPSILON)
    assert decision.verdict is Verdict.KEEP_ADVANCE


def test_overfit_is_discarded_even_when_train_improves():
    # June 9, round 2: train ticked up, held-out fell 2.7x the noise floor.
    baseline = Scores(train=0.8213, heldout=0.7273)
    candidate = Scores(train=0.8255, heldout=0.6818)
    decision = evaluate(baseline, candidate, EPSILON)
    assert decision.verdict is Verdict.DISCARD_OVERFIT
    assert decision.train_delta > 0  # it looked like progress
    assert "over-fit signature" in decision.reason


def test_within_noise_floor_keeps_pareto_and_does_not_promote():
    # July 5: candidate 0.9520 vs promoted baseline 0.9563 — inside the floor.
    baseline = Scores(train=0.9457, heldout=0.9563)
    candidate = Scores(train=0.8363, heldout=0.9520)
    decision = evaluate(baseline, candidate, EPSILON)
    assert decision.verdict is Verdict.KEEP_PARETO


def test_train_gain_alone_never_earns_a_pass():
    baseline = Scores(train=0.50, heldout=0.50)
    candidate = Scores(train=0.99, heldout=0.50)
    assert evaluate(baseline, candidate, EPSILON).verdict is Verdict.KEEP_PARETO


def test_negative_epsilon_is_rejected():
    scores = Scores(train=0.5, heldout=0.5)
    with pytest.raises(ValueError):
        evaluate(scores, scores, -0.01)


def test_estimate_noise_needs_repeated_scores():
    with pytest.raises(ValueError):
        estimate_noise([0.8])


def test_estimate_noise_is_zero_for_identical_scores():
    assert estimate_noise([0.8, 0.8, 0.8]) == 0.0


def test_estimate_noise_grows_with_spread():
    assert estimate_noise([0.7, 0.9]) > estimate_noise([0.79, 0.81])
