"""ADR-0066's anchored chain head — `rqa/record/anchor.py` and `verify`'s anchor step.

No test here reaches the network, a credential store, or the host OS. The publisher is
a fake in every case; `conftest.py` blocks sockets for the whole suite anyway, so a
test that tried would fail loudly rather than quietly depend on a machine.
"""

from __future__ import annotations

import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import AnchorEvidence, AnchorRead, AnchorReadOutcome  # noqa: E402
from rqa.record import BreakKind, verify  # noqa: E402
from rqa.record.anchor import (  # noqa: E402
    Anchor,
    AnchorConflict,
    PublishFailed,
    anchor_job,
    recover_external_anchors,
)
from rqa.record.store import (  # noqa: E402
    anchors_for_job,
    external_anchors_for_job,
    insert_anchor,
    latest_anchor,
)
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

CLOCK = datetime(2026, 9, 16, 12, 0, 0, tzinfo=timezone.utc)


class FakePublisher:
    """Records what it was asked to publish. `error` makes every publish fail."""

    def __init__(self, *, error: BaseException | None = None):
        self.error = error
        self.published: list[Anchor] = []

    def publish(self, *, anchor: Anchor) -> str:
        if self.error is not None:
            raise self.error
        self.published.append(anchor)
        return f"fake:{anchor.job}/{anchor.seq}"


class FakeSource:
    """An E-27 read half for local recovery tests; it never reaches a network."""

    def __init__(self, result: AnchorRead):
        self.result = result
        self.calls: list[dict[str, object]] = []

    def read(self, *, repo: str, number: int, job_id: str, publisher: str) -> AnchorRead:
        self.calls.append(
            {"repo": repo, "number": number, "job_id": job_id, "publisher": publisher}
        )
        return self.result


def chained(entries: int = 3, job: str = "job-1"):
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    for index in range(entries):
        writer.append(job, "transition", {"to_state": f"state-{index}", "step": index})
    return connection


def rows(connection: sqlite3.Connection, job: str = "job-1") -> list[tuple]:
    return connection.execute(
        "SELECT seq, hash FROM record_entries WHERE job = ? ORDER BY seq", (job,)
    ).fetchall()


def found(*anchors: Anchor, locator_prefix: str = "fake:anchor") -> AnchorRead:
    return AnchorRead(
        outcome=AnchorReadOutcome.FOUND,
        evidence=tuple(
            AnchorEvidence(
                anchor=anchor,
                repo="acme/widgets",
                number=42,
                publisher="rqa-anchor-bot",
                locator=f"{locator_prefix}:{index}",
            )
            for index, anchor in enumerate(anchors)
        ),
        detail="authenticated test anchor",
    )


def recover(connection: sqlite3.Connection, read: AnchorRead) -> AnchorRead:
    return recover_external_anchors(
        connection,
        source=FakeSource(read),
        repo="acme/widgets",
        number=42,
        job_id="job-1",
        publisher="rqa-anchor-bot",
    )


# -- the rule that stops the publish/append loop --------------------------------


def test_publishing_an_anchor_appends_no_record_entry() -> None:
    """**The invariant this whole module depends on.**

    Publishing must not write a record entry. If it did, the entry would move the
    head, the new head would need an anchor, and publishing that would append again —
    for ever. `rqa/github/writes.py` is the concrete trap: every mutation there routes
    through `_dispatch`, which calls `record.append(job, "action", ...)`.

    If anyone ever wires anchoring through that layer, this test fails and says why.
    """
    connection = chained(entries=4)
    before = rows(connection)
    assert len(before) == 4

    publisher = FakePublisher()
    anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)

    after = rows(connection)
    assert after == before, "publishing an anchor changed the record"
    assert len(after) == 4, "publishing an anchor added an entry"


def test_anchoring_is_idempotent_so_a_caller_may_run_it_as_often_as_it_likes() -> None:
    """Anchoring the same head twice adds no second row. This is what makes rule 2 —
    "never triggered by an append" — cheap to honour: a caller can anchor on a timer
    without the table growing."""
    connection = chained(entries=2)
    publisher = FakePublisher()

    first = anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)
    second = anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)

    assert first.anchored_seq == 2
    assert second.anchored_seq is None, "the head was already anchored"
    assert len(anchors_for_job(connection=connection, job="job-1")) == 1
    assert len(publisher.published) == 1


# -- what an anchor detects that the chain alone cannot -------------------------


def test_a_removed_tail_is_detected_once_the_head_was_anchored() -> None:
    """The forensic case. A crashed or killed agent truncates its log, and the entries
    that matter most are the last ones. Without an anchor the shortened chain is
    internally consistent and verifies clean; with one, it does not."""
    connection = chained(entries=4)
    anchor_job(connection, "job-1", publisher=FakePublisher(), clock=lambda: CLOCK)

    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq > ?", ("job-1", 2))

    result = verify(connection, "job-1")
    assert result.ok is False
    assert result.kind is BreakKind.TAIL_REMOVED
    assert result.bad_seq == 4, "the anchored seq that is no longer present"
    assert result.anchored_through_seq == 4


def test_the_same_truncation_is_undetected_without_an_anchor() -> None:
    """The contrast that shows what the anchor is buying, stated as a test so the
    claim is not taken on trust. This is ADR-0063's blind spot, unchanged."""
    connection = chained(entries=4)
    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq > ?", ("job-1", 2))

    result = verify(connection, "job-1")
    assert result.ok is True, "a shortened chain is internally consistent"
    assert result.anchored_through_seq == 0


def test_a_wholly_rebuilt_chain_disagrees_with_its_anchor() -> None:
    """The other gap ADR-0066 accepted and this closes: an actor who rewrites a row
    and recomputes every hash after it produces a chain that verifies clean. The
    anchor recorded what the head actually was."""
    connection = chained(entries=3)
    anchor_job(connection, "job-1", publisher=FakePublisher(), clock=lambda: CLOCK)

    connection.execute(
        "UPDATE record_entries SET hash = ? WHERE job = ? AND seq = ?",
        ("f" * 64, "job-1", 3),
    )

    result = verify(connection, "job-1")
    assert result.ok is False
    # The rewrite is caught: either the row no longer hashes to its content, or it no
    # longer matches the anchor. Both are detections; neither is a clean pass.
    assert result.kind in (BreakKind.HASH_MISMATCH, BreakKind.ANCHOR_MISMATCH)


def test_an_anchor_mismatch_is_reported_when_the_chain_is_otherwise_consistent() -> None:
    """A rewrite with every hash consistently recomputed — the case `verify` alone
    cannot see — is caught by the anchor and reported as ANCHOR_MISMATCH."""
    connection = chained(entries=2)
    anchor_job(connection, "job-1", publisher=FakePublisher(), clock=lambda: CLOCK)

    # Rebuild the whole job consistently under the same seqs, so the walk passes.
    connection.execute("DELETE FROM record_entries WHERE job = ?", ("job-1",))
    connection.execute("DELETE FROM record_heads WHERE job = ?", ("job-1",))
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"to_state": "rewritten", "step": 0})
    writer.append("job-1", "transition", {"to_state": "rewritten", "step": 1})

    result = verify(connection, "job-1")
    assert result.ok is False
    assert result.kind is BreakKind.ANCHOR_MISMATCH
    assert result.bad_seq == 2


def test_entries_after_the_last_anchor_are_unattested_not_broken() -> None:
    """The bound on the claim: "complete as at the last anchor", never "complete as at
    the final entry". Rows after the anchor are not covered, and saying so is not the
    same as calling them broken."""
    connection = chained(entries=2)
    anchor_job(connection, "job-1", publisher=FakePublisher(), clock=lambda: CLOCK)
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"to_state": "later", "step": 2})

    result = verify(connection, "job-1")
    assert result.ok is True, "an unanchored tail is not a break"
    assert result.anchored_through_seq == 2
    assert result.checked_through_seq == 3, "the newer entry is read, just not attested"


# -- recovery: authenticated external anchor evidence, persisted locally --------


def test_external_recovery_restores_deleted_anchor_rows_without_record_payload_or_append() -> None:
    """The recovery proof: publish, lose local rows, import source evidence, then
    detect the removed tail.  Recovery persists provenance only and never appends a
    record entry, so it cannot move the chain head it is meant to check."""
    connection = chained(entries=4)
    publisher = FakePublisher()
    anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)
    published = publisher.published[0]
    before_entries = rows(connection)

    connection.execute("DELETE FROM record_anchors WHERE job = ?", ("job-1",))
    recovered = recover(connection, found(published))

    assert recovered.outcome is AnchorReadOutcome.FOUND
    assert rows(connection) == before_entries, "recovery added or changed a record entry"
    evidence = external_anchors_for_job(connection=connection, job="job-1")
    assert len(evidence) == 1
    assert evidence[0].locator == "fake:anchor:0"
    assert evidence[0].publisher == "rqa-anchor-bot"
    assert evidence[0].hash == published.hash
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(record_anchor_evidence)").fetchall()
    }
    assert "payload" not in columns, "external recovery must never retain record payload"

    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq > ?", ("job-1", 2))
    result = verify(connection, "job-1")
    assert (result.ok, result.kind, result.bad_seq) == (False, BreakKind.TAIL_REMOVED, 4)
    assert result.anchor_published is True, "recovered evidence is externally published"


def test_external_recovery_detects_a_rebuilt_chain_at_the_anchored_sequence() -> None:
    """External evidence wins at its sequence after local anchors are gone, so a
    consistently rebuilt local chain cannot turn a recovery into a clean pass."""
    connection = chained(entries=2)
    publisher = FakePublisher()
    anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)
    published = publisher.published[0]
    connection.execute("DELETE FROM record_anchors WHERE job = ?", ("job-1",))
    recover(connection, found(published))

    connection.execute("DELETE FROM record_entries WHERE job = ?", ("job-1",))
    connection.execute("DELETE FROM record_heads WHERE job = ?", ("job-1",))
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"to_state": "rebuilt", "step": 0})
    writer.append("job-1", "transition", {"to_state": "rebuilt", "step": 1})

    result = verify(connection, "job-1")
    assert (result.ok, result.kind, result.bad_seq) == (False, BreakKind.ANCHOR_MISMATCH, 2)


def test_entries_after_a_recovered_anchor_are_unattested_not_broken() -> None:
    """The recovered anchor bounds the claim just like a locally retained one: later
    local content remains readable but is outside external attestation."""
    connection = chained(entries=2)
    publisher = FakePublisher()
    anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)
    published = publisher.published[0]
    connection.execute("DELETE FROM record_anchors WHERE job = ?", ("job-1",))
    recover(connection, found(published))
    SQLiteRecordWriter(connection).append("job-1", "transition", {"to_state": "later", "step": 2})

    result = verify(connection, "job-1")
    assert result.ok is True
    assert (result.anchored_through_seq, result.checked_through_seq) == (2, 3)


def test_same_external_anchor_recovery_is_idempotent_but_conflicts_fail_closed() -> None:
    """Repeated authenticated evidence is harmless; conflicting evidence leaves both
    the record and persisted external provenance exactly as they were."""
    connection = chained(entries=2)
    publisher = FakePublisher()
    anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)
    published = publisher.published[0]
    connection.execute("DELETE FROM record_anchors WHERE job = ?", ("job-1",))
    good = found(published)

    recover(connection, good)
    recover(connection, good)
    before_entries = rows(connection)
    before_evidence = external_anchors_for_job(connection=connection, job="job-1")
    assert len(before_evidence) == 1

    conflicting = Anchor(
        job="job-1", seq=published.seq, hash="0" * 64, at=published.at
    )
    raised = None
    try:
        recover(connection, found(conflicting, locator_prefix="fake:conflict"))
    except AnchorConflict as error:
        raised = error
    assert raised is not None
    assert rows(connection) == before_entries
    assert external_anchors_for_job(connection=connection, job="job-1") == before_evidence


def test_non_found_external_results_fail_closed_without_any_local_mutation() -> None:
    connection = chained(entries=2)
    before_entries = rows(connection)
    unavailable = AnchorRead(
        outcome=AnchorReadOutcome.UNAVAILABLE, evidence=(), detail="test source unavailable"
    )

    assert recover(connection, unavailable) is unavailable
    assert rows(connection) == before_entries
    assert external_anchors_for_job(connection=connection, job="job-1") == ()


def test_source_reported_external_conflict_is_not_selected_or_imported() -> None:
    connection = chained(entries=2)
    before_entries = rows(connection)
    conflicting = AnchorRead(
        outcome=AnchorReadOutcome.CONFLICT,
        evidence=(
            AnchorEvidence(
                anchor=Anchor(job="job-1", seq=2, hash="a" * 64, at="first"),
                repo="acme/widgets",
                number=42,
                publisher="rqa-anchor-bot",
                locator="fake:first",
            ),
            AnchorEvidence(
                anchor=Anchor(job="job-1", seq=2, hash="b" * 64, at="second"),
                repo="acme/widgets",
                number=42,
                publisher="rqa-anchor-bot",
                locator="fake:second",
            ),
        ),
        detail="same sequence, different digests",
    )

    assert recover(connection, conflicting) is conflicting
    assert rows(connection) == before_entries
    assert external_anchors_for_job(connection=connection, job="job-1") == ()


def test_local_anchor_insert_does_not_silently_ignore_a_conflicting_hash() -> None:
    connection = chained(entries=1)
    head = rows(connection)[0]
    insert_anchor(connection=connection, job="job-1", seq=head[0], hash=head[1], at="same")
    raised = None
    try:
        insert_anchor(connection=connection, job="job-1", seq=head[0], hash="f" * 64, at="same")
    except AnchorConflict as error:
        raised = error
    assert raised is not None


# -- a failed publish never blocks anything -------------------------------------


def test_a_failed_publish_is_recorded_and_retried_never_silently_dropped() -> None:
    """A publish that does not land leaves the anchor pending, so the next run picks it
    up. The local row is written first precisely so this case still detects truncation
    with no network at all."""
    connection = chained(entries=2)
    failing = FakePublisher(error=PublishFailed("GitHub was unavailable"))

    result = anchor_job(connection, "job-1", publisher=failing, clock=lambda: CLOCK)
    assert result.anchored_seq == 2
    assert result.published == 0
    assert result.pending == 1
    assert result.failures and "seq 2" in result.failures[0]

    stored = latest_anchor(connection=connection, job="job-1")
    assert stored is not None and stored.published is False

    # ... and the retry on the next run publishes it.
    working = FakePublisher()
    retried = anchor_job(connection, "job-1", publisher=working, clock=lambda: CLOCK)
    assert retried.published == 1
    assert retried.pending == 0
    assert latest_anchor(connection=connection, job="job-1").published is True


def test_a_pending_anchor_still_detects_a_removed_tail_offline() -> None:
    """The offline half of the guarantee, and the reason the local row is written
    before the publish is attempted. `explain` must work with no network — the parent
    feature is "tamper-evident record *and offline explanation*"."""
    connection = chained(entries=3)
    anchor_job(
        connection,
        "job-1",
        publisher=FakePublisher(error=PublishFailed("offline")),
        clock=lambda: CLOCK,
    )
    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq > ?", ("job-1", 1))

    result = verify(connection, "job-1")
    assert result.ok is False
    assert result.kind is BreakKind.TAIL_REMOVED
    assert result.anchor_published is False, "reported honestly as never published"


def test_an_adapter_blow_up_is_contained_at_the_boundary_not_inside_the_record() -> None:
    """Where a misbehaving publisher is contained, and why it is there.

    `anchor_job` catches only `PublishFailed`, its declared contract, because §8's
    guard forbids `except Exception` anywhere in `rqa/record/` — that is how
    U-DISPATCH-20's defect was written, a swallowed failure around a ledger write.

    So honouring the contract is the publisher's job. `GithubAnchorPublisher` converts
    whatever its adapter throws into `PublishFailed`, which is what keeps the promise
    that anchoring can never fail a review — without putting a blanket catch inside
    the package that must never have one.
    """
    from rqa.contracts import Activity, Grant, Job, JobStatus
    from rqa.github.anchor_publisher import GithubAnchorPublisher

    job = Job(
        id="job-1",
        repo="o/r",
        number=7,
        head_sha="H1",
        base_sha="B1",
        head_repo="o/r",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.QUEUED,
    )
    grant = Grant(
        activity=Activity.COMMENT,
        repo="o/r",
        job_id="job-1",
        snapshot_hash="snap-1",
        capability_proof_id=1,
        categories=None,
        entry_seq=1,
    )

    class BrokenAdapter:
        @property
        def transport(self):
            raise AttributeError("adapter is not wired")

    publisher = GithubAnchorPublisher(adapter=BrokenAdapter(), job=job, grant=grant)

    raised = None
    try:
        publisher.publish(anchor=Anchor(job="job-1", seq=1, hash="a" * 64, at="2026-09-16T12:00:00Z"))
    except PublishFailed as exc:
        raised = exc
    assert raised is not None, "an adapter blow-up must surface as PublishFailed"
    assert "AttributeError" in str(raised)

    # ... and through `anchor_job`, that leaves the anchor pending and raises nothing.
    connection = chained(entries=1)
    result = anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)
    assert result.pending == 1
    assert result.published == 0
    assert result.failures


def test_anchoring_a_job_with_no_rows_does_nothing_and_does_not_raise() -> None:
    connection = sqlite3.connect(":memory:")
    SQLiteRecordWriter(connection)  # ensures the schema
    result = anchor_job(connection, "no-such-job", publisher=FakePublisher(), clock=lambda: CLOCK)
    assert result.anchored_seq is None
    assert result.published == 0 and result.pending == 0


# -- what the anchor may carry ---------------------------------------------------


def test_an_anchor_carries_no_record_content() -> None:
    """A digest, never payload. This is what makes publishing one safe to send
    somewhere the record itself must never go (RQA-NFR-023/027/029)."""
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"to_state": "queued", "secret_looking": "SHIBBOLETH"})

    publisher = FakePublisher()
    anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)

    published = publisher.published[0]
    assert set(vars(published)) == {"job", "seq", "hash", "at"}
    assert "SHIBBOLETH" not in repr(published)

    from rqa.github.anchor_publisher import anchor_body

    assert "SHIBBOLETH" not in anchor_body(anchor=published)


def test_the_github_publisher_refuses_without_a_grant_and_never_sends() -> None:
    """Bypassing `writes.py` bypasses its authority gate, so the publisher runs the
    same check itself. An advisory-only repository holds no comment authority, and
    must send nothing rather than silently widening what RQA may do."""
    from rqa.contracts import Job, JobStatus
    from rqa.github.anchor_publisher import GithubAnchorPublisher

    class ExplodingAdapter:
        @property
        def transport(self):  # pragma: no cover - reaching this is the failure
            raise AssertionError("the publisher sent something without a grant")

    job = Job(
        id="job-1",
        repo="o/r",
        number=7,
        head_sha="H1",
        base_sha="B1",
        head_repo="o/r",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.QUEUED,
    )
    publisher = GithubAnchorPublisher(adapter=ExplodingAdapter(), job=job, grant=None)

    raised = None
    try:
        publisher.publish(anchor=Anchor(job="job-1", seq=1, hash="a" * 64, at="2026-09-16T12:00:00Z"))
    except PublishFailed as exc:
        raised = exc
    assert raised is not None, "a missing grant must refuse"
    assert "no authority" in str(raised)


# -- the wiring: `rqa anchor`, and the ordering rule it must keep -----------------


def test_the_grant_is_minted_before_the_head_is_read() -> None:
    """**The second loop, and the reason anchoring is wired in the composition root.**

    `authority.grant` records a `grant` entry (E-04), so minting a grant *moves the
    head*. If the head were read first and the grant minted second, every anchor run
    would leave the head one entry ahead of the anchor, for ever — the publish/append
    loop again, arriving through the authority path instead of the write path.

    Minting first and reading the head after means the anchor covers its own grant
    entry and nothing is appended behind it. This test pins the ordering by driving
    the same sequence against a fake: an append that lands *before* the head read is
    covered; one that lands after would not be.
    """
    connection = chained(entries=2)
    writer = SQLiteRecordWriter(connection)

    # Stand in for `authority.grant`: it appends, exactly as E-04 does.
    writer.append("job-1", "grant", {"activity": "comment", "decision": "granted"})

    publisher = FakePublisher()
    result = anchor_job(connection, "job-1", publisher=publisher, clock=lambda: CLOCK)

    assert result.anchored_seq == 3, "the anchor must cover the grant entry"
    verified = verify(connection, "job-1")
    assert verified.anchored_through_seq == 3
    assert verified.checked_through_seq == 3, "nothing is appended behind the anchor"


def test_rqa_anchor_is_a_real_command_that_reaches_the_record() -> None:
    """The feature is reachable by an operator, not just importable.

    Exercises the actual CLI dispatch against a temp state directory. GitHub is never
    reached: with no capability configured the grant is denied, which is the
    advisory-only path — the anchor is still recorded locally, which is what detects a
    crash-truncated log offline, and the command still exits 0 because anchoring must
    never be able to fail a review.
    """
    import json
    import tempfile
    from io import StringIO
    from unittest.mock import patch

    from rqa.cli.main import main

    with tempfile.TemporaryDirectory() as directory:
        out = StringIO()
        with patch("sys.stdout", out):
            code = main(["--state-dir", directory, "anchor", "job-does-not-exist"])
        assert code == 0, "an unanchorable job is a reported state, not a failure"
        payload = json.loads(out.getvalue())
        assert payload["outcome"] == "ok"
        assert payload["result"]["job_id"] == "job-does-not-exist"
        assert payload["result"]["anchored_seq"] is None
        assert "no such job" in (payload["result"]["detail"] or "")


def test_anchor_job_for_leaves_nothing_appended_behind_the_anchor() -> None:
    """Pins the ORDERING inside `anchor_job_for`, not just the property.

    The sibling test above proves that an anchor covers a grant entry appended before
    it. It does not prove the production function mints the grant first — swap the two
    statements and that test still passes. This one drives `anchor_job_for` itself with
    an authority stand-in that appends a `grant` entry exactly as E-04 does, and
    asserts the head is not ahead of the anchor afterwards.

    If anyone reorders it so the head is read before the grant is minted, the anchor
    lands one entry short and this fails.
    """
    from rqa.cli.composition import anchor_job_for
    from rqa.contracts import Grant, Job, JobStatus, Snapshot
    from rqa.policy.store import StoredSnapshot
    from rqa.record.store import head_entry, latest_anchor

    connection = chained(entries=2)
    writer = SQLiteRecordWriter(connection)
    job = Job(
        id="job-1",
        repo="o/r",
        number=7,
        head_sha="H1",
        base_sha="B1",
        head_repo="o/r",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash="snap-1",
        status=JobStatus.QUEUED,
    )

    class Authority:
        github = object()
        store = object()

        def grant(self, **kwargs):
            # E-04 records its decision. That is the whole hazard: this append moves
            # the head, so it must happen before the head is read.
            entry = writer.append(
                "job-1", "grant", {"activity": "comment", "decision": "granted"}
            )
            return Grant(
                activity=kwargs["activity"],
                repo="o/r",
                job_id="job-1",
                snapshot_hash="snap-1",
                capability_proof_id=1,
                categories=None,
                entry_seq=entry.seq,
            )

    class Jobs:
        def get(self, job_id):
            return job

    class SnapshotStore:
        """The CLI's stored-snapshot preflight needs only this pinned snapshot."""

        def get(self, hash):
            assert hash == "snap-1"
            return StoredSnapshot(
                snapshot=Snapshot(
                    hash="snap-1",
                    repo="",
                    protocol_hash="protocol-1",
                    authority={},
                    routes=(),
                    external=None,
                    policy=None,
                    budget=None,
                ),
                activated_at=CLOCK,
            )

    class Comp:
        connection = None
        clock = lambda self: CLOCK  # noqa: E731
        jobs = Jobs()
        authority = Authority()
        record = writer
        github = object()
        snapshot_store = SnapshotStore()

    comp = Comp()
    comp.connection = connection

    outcome = anchor_job_for(comp, "job-1")

    head = head_entry(connection=connection, job="job-1")
    anchor = latest_anchor(connection=connection, job="job-1")
    assert head is not None and anchor is not None
    assert anchor.seq == head.seq, (
        f"anchor at seq {anchor.seq} but head is at {head.seq} — the grant entry landed "
        "after the head was read, which is the loop this ordering exists to prevent"
    )
    assert outcome.anchored_seq == head.seq
