"""The full loop: gate verdict -> acknowledged promotion -> auditable log.

Also demonstrates the two refusals: a candidate that didn't pass the gate,
and an acknowledgment nobody actually wrote.
"""
from pathlib import Path
from tempfile import TemporaryDirectory

from verification_spine import PromotionLog, Scores, evaluate

EPSILON = 0.0167

with TemporaryDirectory() as tmp:
    log = PromotionLog(Path(tmp) / "promotions.log")

    # A genuine improvement passes the gate...
    good = evaluate(Scores(0.7593, 0.8247), Scores(0.8948, 0.9336), EPSILON)
    print(good.verdict)

    # ...but promotion still needs an explicit acknowledgment:
    try:
        log.promote("july-4-candidate", "instruction text", heldout=0.9336, ack="", decision=good)
    except ValueError as e:
        print("refused:", e)

    entry = log.promote(
        "july-4-candidate", "instruction text", heldout=0.9336,
        ack="approved after review", decision=good,
    )
    print("promoted:", entry.candidate_id, entry.sha256[:12])

    # A discarded candidate cannot be promoted at all — with any ack:
    overfit = evaluate(Scores(0.8213, 0.7273), Scores(0.8255, 0.6818), EPSILON)
    try:
        log.promote("june-9-round-2", "instruction text", heldout=0.6818, ack="yes", decision=overfit)
    except ValueError as e:
        print("refused:", e)

    print("log entries:", [e.candidate_id for e in log.entries()])
