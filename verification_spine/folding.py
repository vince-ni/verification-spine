"""Targeted full-width folding — the repair from a real judge regression.

The obvious fix for full-width evasion ("ＦＵＲＩＺＥＮ" sneaking past rules
keyed to "FURIZEN") is NFKC normalization. But NFKC performs *compatibility*
folding: it also turns ™ (U+2122) into "TM", ﬁ into "fi", and a long tail of
symbols into their ASCII spellings — which silently broke every rule keyed to
a literal ™ in the judge this function was extracted from
(docs/cross-vendor-review.md). When rules depend on literal characters, fold
exactly the range you intend and nothing else.
"""
from __future__ import annotations

# Full-width ASCII block (U+FF01–FF5E) maps to ASCII by a fixed offset.
_FULLWIDTH_TO_ASCII = {code: code - 0xFEE0 for code in range(0xFF01, 0xFF5F)}


def fold_fullwidth(text: str) -> str:
    """Map full-width ASCII characters to ASCII. Symbols are left untouched."""
    return text.translate(_FULLWIDTH_TO_ASCII)
