"""`stable_hash()` and `job_id()` — the one deterministic hash P-01 owns
(U-RESILIENCE-13), `code/P-01-intake.md` §1.

`rqa.github` imports this module directly for its own mutation ids
(`code/P-01-intake.md` §1: "`rqa.github` imports `rqa.intake.identity` directly
for `stable_hash`, because U-RESILIENCE-13 places the one hashing mechanism
here and names P-09 as its other user"). Until this package landed,
`rqa.github.writes._stable_hash` fell back to this exact formula —
`sha256("\\x1f".join(parts).encode()).hexdigest()` — so both paths were always
byte-identical and no `client_mutation_id` changes now that this module
exists.
"""

from __future__ import annotations

import hashlib

__all__ = ["stable_hash", "job_id"]


def stable_hash(*parts: str) -> str:
    """SHA-256 hex digest of `parts` joined by the ASCII unit-separator
    (`\\x1f`), so no part's own content can be crafted to collide with a
    different split of the same joined bytes."""
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()


def job_id(repo: str, number: int, head_sha: str) -> str:
    """`Job.id` (`CONTRACTS.md` §1: "stable_hash(repo, number, head_sha)")."""
    return stable_hash(repo, str(number), head_sha)
