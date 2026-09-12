"""`rqa.reuse` — P-13 revision reuse.

The package exposes only §1's E-05 entry point and two local decision/error types. Shared
`CarryOver` and `CarriedEvidence` values remain defined and imported through `rqa.contracts`.
"""

from __future__ import annotations

from rqa.reuse.obligations import Reason, ReuseError
from rqa.reuse.reuse import carry_over

__all__ = ["carry_over", "Reason", "ReuseError"]
