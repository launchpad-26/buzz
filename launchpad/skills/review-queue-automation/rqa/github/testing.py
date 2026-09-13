"""U-DOCS-24's salvaged mechanism: a deliberately non-token-shaped credential
paired with a socket constructor that raises on construction.
`code/P-09-github-adapter.md` §1, §4, §8 (T10).

The adapter is the one place in RQA where real GitHub transports exist, so a
test suite that regressed into a live call would authenticate as a real
account against a real pull request. These two helpers turn that reach into a
deterministic failure at the point of the call: every test in this package —
and any other part's fakes for this adapter — uses `NON_TOKEN_CREDENTIAL`
instead of anything resolvable, and `raising_socket()` guarantees that a code
path which bypasses the injected fake sender cannot complete a connection.

The estate's `tests/conftest.py` applies the same pairing suite-wide under
pytest; this module is the package-owned, runner-independent form, so the
guarantee also holds under `tests/run_all.py`, which never imports conftest.
"""

from __future__ import annotations

import socket
from contextlib import contextmanager

__all__ = ["NON_TOKEN_CREDENTIAL", "raising_socket"]

#: Deliberately not token-shaped: nothing may be tempted to send it, and a
#: secret scanner should not have to decide whether it is real.
NON_TOKEN_CREDENTIAL = "not-a-real-token-rqa-github-sentinel"


class _RaisingSocket(socket.socket):
    """Any attempt to open a socket while the guard is active is a defect."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise RuntimeError(
            "rqa.github attempted a live network connection; every test must "
            "inject a fake sender and use NON_TOKEN_CREDENTIAL"
        )


def _raising_getaddrinfo(*args: object, **kwargs: object) -> object:
    raise RuntimeError(
        "rqa.github attempted a live network connection; every test must "
        "inject a fake sender and use NON_TOKEN_CREDENTIAL"
    )


@contextmanager
def raising_socket():
    """Swap `socket.socket` AND `socket.getaddrinfo` for guards that raise,
    restoring the prior ones on exit. Name resolution is guarded too, so not
    even a DNS query leaves the process and the failure is deterministic
    offline. The raised `RuntimeError` is deliberately not an `OSError`: the
    transport's availability handling must not swallow it (§8 T10)."""
    original_socket = socket.socket
    original_getaddrinfo = socket.getaddrinfo
    socket.socket = _RaisingSocket  # type: ignore[misc]
    socket.getaddrinfo = _raising_getaddrinfo  # type: ignore[assignment]
    try:
        yield _RaisingSocket
    finally:
        socket.socket = original_socket  # type: ignore[misc]
        socket.getaddrinfo = original_getaddrinfo  # type: ignore[assignment]
