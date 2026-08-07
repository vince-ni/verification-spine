"""Evaluate a candidate against a baseline through the noise floor.

The numbers are the June 9, 2026 incident (docs/heldout-gate.md): the
candidate "improved" on train and regressed on held-out — the gate discards it.
"""
from verification_spine import Scores, estimate_noise, evaluate

# Estimate the noise floor by re-scoring the SAME artifact several times.
epsilon = estimate_noise([0.812, 0.798, 0.805, 0.821])
print(f"noise floor ε = {epsilon:.4f}")

baseline = Scores(train=0.8213, heldout=0.7273)
candidate = Scores(train=0.8255, heldout=0.6818)  # train up, held-out down

decision = evaluate(baseline, candidate, epsilon)
print(decision.verdict)
print(decision.reason)
