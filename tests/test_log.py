import json

import pytest

from verification_spine import PromotionLog, Scores, evaluate

EPSILON = 0.0167


def advance_decision():
    return evaluate(Scores(train=0.5, heldout=0.5), Scores(train=0.9, heldout=0.9), EPSILON)


def discard_decision():
    return evaluate(Scores(train=0.8213, heldout=0.7273), Scores(train=0.8255, heldout=0.6818), EPSILON)


def pareto_decision():
    return evaluate(Scores(train=0.5, heldout=0.5), Scores(train=0.5, heldout=0.5), EPSILON)


def test_promotion_requires_a_keep_advance_verdict(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    for decision in (discard_decision(), pareto_decision()):
        with pytest.raises(ValueError, match="keep-advance"):
            log.promote("cand", "artifact", heldout=0.9, ack="approved", decision=decision)
    assert log.entries() == []


def test_promotion_without_ack_is_refused(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    for bad_ack in ("", "   "):
        with pytest.raises(ValueError):
            log.promote("cand", "artifact", heldout=0.9, ack=bad_ack, decision=advance_decision())
    assert log.entries() == []


def test_zero_width_only_ack_is_refused(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    with pytest.raises(ValueError):
        log.promote("cand", "artifact", heldout=0.9, ack="​​", decision=advance_decision())
    assert log.entries() == []


def test_invalid_heldout_is_refused(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    for bad in (float("nan"), float("inf"), -1.0, 2.0):
        with pytest.raises(ValueError, match="heldout"):
            log.promote("cand", "artifact", heldout=bad, ack="approved", decision=advance_decision())
    assert log.entries() == []


def test_promotion_appends_and_reads_back(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    entry = log.promote("cand-1", "instruction text", heldout=0.9336, ack="approved after review", decision=advance_decision())
    (read,) = log.entries()
    assert read.candidate_id == "cand-1"
    assert read.sha256 == entry.sha256
    assert read.heldout == pytest.approx(0.9336)
    assert read.ack == "approved after review"


def test_log_only_grows_and_preserves_order(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    log.promote("first", "a", heldout=0.90, ack="ok", decision=advance_decision())
    log.promote("second", "b", heldout=0.95, ack="ok", decision=advance_decision())
    assert [e.candidate_id for e in log.entries()] == ["first", "second"]


def test_field_separator_content_cannot_forge_or_break_entries(tmp_path):
    # The injection a plain-text format allowed: JSONL keeps it inert data.
    log = PromotionLog(tmp_path / "promotions.log")
    log.promote("good | sha256=forged", "artifact", heldout=0.9, ack="approved | extra=value", decision=advance_decision())
    (read,) = log.entries()
    assert read.candidate_id == "good | sha256=forged"
    assert read.ack == "approved | extra=value"


def test_newline_in_ack_is_rejected(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    with pytest.raises(ValueError, match="control"):
        log.promote("cand", "artifact", heldout=0.9, ack="approved\nBROKEN", decision=advance_decision())
    assert log.entries() == []


def test_control_characters_in_candidate_id_are_rejected(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    with pytest.raises(ValueError, match="control"):
        log.promote("evil\nid", "artifact", heldout=0.9, ack="approved", decision=advance_decision())


def test_malformed_line_is_reported_with_its_line_number(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    log.promote("cand", "artifact", heldout=0.9, ack="ok", decision=advance_decision())
    with open(log.path, "a", encoding="utf-8") as f:
        f.write("not json\n")
    with pytest.raises(ValueError, match="line 2"):
        log.entries()


def test_entries_are_valid_jsonl(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    log.promote("cand", "artifact", heldout=0.9, ack="ok", decision=advance_decision())
    record = json.loads(log.path.read_text().splitlines()[0])
    assert set(record) == {"timestamp", "candidate_id", "sha256", "heldout", "ack"}
