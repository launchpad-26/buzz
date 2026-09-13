#!/usr/bin/env python3
"""`explain` / `explain_job` / `resolve_job` — `code/P-12-record.md` §3.3 and §8 rows
T6, T7, T8, T9's `explain_job` half, T18's `explain_job` half, T19, T20.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

**Why every test job here is built entirely unkeyed.** `explain`/`explain_job`'s
signatures are fixed positionally by `code/P-12-record.md` §3.3 —
`explain_job(connection, job_id)` — with no `keystore` parameter to inject a fake
through, unlike `verify(connection, job_id, *, keystore=...)`. `verify` never asks
the key store for an unkeyed row at all (§3.2 step 3), so building every row here
through a `FakeKeyStore(key=None)` writer makes `explain_job`'s internal `verify`
call deterministic and keychain-free regardless of which `KeyStore` it happens to
construct — satisfying §8's "none touches a real OS keychain" without needing one.
`test_t18_...` is the one row that genuinely needs an authenticated keyed segment;
it monkeypatches `rqa.record.explain.OSKeyStore` — the one place `explain_job`
constructs its key store — to a fixed fake for that test's duration, which changes
nothing about `explain_job`'s public two-argument signature.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import importlib  # noqa: E402

from rqa.contracts import ExplanationUnavailable  # noqa: E402
from rqa.record.explain import Explanation, ReuseResolutionError, explain, explain_job  # noqa: E402

# `rqa/record/__init__.py` imports the name `explain` (the function) from this
# same-named submodule, which shadows the submodule as an attribute of the
# `rqa.record` package thereafter (a plain package/attribute name collision, not
# a bug in the function). `importlib.import_module` resolves the submodule
# directly from `sys.modules`, bypassing that shadowing, for the one place this
# file needs the actual module object: patching its `OSKeyStore` default.
explain_module = importlib.import_module("rqa.record.explain")  # noqa: E402
from rqa.record.hashing import LEGACY_PREV_HASH  # noqa: E402
from rqa.record.reader import AmbiguousHead, NoRecord, ResolvedJob, resolve_job  # noqa: E402
from rqa.record.store import StoredEntry, insert_entry  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402


class FakeKeyStore:
    """§8's fake `KeyStore`. `key=None` means every row this writer appends is
    unkeyed — no HMAC, and `verify` never asks any key store about it."""

    def __init__(self, *, key: bytes | None = None):
        self.key = key

    def read(self, name: str) -> bytes | None:
        return self.key


def unkeyed_writer(*, connection: sqlite3.Connection | None = None) -> tuple[sqlite3.Connection, SQLiteRecordWriter]:
    connection = connection or sqlite3.connect(":memory:")
    return connection, SQLiteRecordWriter(connection, keystore=FakeKeyStore(key=None))


TRANSITION = {"repo": "acme/widgets", "number": 42, "head_sha": "sha-abc", "base_sha": "sha-base"}


def full_job(connection: sqlite3.Connection, writer: SQLiteRecordWriter, *, job: str = "job-1") -> None:
    """A normal job: transition, plan, bundle, attestations, panel, judgement,
    action, terminal transition — T6's Given."""
    writer.append(
        job,
        "transition",
        {**TRANSITION, "from_state": None, "to_state": "queued", "reason": "arrived", "predecessor_job": None},
    )
    writer.append(
        job,
        "plan",
        {
            "obligations": ["ob1"],
            "omitted": {},
            "strategy": "single",
            "participants": 1,
            "risk_class": "low",
            "head_sha": "sha-abc",
            "snapshot_hash": "snap-1",
            "protocol_hash": "proto-1",
            "policy_version": "policy-1",
        },
    )
    writer.append(
        job,
        "bundle",
        {"status": "ready", "nonce": "n1", "protocol_hash": "proto-1", "manifest": {}, "reason": None},
    )
    writer.append(
        job,
        "attestation",
        {
            "attempt_id": "attempt-1",
            "harness": "codex",
            "model": "gpt-x",
            "provider": "openai",
            "route_family": "default",
            "external": False,
            "effort": "medium",
            "started_at": "2026-01-01T00:00:00+00:00",
            "ended_at": "2026-01-01T00:05:00+00:00",
            "exit_code": 0,
            "self_reported_identity": None,
        },
    )
    writer.append(
        job,
        "panel",
        {
            "attempt_ids": ["attempt-1"],
            "complete": True,
            "incomplete_reason": None,
            "evidence_cutoff": "2026-01-01T00:05:01+00:00",
            "bound_reached": False,
        },
    )
    writer.append(
        job,
        "judgement",
        {
            "obligations": {"ob1": "verified"},
            "findings": [
                {
                    "id": "f1",
                    "categories": ["correctness"],
                    "extra_tags": [],
                    "location": {"path": "x.py", "line": 10},
                    "evidence": "the fix is present",
                    "severity": "high",
                    "remedy": None,
                    "behaviour_changing": False,
                    "source_attempt": "attempt-1",
                },
                {
                    "id": "f2",
                    "categories": ["mechanical"],
                    "extra_tags": [],
                    "location": {"path": "y.py", "line": 3},
                    "evidence": "style nit",
                    "severity": "low",
                    "remedy": None,
                    "behaviour_changing": False,
                    "source_attempt": "attempt-1",
                },
                {
                    "id": "f3",
                    "categories": ["mechanical"],
                    "extra_tags": [],
                    "location": {"path": "z.py", "line": 1},
                    "evidence": "unused import",
                    "severity": "low",
                    "remedy": None,
                    "behaviour_changing": False,
                    "source_attempt": "attempt-1",
                },
            ],
            "corroborated": ["f1", "f2"],
            "blocking": ["f1"],
            "attribution": {"f1": "pr", "f2": "pr", "f3": "pr"},
            "assurance": {"required": 1, "achieved": 1},
            "remediation_candidates": [],
            "escalation_causes": [],
            "disposition": "approve",
            "reused_from": None,
            "snapshot_hash": "snap-1",
            "protocol_hash": "proto-1",
            "facts_fetched_at": "2026-01-01T00:05:00+00:00",
            "cutoff": "2026-01-01T00:05:01+00:00",
            "rendered_body": "obligations satisfied; approving",
        },
    )
    writer.append(
        job,
        "action",
        {
            "mutation_id": "mut-1",
            "operation": "review_submit",
            "outcome": "submitted",
            "accepted": True,
            "github_response": None,
            "grant_entry_seq": None,
        },
    )
    writer.append(
        job,
        "transition",
        {**TRANSITION, "from_state": "judged", "to_state": "approved", "reason": "submitted", "predecessor_job": None},
    )


# -- T6 and T7: the twelve-element reconstruction -----------------------------


def test_t6_a_normal_job_returns_all_twelve_elements() -> None:
    connection, writer = unkeyed_writer()
    full_job(connection, writer)

    result = explain_job(connection, "job-1")
    assert isinstance(result, Explanation)
    assert result.repo == "acme/widgets"
    assert result.number == 42
    assert result.pr_revision == "sha-abc"
    assert result.protocol_hash == "proto-1"
    assert result.policy_version == "policy-1"
    assert result.snapshot_hash == "snap-1"
    assert result.reviewer_identity == ("codex",)
    assert result.reviewer_type == "ai"
    assert result.harness == ("codex",)
    assert result.model == ("gpt-x",)
    assert result.provider == ("openai",)
    assert result.evidence == {"ob1": "verified"}
    assert result.decision_basis == "obligations satisfied; approving"
    assert result.disposition == "review-complete"
    assert len(result.findings) == 3
    by_id = {finding["id"]: finding for finding in result.findings}
    assert (by_id["f1"]["blocking"], by_id["f1"]["corroborated"]) == (True, True)
    assert (by_id["f2"]["blocking"], by_id["f2"]["corroborated"]) == (False, True)
    assert (by_id["f3"]["blocking"], by_id["f3"]["corroborated"]) == (False, False)


def test_t6_explain_by_repo_and_number_resolves_the_same_job() -> None:
    connection, writer = unkeyed_writer()
    full_job(connection, writer)
    result = explain(connection, "acme/widgets", 42)
    assert isinstance(result, Explanation)
    assert result.job_id == "job-1"
    assert result.disposition == "review-complete"


def test_t7_a_socket_that_raises_does_not_affect_explain() -> None:
    """T7: socket calls patched to raise during T6's `explain` are unaffected — no
    network is ever reached (§1, §3.3's guarantees)."""
    import socket

    connection, writer = unkeyed_writer()
    full_job(connection, writer)

    original = socket.socket

    def _boom(*_args, **_kwargs):
        raise AssertionError("explain must never open a socket")

    socket.socket = _boom  # type: ignore[assignment]
    try:
        result = explain_job(connection, "job-1")
    finally:
        socket.socket = original  # type: ignore[assignment]

    assert isinstance(result, Explanation)
    assert result.disposition == "review-complete"


# -- T8: truncation at an integrity break -------------------------------------


def test_t8_an_integrity_break_at_the_judgement_truncates_there() -> None:
    """T8: integrity break at judgement → explanation truncates there and does not
    source later facts (the later `action` and the terminal `approved` transition
    are both past the break, and neither one is used)."""
    connection, writer = unkeyed_writer()
    full_job(connection, writer)

    # Corrupt the judgement row (seq 6) in place, without recomputing its hash:
    # `verify` will call this a HASH_MISMATCH at seq 6, so `bad_seq == 6` and
    # nothing at seq 6 or later contributes.
    connection.execute(
        "UPDATE record_entries SET payload = ? WHERE job = ? AND seq = ?",
        ('{"rendered_body": "a tampered basis"}', "job-1", 6),
    )

    result = explain_job(connection, "job-1")
    assert isinstance(result, Explanation)
    assert result.truncated_at == 6
    # Only the arrival transition (seq 1) is readable; "approved" (seq 8) is not.
    assert result.disposition == "being reviewed"
    # No judgement is readable, so nothing judgement-sourced is fabricated.
    assert result.decision_basis is None
    assert result.evidence == {}
    assert result.findings == ()
    # Pre-break facts still contribute.
    assert result.protocol_hash == "proto-1"
    assert result.harness == ("codex",)


# -- explain / resolve_job absence and ambiguity ------------------------------


def test_explain_with_no_record_is_explanation_unavailable() -> None:
    connection, _writer = unkeyed_writer()
    result = explain(connection, "acme/widgets", 1)
    assert result == ExplanationUnavailable(repo="acme/widgets", number=1, reason="no_record")


def test_resolve_job_finds_no_record() -> None:
    connection, _writer = unkeyed_writer()
    assert resolve_job(connection, "acme/widgets", 1) == NoRecord()


def test_resolve_job_is_ambiguous_when_two_heads_name_no_predecessor() -> None:
    connection, writer = unkeyed_writer()
    writer.append("job-a", "transition", {**TRANSITION, "from_state": None, "to_state": "queued", "reason": "x", "predecessor_job": None})
    writer.append("job-b", "transition", {**TRANSITION, "from_state": None, "to_state": "queued", "reason": "x", "predecessor_job": None})

    resolved = resolve_job(connection, "acme/widgets", 42)
    assert isinstance(resolved, AmbiguousHead)
    assert sorted(resolved.candidates) == ["job-a", "job-b"]

    result = explain(connection, "acme/widgets", 42)
    assert result == ExplanationUnavailable(repo="acme/widgets", number=42, reason="ambiguous_head")


def test_resolve_job_excludes_a_job_named_as_another_jobs_predecessor() -> None:
    connection, writer = unkeyed_writer()
    writer.append("job-old", "transition", {**TRANSITION, "from_state": None, "to_state": "superseded", "reason": "new head arrived", "predecessor_job": None})
    writer.append("job-new", "transition", {**TRANSITION, "from_state": None, "to_state": "queued", "reason": "new head", "predecessor_job": "job-old"})

    assert resolve_job(connection, "acme/widgets", 42) == ResolvedJob(job_id="job-new")


# -- T9 and T18's `explain_job` halves: legacy rows never authenticate --------


def migrated_row(connection: sqlite3.Connection, job: str, seq: int, kind: str, payload: str = "{}") -> None:
    insert_entry(
        connection=connection,
        entry=StoredEntry(
            job=job,
            seq=seq,
            kind=kind,
            at="2025-01-01T00:00:00.000000+00:00",
            payload=payload,
            prev_hash=LEGACY_PREV_HASH,
            hash="a" * 64,
            hmac=None,
            keyed=False,
        ),
    )


def test_t9_a_job_of_only_migrated_rows_is_legacy_and_never_verified() -> None:
    """T9's `explain_job` half: a job with only migrated rows (`legacy`, `decision`,
    `spend`, all `prev_hash="legacy"`) → `legacy=True, verified=False` regardless."""
    connection = sqlite3.connect(":memory:")
    SQLiteRecordWriter(connection, keystore=FakeKeyStore())
    migrated_row(connection, "job-legacy", 1, "legacy")
    migrated_row(connection, "job-legacy", 2, "decision")
    migrated_row(connection, "job-legacy", 3, "spend")

    result = explain_job(connection, "job-legacy")
    assert isinstance(result, Explanation)
    assert result.legacy is True
    assert result.verified is False


def test_t18_a_keyed_row_a_migrated_row_and_an_unkeyed_row_are_legacy_and_unverified() -> None:
    """T18's `explain_job` half: rows `[keyed real seq=1, legacy, unkeyed real seq=2
    chained to seq=1]` → `legacy=True, verified=False`, reporting the unkeyed
    segment without calling the record broken."""
    key = b"a-test-key-that-never-leaves-this-process"

    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, keystore=FakeKeyStore(key=key))
    writer.append(
        "job-1", "transition", {**TRANSITION, "from_state": None, "to_state": "queued", "reason": "x", "predecessor_job": None}
    )
    migrated_row(connection, "job-1", 3, "legacy")
    # A second unkeyed writer picks up the same live chain (still seq 2, chained to
    # seq 1) — `head_entry` ignores the migrated seq-3 row entirely.
    unkeyed = SQLiteRecordWriter(connection, keystore=FakeKeyStore(key=None))
    unkeyed.append(
        "job-1", "transition", {**TRANSITION, "from_state": "queued", "to_state": "claimed", "reason": "y", "predecessor_job": None}
    )

    original_os_keystore = explain_module.OSKeyStore
    explain_module.OSKeyStore = lambda: FakeKeyStore(key=key)  # type: ignore[assignment]
    try:
        result = explain_job(connection, "job-1")
    finally:
        explain_module.OSKeyStore = original_os_keystore  # type: ignore[assignment]

    assert isinstance(result, Explanation)
    assert result.legacy is True
    assert result.verified is False
    assert len(result.unverifiable) == 1
    assert result.unverifiable[0].reason == "no key"
    # Not called broken: the chain-valid, non-legacy real rows still verify ok.
    assert result.truncated_at is None


# -- T19: the three-way blocking/corroborated split ---------------------------


def test_t19_findings_get_the_three_way_blocking_corroborated_split() -> None:
    connection, writer = unkeyed_writer()
    full_job(connection, writer)
    result = explain_job(connection, "job-1")
    assert isinstance(result, Explanation)
    by_id = {finding["id"]: finding for finding in result.findings}
    assert by_id["f1"]["blocking"] is True and by_id["f1"]["corroborated"] is True
    assert by_id["f2"]["blocking"] is False and by_id["f2"]["corroborated"] is True
    assert by_id["f3"]["blocking"] is False and by_id["f3"]["corroborated"] is False


# -- T20: following a materialised reused_from judgement ----------------------


def test_t20_a_carry_only_successor_obtains_attestations_from_its_predecessor() -> None:
    """T20: predecessor has a valid plan, harness attestations, and judgement;
    successor has no attestation, a materialised judgement with
    `reused_from=<predecessor>`, and a transition → `explain_job(successor)`
    follows `reused_from`, returns all twelve elements, and obtains reviewer
    identity/harness/model/provider from the predecessor's attestations."""
    connection, writer = unkeyed_writer()

    # Predecessor: plan, harness attestation, judgement.
    writer.append(
        "job-pred", "plan",
        {
            "obligations": ["ob1"], "omitted": {}, "strategy": "single", "participants": 1,
            "risk_class": "low", "head_sha": "sha-pred", "snapshot_hash": "snap-pred",
            "protocol_hash": "proto-pred", "policy_version": "policy-pred",
        },
    )
    writer.append(
        "job-pred", "attestation",
        {
            "attempt_id": "attempt-pred", "harness": "claude", "model": "opus", "provider": "anthropic",
            "route_family": "default", "external": False, "effort": "high",
            "started_at": "2026-01-01T00:00:00+00:00", "ended_at": "2026-01-01T00:05:00+00:00",
            "exit_code": 0, "self_reported_identity": None,
        },
    )
    writer.append(
        "job-pred", "judgement",
        {
            "obligations": {"ob1": "verified"}, "findings": [], "corroborated": [], "blocking": [],
            "attribution": {}, "assurance": {"required": 1, "achieved": 1},
            "remediation_candidates": [], "escalation_causes": [], "disposition": "approve",
            "reused_from": None, "snapshot_hash": "snap-pred", "protocol_hash": "proto-pred",
            "facts_fetched_at": "2026-01-01T00:05:00+00:00", "cutoff": "2026-01-01T00:05:01+00:00",
            "rendered_body": "predecessor basis",
        },
    )

    # Successor: no attestation of its own, a carry-only judgement, and a transition.
    writer.append(
        "job-succ", "judgement",
        {
            "obligations": {"ob1": "verified"}, "findings": [], "corroborated": [], "blocking": [],
            "attribution": {}, "assurance": {"required": 1, "achieved": 1},
            "remediation_candidates": [], "escalation_causes": [], "disposition": "approve",
            "reused_from": "job-pred", "snapshot_hash": None, "protocol_hash": None,
            "facts_fetched_at": "2026-01-01T00:05:02+00:00", "cutoff": "2026-01-01T00:05:02+00:00",
            "rendered_body": "carried forward from predecessor",
        },
    )
    writer.append(
        "job-succ", "transition",
        {**TRANSITION, "from_state": None, "to_state": "judged", "reason": "carried", "predecessor_job": "job-pred"},
    )

    result = explain_job(connection, "job-succ")
    assert isinstance(result, Explanation)
    assert result.reviewer_identity == ("claude",)
    assert result.reviewer_type == "ai"
    assert result.harness == ("claude",)
    assert result.model == ("opus",)
    assert result.provider == ("anthropic",)
    assert result.decision_basis == "carried forward from predecessor"
    assert result.disposition == "being reviewed"


def test_reused_from_a_missing_predecessor_raises_reuse_resolution_error() -> None:
    connection, writer = unkeyed_writer()
    writer.append(
        "job-succ", "judgement",
        {
            "obligations": {}, "findings": [], "corroborated": [], "blocking": [], "attribution": {},
            "assurance": {"required": 0, "achieved": 0}, "remediation_candidates": [],
            "escalation_causes": [], "disposition": "approve", "reused_from": "job-nonexistent",
            "snapshot_hash": None, "protocol_hash": None, "facts_fetched_at": "2026-01-01T00:00:00+00:00",
            "cutoff": "2026-01-01T00:00:00+00:00", "rendered_body": "x",
        },
    )
    raised = False
    try:
        explain_job(connection, "job-succ")
    except ReuseResolutionError:
        raised = True
    assert raised


def test_reused_from_a_predecessor_with_no_judgement_raises_reuse_resolution_error() -> None:
    connection, writer = unkeyed_writer()
    writer.append(
        "job-pred", "transition",
        {**TRANSITION, "from_state": None, "to_state": "queued", "reason": "x", "predecessor_job": None},
    )
    writer.append(
        "job-succ", "judgement",
        {
            "obligations": {}, "findings": [], "corroborated": [], "blocking": [], "attribution": {},
            "assurance": {"required": 0, "achieved": 0}, "remediation_candidates": [],
            "escalation_causes": [], "disposition": "approve", "reused_from": "job-pred",
            "snapshot_hash": None, "protocol_hash": None, "facts_fetched_at": "2026-01-01T00:00:00+00:00",
            "cutoff": "2026-01-01T00:00:00+00:00", "rendered_body": "x",
        },
    )
    raised = False
    try:
        explain_job(connection, "job-succ")
    except ReuseResolutionError:
        raised = True
    assert raised


def test_reused_from_a_cycle_raises_reuse_resolution_error() -> None:
    connection, writer = unkeyed_writer()
    writer.append(
        "job-a", "judgement",
        {
            "obligations": {}, "findings": [], "corroborated": [], "blocking": [], "attribution": {},
            "assurance": {"required": 0, "achieved": 0}, "remediation_candidates": [],
            "escalation_causes": [], "disposition": "approve", "reused_from": "job-b",
            "snapshot_hash": None, "protocol_hash": None, "facts_fetched_at": "2026-01-01T00:00:00+00:00",
            "cutoff": "2026-01-01T00:00:00+00:00", "rendered_body": "x",
        },
    )
    writer.append(
        "job-b", "judgement",
        {
            "obligations": {}, "findings": [], "corroborated": [], "blocking": [], "attribution": {},
            "assurance": {"required": 0, "achieved": 0}, "remediation_candidates": [],
            "escalation_causes": [], "disposition": "approve", "reused_from": "job-a",
            "snapshot_hash": None, "protocol_hash": None, "facts_fetched_at": "2026-01-01T00:00:00+00:00",
            "cutoff": "2026-01-01T00:00:00+00:00", "rendered_body": "x",
        },
    )
    raised = False
    try:
        explain_job(connection, "job-a")
    except ReuseResolutionError:
        raised = True
    assert raised


def test_explain_job_with_no_rows_is_explanation_unavailable() -> None:
    connection, _writer = unkeyed_writer()
    result = explain_job(connection, "no-such-job")
    assert result == ExplanationUnavailable(repo="", number=0, reason="no_record")
