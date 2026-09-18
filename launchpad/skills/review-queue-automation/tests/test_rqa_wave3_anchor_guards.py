#!/usr/bin/env python3
"""Wave 3 adversarial acceptance guards for ADR-0066 anchoring.

These checks deliberately cover the easy-to-miss negative boundaries around an
otherwise small feature.  They use in-memory SQLite and fake transports only:
an anchor test must never need a credential or a GitHub connection to prove
that it will fail closed.

Two assertions below are structural rather than behavioural.  They protect
the two recursion hazards whose bad path has no valid terminal result to
observe: sending an anchor through ``writes.comment`` (which records an
``action``) and calling anchoring from ``RecordWriter.append``.
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import inspect
import io
import json
import pathlib
import socket
import sqlite3
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.cli import exitcodes  # noqa: E402
from rqa.cli.composition import AnchorOutcome, anchor_job_for  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    Anchor,
    AnchorEvidence,
    AnchorRead,
    AnchorReadOutcome,
    Blocking,
    Budget,
    External,
    Grant,
    Job,
    JobStatus,
    Mechanical,
    Policy,
    RemediationPolicy,
    Snapshot,
)
from rqa.github.anchor_publisher import GithubAnchorPublisher, anchor_body  # noqa: E402
from rqa.policy.store import StoredSnapshot  # noqa: E402
from rqa.record import BreakKind, SQLiteRecordWriter, explain, verify  # noqa: E402
from rqa.record.anchor import anchor_job, recover_external_anchors  # noqa: E402
from rqa.record.store import (  # noqa: E402
    AnchorConflict,
    anchors_for_job,
    external_anchors_for_job,
    import_external_anchors,
    insert_anchor,
    mark_anchor_published,
)


REPO = "acme/widgets"
NUMBER = 42
JOB_ID = "wave-3-job"
NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)
SNAPSHOT_HASH = "a" * 64

main_module = importlib.import_module("rqa.cli.main")
composition_module = importlib.import_module("rqa.cli.composition")


def _snapshot() -> Snapshot:
    return Snapshot(
        hash=SNAPSHOT_HASH,
        repo="",
        protocol_hash="b" * 64,
        authority={activity: activity is Activity.COMMENT for activity in Activity},
        routes=(),
        external=External(allowed=True, deny_label=""),
        policy=Policy(
            version="wave-3-test",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(categories=frozenset(), tools=frozenset()),
            assurance={},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


def _job() -> Job:
    return Job(
        id=JOB_ID,
        repo=REPO,
        number=NUMBER,
        head_sha="head",
        base_sha="base",
        head_repo=REPO,
        head_ref="feature/wave-3",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=SNAPSHOT_HASH,
        status=JobStatus.QUEUED,
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

    def get(self, snapshot_hash: str) -> StoredSnapshot | None:
        self.calls.append(snapshot_hash)
        return self.stored


class _Authority:
    github = object()
    store = object()

    def __init__(self, *, repos: set[str], on_grant=None):
        self.gate = SimpleNamespace(repos=repos)
        self.on_grant = on_grant
        self.calls = 0

    def grant(self, **kwargs):
        self.calls += 1
        if self.on_grant is not None:
            return self.on_grant(**kwargs)
        return Grant(
            activity=Activity.COMMENT,
            repo=kwargs["repo"],
            job_id=kwargs["job_id"],
            snapshot_hash=kwargs["snapshot"].hash,
            capability_proof_id=7,
            categories=None,
            entry_seq=1,
        )


def _composition(*, stored: StoredSnapshot | None, authority: _Authority):
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, clock=lambda: NOW)
    writer.append(JOB_ID, "transition", {"repo": REPO, "number": NUMBER, "head_sha": "head"})
    return SimpleNamespace(
        connection=connection,
        record=writer,
        jobs=_Jobs(_job()),
        snapshot_store=_Snapshots(stored),
        authority=authority,
        github=object(),
        clock=lambda: NOW,
    )


def _stored_snapshot() -> StoredSnapshot:
    return StoredSnapshot(snapshot=_snapshot(), activated_at=NOW)


class _Publisher:
    instances: list["_Publisher"] = []

    def __init__(self, *, adapter, job: Job, grant: Grant | None):
        self.job = job
        self.grant = grant
        self.published: list[Anchor] = []
        type(self).instances.append(self)

    def publish(self, *, anchor: Anchor) -> str:
        self.published.append(anchor)
        return f"fake:{anchor.job}/{anchor.seq}"


@contextlib.contextmanager
def _fake_publisher():
    _Publisher.instances = []
    with patch.object(composition_module, "GithubAnchorPublisher", _Publisher):
        yield _Publisher


def test_anchor_command_passes_the_durable_configured_repo_set_to_composition() -> None:
    """A CLI refactor cannot turn ``rqa anchor`` into an unscoped composition."""
    seen: list[tuple[pathlib.Path, tuple[str, ...]]] = []
    outcome = AnchorOutcome(JOB_ID, None, 0, 0, "test only")

    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory)
        (state_dir / "repos.json").write_text(json.dumps([REPO, "acme/other"]), encoding="utf-8")

        def build(state_dir_arg: pathlib.Path, *, repos: tuple[str, ...] = ()):  # type: ignore[no-untyped-def]
            seen.append((state_dir_arg, repos))
            return SimpleNamespace(connection=sqlite3.connect(":memory:"))

        output = io.StringIO()
        with patch.object(main_module, "build_composition", build), patch.object(
            main_module, "anchor_job_for", return_value=outcome
        ), contextlib.redirect_stdout(output):
            code = main_module.main(["--state-dir", str(state_dir), "anchor", JOB_ID])

    assert code == exitcodes.OK
    assert seen == [(state_dir, (REPO, "acme/other"))]


def test_missing_pinned_snapshot_cannot_mint_a_grant_or_construct_a_publisher() -> None:
    """``snapshot=None`` is a publication refusal, not an optional policy input."""
    authority = _Authority(
        repos={REPO},
        on_grant=lambda **_: (_ for _ in ()).throw(AssertionError("grant must not run")),
    )
    comp = _composition(stored=None, authority=authority)

    with _fake_publisher() as publisher:
        outcome = anchor_job_for(comp, JOB_ID)

    assert "snapshot is missing" in (outcome.detail or "")
    assert authority.calls == 0
    assert publisher.instances == []
    assert anchors_for_job(connection=comp.connection, job=JOB_ID) == ()


def test_completed_anchor_is_checked_before_any_new_grant() -> None:
    """A no-op repeat must not create authority evidence merely to learn it is a no-op."""
    authority = _Authority(
        repos={REPO},
        on_grant=lambda **_: (_ for _ in ()).throw(AssertionError("no-op asked the gate")),
    )
    comp = _composition(stored=None, authority=authority)
    head = comp.connection.execute(
        "SELECT seq, hash FROM record_entries WHERE job = ?", (JOB_ID,)
    ).fetchone()
    assert head is not None
    insert_anchor(connection=comp.connection, job=JOB_ID, seq=head[0], hash=head[1], at="test")
    mark_anchor_published(connection=comp.connection, job=JOB_ID, seq=head[0], destination="fake:done")

    with _fake_publisher() as publisher:
        outcome = anchor_job_for(comp, JOB_ID)

    assert outcome.detail is None and outcome.published == 0
    assert authority.calls == 0
    assert publisher.instances == []
    assert comp.snapshot_store.calls == [], "no-op must precede archived-policy lookup too"


class _PublishingTransport:
    def __init__(self):
        self.calls: list[str] = []

    def graphql(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["operation"] == "anchor"
        self.calls.append("preflight")
        return {
            "viewer": {"login": "rqa-bot", "id": "U_1"},
            "repository": {
                "pullRequest": {
                    "id": "PR_1",
                    "state": "OPEN",
                    "headRefOid": "head",
                    "assignees": {"nodes": []},
                }
            },
        }

    def mutate(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        assert self.calls == ["preflight"], "an anchor mutation requires a live PR-node preflight"
        self.calls.append("mutate")
        assert kwargs["operation"] == "anchor"
        return {"addPullRequestReview": {"pullRequestReview": {"id": "PRR_1"}}}


def _grant() -> Grant:
    return Grant(
        activity=Activity.COMMENT,
        repo=REPO,
        job_id=JOB_ID,
        snapshot_hash=SNAPSHOT_HASH,
        capability_proof_id=7,
        categories=None,
        entry_seq=1,
    )


def test_anchor_publisher_preflights_then_uses_direct_transport_not_writes_comment() -> None:
    """The E-27 write is a review mutation with a read-before-write safety check."""
    transport = _PublishingTransport()
    adapter = SimpleNamespace(transport=transport)
    anchor = Anchor(job=JOB_ID, seq=9, hash="c" * 64, at="2026-09-18T00:00:00+00:00")

    with patch("rqa.github.writes.comment", side_effect=AssertionError("writes.comment recurses")):
        locator = GithubAnchorPublisher(adapter=adapter, job=_job(), grant=_grant()).publish(anchor=anchor)

    assert locator == "github:pull-request-review:PRR_1"
    assert transport.calls == ["preflight", "mutate"]


def test_anchor_publisher_source_excludes_comment_dispatch_and_record_content() -> None:
    """Structural guards for the two non-terminating/disclosure regressions."""
    publisher_tree = ast.parse(textwrap.dedent(inspect.getsource(GithubAnchorPublisher.publish)))
    calls = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(publisher_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    assert "comment" not in calls, "anchor publication must bypass writes.comment/_dispatch"
    assert "mutate" in calls, "anchor publication must use the direct transport mutation"

    body_tree = ast.parse(textwrap.dedent(inspect.getsource(anchor_body)))
    anchor_fields = {
        node.attr
        for node in ast.walk(body_tree)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "anchor"
    }
    assert anchor_fields == {"job", "seq", "hash", "at"}
    rendered = anchor_body(
        anchor=Anchor(job=JOB_ID, seq=9, hash="c" * 64, at="2026-09-18T00:00:00+00:00")
    )
    assert "payload" not in rendered.lower() and "record content" not in rendered.lower()


def test_conflicting_same_sequence_external_evidence_is_rejected_before_persistence() -> None:
    """Timestamp ordering is not a conflict-resolution policy for authenticated anchors."""
    connection = sqlite3.connect(":memory:")
    SQLiteRecordWriter(connection)
    first = AnchorEvidence(
        anchor=Anchor(job=JOB_ID, seq=3, hash="1" * 64, at="first"),
        repo=REPO,
        number=NUMBER,
        publisher="rqa-bot",
        locator="github:review:one",
    )
    conflict = AnchorEvidence(
        anchor=Anchor(job=JOB_ID, seq=3, hash="2" * 64, at="later"),
        repo=REPO,
        number=NUMBER,
        publisher="rqa-bot",
        locator="github:review:two",
    )

    try:
        import_external_anchors(connection=connection, job=JOB_ID, evidence=(first, conflict))
    except AnchorConflict:
        pass
    else:
        raise AssertionError("conflicting same-sequence anchors were accepted")
    assert external_anchors_for_job(connection=connection, job=JOB_ID) == ()


@dataclass
class _Source:
    result: AnchorRead

    def read(self, **kwargs):  # type: ignore[no-untyped-def]
        return self.result


class _OfflinePublisher:
    def __init__(self):
        self.published: list[Anchor] = []

    def publish(self, *, anchor: Anchor) -> str:
        self.published.append(anchor)
        return f"github:review:{anchor.seq}"


def test_external_recovery_keeps_tail_protection_after_local_anchor_rows_are_deleted() -> None:
    """Local loss is recoverable from authenticated external provenance, not payload copies."""
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, clock=lambda: NOW)
    for index in range(3):
        writer.append(JOB_ID, "transition", {"repo": REPO, "number": NUMBER, "step": index})
    publisher = _OfflinePublisher()
    anchor_job(connection, JOB_ID, publisher=publisher, clock=lambda: NOW)
    published = publisher.published[0]
    connection.execute("DELETE FROM record_anchors WHERE job = ?", (JOB_ID,))

    evidence = AnchorEvidence(
        anchor=published,
        repo=REPO,
        number=NUMBER,
        publisher="rqa-bot",
        locator="github:review:3",
    )
    recovered = recover_external_anchors(
        connection,
        source=_Source(AnchorRead(AnchorReadOutcome.FOUND, (evidence,), "fixture")),
        repo=REPO,
        number=NUMBER,
        job_id=JOB_ID,
        publisher="rqa-bot",
    )
    assert recovered.outcome is AnchorReadOutcome.FOUND
    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq = 3", (JOB_ID,))

    result = verify(connection, JOB_ID)
    assert (result.ok, result.kind, result.bad_seq) == (False, BreakKind.TAIL_REMOVED, 3)


def test_explain_is_offline_even_when_a_network_constructor_is_forbidden() -> None:
    """E-17 reconstructs from SQLite; it must not use a remote anchor read as a crutch."""
    connection = sqlite3.connect(":memory:")
    SQLiteRecordWriter(connection, clock=lambda: NOW).append(
        JOB_ID,
        "transition",
        {"repo": REPO, "number": NUMBER, "head_sha": "head", "to_state": "queued"},
    )

    with patch.object(socket, "socket", side_effect=AssertionError("explain opened a socket")):
        result = explain(connection, REPO, NUMBER)

    assert result.job_id == JOB_ID
    assert result.repo == REPO and result.number == NUMBER


def test_record_append_source_cannot_invoke_anchoring() -> None:
    """Anchoring is caller-scheduled; append-triggered anchoring would chase its own head forever."""
    writer_tree = ast.parse(textwrap.dedent(inspect.getsource(SQLiteRecordWriter.append)))
    calls = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(writer_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    assert "anchor_job" not in calls
    module_tree = ast.parse(
        pathlib.Path(inspect.getsourcefile(SQLiteRecordWriter) or "").read_text(encoding="utf-8")
    )
    imported_anchor_module = any(
        isinstance(node, ast.ImportFrom) and node.module == "rqa.record.anchor"
        for node in ast.walk(module_tree)
    )
    assert not imported_anchor_module, "writer must not acquire an anchoring dependency"
