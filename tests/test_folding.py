"""The folding tests encode the regression suite that caught a real judge bug.

An NFKC-based "fix" folded ™ into TM and silently weakened the judge
(docs/cross-vendor-review.md). These tests are the suite that would have
caught it — and the last one documents the trap itself.
"""
import unicodedata

from verification_spine import fold_fullwidth


def test_fullwidth_letters_fold_to_ascii():
    assert fold_fullwidth("ＦＵＲＩＺＥＮ") == "FURIZEN"


def test_fullwidth_digits_and_punctuation_fold():
    assert fold_fullwidth("！５０％") == "!50%"


def test_trademark_symbol_is_preserved():
    # The regression that NFKC introduced: rules keyed to a literal ™ broke.
    assert fold_fullwidth("Brand™ Dog Bed") == "Brand™ Dog Bed"


def test_ligatures_are_preserved():
    assert fold_fullwidth("ﬁ") == "ﬁ"


def test_plain_ascii_passes_through():
    text = "FURIZEN 48\" x 30\" x 6\" (L)"
    assert fold_fullwidth(text) == text


def test_nfkc_demonstrates_the_trap():
    # Why this module exists: blanket NFKC folds symbols along with widths.
    assert unicodedata.normalize("NFKC", "™") == "TM"
    assert fold_fullwidth("™") == "™"
