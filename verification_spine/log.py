"""Append-only promotion log, coupled to the gate, with a mandatory acknowledgment.

Passing the held-out gate earns advancement inside the optimization loop.
Taking over production is a different event, and this log enforces the
coupling: a promotion requires a gate ``Decision`` whose verdict is
``keep-advance``, plus an explicit acknowledgment string. What the library
can enforce is that *some caller* supplied the acknowledgment — proving the
acknowledger is human is the deployment's job (approval UIs, signed slips,
filesystem permissions on this file).

Entries are JSON Lines: one self-contained JSON object per line, so no
field content can forge or corrupt neighbouring records.
"""
from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from verification_spine.gate import Decision, Verdict

_INVISIBLE_CATEGORIES = {"Cc", "Cf", "Zs", "Zl", "Zp"}


def _has_visible_character(text: str) -> bool:
    return any(unicodedata.category(ch) not in _INVISIBLE_CATEGORIES for ch in text)


def _reject_control_characters(value: str, field: str) -> None:
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        raise ValueError(f"{field} must not contain control characters")


@dataclass(frozen=True)
class Promotion:
    timestamp: str
    candidate_id: str
    sha256: str
    heldout: float
    ack: str


class PromotionLog:
    """One JSON object per line: timestamp, candidate id, sha256(artifact), held-out, ack.

    The interface only appends. Tamper-evidence, durability, and concurrent
    writers are out of scope here — layer file permissions, git history, or a
    hash chain on top in deployment.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def promote(
        self,
        candidate_id: str,
        artifact: str,
        heldout: float,
        ack: str,
        decision: Decision,
    ) -> Promotion:
        """Record a promotion. Refuses candidates that did not pass the gate.

        Raises ``ValueError`` if the decision's verdict is not ``keep-advance``,
        if ``heldout`` is not a finite number in [0, 1], or if ``ack`` carries
        no visible characters (empty, whitespace-only, and zero-width strings
        are refused — a promotion nobody explicitly acknowledged is not one).
        """
        if decision.verdict is not Verdict.KEEP_ADVANCE:
            raise ValueError(
                f"only keep-advance candidates can be promoted; "
                f"verdict was {decision.verdict.value}"
            )
        if not math.isfinite(heldout) or not 0.0 <= heldout <= 1.0:
            raise ValueError(f"heldout must be a finite number in [0, 1], got {heldout!r}")
        _reject_control_characters(candidate_id, "candidate_id")
        _reject_control_characters(ack, "ack")
        if not ack or not _has_visible_character(ack):
            raise ValueError("promotion requires an explicit acknowledgment; refusing")

        entry = Promotion(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            candidate_id=candidate_id,
            sha256=hashlib.sha256(artifact.encode("utf-8")).hexdigest(),
            heldout=heldout,
            ack=ack.strip(),
        )
        line = json.dumps(
            {
                "timestamp": entry.timestamp,
                "candidate_id": entry.candidate_id,
                "sha256": entry.sha256,
                "heldout": entry.heldout,
                "ack": entry.ack,
            },
            ensure_ascii=False,
        )
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        return entry

    def entries(self) -> list[Promotion]:
        """Parse the log. Raises ``ValueError`` naming the first malformed line."""
        if not self.path.exists():
            return []
        promotions = []
        for lineno, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                promotions.append(
                    Promotion(
                        timestamp=record["timestamp"],
                        candidate_id=record["candidate_id"],
                        sha256=record["sha256"],
                        heldout=float(record["heldout"]),
                        ack=record["ack"],
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"malformed promotion log line {lineno}: {exc}") from exc
        return promotions
