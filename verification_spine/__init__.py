"""verification-spine: a minimal held-out promotion gate for self-improving prompts and agents."""

from verification_spine.folding import fold_fullwidth
from verification_spine.gate import Decision, Scores, Verdict, estimate_noise, evaluate
from verification_spine.log import Promotion, PromotionLog

__all__ = [
    "Decision",
    "Promotion",
    "PromotionLog",
    "Scores",
    "Verdict",
    "estimate_noise",
    "evaluate",
    "fold_fullwidth",
]

__version__ = "0.1.0"
