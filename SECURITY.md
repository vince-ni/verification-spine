# Security

## Reporting

Use GitHub's private vulnerability reporting on this repository. You should
receive a response within a week.

## Supported versions

Only the latest release receives fixes.

## Threat model — what this library does and does not guarantee

This project's whole premise is honest verification, so here is its own
honest boundary:

**Enforced by the library:**
- The gate fails closed on invalid scores and epsilon.
- The promotion log refuses candidates without a `keep-advance` verdict,
  refuses invisible or control-character acknowledgments, and stores entries
  as JSON Lines so field content cannot forge or corrupt neighbouring
  records.

**Not enforced — layer these in deployment:**
- **Human-ness of the acknowledgment.** The library can require *an*
  acknowledgment; it cannot prove a human supplied it. Use approval UIs,
  signed slips, or reviewed pull requests.
- **Tamper evidence and durability.** "Append-only" describes the API, not
  the file. Protect the log with filesystem permissions, git history, or a
  hash chain.
- **Concurrent writers.** No file locking is provided.
- **Visual spoofing.** Bidirectional and other invisible-but-`Cf` Unicode
  characters mixed into visible acks are not rejected.

## A note on normalization

`fold_fullwidth()` exists because blanket NFKC normalization silently folded
™ into "TM" and weakened a production judge (docs/cross-vendor-review.md).
If you extend folding, run the regression suite in `tests/test_folding.py` —
it encodes that incident.
