"""`rqa.judgement` — `code/CONTRACTS.md` §9 E-09, owned by `code/P-07-judgement.md`.

Turns the selected plan, carried evidence, validated panel verdicts, pinned
policy, and canonical captured facts into one deterministic current-job
`Judgement` (`judge`), and renders it into a pure GitHub review/comment body
(`render`). No other RQA module imports from `rqa.judgement` except through
this file (§1); `Judgement` and `Assurance` are `rqa.contracts` types,
re-exported here rather than redefined.
"""

from __future__ import annotations

from rqa.contracts import Assurance, Judgement
from rqa.judgement.judge import JudgementError, judge
from rqa.judgement.render import render

__all__ = ["judge", "render", "Judgement", "Assurance", "JudgementError"]
