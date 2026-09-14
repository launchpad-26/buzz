"""The five `rqa` exit codes and nothing else — architecture.md §11, the
issue's own DoD ("Exit codes are exactly 0 ok, 1 input error, 2 network, 3
auth, 4 other").
"""

from __future__ import annotations

OK = 0
INPUT_ERROR = 1
NETWORK = 2
AUTH = 3
OTHER = 4

__all__ = ["OK", "INPUT_ERROR", "NETWORK", "AUTH", "OTHER"]
