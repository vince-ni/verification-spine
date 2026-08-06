# When the Judge Regresses: A Cross-Vendor Review Catch

*Who reviews the reviewer? An incident report from the other side of the eval gate.*

> **TL;DR** — In mid-July 2026 I patched the lint script that judges my agent's output for brand-canon compliance. The patch passed my own review. A reviewer model from a different vendor — contractually required to *execute* the patched judge against evasion and regression suites, not just read it — caught that my one-line fix had silently degraded the judge below its pre-patch state. Three weeks later the pattern repeated at larger scale: same-vendor review of a batch of judging tools found zero must-fix issues; cross-vendor re-review found eight, all of which reproduced. The rule I now operate under: **for judging assets, same-vendor review counts as unreviewed.**

## The incident

My agent system's outputs are gated by deterministic judges — among them a canon-lint script that checks brand copy: trademark casing, deprecated product names, forbidden vocabulary. Hard failures block publication.

The lint had an evasion hole: full-width Unicode lookalikes. "ＦＵＲＩＺＥＮ" reads like "FURIZEN" to a human and matches nothing in a byte-comparing rule. My fix was the idiomatic one — normalize before checking:

```python
text = unicodedata.normalize("NFKC", text)
```

One line, standard library, textbook. It also happens to be wrong.

NFKC performs *compatibility* folding, and compatibility folding does not stop at full-width letters. It folds **™ (U+2122) into the two ASCII letters "TM"** — along with ligatures, superscripts, and a long tail of symbols. Every rule keyed to the literal ™ character broke at once: correctly written product names started drawing false warnings, and — worse — the check that should hard-FAIL a deprecated name **degraded to a soft WARN**. The patched judge was more permissive than the unpatched one. A fix for one evasion had quietly opened a second, larger hole — in the judge itself.

## Why self-review missed it

I reviewed my own patch and passed it. So would most people, and — this is the uncomfortable part — so did the model that wrote it, when asked to double-check.

The mechanism is author anchoring. When you verify your own change, you verify your *intent*: does it now catch full-width evasion? It does. Test written, test green, ship. The question you don't ask is the one that matters: *what else did this line change?* The author — human or model — is structurally the wrong entity to ask it, because the author's attention is organized around the goal, not the side effects. A same-family model reviewing the patch inherits the same organization of attention. Agreement between them measures shared perspective, not correctness.

## The catch

The reviewer that caught it was a model from a different vendor, and the review contract was the operative part:

- **Execute, don't read.** The reviewer must run the patched judge, not reason about it from the diff.
- **Two suites, not one.** An *evasion suite* (violations that must still be caught) and a *regression suite* (previously-correct inputs that must still pass). Authors always run the first. The second is where side effects live.

The regression suite lit up immediately: canonical product names — with their ™ intact — were failing checks they had passed for months. I reproduced the failure byte-by-byte before accepting it (reviewers produce false positives too; more below), then replaced the blanket NFKC call with **targeted folding** — mapping only the full-width ASCII range (U+FF01–FF5E) and leaving symbols untouched — and re-ran the full matrix before shipping.

## It wasn't a one-off

Three weeks later, August 1: a batch of new judging tools went through adversarial review by a same-vendor model. Verdict: zero must-fix findings. I sent the same batch to a cross-vendor reviewer with the same execute-don't-read contract. Verdict: **eight must-fix findings, every one of which I reproduced by hand** — including a mandatory-confirmation gate that an alternate output flag bypassed entirely, and a code-fence pattern that masked failing checks as green.

Zero versus eight, on the same code, same week. That spread is the empirical case for the rule I now keep in writing: judging assets — lints, metamorphic checks, oracles — do not count as reviewed until a model from a different vendor has executed them adversarially.

## Asymmetric trust

Cross-vendor review comes with a trust rule that sounds paranoid and is merely accurate:

> **A refutation is evidence. An endorsement is not.**

When the outside reviewer says "this is broken," that claim is checkable — you reproduce it and it either holds or it doesn't. When it says "looks good," you have learned almost nothing: models trained on similar data with similar methods share blind spots, and the research literature keeps finding that model agreement and correctness are different quantities. Consensus between two judges can mean both are right or both are blind, and it does not tell you which.

The symmetric corollary: reviewers get things wrong in the accusing direction too. Every refutation in both incidents above was accepted only after I reproduced it against real bytes. The pipeline is fixed: **cross-vendor refutation → human reproduction → fix → full re-verification** (both suites — the fix must catch what it should *and* not break what it shouldn't).

## What this costs, honestly

A second vendor's review costs money and wall-clock time. I don't apply it to everything — only to assets where an undetected error compounds: the judges themselves, anything published externally, anything touching permissions or data. And it is not insurance: different vendors' models still share training-distribution overlap, so cross-vendor buys you *less-correlated* blind spots, not uncorrelated ones. The final backstop is unchanged — consequential judgments get reproduced by a human.

## Takeaways

- **The judge is code too, and its regressions are the expensive ones.** A broken worker fails a task; a broken judge silently corrupts every verdict after it.
- **Verify side effects, not intent.** After any fix, run the inputs that used to pass. The author will never think to; that's not a character flaw, it's what authorship does to attention.
- **Same-family review measures agreement, not correctness.** If the review matters, the reviewer should come from a different stable — and should be made to execute the code.
- **Trust asymmetrically.** Investigate refutations; discount endorsements. Then reproduce before you believe either.
- **Blanket normalization is a loaded gun.** NFKC folds symbols, ligatures, and superscripts along with the characters you meant. When rules depend on literal characters, fold *exactly* the range you intend and nothing else.

## References

- Unicode Standard Annex #15, *Unicode Normalization Forms* — the specification of NFKC's compatibility folding, side effects included.
- Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (2023), [arXiv:2306.05685](https://arxiv.org/abs/2306.05685) — systematic biases of model judges.
- Companion post: [Prompt Evolution Overfits: An Incident Report](heldout-gate.md) — the held-out gate on the other side of this same system.
