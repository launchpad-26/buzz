#!/usr/bin/env python3
"""Task #2216 — ADR-0062's executable half: a grant rests on a probe-proven
capability and never on an attested one, and a missing scope is denied rather
than attempted (RQA-NFR-024).

ADR-0062 §1, verbatim: "P-08 grants an activity only when both hold: the pinned
policy snapshot grants it, *and* a per-job capability probe (E-16) proves the
credential can actually perform it on that repository. A failed probe yields no
grant ... rather than an attempt." §3: "What the token could do elsewhere is
recorded, not hidden."

These tests drive the REAL `Gate` and the REAL E-16 `probe` with injected probes
and transports (the same seams E-04/E-16 declare) and assert the decision
vocabulary at the boundary. They do not assert the composed wiring can reach the
probe (it cannot today — #2274 denies REPO_NOT_MANAGED at step 1, before step 7);
the recorded runbook (`TESTING.md` Part 2 §11.2) carries that evidence.
"""

from __future__ import annotations

import contextlib
import importlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    REPO,
    bench,
    latest_payload,
    make_snapshot,
)

from rqa.authority.gate import Gate  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    CapabilityReading,
    Deny,
    DenyReason,
    GithubUnavailable,
)
from rqa.github import transport as transport_module  # noqa: E402
from rqa.github.capability import probe  # noqa: E402

_READS = frozenset({"pulls:read", "contents:read", "checks:read"})
_WRITES = frozenset({"pulls:write", "contents:write", "issues:write"})

#: Deliberately not token-shaped, exactly like the suite-wide sentinel: nothing may
#: be tempted to send it and no scanner has to wonder.
_SENTINEL_CREDENTIAL = "not-a-real-token-adr0062"


@contextlib.contextmanager
def _no_real_credential():
    """Substitute E-22 for one call: no test in this skill may launch `gh`."""
    capability = importlib.import_module("rqa.authority.capability")
    original = capability.credential
    capability.credential = lambda: _SENTINEL_CREDENTIAL
    try:
        yield
    finally:
        capability.credential = original


class _RecordingProbe:
    """E-16 as E-04 injects it, scripted with one reading and recording every call."""

    def __init__(self, reading) -> None:
        self.reading = reading
        self.calls: list[str] = []

    def probe(self, *, repo: str, credential: str):
        self.calls.append(repo)
        return self.reading


class _MemoryCapabilityStore:
    """The per-job proof cache, in memory: `current` and `put`, nothing else."""

    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], object] = {}

    def current(self, repo: str, job_id: str):
        return self.rows.get((repo, job_id))

    def put(self, proof) -> int:
        self.rows[(proof.repo, proof.job_id)] = proof
        return len(self.rows)


def _grant(*, activity: Activity, reading, repos: frozenset[str] | None = None):
    """One real Gate.grant over the bench record, returning (answer, probe, connection)."""
    connection, record, job = bench()
    gate = Gate(repos=repos if repos is not None else frozenset({REPO}))
    github = _RecordingProbe(reading)
    with _no_real_credential():
        answer = gate.grant(
            repo=REPO,
            activity=activity,
            snapshot=make_snapshot(),
            job_id=job.id,
            categories=None,
            record=record,
            github=github,
            store=_MemoryCapabilityStore(),
        )
    connection.commit()
    return answer, github, connection


def test_adr0062_an_attested_but_unproven_write_grants_nothing() -> None:
    """The credential floor is a proof, not a hope: GitHub *attesting* `pulls:write`
    (push permission reported, never exercised) yields a denial, not a grant and not
    an attempted write."""
    reading = CapabilityReading(
        capabilities=_READS, attested_not_proven=_WRITES, login="operator"
    )
    answer, github, connection = _grant(activity=Activity.COMMENT, reading=reading)
    assert isinstance(answer, Deny), answer
    assert answer.reason is DenyReason.CAPABILITY_MISSING
    assert "pulls:write" in answer.detail
    assert github.calls == [REPO], "exactly one probe, and only for the asked repository"


def test_adr0062_the_attestation_entry_separates_proven_from_attested() -> None:
    """§3: what the token could do but the probe could not prove is recorded, not
    hidden — and the credential itself is in no record payload."""
    reading = CapabilityReading(
        capabilities=_READS, attested_not_proven=_WRITES, login="operator"
    )
    answer, github, connection = _grant(activity=Activity.COMMENT, reading=reading)
    attestation = latest_payload(connection, "attestation")
    assert attestation["capabilities"] == sorted(_READS)
    assert attestation["attested_not_proven"] == sorted(_WRITES)
    assert attestation["login"] == "operator"
    every_payload = "\n".join(
        row[0]
        for row in connection.execute("SELECT payload FROM record_entries")
    )
    assert _SENTINEL_CREDENTIAL not in every_payload, (
        "no credential byte may reach the record (RQA-NFR-025)"
    )


def test_adr0062_a_proven_capability_set_covering_the_activity_grants() -> None:
    """The floor's positive half, at the same seam: a probe that PROVES `pulls:write`
    on this repository yields a grant carrying the proof's id. (Today's E-16 never
    proves a write — that collision is recorded evidence in TESTING.md Part 2, not a
    property tests may pin either way.)"""
    reading = CapabilityReading(
        capabilities=_READS | frozenset({"pulls:write"}),
        attested_not_proven=frozenset(),
        login="operator",
    )
    answer, github, connection = _grant(activity=Activity.COMMENT, reading=reading)
    assert not isinstance(answer, Deny), answer
    assert answer.capability_proof_id is not None
    grant_row = latest_payload(connection, "grant")
    assert grant_row["decision"] == "granted"


def test_adr0062_an_unmanaged_repository_is_denied_before_any_probe_runs() -> None:
    """§2: "P-09 never addresses a repository outside the configured set." The
    REPO_NOT_MANAGED denial precedes the probe, so the credential never even reads
    an unmanaged repository."""
    reading = CapabilityReading(
        capabilities=_READS, attested_not_proven=_WRITES, login="operator"
    )
    answer, github, connection = _grant(
        activity=Activity.COMMENT, reading=reading, repos=frozenset({"someone/else"})
    )
    assert isinstance(answer, Deny) and answer.reason is DenyReason.REPO_NOT_MANAGED
    assert github.calls == [], "the probe must never run for an unmanaged repository"


def test_adr0062_an_unanswerable_probe_denies_every_activity() -> None:
    """A repository GitHub would not answer about proves nothing: the empty proof
    denies CAPABILITY_MISSING rather than assuming anything."""
    reading = GithubUnavailable(op="probe", reason="unreachable", retriable=True)
    answer, github, connection = _grant(activity=Activity.REVIEW, reading=reading)
    assert isinstance(answer, Deny) and answer.reason is DenyReason.CAPABILITY_MISSING


class _FakeTransport:
    """`rest_json` scripted per path — the E-16 probe's whole transport surface."""

    def __init__(self, *, permissions=None, repo_status: int | None = None) -> None:
        self.permissions = permissions or {}
        self.repo_status = repo_status

    def rest_json(self, path: str, *, operation: str, credential: str | None = None):
        if path == "/user":
            return {"login": "operator"}
        if self.repo_status is not None:
            raise transport_module.Unavailable(
                reason="forbidden", retriable=False, status=self.repo_status
            )
        return {"permissions": self.permissions}


class _FakeAdapter:
    def __init__(self, transport) -> None:
        self.transport = transport


def test_adr0062_the_probe_proves_reads_and_only_attests_writes() -> None:
    """E-16's split, from GitHub's own permissions block: `pull` proves the three
    reads (the probe exercised authenticated reads); push-or-higher is only ever
    attested, because proving a write would mean performing one."""
    adapter = _FakeAdapter(_FakeTransport(
        permissions={"pull": True, "triage": True, "push": True, "admin": True}
    ))
    reading = probe(adapter=adapter, repo=REPO, credential=_SENTINEL_CREDENTIAL)
    assert isinstance(reading, CapabilityReading)
    assert reading.capabilities == _READS
    assert reading.attested_not_proven == _WRITES


def test_adr0062_an_unreachable_repository_probes_to_the_empty_reading() -> None:
    """403/404: not reachable with this credential is the EMPTY capability reading —
    every activity then denies CAPABILITY_MISSING instead of being attempted."""
    adapter = _FakeAdapter(_FakeTransport(repo_status=403))
    reading = probe(adapter=adapter, repo=REPO, credential=_SENTINEL_CREDENTIAL)
    assert isinstance(reading, CapabilityReading)
    assert reading.capabilities == frozenset()
    assert reading.attested_not_proven == frozenset()
