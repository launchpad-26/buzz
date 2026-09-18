"""CLI anchoring: pinned authority, safe retries, and genuine no-op repeats.

Every collaborator beyond the record's in-memory SQLite implementation is a fake.
In particular, ``GithubAnchorPublisher`` is replaced before a command runs, so these
tests never invoke a transport, a credential helper, or a live GitHub mutation.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import pathlib
import sqlite3
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.cli import exitcodes
from rqa.cli.composition import anchor_job_for
from rqa.contracts import (
    Activity,
    Anchor,
    AnchorEvidence,
    AnchorRead,
    AnchorReadOutcome,
    AppendFailed,
    Blocking,
    Budget,
    Deny,
    DenyReason,
    External,
    Grant,
    Job,
    JobStatus,
    Mechanical,
    Policy,
    RemediationPolicy,
    Snapshot,
)
from rqa.authority import GateError
from rqa.policy.store import StoredSnapshot
from rqa.record import PublishFailed, SQLiteRecordWriter, explain_job, verify
from rqa.record.store import anchors_for_job, entries_for_job, external_anchors_for_job

main_module = importlib.import_module("rqa.cli.main")
composition_module = importlib.import_module("rqa.cli.composition")

_CLOCK = lambda: datetime(2026, 9, 18, tzinfo=timezone.utc)  # noqa: E731
_HASH = "a" * 64


def _snapshot(*, repo: str = "") -> Snapshot:
    return Snapshot(
        hash=_HASH,
        repo=repo,
        protocol_hash="b" * 64,
        authority={activity: activity is Activity.COMMENT for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label=""),
        policy=Policy(
            version="test",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(categories=frozenset(), tools=frozenset()),
            assurance={},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


class _Jobs:
    def __init__(self, job: Job):
        self.job = job

    def get(self, job_id: str) -> Job | None:
        return self.job if job_id == self.job.id else None


class _Snapshots:
    def __init__(self, stored: StoredSnapshot | None):
        self.stored = stored
        self.calls: list[str] = []

    def get(self, hash_: str) -> StoredSnapshot | None:
        self.calls.append(hash_)
        return self.stored


class _Authority:
    github = object()
    store = object()

    def __init__(self, writer: SQLiteRecordWriter, *, denied: bool = False):
        self.writer = writer
        self.denied = denied
        self.calls: list[dict] = []

    def grant(self, **kwargs):
        self.calls.append(kwargs)
        entry = self.writer.append(
            kwargs["job_id"],
            "grant",
            {
                "activity": kwargs["activity"].value,
                "snapshot_hash": kwargs["snapshot"].hash if kwargs["snapshot"] else None,
                "categories": None,
                "capability_proof_id": 71,
                "decision": "denied" if self.denied else "granted",
                "reason": "repo_not_managed" if self.denied else None,
                "detail": "test",
            },
        )
        if self.denied:
            return Deny(
                activity=Activity.COMMENT,
                repo=kwargs["repo"],
                job_id=kwargs["job_id"],
                reason=DenyReason.REPO_NOT_MANAGED,
                detail="test",
                entry_seq=entry.seq,
            )
        return Grant(
            activity=Activity.COMMENT,
            repo=kwargs["repo"],
            job_id=kwargs["job_id"],
            snapshot_hash=kwargs["snapshot"].hash,
            capability_proof_id=71,
            categories=None,
            entry_seq=entry.seq,
        )


class _Publisher:
    calls: list[tuple[Grant | None, int]] = []
    failures_remaining = 0

    def __init__(self, *, adapter, job: Job, grant: Grant | None):
        self.job = job
        self.grant = grant

    def publish(self, *, anchor):
        type(self).calls.append((self.grant, anchor.seq))
        if type(self).failures_remaining:
            type(self).failures_remaining -= 1
            raise PublishFailed("offline fake")
        if self.grant is None:
            raise PublishFailed("fake requires grant")
        return f"fake:{self.job.repo}#{self.job.number}"


class _Reader:
    """A read-only E-27 source double shared by the publish/recover integration run."""

    result = AnchorRead(AnchorReadOutcome.NONE, (), "no trusted anchor found")
    calls: list[dict] = []

    def __init__(self, *, adapter):
        self.adapter = adapter

    def read(self, **kwargs):
        type(self).calls.append(kwargs)
        return type(self).result


class _Comp:
    def __init__(self, *, snapshot: StoredSnapshot | None, denied: bool = False):
        self.connection = sqlite3.connect(":memory:")
        self.clock = _CLOCK
        self.record = SQLiteRecordWriter(self.connection, clock=_CLOCK)
        self.job = Job(
            id="anchor-job",
            repo="acme/widget",
            number=7,
            head_sha="head",
            base_sha="base",
            head_repo="acme/widget",
            head_ref="feature",
            predecessor_job=None,
            predecessor_head_sha=None,
            snapshot_hash=_HASH,
            status=JobStatus.QUEUED,
        )
        self.jobs = _Jobs(self.job)
        self.snapshot_store = _Snapshots(snapshot)
        self.authority = _Authority(self.record, denied=denied)
        self.github = object()
        self.record.append(self.job.id, "transition", {"to_state": "queued"})
        # Recovery failures roll back their own transaction.  The fixture's
        # pre-existing record is durable state, not part of that transaction.
        self.connection.commit()


@contextlib.contextmanager
def _fake_publisher(*, failures: int = 0):
    _Publisher.calls = []
    _Publisher.failures_remaining = failures
    with patch.object(composition_module, "GithubAnchorPublisher", _Publisher):
        yield _Publisher


def _stored_snapshot() -> StoredSnapshot:
    return StoredSnapshot(snapshot=_snapshot(), activated_at=_CLOCK())


def _record_count(comp: _Comp) -> int:
    return len(entries_for_job(connection=comp.connection, job=comp.job.id))


def _run_anchor(state_dir: pathlib.Path, job_id: str) -> tuple[int, dict]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = main_module.main(["--state-dir", str(state_dir), "anchor", job_id])
    return code, json.loads(output.getvalue())


def _run(*argv: str) -> tuple[int, dict]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = main_module.main(list(argv))
    return code, json.loads(output.getvalue())


@contextlib.contextmanager
def _fake_reader(result: AnchorRead):
    _Reader.result = result
    _Reader.calls = []
    with patch.object(composition_module, "GithubAnchorReader", _Reader):
        yield _Reader


def _found_anchor(comp: _Comp, anchor: Anchor) -> AnchorRead:
    return AnchorRead(
        outcome=AnchorReadOutcome.FOUND,
        evidence=(
            AnchorEvidence(
                anchor=anchor,
                repo=comp.job.repo,
                number=comp.job.number,
                publisher="rqa-bot",
                locator="fake:immutable-review",
            ),
        ),
        detail="trusted anchor found",
    )


def test_anchor_command_uses_configured_repos_and_pinned_stored_snapshot() -> None:
    """An existing job resolves its archived policy before publishing with a grant."""
    comp = _Comp(snapshot=_stored_snapshot())
    with tempfile.TemporaryDirectory() as directory, _fake_publisher() as publisher:
        state_dir = pathlib.Path(directory)
        (state_dir / "repos.json").write_text('["acme/widget"]', encoding="utf-8")
        calls: list[tuple[pathlib.Path, tuple[str, ...]]] = []

        def build(state, *, repos=()):
            calls.append((state, repos))
            return comp

        with patch.object(main_module, "build_composition", build):
            code, payload = _run_anchor(state_dir, comp.job.id)

    assert code == exitcodes.OK
    assert payload["result"]["published"] == 1
    assert calls == [(state_dir, ("acme/widget",))]
    assert comp.snapshot_store.calls == [_HASH]
    assert comp.authority.calls[0]["snapshot"] == replace(_snapshot(), repo="acme/widget")
    assert len(publisher.calls) == 1 and publisher.calls[0][0] is not None


def test_anchor_missing_snapshot_and_unmanaged_repo_fail_closed() -> None:
    """Neither absent policy evidence nor a denied repository can reach GitHub."""
    missing = _Comp(snapshot=None)
    with _fake_publisher() as publisher:
        outcome = anchor_job_for(missing, missing.job.id)
    assert "snapshot is missing" in (outcome.detail or "")
    assert missing.authority.calls == []
    assert publisher.calls == []
    assert anchors_for_job(connection=missing.connection, job=missing.job.id) == ()

    malformed = _Comp(snapshot=_stored_snapshot())
    malformed.snapshot_store.stored = object()  # type: ignore[assignment]
    with _fake_publisher() as publisher:
        outcome = anchor_job_for(malformed, malformed.job.id)
    assert "snapshot is malformed" in (outcome.detail or "")
    assert malformed.authority.calls == []
    assert publisher.calls == []

    unmanaged = _Comp(snapshot=_stored_snapshot(), denied=True)
    with _fake_publisher() as publisher:
        outcome = anchor_job_for(unmanaged, unmanaged.job.id)
    assert outcome.detail == "not published: repo_not_managed"
    assert len(unmanaged.authority.calls) == 1
    assert publisher.calls == []
    assert anchors_for_job(connection=unmanaged.connection, job=unmanaged.job.id) == ()


def test_successful_unchanged_anchor_is_a_true_no_op() -> None:
    comp = _Comp(snapshot=_stored_snapshot())
    with _fake_publisher() as publisher:
        first = anchor_job_for(comp, comp.job.id)
        after_first = _record_count(comp)
        second = anchor_job_for(comp, comp.job.id)

    assert first.published == 1
    assert second.published == 0 and second.pending == 0
    assert len(comp.authority.calls) == 1
    assert len(publisher.calls) == 1
    assert _record_count(comp) == after_first
    assert len(anchors_for_job(connection=comp.connection, job=comp.job.id)) == 1


def test_pending_retry_reuses_recorded_grant_without_chain_growth() -> None:
    comp = _Comp(snapshot=_stored_snapshot())
    with _fake_publisher(failures=1) as publisher:
        first = anchor_job_for(comp, comp.job.id)
        after_first = _record_count(comp)
        second = anchor_job_for(comp, comp.job.id)

    assert first.pending == 1 and first.published == 0
    assert second.pending == 0 and second.published == 1
    assert len(comp.authority.calls) == 1
    assert len(publisher.calls) == 2
    assert publisher.calls[1][0] is not None
    assert _record_count(comp) == after_first
    assert len(anchors_for_job(connection=comp.connection, job=comp.job.id)) == 1


def test_anchor_normalizes_gate_and_record_failures_at_the_cli_boundary() -> None:
    """Both are internal failures, never a traceback or an invented success."""
    for failure in (GateError("bad gate call"), AppendFailed("record unavailable")):
        comp = _Comp(snapshot=_stored_snapshot())
        with patch.object(main_module, "build_composition", return_value=comp), patch.object(
            main_module, "anchor_job_for", side_effect=failure
        ):
            with tempfile.TemporaryDirectory() as directory:
                code, payload = _run_anchor(pathlib.Path(directory), comp.job.id)
        assert code == exitcodes.OTHER
        assert payload == {
            "outcome": "error",
            "error_type": type(failure).__name__,
            "detail": str(failure),
        }


def test_anchor_recover_restores_external_evidence_then_offline_explain_reports_rebuild() -> None:
    """End-to-end Wave 3: publication, explicit recovery, then offline detection.

    The reader is a fixture-only E-27 double and the publisher records an immutable
    anchor-shaped value; neither can reach GitHub.  ``explain`` is intentionally run
    after the reader patch has ended, proving reconstruction needs no external call.
    """
    comp = _Comp(snapshot=_stored_snapshot())
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory)
        sqlite3.connect(state_dir / "state.db").close()
        (state_dir / "repos.json").write_text('["acme/widget"]', encoding="utf-8")
        with patch.object(main_module, "build_composition", return_value=comp), _fake_publisher() as publisher, _fake_reader(
            AnchorRead(AnchorReadOutcome.NONE, (), "no trusted anchor found")
        ):
            code, published = _run(
                "--state-dir", str(state_dir), "anchor", comp.job.id, "--publisher", "rqa-bot"
            )
            assert code == exitcodes.OK
            assert published["result"]["published"] == 1
            assert published["result"]["preflight"] == AnchorReadOutcome.NONE.value
            assert len(publisher.calls) == 1
            published_anchor = Anchor(
                job=comp.job.id,
                seq=publisher.calls[0][1],
                hash=anchors_for_job(connection=comp.connection, job=comp.job.id)[0].hash,
                at=anchors_for_job(connection=comp.connection, job=comp.job.id)[0].at,
            )

        comp.connection.execute("DELETE FROM record_anchors WHERE job = ?", (comp.job.id,))
        before_entries = entries_for_job(connection=comp.connection, job=comp.job.id)
        with patch.object(main_module, "build_composition", return_value=comp), _fake_reader(
            _found_anchor(comp, published_anchor)
        ) as reader:
            code, recovered = _run(
                "--state-dir", str(state_dir), "anchor", "recover", comp.job.id, "--publisher", "rqa-bot"
            )
        assert code == exitcodes.OK
        assert recovered["outcome"] == "recovered"
        assert recovered["result"]["integrity"] == "verified"
        assert len(reader.calls) == 1
        assert entries_for_job(connection=comp.connection, job=comp.job.id) == before_entries
        assert len(external_anchors_for_job(connection=comp.connection, job=comp.job.id)) == 1

        # Rebuild a self-consistent chain at the same length.  Only the recovered,
        # externally authenticated anchor makes this visible; explain stays offline.
        comp.connection.execute("DELETE FROM record_entries WHERE job = ?", (comp.job.id,))
        comp.connection.execute("DELETE FROM record_heads WHERE job = ?", (comp.job.id,))
        writer = SQLiteRecordWriter(comp.connection, clock=_CLOCK)
        writer.append(comp.job.id, "transition", {"to_state": "rewritten", "step": 0})
        writer.append(comp.job.id, "transition", {"to_state": "rewritten", "step": 1})
        integrity = verify(comp.connection, comp.job.id)
        assert integrity.ok is False
        assert integrity.kind.value == "anchor_mismatch"

        with patch.object(main_module, "build_composition", return_value=comp):
            code, explained = _run("--state-dir", str(state_dir), "explain", "job", comp.job.id)
        assert code == exitcodes.OK
        assert explained["result"]["verified"] is False
        assert explained["result"]["truncated_at"] == published_anchor.seq


def test_anchor_recover_failure_outcomes_are_non_mutating_and_never_publish() -> None:
    comp = _Comp(snapshot=_stored_snapshot())
    outcomes = (
        (AnchorReadOutcome.NONE, exitcodes.INPUT_ERROR),
        (AnchorReadOutcome.UNAVAILABLE, exitcodes.NETWORK),
        (AnchorReadOutcome.UNAUTHENTICATED, exitcodes.AUTH),
        (AnchorReadOutcome.MALFORMED, exitcodes.OTHER),
        (AnchorReadOutcome.CONFLICT, exitcodes.OTHER),
    )
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory)
        sqlite3.connect(state_dir / "state.db").close()
        for source_outcome, expected_code in outcomes:
            before_entries = entries_for_job(connection=comp.connection, job=comp.job.id)
            before_evidence = external_anchors_for_job(connection=comp.connection, job=comp.job.id)
            with patch.object(main_module, "build_composition", return_value=comp), _fake_publisher() as publisher, _fake_reader(
                AnchorRead(source_outcome, (), f"{source_outcome.value} fixture")
            ):
                code, payload = _run(
                    "--state-dir", str(state_dir), "anchor", "recover", comp.job.id, "--publisher", "rqa-bot"
                )
            assert code == expected_code
            assert payload["outcome"] == source_outcome.value
            assert publisher.calls == []
            assert entries_for_job(connection=comp.connection, job=comp.job.id) == before_entries
            assert external_anchors_for_job(connection=comp.connection, job=comp.job.id) == before_evidence
