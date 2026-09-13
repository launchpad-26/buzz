#!/usr/bin/env python3
"""The snapshot store — `code/P-03-policy.md` §5 and §8 rows T13 and T14.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

These tests drive the real `SqliteSnapshotStore` over a temporary state directory,
because the properties under test are exactly the ones a fake cannot have: an
archive that exists complete-or-not-at-all, a row written only after it, and bytes
that are re-hashed on every read.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import pathlib
import sqlite3
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.policy.validate as policy_validate  # noqa: E402
from rqa.contracts import Job, JobStatus, Snapshot, ValidationFailure  # noqa: E402
from rqa.policy import PolicyError, SnapshotStoreCorrupted, snapshot_for  # noqa: E402
from rqa.policy.snapshot import canonical_bytes, digest_of  # noqa: E402
from rqa.policy.store import (  # noqa: E402
    ARCHIVE_DIR_NAME,
    SnapshotStore,
    SqliteSnapshotStore,
    StoredSnapshot,
)
from rqa.policy.types import utcnow  # noqa: E402


@contextlib.contextmanager
def tool_set(registry: dict):
    """Substitute P-10's registry lookup for the duration of one test.

    Never a test of whether `rqa.remediation` exists: the registry's *membership* is
    what the contract fixes, and this substitution keeps working once P-10 lands.
    """
    original = policy_validate._mechanical_tool_set
    policy_validate._mechanical_tool_set = lambda: registry
    try:
        yield
    finally:
        policy_validate._mechanical_tool_set = original


def pinned_job(repo: str, snapshot_hash: str) -> Job:
    return Job(
        id="job-1",
        repo=repo,
        number=7,
        head_sha="a" * 40,
        base_sha="b" * 40,
        head_repo=repo,
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=snapshot_hash,
        status=JobStatus.QUEUED,
    )


class CountingStore(SqliteSnapshotStore):
    """Counts row insertions, and can fail the first one to simulate a crash
    between §5's step 2 (archive written) and step 3 (row inserted)."""

    def __init__(self, state_dir, *, fail_first_insert: bool = False):
        super().__init__(state_dir)
        self.inserts = 0
        self.fail_first_insert = fail_first_insert

    def _insert_row(self, **kwargs) -> None:
        if self.fail_first_insert:
            self.fail_first_insert = False
            raise RuntimeError("interrupted between archive and row")
        self.inserts += 1
        super()._insert_row(**kwargs)


@contextlib.contextmanager
def state_and_repo(config: dict | None = None):
    """A temporary state directory plus a repository carrying `.rqa/config.json`."""
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        repo = root / "repo"
        (repo / ".rqa").mkdir(parents=True)
        document = policy_validate.starter_config() if config is None else config
        (repo / ".rqa" / "config.json").write_text(json.dumps(document), encoding="utf-8")
        yield root / "state", str(repo), document


def rows(state_dir: pathlib.Path) -> list[tuple]:
    connection = sqlite3.connect(state_dir / "state.db")
    try:
        return list(
            connection.execute(
                "SELECT hash, repo, policy_version, protocol_hash, activated_at, path "
                "FROM snapshots ORDER BY hash"
            )
        )
    finally:
        connection.close()


def archives(state_dir: pathlib.Path) -> list[str]:
    directory = state_dir / ARCHIVE_DIR_NAME
    return sorted(path.name for path in directory.iterdir()) if directory.is_dir() else []


# -- the read protocol --------------------------------------------------------


def test_get_returns_none_when_no_row_exists() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = SqliteSnapshotStore(directory)
        assert store.get("a" * 64) is None


def test_activate_then_get_returns_the_stored_snapshot_with_a_placeholder_repo() -> None:
    with state_and_repo() as (state_dir, _repo, document):
        store = SqliteSnapshotStore(state_dir)
        moment = utcnow()
        stored = store.activate(digest_of(document), document, at=moment)
        assert isinstance(stored, StoredSnapshot)
        assert isinstance(stored.snapshot, Snapshot)
        assert stored.snapshot.repo == ""
        assert stored.activated_at == moment
        assert store.get(digest_of(document)) == stored


def test_get_raises_when_the_archived_bytes_no_longer_hash_to_their_own_name() -> None:
    with state_and_repo() as (state_dir, _repo, document):
        store = SqliteSnapshotStore(state_dir)
        digest = digest_of(document)
        store.activate(digest, document, at=utcnow())
        archive = state_dir / ARCHIVE_DIR_NAME / f"{digest}.json"
        archive.write_bytes(archive.read_bytes()[:-3])  # a truncated file
        raised = None
        try:
            store.get(digest)
        except SnapshotStoreCorrupted as exc:
            raised = exc
        assert isinstance(raised, SnapshotStoreCorrupted)
        assert "hashes to its own name" in str(raised) or "no longer hashes" in str(raised)


def test_get_raises_when_a_row_has_no_archive_at_all() -> None:
    with state_and_repo() as (state_dir, _repo, document):
        store = SqliteSnapshotStore(state_dir)
        digest = digest_of(document)
        store.activate(digest, document, at=utcnow())
        (state_dir / ARCHIVE_DIR_NAME / f"{digest}.json").unlink()
        raised = None
        try:
            store.get(digest)
        except SnapshotStoreCorrupted as exc:
            raised = exc
        assert isinstance(raised, SnapshotStoreCorrupted)


def test_the_archive_holds_exactly_the_canonical_bytes_the_digest_covers() -> None:
    with state_and_repo() as (state_dir, _repo, document):
        store = SqliteSnapshotStore(state_dir)
        digest = digest_of(document)
        store.activate(digest, document, at=utcnow())
        body = (state_dir / ARCHIVE_DIR_NAME / f"{digest}.json").read_bytes()
    assert body == canonical_bytes(document)
    assert hashlib.sha256(body).hexdigest() == digest


def test_the_row_records_the_documented_columns() -> None:
    document = policy_validate.starter_config()
    document["policy"]["version"] = "2026-09-01"
    with state_and_repo(document) as (state_dir, _repo, _document):
        store = SqliteSnapshotStore(state_dir)
        digest = digest_of(document)
        moment = utcnow()
        stored = store.activate(digest, document, at=moment)
        (row,) = rows(state_dir)
    assert row[0] == digest
    assert row[2] == "2026-09-01"
    assert row[3] == stored.snapshot.protocol_hash
    assert row[4] == moment.isoformat()
    assert row[5] == f"{ARCHIVE_DIR_NAME}/{digest}.json"


# -- T13: interrupted between archive and row ---------------------------------


def test_t13_an_interrupted_activation_leaves_a_complete_correct_archive() -> None:
    with state_and_repo() as (state_dir, repo, document):
        store = CountingStore(state_dir, fail_first_insert=True)
        digest = digest_of(document)
        raised = None
        try:
            snapshot_for(repo=repo, job=None, store=store, record=None)
        except RuntimeError as exc:
            raised = exc
        assert raised is not None
        # Step 2 ran: the archive is present, complete and correctly hashed.
        assert archives(state_dir) == [f"{digest}.json"]
        body = (state_dir / ARCHIVE_DIR_NAME / f"{digest}.json").read_bytes()
        assert hashlib.sha256(body).hexdigest() == digest
        # Step 3 did not: there is no row yet, so `get` reports nothing stored.
        assert rows(state_dir) == []
        assert store.get(digest) is None

        # The retry reaches the same hash and completes activation.
        snapshot = snapshot_for(repo=repo, job=None, store=store, record=None)
        assert isinstance(snapshot, Snapshot)
        assert snapshot.hash == digest
        assert store.inserts == 1
        assert len(rows(state_dir)) == 1
        assert archives(state_dir) == [f"{digest}.json"]
        # No temp file is left behind by either attempt.
        assert not list((state_dir / ARCHIVE_DIR_NAME).glob("*.tmp"))


# -- T14: content addressing across repositories ------------------------------


def test_t14_byte_identical_configs_in_two_repositories_share_one_row() -> None:
    document = policy_validate.starter_config()
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        state_dir = root / "state"
        store = CountingStore(state_dir)
        repos = []
        for name in ("first", "second"):
            repo = root / name
            (repo / ".rqa").mkdir(parents=True)
            (repo / ".rqa" / "config.json").write_text(json.dumps(document), encoding="utf-8")
            repos.append(str(repo))
        one = snapshot_for(repo=repos[0], job=None, store=store, record=None)
        two = snapshot_for(repo=repos[1], job=None, store=store, record=None)
        assert one.hash == two.hash
        assert store.inserts == 1
        assert len(rows(state_dir)) == 1
        assert archives(state_dir) == [f"{one.hash}.json"]
        # Each caller still gets its own repository on the snapshot it was handed.
        assert one.repo == repos[0]
        assert two.repo == repos[1]


def test_key_order_in_the_source_file_does_not_change_the_hash() -> None:
    document = policy_validate.starter_config()
    reordered = dict(reversed(list(document.items())))
    assert list(reordered) != list(document)
    assert digest_of(reordered) == digest_of(document)


# -- last-known-good retention ------------------------------------------------


def test_activating_a_different_hash_leaves_the_earlier_one_byte_for_byte() -> None:
    first = policy_validate.starter_config()
    second = policy_validate.starter_config()
    second["authority"]["review"] = True
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory) / "state"
        store = SqliteSnapshotStore(state_dir)
        store.activate(digest_of(first), first, at=utcnow())
        original = (state_dir / ARCHIVE_DIR_NAME / f"{digest_of(first)}.json").read_bytes()
        store.activate(digest_of(second), second, at=utcnow())
        assert (
            state_dir / ARCHIVE_DIR_NAME / f"{digest_of(first)}.json"
        ).read_bytes() == original
        assert store.get(digest_of(first)) is not None
        assert sorted(archives(state_dir)) == sorted(
            [f"{digest_of(first)}.json", f"{digest_of(second)}.json"]
        )
        assert len(rows(state_dir)) == 2


def test_re_activating_the_same_hash_returns_the_first_activation_time() -> None:
    document = policy_validate.starter_config()
    with tempfile.TemporaryDirectory() as directory:
        store = CountingStore(pathlib.Path(directory) / "state")
        first_moment = utcnow()
        first = store.activate(digest_of(document), document, at=first_moment)
        later = store.activate(digest_of(document), document, at=utcnow())
    assert later.activated_at == first_moment
    assert later == first
    assert store.inserts == 1


def test_activate_refuses_to_archive_bytes_under_a_hash_they_do_not_produce() -> None:
    document = policy_validate.starter_config()
    with tempfile.TemporaryDirectory() as directory:
        store = SqliteSnapshotStore(pathlib.Path(directory) / "state")
        raised = None
        try:
            store.activate("c" * 64, document, at=utcnow())
        except SnapshotStoreCorrupted as exc:
            raised = exc
    assert isinstance(raised, SnapshotStoreCorrupted)


def test_the_concrete_store_satisfies_the_protocol_signatures_verbatim() -> None:
    import inspect

    for name in ("get", "activate"):
        expected = inspect.signature(getattr(SnapshotStore, name))
        actual = inspect.signature(getattr(SqliteSnapshotStore, name))
        assert list(actual.parameters) == list(expected.parameters), name
        assert [
            parameter.kind for parameter in actual.parameters.values()
        ] == [parameter.kind for parameter in expected.parameters.values()], name


# -- M3 (ruling 2026-09-11, "pinned reads never fail") ------------------------


def test_a_pinned_read_succeeds_after_a_pinned_tool_leaves_the_registry() -> None:
    """A pin that succeeded must not start failing because P-10's registry changed.

    The registry is resolved per call and each `rqa tick` is a fresh process (E-21),
    so membership genuinely can differ between the process that pinned a snapshot and
    one that later reads it. `get()` re-hashes the archived bytes — proof they are the
    bytes that passed membership at pin time — and does not re-test membership.
    """
    config = policy_validate.starter_config()
    config["policy"]["mechanical"]["tools"] = ["ruff"]
    with state_and_repo(config) as (state_dir, repo, document):
        store = SqliteSnapshotStore(state_dir)
        with tool_set({"ruff": object()}):
            pinned = snapshot_for(repo=repo, job=None, store=store, record=None)
        assert isinstance(pinned, Snapshot)
        assert pinned.policy.mechanical.tools == frozenset({"ruff"})

        with tool_set({}):  # `ruff` has since left the registry
            stored = store.get(pinned.hash)
            assert stored is not None
            assert stored.snapshot.policy.mechanical.tools == frozenset({"ruff"})
            assert stored.snapshot.hash == pinned.hash
            # And through §3 branch 1, the path a pinned job actually takes.
            through_branch_one = snapshot_for(
                repo=repo, job=pinned_job(repo, pinned.hash), store=store, record=None
            )
            assert isinstance(through_branch_one, Snapshot)
            assert through_branch_one.hash == pinned.hash
            assert through_branch_one.policy.mechanical.tools == frozenset({"ruff"})

            # Non-vacuity: under the identical registry state a *live* read is still
            # fail-closed, so the pinned read above is not passing because the
            # substitution failed to take effect.
            live = snapshot_for(repo=repo, job=None, store=store, record=None)
            assert isinstance(live, ValidationFailure)
            assert [error.code.value for error in live.errors] == ["tool_not_in_set"]


def test_a_pinned_read_still_re_hashes_the_bytes_it_trusts() -> None:
    """The integrity gate is why skipping membership is safe; it is not weakened."""
    config = policy_validate.starter_config()
    config["policy"]["mechanical"]["tools"] = ["ruff"]
    with state_and_repo(config) as (state_dir, repo, _document):
        store = SqliteSnapshotStore(state_dir)
        with tool_set({"ruff": object()}):
            pinned = snapshot_for(repo=repo, job=None, store=store, record=None)
        archive = state_dir / ARCHIVE_DIR_NAME / f"{pinned.hash}.json"
        tampered = json.loads(archive.read_bytes().decode("utf-8"))
        tampered["authority"]["merge"] = True  # a widening edit to the archive
        archive.write_bytes(canonical_bytes(tampered))
        raised = None
        try:
            store.get(pinned.hash)
        except SnapshotStoreCorrupted as exc:
            raised = exc
    assert isinstance(raised, SnapshotStoreCorrupted)


def test_archived_bytes_that_are_not_a_config_are_corruption_not_a_policy_error() -> None:
    """§5 names exactly one failure for a stored read. A trusted-archive rebuild that
    cannot produce a Snapshot is that failure, never a third outcome."""
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory) / "state"
        store = SqliteSnapshotStore(state_dir)
        document = policy_validate.starter_config()
        digest = digest_of(document)
        store.activate(digest, document, at=utcnow())
        # Replace the archive with bytes that hash to their own name but are not a
        # config, and repoint the row at them.
        rubbish = b'{"authority":{}}'
        rubbish_digest = hashlib.sha256(rubbish).hexdigest()
        (state_dir / ARCHIVE_DIR_NAME / f"{rubbish_digest}.json").write_bytes(rubbish)
        connection = sqlite3.connect(state_dir / "state.db")
        try:
            with connection:
                connection.execute(
                    "UPDATE snapshots SET hash = ?, path = ? WHERE hash = ?",
                    (rubbish_digest, f"{ARCHIVE_DIR_NAME}/{rubbish_digest}.json", digest),
                )
        finally:
            connection.close()
        raised = None
        try:
            store.get(rubbish_digest)
        except SnapshotStoreCorrupted as exc:
            raised = exc
    assert isinstance(raised, SnapshotStoreCorrupted)


# -- G2201R2-01: the write path keeps its own registry check -------------------


def tooled_config(tool_id: str) -> dict:
    config = policy_validate.starter_config()
    config["policy"]["mechanical"]["tools"] = [tool_id]
    return config


def test_activate_alone_refuses_a_tool_id_outside_the_registry() -> None:
    """`activate()` validates in full itself and does not trust its caller.

    `snapshot_for` always validates at §3 step 3 before calling `activate` at step 5,
    so this is redundant on the documented E-03 path — deliberately, per §4's
    three-sided membership check: a store that archived a tool id on its caller's word
    would be a fourth site relying on someone else having looked. Nothing may be
    written before that check, or the store would serve an under-checked snapshot on
    that hash forever.
    """
    config = tooled_config("not-registered")
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory) / "state"
        store = SqliteSnapshotStore(state_dir)
        digest = digest_of(config)
        raised = None
        with tool_set({}):
            try:
                store.activate(digest, config, at=utcnow())
            except PolicyError as exc:
                raised = exc
        assert isinstance(raised, PolicyError)
        assert "tool_not_in_set" in str(raised)
        # Refused before any write: no archive, no row, nothing to serve later.
        assert archives(state_dir) == []
        assert rows(state_dir) == []
        assert store.get(digest) is None


def test_activate_accepts_the_same_config_once_the_tool_is_in_the_registry() -> None:
    """Non-vacuity for the test above: the refusal is the registry's doing, not a
    config this store would reject whatever the registry said."""
    config = tooled_config("ruff")
    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory) / "state"
        store = SqliteSnapshotStore(state_dir)
        digest = digest_of(config)
        with tool_set({"ruff": object()}):
            stored = store.activate(digest, config, at=utcnow())
        assert stored.snapshot.policy.mechanical.tools == frozenset({"ruff"})
        assert archives(state_dir) == [f"{digest}.json"]
        assert len(rows(state_dir)) == 1


def test_the_read_path_is_relaxed_and_the_write_path_is_not_under_one_registry() -> None:
    """The pair that stops the trusted-archive flag leaking across the boundary.

    One config, one registry state, two stores: the one that pinned it while `ruff`
    was registered still serves it (M3), and a store being asked to archive the same
    config for the first time now refuses it (G2201R2-01).
    """
    config = tooled_config("ruff")
    digest = digest_of(config)
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        repo = root / "repo"
        (repo / ".rqa").mkdir(parents=True)
        (repo / ".rqa" / "config.json").write_text(json.dumps(config), encoding="utf-8")
        pinned_store = SqliteSnapshotStore(root / "pinned-state")
        with tool_set({"ruff": object()}):
            pinned = snapshot_for(repo=str(repo), job=None, store=pinned_store, record=None)
        assert isinstance(pinned, Snapshot)
        assert pinned.hash == digest

        fresh_store = SqliteSnapshotStore(root / "fresh-state")
        with tool_set({}):
            # Read path: the pin holds, through `get` and through §3 branch 1.
            stored = pinned_store.get(digest)
            assert stored is not None
            assert stored.snapshot.policy.mechanical.tools == frozenset({"ruff"})
            assert isinstance(
                snapshot_for(
                    repo=str(repo),
                    job=pinned_job(str(repo), digest),
                    store=pinned_store,
                    record=None,
                ),
                Snapshot,
            )
            # Write path: the identical config, first activation, is refused.
            raised = None
            try:
                fresh_store.activate(digest, config, at=utcnow())
            except PolicyError as exc:
                raised = exc
            # A live read through E-03 is refused too, as it was at round 2.
            live = snapshot_for(repo=str(repo), job=None, store=fresh_store, record=None)
        assert isinstance(raised, PolicyError)
        assert archives(root / "fresh-state") == []
        assert rows(root / "fresh-state") == []
        assert isinstance(live, ValidationFailure)
        assert [error.code.value for error in live.errors] == ["tool_not_in_set"]


def test_re_activating_an_archived_hash_still_short_circuits_to_the_read_path() -> None:
    """§5 step 1 is a read, so it is entitled to M3's relaxation: an already-archived
    hash is returned unchanged without re-validating, whatever the registry now says.
    That is the pin holding, not the write path's check being skipped."""
    config = tooled_config("ruff")
    digest = digest_of(config)
    with tempfile.TemporaryDirectory() as directory:
        store = SqliteSnapshotStore(pathlib.Path(directory) / "state")
        with tool_set({"ruff": object()}):
            first = store.activate(digest, config, at=utcnow())
        with tool_set({}):
            again = store.activate(digest, config, at=utcnow())
    assert again == first
