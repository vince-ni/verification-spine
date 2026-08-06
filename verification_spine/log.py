"""Append-only promotion log with a mandatory human acknowledgment.

Passing the held-out gate earns advancement inside the optimization loop.
Taking over production is a different event, and it is human-anchored: this
log refuses any entry without an explicit acknowledgment string, and its
interface can only append. (Protecting the file itself from edits is a
deployment concern — filesystem permissions, git history, or both.)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_SEP = " | "


@dataclass(frozen=True)
class Promotion:
    timestamp: str
    candidate_id: str
    sha256: str
    heldout: float
    ack: str


class PromotionLog:
    """One line per promotion: timestamp | id | sha256(artifact) | held-out | ack."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def promote(self, candidate_id: str, artifact: str, heldout: float, ack: str) -> Promotion:
        """Record a promotion. Refuses silently-automated promotions by design."""
        if not ack or not ack.strip():
            raise ValueError(
                "promotion requires an explicit human acknowledgment; refusing"
            )
        entry = Promotion(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            candidate_id=candidate_id,
            sha256=hashlib.sha256(artifact.encode("utf-8")).hexdigest(),
            heldout=heldout,
            ack=ack.strip(),
        )
        line = _SEP.join(
            [
                entry.timestamp,
                f"id={entry.candidate_id}",
                f"sha256={entry.sha256}",
                f"heldout={entry.heldout:.4f}",
                f"ack={entry.ack}",
            ]
        )
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        return entry

    def entries(self) -> list[Promotion]:
        if not self.path.exists():
            return []
        promotions = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                promotions.append(_parse(line))
        return promotions


def _parse(line: str) -> Promotion:
    timestamp, candidate_id, sha256, heldout, ack = line.split(_SEP, 4)
    return Promotion(
        timestamp=timestamp,
        candidate_id=candidate_id.removeprefix("id="),
        sha256=sha256.removeprefix("sha256="),
        heldout=float(heldout.removeprefix("heldout=")),
        ack=ack.removeprefix("ack="),
    )
