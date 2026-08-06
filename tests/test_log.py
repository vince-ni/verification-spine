import pytest

from verification_spine import PromotionLog


def test_promotion_without_ack_is_refused(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    with pytest.raises(ValueError):
        log.promote("cand-1", "instruction text", heldout=0.93, ack="")
    with pytest.raises(ValueError):
        log.promote("cand-1", "instruction text", heldout=0.93, ack="   ")
    assert log.entries() == []  # a refused promotion leaves no trace


def test_promotion_appends_and_reads_back(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    entry = log.promote("cand-1", "instruction text", heldout=0.9336, ack="approved after review")
    (read,) = log.entries()
    assert read.candidate_id == "cand-1"
    assert read.sha256 == entry.sha256
    assert read.heldout == pytest.approx(0.9336)
    assert read.ack == "approved after review"


def test_log_only_grows_and_preserves_order(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    log.promote("first", "a", heldout=0.90, ack="ok")
    log.promote("second", "b", heldout=0.95, ack="ok")
    ids = [e.candidate_id for e in log.entries()]
    assert ids == ["first", "second"]


def test_ack_may_contain_the_separator(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    log.promote("cand", "text", heldout=0.9, ack="approved | numbers must trace to a source")
    (read,) = log.entries()
    assert read.ack == "approved | numbers must trace to a source"
