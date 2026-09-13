#!/usr/bin/env python3
"""P-13 §8 T1-T14 — authenticated, deterministic revision reuse with recorded provenance."""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone
from types import MappingProxyType

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.protocol.paths  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Blocking,
    Budget,
    Category,
    CheckConclusion,
    CheckRun,
    Entry,
    EvidenceState,
    External,
    Facts,
    Job,
    JobStatus,
    Mechanical,
    Obligation,
    Policy,
    PrFacts,
    RecordRow,
    RecordTrustFailureReason,
    RecordUntrusted,
    RemediationPolicy,
    Snapshot,
    SubmittedReview,
    VerifiedRecordPrefix,
)
from rqa.reuse import Reason, ReuseError, carry_over  # noqa: E402

MOMENT = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)
REPO = "acme/widgets"
SOURCE_JOB = "job-predecessor"
PROTOCOL_HASH = "protocol-current"
POLICY_VERSION = "policy-current"

A = Obligation(
    id="A",
    paths=("src/a/**",),
    required_for=frozenset({"standard"}),
    evidence="A evidence",
)
B = Obligation(
    id="B",
    paths=("docs/**",),
    required_for=frozenset({"standard"}),
    evidence="B evidence",
)
C = Obligation(
    id="C",
    paths=("config/*.toml",),
    required_for=frozenset({"standard"}),
    evidence="C evidence",
)
ALL = (A, B, C)


class FakeReader:
    """Only the authenticated E-13 reader edge is usable; other reads fail the test."""

    def __init__(self, answer) -> None:
        self.answer = answer
        self.trusted_calls: list[str] = []
        self.entries_calls: list[tuple] = []
        self.latest_calls: list[tuple] = []

    def trusted_prefix(self, job_id: str):
        self.trusted_calls.append(job_id)
        return self.answer

    def entries(self, job_id: str, kind=None):
        self.entries_calls.append((job_id, kind))
        raise AssertionError("P-13 must not call unauthenticated entries()")

    def latest(self, job_id: str, kind: str):
        self.latest_calls.append((job_id, kind))
        raise AssertionError("P-13 must not call unauthenticated latest()")


class FakeWriter:
    """In-memory E-13 writer that retains exactly the JSON-safe payload it receives."""

    def __init__(self, *, failure: AppendFailed | None = None) -> None:
        self.failure = failure
        self.calls: list[tuple[str, str, dict]] = []
        self.attempts = 0

    def append(self, job_id: str, kind: str, payload) -> Entry:
        self.attempts += 1
        if self.failure is not None:
            raise self.failure
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self.calls.append((job_id, kind, json.loads(encoded)))
        return Entry(seq=len(self.calls), hash=f"hash-{len(self.calls)}")


def _job(*, repo: str = REPO, predecessor: str | None = SOURCE_JOB) -> Job:
    return Job(
        id="job-current",
        repo=repo,
        number=2196,
        head_sha="a" * 40,
        base_sha="b" * 40,
        head_repo=repo,
        head_ref="feature/reuse",
        predecessor_job=predecessor,
        predecessor_head_sha="c" * 40 if predecessor is not None else None,
        snapshot_hash="snapshot-current",
        status=JobStatus.PLANNED,
    )


def _facts(
    *,
    changed_paths: frozenset[str] = frozenset(),
    revision_changed_paths: frozenset[str] = frozenset(),
) -> Facts:
    return Facts(
        pr=PrFacts(
            repo=REPO,
            number=2196,
            head_sha="a" * 40,
            base_sha="b" * 40,
            merge_base_sha="b" * 40,
            head_repo=REPO,
            head_ref="feature/reuse",
            head_protected=False,
            author="reviewer",
            labels=frozenset(),
            title="Revision reuse",
            body="No credentials or untrusted attestation claims.",
        ),
        diff="",
        changed_paths=changed_paths,
        revision_changed_paths=revision_changed_paths,
        files={},
        checks=(
            CheckRun(
                name="unit",
                conclusion=CheckConclusion.SUCCESS,
                sha="a" * 40,
                observed_at=MOMENT,
            ),
        ),
        base_checks=(),
        reviews=(
            SubmittedReview(
                id="review-1",
                actor="reviewer",
                outcome="approved",
                head_sha="a" * 40,
                submitted_at=MOMENT,
            ),
        ),
        fetched_at=MOMENT,
    )


def _snapshot(
    *,
    obligations: tuple[Obligation, ...] = ALL,
    repo: str = REPO,
    protocol_hash: str = PROTOCOL_HASH,
    policy_version: str = POLICY_VERSION,
) -> Snapshot:
    policy = Policy(
        version=policy_version,
        obligations=obligations,
        blocking=Blocking(
            categories=frozenset({Category.SECURITY}),
            severities=frozenset({"high"}),
            corroboration=1,
        ),
        mechanical=Mechanical(
            categories=frozenset({Category.MECHANICAL}), tools=frozenset({"format"})
        ),
        assurance={"standard": 1},
        remediation=RemediationPolicy(allow_forks=False),
    )
    return Snapshot(
        hash="snapshot-current",
        repo=repo,
        protocol_hash=protocol_hash,
        authority={activity: False for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label="external-denied"),
        policy=policy,
        budget=Budget(
            per_pr_tokens=None,
            per_repo_daily_tokens=None,
            per_model_daily_tokens=None,
        ),
    )


def _row(*, seq: int, kind: str, payload) -> RecordRow:
    return RecordRow(seq=seq, kind=kind, at=MOMENT, payload=payload)


def _plan_row(
    *,
    seq: int = 1,
    protocol_hash: object = PROTOCOL_HASH,
    policy_version: object = POLICY_VERSION,
) -> RecordRow:
    return _row(
        seq=seq,
        kind="plan",
        payload={"protocol_hash": protocol_hash, "policy_version": policy_version},
    )


def _judgement_row(
    *,
    seq: int = 2,
    states: dict[str, object] | None = None,
    contributions: object | None = None,
    payload=None,
) -> RecordRow:
    if payload is None:
        obligations = states if states is not None else {ob.id: "verified" for ob in ALL}
        attempts = (
            contributions
            if contributions is not None
            else {ob.id: [f"attempt-{ob.id.lower()}"] for ob in ALL}
        )
        payload = {"obligations": obligations, "contributing_attempts": attempts}
    return _row(seq=seq, kind="judgement", payload=payload)


def _prefix(
    *, rows: tuple[RecordRow, ...], job_id: str = SOURCE_JOB
) -> VerifiedRecordPrefix:
    return VerifiedRecordPrefix(
        job_id=job_id,
        rows=rows,
        checked_through_seq=max((row.seq for row in rows), default=0),
    )


def _invoke(
    *,
    prefix,
    facts: Facts | None = None,
    job: Job | None = None,
    snapshot: Snapshot | None = None,
    writer: FakeWriter | None = None,
):
    reader = FakeReader(prefix)
    sink = writer or FakeWriter()
    result = carry_over(
        job=job or _job(),
        prior=reader,
        facts=facts or _facts(),
        snapshot=snapshot or _snapshot(),
        record=sink,
    )
    return result, reader, sink


def _assert_reuse_error(*, prefix, snapshot: Snapshot | None = None) -> tuple[FakeReader, FakeWriter]:
    reader = FakeReader(prefix)
    writer = FakeWriter()
    raised = False
    try:
        carry_over(
            job=_job(),
            prior=reader,
            facts=_facts(),
            snapshot=snapshot or _snapshot(),
            record=writer,
        )
    except ReuseError:
        raised = True
    assert raised, "malformed trusted predecessor must raise ReuseError"
    assert writer.calls == []
    return reader, writer


def _reasons(*, reason: Reason, obligations: tuple[Obligation, ...] = ALL) -> dict[str, str]:
    return {obligation.id: reason.value for obligation in obligations}


# -- P-13 §8 rows --------------------------------------------------------------


def test_t1_all_verified_obligations_carry_trusted_provenance_and_pin_2236_latest_sequence() -> None:
    """T1 and #2236: `prefix.latest` makes seq 7, not older seq 2, the interim source."""
    older = _judgement_row(
        seq=2,
        contributions={ob.id: [f"old-{ob.id.lower()}"] for ob in ALL},
    )
    latest = _judgement_row(
        seq=7,
        contributions={ob.id: [f"latest-{ob.id.lower()}"] for ob in ALL},
    )
    result, reader, writer = _invoke(prefix=_prefix(rows=(_plan_row(), older, latest)))

    assert tuple(item.obligation_id for item in result.reused) == ("A", "B", "C")
    assert all(item.state is EvidenceState.VERIFIED for item in result.reused)
    assert all(item.source_job == SOURCE_JOB for item in result.reused)
    assert all(item.source_judgement_seq == 7 for item in result.reused)
    assert tuple(item.source_attestations for item in result.reused) == (
        ("latest-a",),
        ("latest-b",),
        ("latest-c",),
    )
    assert result.regenerated == ()
    assert result.reasons == _reasons(reason=Reason.UNCHANGED_VERIFIED)
    assert reader.trusted_calls == [SOURCE_JOB]
    assert reader.entries_calls == reader.latest_calls == []
    assert len(writer.calls) == 1


def test_t2_only_revision_matched_obligation_regenerates_and_pr_wide_paths_are_ignored() -> None:
    calls: list[tuple[str, str]] = []
    original = rqa.protocol.paths.matches

    def counting_match(path: str, pattern: str) -> bool:
        calls.append((path, pattern))
        return original(path, pattern)

    rqa.protocol.paths.matches = counting_match
    try:
        result, _, _ = _invoke(
            prefix=_prefix(rows=(_plan_row(), _judgement_row())),
            facts=_facts(
                changed_paths=frozenset({"src/a/code.py", "docs/pr-wide-only.md"}),
                revision_changed_paths=frozenset({"src/a/code.py"}),
            ),
        )
    finally:
        rqa.protocol.paths.matches = original

    assert result.regenerated == ("A",)
    assert tuple(item.obligation_id for item in result.reused) == ("B", "C")
    assert tuple(item.source_attestations for item in result.reused) == (
        ("attempt-b",),
        ("attempt-c",),
    )
    assert tuple(item.source_judgement_seq for item in result.reused) == (2, 2)
    assert result.reasons == {
        "A": Reason.PATH_TOUCHED.value,
        "B": Reason.UNCHANGED_VERIFIED.value,
        "C": Reason.UNCHANGED_VERIFIED.value,
    }
    assert ("src/a/code.py", "src/a/**") in calls
    assert all(path != "docs/pr-wide-only.md" for path, _ in calls)


def test_t3_moved_protocol_or_policy_pin_and_absent_plan_regenerate_every_obligation() -> None:
    variants = (
        (_plan_row(protocol_hash="protocol-old"),),
        (_plan_row(policy_version="policy-old"),),
        (),
    )
    for plan_rows in variants:
        result, _, writer = _invoke(
            prefix=_prefix(rows=plan_rows + (_judgement_row(),))
        )
        assert result.reused == ()
        assert result.regenerated == ("A", "B", "C")
        assert result.reasons == _reasons(reason=Reason.PIN_CHANGED)
        assert len(writer.calls) == 1


def test_t4_non_verified_regenerates_while_verified_untouched_evidence_carries() -> None:
    judgement = _judgement_row(
        states={"A": "failed", "B": "verified"},
        contributions={"B": ["attempt-b"]},
    )
    result, _, _ = _invoke(
        prefix=_prefix(rows=(_plan_row(), judgement)),
        snapshot=_snapshot(obligations=(A, B)),
    )
    assert result.regenerated == ("A",)
    assert tuple(item.obligation_id for item in result.reused) == ("B",)
    assert result.reused[0].source_attestations == ("attempt-b",)
    assert result.reasons == {
        "A": Reason.NOT_VERIFIED.value,
        "B": Reason.UNCHANGED_VERIFIED.value,
    }


def test_t5_current_obligation_absent_from_predecessor_is_new_and_regenerates() -> None:
    judgement = _judgement_row(
        states={"A": "verified"}, contributions={"A": ["attempt-a"]}
    )
    result, _, _ = _invoke(
        prefix=_prefix(rows=(_plan_row(), judgement)),
        snapshot=_snapshot(obligations=(A, C)),
    )
    assert tuple(item.obligation_id for item in result.reused) == ("A",)
    assert result.regenerated == ("C",)
    assert result.reasons == {
        "A": Reason.UNCHANGED_VERIFIED.value,
        "C": Reason.NEW_OBLIGATION.value,
    }


def test_t6_absent_predecessor_judgement_regenerates_without_carried_evidence() -> None:
    result, reader, writer = _invoke(prefix=_prefix(rows=(_plan_row(),)))
    assert result.reused == ()
    assert result.regenerated == ("A", "B", "C")
    assert result.reasons == _reasons(reason=Reason.NO_PRIOR_JUDGEMENT)
    assert result.source_job == SOURCE_JOB
    assert reader.trusted_calls == [SOURCE_JOB]
    assert len(writer.calls) == 1


def test_t7_no_predecessor_regenerates_with_null_source_and_skips_every_reader_call() -> None:
    unreadable = RecordUntrusted(
        reason=RecordTrustFailureReason.INTEGRITY_BREAK, detail="must remain unread"
    )
    result, reader, writer = _invoke(prefix=unreadable, job=_job(predecessor=None))
    assert result.reused == ()
    assert result.regenerated == ("A", "B", "C")
    assert result.reasons == _reasons(reason=Reason.NO_PREDECESSOR)
    assert result.source_job is None
    assert reader.trusted_calls == reader.entries_calls == reader.latest_calls == []
    assert writer.calls[0][2]["source_job"] is None


def test_t8_missing_or_malformed_contributing_attempts_raise_without_append() -> None:
    malformed_payloads = (
        {"obligations": {"A": "verified"}},
        {"obligations": {"A": "verified"}, "contributing_attempts": {}},
        {"obligations": {"A": "verified"}, "contributing_attempts": {"A": "attempt-a"}},
        {"obligations": {"A": "verified"}, "contributing_attempts": {"A": []}},
        {"obligations": {"A": "verified"}, "contributing_attempts": {"A": [""]}},
        {"obligations": {"A": "verified"}, "contributing_attempts": {"A": [7]}},
    )
    for payload in malformed_payloads:
        _assert_reuse_error(
            prefix=_prefix(rows=(_plan_row(), _judgement_row(payload=payload))),
            snapshot=_snapshot(obligations=(A,)),
        )


def test_t9_record_serializes_full_evidence_and_complete_disjoint_decision_sets() -> None:
    judgement = _judgement_row(
        states={"A": "verified", "B": "incomplete"},
        contributions={"A": ["attempt-a-1", "attempt-a-2"]},
    )
    result, _, writer = _invoke(prefix=_prefix(rows=(_plan_row(), judgement)))
    assert result.regenerated == ("B", "C")
    payload = writer.calls[0][2]
    assert writer.calls[0][:2] == ("job-current", "carry_over")
    assert payload == {
        "source_job": SOURCE_JOB,
        "reused": [
            {
                "obligation_id": "A",
                "state": "verified",
                "source_job": SOURCE_JOB,
                "source_judgement_seq": 2,
                "source_attestations": ["attempt-a-1", "attempt-a-2"],
            }
        ],
        "regenerated": ["B", "C"],
        "reasons": {
            "A": Reason.UNCHANGED_VERIFIED.value,
            "B": Reason.NOT_VERIFIED.value,
            "C": Reason.NEW_OBLIGATION.value,
        },
        "protocol_hash": PROTOCOL_HASH,
        "policy_version": POLICY_VERSION,
    }
    reused_ids = {item["obligation_id"] for item in payload["reused"]}
    regenerated_ids = set(payload["regenerated"])
    assert reused_ids | regenerated_ids == {"A", "B", "C"}
    assert reused_ids.isdisjoint(regenerated_ids)
    assert set(payload["reasons"]) == {"A", "B", "C"}


def test_t10_malformed_trusted_judgement_or_plan_pin_raises_without_append() -> None:
    bad_judgements = (
        {},
        {"obligations": [], "contributing_attempts": {}},
        {"obligations": {"A": "invented"}, "contributing_attempts": {"A": ["attempt-a"]}},
        {
            "obligations": {"A": EvidenceState.VERIFIED},
            "contributing_attempts": {"A": ["attempt-a"]},
        },
    )
    for payload in bad_judgements:
        _assert_reuse_error(
            prefix=_prefix(rows=(_plan_row(), _judgement_row(payload=payload))),
            snapshot=_snapshot(obligations=(A,)),
        )

    bad_plans = (
        {"policy_version": POLICY_VERSION},
        {"protocol_hash": PROTOCOL_HASH},
        {"protocol_hash": "", "policy_version": POLICY_VERSION},
        {"protocol_hash": PROTOCOL_HASH, "policy_version": 7},
    )
    for payload in bad_plans:
        _assert_reuse_error(
            prefix=_prefix(
                rows=(
                    _row(seq=1, kind="plan", payload=payload),
                    _judgement_row(
                        states={"A": "verified"},
                        contributions={"A": ["attempt-a"]},
                    ),
                )
            ),
            snapshot=_snapshot(obligations=(A,)),
        )


def test_t11_append_failed_propagates_without_returning_a_result() -> None:
    failure = AppendFailed("injected durable append failure")
    reader = FakeReader(_prefix(rows=(_plan_row(), _judgement_row())))
    writer = FakeWriter(failure=failure)
    caught = None
    try:
        carry_over(
            job=_job(), prior=reader, facts=_facts(), snapshot=_snapshot(), record=writer
        )
    except AppendFailed as exc:
        caught = exc
    assert caught is failure
    assert writer.attempts == 1
    assert writer.calls == []


def test_t12_repository_snapshot_mismatch_raises_and_touches_neither_collaborator() -> None:
    reader = FakeReader(_prefix(rows=(_plan_row(), _judgement_row())))
    writer = FakeWriter()
    raised = False
    try:
        carry_over(
            job=_job(repo="acme/other"),
            prior=reader,
            facts=_facts(),
            snapshot=_snapshot(repo=REPO),
            record=writer,
        )
    except ReuseError:
        raised = True
    assert raised
    assert reader.trusted_calls == reader.entries_calls == reader.latest_calls == []
    assert writer.attempts == 0
    assert writer.calls == []


def test_t13_identical_immutable_inputs_produce_byte_identical_results_and_payloads() -> None:
    plan_payload = MappingProxyType(
        {"protocol_hash": PROTOCOL_HASH, "policy_version": POLICY_VERSION}
    )
    judgement_payload = MappingProxyType(
        {
            "obligations": MappingProxyType({"A": "verified"}),
            "contributing_attempts": MappingProxyType({"A": ("attempt-a",)}),
        }
    )
    prefix = _prefix(
        rows=(
            _row(seq=1, kind="plan", payload=plan_payload),
            _row(seq=5, kind="judgement", payload=judgement_payload),
        )
    )
    snapshot = _snapshot(obligations=(A,))
    facts = _facts()

    first, _, first_writer = _invoke(prefix=prefix, snapshot=snapshot, facts=facts)
    second, _, second_writer = _invoke(prefix=prefix, snapshot=snapshot, facts=facts)
    assert first == second
    first_bytes = json.dumps(first_writer.calls[0][2], sort_keys=True, separators=(",", ":"))
    second_bytes = json.dumps(second_writer.calls[0][2], sort_keys=True, separators=(",", ":"))
    assert first_bytes == second_bytes


def test_t14_every_untrusted_predecessor_reason_regenerates_all_without_reading_rows() -> None:
    for failure in RecordTrustFailureReason:
        untrusted = RecordUntrusted(reason=failure, detail=f"untrusted: {failure.value}")
        result, reader, writer = _invoke(prefix=untrusted)
        assert result.reused == ()
        assert result.regenerated == ("A", "B", "C")
        assert result.reasons == _reasons(reason=Reason.UNTRUSTED_PREDECESSOR)
        assert result.source_job == SOURCE_JOB
        assert reader.trusted_calls == [SOURCE_JOB]
        assert reader.entries_calls == reader.latest_calls == []
        assert len(writer.calls) == 1


# -- Fail-closed decisions beyond §8's mandated rows ---------------------------


def test_decision_mismatched_predecessor_prefix_job_id_raises_without_append() -> None:
    reader, writer = _assert_reuse_error(
        prefix=_prefix(
            rows=(_plan_row(), _judgement_row()),
            job_id="job-other",
        )
    )
    assert reader.trusted_calls == [SOURCE_JOB]
    assert writer.calls == []


def test_decision_non_positive_judgement_sequence_raises_without_append() -> None:
    _, writer = _assert_reuse_error(
        prefix=_prefix(
            rows=(
                _plan_row(),
                _judgement_row(
                    seq=0,
                    states={"A": "verified"},
                    contributions={"A": ["attempt-a"]},
                ),
            )
        ),
        snapshot=_snapshot(obligations=(A,)),
    )
    assert writer.calls == []
