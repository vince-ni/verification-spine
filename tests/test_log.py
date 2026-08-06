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


def test_newline_injection_in_ack_is_rejected(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    forged = "approved\n2026-01-01T00:00:00+00:00 | id=evil | sha256=fake | heldout=1.0000 | ack=forged"
    with pytest.raises(ValueError):
        log.promote("real", "artifact", heldout=0.9, ack=forged)
    assert log.entries() == []


def test_control_characters_in_candidate_id_are_rejected(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    with pytest.raises(ValueError):
        log.promote("evil\nid", "artifact", heldout=0.9, ack="approved")


def test_zero_width_only_ack_is_rejected(tmp_path):
    log = PromotionLog(tmp_path / "promotions.log")
    with pytest.raises(ValueError):
        log.promote("cand", "artifact", heldout=0.9, ack="​​")
    assert log.entries() == []
