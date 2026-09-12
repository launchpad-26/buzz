"""Credential resolution and per-repository capability probing — E-22 and E-16,
`code/P-08-authority-gate.md` §4.

**The credential never leaves this module's stack frame.** `credential()` shells out to
`gh auth token` (E-22) and hands the value to exactly one caller, `probe_capability`,
which passes it to the injected probe and drops it. It is never returned to the gate,
never stored, never recorded, never logged and never reachable from an exception —
not in its message, not on `__context__` or `__cause__`, and not in the locals of any
frame its traceback keeps. That last clause is the one round 1 got wrong: `raise ...
from None` hides a chain without breaking it, so a caught `subprocess.TimeoutExpired`
kept the captured credential on `__context__.output` (gate G-2192 F1). `_raise_unavailable`
severs it; the `finally: del` in `probe_capability` and the `del completed` in
`credential` do the same for frame locals.

**`GithubUnavailable` is a value, not a failure.** An adapter that could not answer is
persisted as an empty capability set, so every activity is denied `CAPABILITY_MISSING`
until a later job re-probes (§4). Nothing is assumed on trust: an unreachable GitHub
never widens authority.

**What is attested but not proven is recorded, not hidden.** `CapabilityProof` carries
`attested_not_proven` straight from the reading, which is where ADR-0062's accepted
residual is written down: RQA confines the authority it *exercises*, and the breadth of
the operator's `gh auth token` is outside RQA to narrow.

**P-09 is not imported.** `probe_capability` takes the probe as an argument, exactly as
E-04 hands it to the gate, and both values E-16 may return — `CapabilityReading`,
`GithubUnavailable` — are `CONTRACTS.md` §4 types. How GitHub's permission levels and
token scopes become the capability vocabulary is `rqa.github`'s to decide (§4).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING, NoReturn, Protocol

from rqa.authority.gate import GateError
from rqa.contracts import CapabilityReading, GithubUnavailable

if TYPE_CHECKING:  # annotation-only; `store` imports this module, never the reverse
    from rqa.authority.store import CapabilityStore

__all__ = [
    "CapabilityProof",
    "CredentialGithubUnavailable",
    "GithubProbe",
    "credential",
    "probe_capability",
]

#: E-22's process, named once. `--hostname` is deliberately absent: the operator's
#: default host is the one `gh` is authenticated against, and P-08 reads no
#: configuration of its own (§7) from which a different one could come.
GH_TOKEN_ARGV: tuple[str, ...] = ("gh", "auth", "token")

#: A credential read that hangs is a credential read that failed.
CREDENTIAL_TIMEOUT_SECONDS = 30.0


class CredentialGithubUnavailable(GateError):
    """`gh` is absent, not logged in, or exited non-zero, so no probe can be made.

    A `GateError` subclass by §4: no credential is not a policy answer about a
    repository, it is RQA being unable to ask the question at all.
    """


class GithubProbe(Protocol):
    """P-08's view of P-09's E-16 capability probe, injected into `grant` (E-04).

    Declared here, not in `rqa/edges.py`: `CONTRACTS.md` §9 names this Protocol in
    E-04's signature and `rqa.edges` keeps it an empty Protocol whose docstring says
    its shape is P-08's to state. This is that statement, and the method repeats E-16's
    free signature verbatim — `probe(*, repo, credential) -> CapabilityReading |
    GithubUnavailable`.
    """

    def probe(self, *, repo: str, credential: str) -> CapabilityReading | GithubUnavailable: ...


@dataclass(frozen=True)
class CapabilityProof:
    id: int
    repo: str
    job_id: str
    capabilities: frozenset[str]  # adapter vocabulary, e.g. "pulls:write"
    login: str  # the GitHub login the token belongs to (for the record; never for auth decisions)
    probed_at: datetime
    attested_not_proven: frozenset[str]  # capabilities GitHub reports but the probe could
    #                                      not exercise (ADR-0062's accepted residual)


def _now() -> datetime:
    """The probe clock: an aware UTC timestamp. Substituted in tests."""
    return datetime.now(timezone.utc)


def _run(argv: tuple[str, ...]) -> subprocess.CompletedProcess:
    """The one process launch in P-08 — E-22, `container.md`'s GitHub CLI edge.

    Isolated behind a module-level name so the suite can exercise every branch of
    `credential()` without a real `gh` on the machine: no test in this skill runs a
    real process or reaches the network.
    """
    return subprocess.run(
        list(argv), capture_output=True, timeout=CREDENTIAL_TIMEOUT_SECONDS, check=False
    )


def _raise_unavailable(message: str) -> NoReturn:
    """Raise `CredentialGithubUnavailable` with no reachable predecessor of any kind.

    `raise X from None` is not enough and never was. It sets `__cause__ = None` and
    `__suppress_context__ = True`, which suppress the chain's *display*; Python's
    implicit chaining still attaches the exception being handled to `__context__`, whole
    and readable. On this path that object is a real `subprocess.TimeoutExpired` whose
    `.output` is the credential, so `error.__context__.output` hands the token to
    anything that introspects the exception instead of formatting it — P-02's error
    handling, a structured reporter, `traceback.TracebackException(chain=True)`, a
    debugger, `vars(error)`. `str(error)` shows nothing, which is exactly why a
    text-only guard cannot see it (gate G-2192 F1).

    Severing *before* the raise does not work either: the `raise` statement re-attaches
    the handled exception afterwards. The severance therefore happens in a `finally`
    while the exception is already propagating, which is both unconditional and
    independent of whatever the caller happened to be handling. `from None` is kept
    beside it rather than replaced by it — it is the declaration of intent at the raise
    site, and the `finally` is what makes the intent true.
    """
    error = CredentialGithubUnavailable(message)
    try:
        raise error from None
    finally:
        error.__cause__ = None
        error.__context__ = None
        error.__suppress_context__ = True


def credential() -> str:
    """E-22. Runs `gh auth token` and returns its stdout, stripped.

    Raises `CredentialGithubUnavailable` if gh is absent, not logged in, or exits
    non-zero. The value is held in memory for the duration of one probe and never
    written anywhere — not to the store, not to the record, not to logs, and not on any
    attribute or frame reachable from the exception a failure raises.

    No failure message quotes the process's output. On success that output *is* the
    credential, and a message that echoes it on one branch is a message that leaks it
    the day the branches are refactored. For the same reason the `CompletedProcess` is
    unbound before either failure branch raises: a traceback keeps its frames, and a
    frame holding the process result holds the credential.
    """
    try:
        completed = _run(GH_TOKEN_ARGV)
    except (OSError, subprocess.SubprocessError) as exc:
        _raise_unavailable(
            f"`gh auth token` could not be run ({type(exc).__name__}); "
            "RQA has no GitHub credential"
        )
    returncode = completed.returncode
    token = completed.stdout
    del completed
    if isinstance(token, bytes):
        token = token.decode("utf-8", "replace")
    token = token.strip()
    if returncode != 0:
        del token
        _raise_unavailable(
            f"`gh auth token` exited {returncode}; RQA has no GitHub credential"
        )
    if not token:
        _raise_unavailable(
            "`gh auth token` produced no credential; RQA has no GitHub credential"
        )
    return token


def probe_capability(
    repo: str, github: GithubProbe, store: CapabilityStore, job_id: str
) -> CapabilityProof:
    """Wraps P-09's E-16 `probe(*, repo, credential) -> CapabilityReading |
    GithubUnavailable` (CONTRACTS.md §9), persists the reading as a CapabilityProof for
    this job, and returns it. `GithubUnavailable` from the adapter is persisted as an
    empty capability set, so every activity is denied `CAPABILITY_MISSING` until a later
    job re-probes.

    The credential is resolved here and released here: a failure to resolve it raises
    before anything is probed or persisted (T14).
    """
    token = credential()
    try:
        reading = github.probe(repo=repo, credential=token)
    finally:
        del token
    if isinstance(reading, CapabilityReading):
        capabilities = frozenset(reading.capabilities)
        attested = frozenset(reading.attested_not_proven)
        login = reading.login
    elif isinstance(reading, GithubUnavailable):
        # Nothing is assumed for a repository GitHub would not answer about.
        capabilities = frozenset()
        attested = frozenset()
        login = ""
    else:
        raise GateError(
            "E-16 returns CapabilityReading | GithubUnavailable; the injected probe "
            f"returned {type(reading).__name__}"
        )
    proof = CapabilityProof(
        id=0,
        repo=repo,
        job_id=job_id,
        capabilities=capabilities,
        login=login,
        probed_at=_now(),
        attested_not_proven=attested,
    )
    return replace(proof, id=store.put(proof))


def _probe_signature_for_reference(*, repo: str, credential: str) -> CapabilityReading | GithubUnavailable:
    """E-16. Asks the adapter what the credential can do on `repo`, persists the result
    for this job, returns it. The adapter's probe is read-only against GitHub: it
    inspects the authenticated user's permission level on the repository and the token's
    reported scopes; it performs no write to establish a write capability.

    A declaration, not an implementation: P-09 provides E-16 and this module consumes it
    through `GithubProbe`. It is here because §4 states it here, so the shape P-08 calls
    is readable beside the call.
    """
