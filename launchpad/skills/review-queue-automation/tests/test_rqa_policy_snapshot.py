#!/usr/bin/env python3
"""`snapshot_for` (E-03) — `code/P-03-policy.md` §8 rows T7-T12 and T15-T17.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Each test uses a fake `SnapshotStore` and a fake `RecordWriter` over a real
filesystem fixture for `.rqa/config.json`, which is what §8 asks for. The fake store
is deliberately a *different* implementation from `rqa.policy.store`: these tests
prove `snapshot_for`'s branches, and `test_rqa_policy_store.py` proves the real
store's activation protocol.

The record fake asserts its `kind` is a member of `ENTRY_KINDS` on every call, so a
payload written under a kind outside `CONTRACTS.md` §7's one closed set fails here
rather than reaching a real record (RQA-FR-012).
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.policy.validate as policy_validate  # noqa: E402
from rqa.contracts import (  # noqa: E402
    ENTRY_KINDS,
    AppendFailed,
    Category,
    Entry,
    Job,
    JobStatus,
    Route,
    Snapshot,
    ValidationErrorCode,
    ValidationFailure,
)
from rqa.policy import PolicyError, SnapshotStoreCorrupted, snapshot_for  # noqa: E402
from rqa.policy.snapshot import digest_of, snapshot_from_verified_archive  # noqa: E402
from rqa.policy.store import StoredSnapshot  # noqa: E402
from rqa.policy.types import utcnow  # noqa: E402
from rqa.protocol import protocol_hash  # noqa: E402

# -- fakes --------------------------------------------------------------------


class FakeStore:
    """An in-memory `SnapshotStore`: content-addressed, append-only, idempotent."""

    def __init__(self) -> None:
        self.archived: dict[str, tuple[dict, object]] = {}
        self.activations = 0
        self.missing: set[str] = set()

    def get(self, hash: str) -> StoredSnapshot | None:
        if hash in self.missing:
            return None
        entry = self.archived.get(hash)
        if entry is None:
            return None
        raw, at = entry
        return StoredSnapshot(
            snapshot=snapshot_from_verified_archive(
                raw=raw, digest=hash, repo="", protocol=protocol_hash()
            ),
            activated_at=at,
        )

    def activate(self, hash: str, raw, at) -> StoredSnapshot:
        existing = self.get(hash)
        if existing is not None:
            return existing
        self.activations += 1
        self.archived[hash] = (json.loads(json.dumps(raw)), at)
        stored = self.get(hash)
        assert stored is not None
        return stored


class FakeRecord:
    def __init__(self) -> None:
        self.appended: list[tuple[str, str, dict]] = []

    def append(self, job_id: str, kind: str, payload) -> Entry:
        assert kind in ENTRY_KINDS, f"{kind!r} is outside the closed ENTRY_KINDS set"
        self.appended.append((job_id, kind, dict(payload)))
        return Entry(seq=len(self.appended), hash="0" * 64)


class FailingRecord(FakeRecord):
    def append(self, job_id: str, kind: str, payload) -> Entry:
        raise AppendFailed("the record could not be appended")


# -- fixtures without fixtures ------------------------------------------------


@contextlib.contextmanager
def repository(config: dict | None = None, *, text: str | None = None):
    """A temporary repository root carrying `.rqa/config.json`."""
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory) / "repo"
        (root / ".rqa").mkdir(parents=True)
        if text is None:
            text = json.dumps(policy_validate.starter_config() if config is None else config)
        (root / ".rqa" / "config.json").write_text(text, encoding="utf-8")
        yield str(root)


def write_config(repo: str, config: dict) -> None:
    pathlib.Path(repo, ".rqa", "config.json").write_text(json.dumps(config), encoding="utf-8")


def job(repo: str, *, snapshot_hash: str | None = None) -> Job:
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


def full_config() -> dict:
    """A config exercising every shared boundary: routes with all five `Route`
    fields, mechanical categories including `MECHANICAL`, an obligation, a budget."""
    config = policy_validate.starter_config()
    config["routes"] = [
        {
            "harness": "claude",
            "model": "opus",
            "provider": "anthropic",
            "family": "claude",
            "external": True,
        },
        {
            "harness": "codex",
            "model": "gpt",
            "provider": "openai",
            "family": "gpt",
            "external": True,
        },
    ]
    config["policy"]["version"] = "2026-09-01"
    config["policy"]["mechanical"]["categories"] = ["mechanical", "procedural"]
    config["policy"]["blocking"]["categories"] = ["security"]
    config["policy"]["blocking"]["severities"] = ["high"]
    config["policy"]["assurance"] = {"high": 2}
    config["budget"]["per_pr_tokens"] = 100_000
    return config


# -- T7, T8: the shared Snapshot tree, per repository -------------------------


def test_t7_the_returned_snapshot_is_the_contracts_shared_tree() -> None:
    with repository(full_config()) as repo:
        snapshot = snapshot_for(repo=repo, job=None, store=FakeStore(), record=None)
    assert isinstance(snapshot, Snapshot)
    assert isinstance(snapshot.routes, tuple)
    assert all(isinstance(route, Route) for route in snapshot.routes)
    assert snapshot.routes[0].family == "claude"
    assert isinstance(snapshot.policy.mechanical.categories, frozenset)
    assert snapshot.policy.mechanical.categories == frozenset(
        {Category.MECHANICAL, Category.PROCEDURAL}
    )
    assert snapshot.protocol_hash == protocol_hash()
    assert snapshot.repo == repo


def test_t7_the_six_activities_are_carried_independently_per_repository() -> None:
    config = full_config()
    config["authority"]["review"] = True
    config["authority"]["merge"] = True
    with repository(config) as repo:
        snapshot = snapshot_for(repo=repo, job=None, store=FakeStore(), record=None)
    from rqa.contracts import Activity

    assert snapshot.authority[Activity.REVIEW] is True
    assert snapshot.authority[Activity.MERGE] is True
    assert snapshot.authority[Activity.APPROVE] is False


def test_t8_two_repositories_external_permission_never_leaks_in_one_process() -> None:
    permitting = full_config()
    permitting["external"]["allowed"] = True
    permitting["external"]["deny_label"] = "no-external"
    forbidding = full_config()
    forbidding["external"]["allowed"] = False
    store = FakeStore()
    with repository(permitting) as allowed_repo, repository(forbidding) as denied_repo:
        allowed = snapshot_for(repo=allowed_repo, job=None, store=store, record=None)
        denied = snapshot_for(repo=denied_repo, job=None, store=store, record=None)
        # Interleave, so a process-wide flag would be caught rather than masked by
        # ordering: read the first repository again after the second.
        allowed_again = snapshot_for(repo=allowed_repo, job=None, store=store, record=None)
    assert allowed.external.allowed is True
    assert denied.external.allowed is False
    assert allowed_again.external.allowed is True
    assert allowed.hash != denied.hash


# -- T9, T10: a live read on every call ---------------------------------------


def test_t9_two_calls_with_no_edit_return_the_identical_snapshot_and_hash() -> None:
    store = FakeStore()
    with repository(full_config()) as repo:
        first = snapshot_for(repo=repo, job=None, store=store, record=None)
        second = snapshot_for(repo=repo, job=None, store=store, record=None)
    assert first == second
    assert first.hash == second.hash
    assert store.activations == 1


def test_t10_an_edit_between_calls_is_visible_to_the_next_call() -> None:
    store = FakeStore()
    edited = full_config()
    edited["authority"]["review"] = True
    with repository(full_config()) as repo:
        before = snapshot_for(repo=repo, job=None, store=store, record=None)
        write_config(repo, edited)
        after = snapshot_for(repo=repo, job=None, store=store, record=None)
    from rqa.contracts import Activity

    assert before.hash != after.hash
    assert before.authority[Activity.REVIEW] is False
    assert after.authority[Activity.REVIEW] is True
    assert store.activations == 2


def test_an_unreadable_config_is_an_unreadable_failure_with_nothing_written() -> None:
    store = FakeStore()
    record = FakeRecord()
    with tempfile.TemporaryDirectory() as directory:
        outcome = snapshot_for(repo=directory, job=None, store=store, record=record)
    assert isinstance(outcome, ValidationFailure)
    assert [error.code for error in outcome.errors] == [ValidationErrorCode.UNREADABLE]
    assert outcome.repo == directory
    assert store.activations == 0
    assert record.appended == []


def test_a_config_that_is_not_json_is_unreadable_not_a_crash() -> None:
    store = FakeStore()
    with repository(text="{not json") as repo:
        outcome = snapshot_for(repo=repo, job=None, store=store, record=None)
    assert isinstance(outcome, ValidationFailure)
    assert [error.code for error in outcome.errors] == [ValidationErrorCode.UNREADABLE]
    assert store.activations == 0


def test_an_invalid_config_is_refused_and_never_served_a_previous_snapshot() -> None:
    """§7: an invalid config is a ValidationFailure, never the last-known-good."""
    store = FakeStore()
    invalid = full_config()
    invalid["webhooks"] = {}
    with repository(full_config()) as repo:
        good = snapshot_for(repo=repo, job=None, store=store, record=None)
        assert isinstance(good, Snapshot)
        write_config(repo, invalid)
        outcome = snapshot_for(repo=repo, job=None, store=store, record=None)
    assert isinstance(outcome, ValidationFailure)
    assert [error.code for error in outcome.errors] == [ValidationErrorCode.UNKNOWN_KEY]
    # The earlier snapshot is still readable, but it was not returned.
    assert store.get(good.hash) is not None
    assert store.activations == 1


# -- T11, T12, T16: the pin ---------------------------------------------------


def test_t11_a_pinned_job_keeps_its_snapshot_across_a_config_edit() -> None:
    store = FakeStore()
    record = FakeRecord()
    edited = full_config()
    edited["authority"]["merge"] = True
    with repository(full_config()) as repo:
        first = snapshot_for(repo=repo, job=job(repo), store=store, record=record)
        assert isinstance(first, Snapshot)
        pinned = job(repo, snapshot_hash=first.hash)
        write_config(repo, edited)
        second = snapshot_for(repo=repo, job=pinned, store=store, record=record)
        live = snapshot_for(repo=repo, job=None, store=store, record=record)
    assert second == first
    assert second.hash == first.hash
    # A live read right now genuinely differs — that is what the pin is holding off.
    assert live.hash != first.hash


def test_t11_the_pinned_branch_does_not_read_the_file_at_all() -> None:
    store = FakeStore()
    record = FakeRecord()
    with repository(full_config()) as repo:
        first = snapshot_for(repo=repo, job=job(repo), store=store, record=record)
        pinned = job(repo, snapshot_hash=first.hash)
        # Delete the config outright: a branch that read it would fail here.
        pathlib.Path(repo, ".rqa", "config.json").unlink()
        second = snapshot_for(repo=repo, job=pinned, store=store, record=record)
    assert second.hash == first.hash


def test_t12_a_pin_the_store_cannot_produce_raises_snapshot_store_corrupted() -> None:
    store = FakeStore()
    absent = "f" * 64
    store.missing.add(absent)
    with repository(full_config()) as repo:
        pinned = job(repo, snapshot_hash=absent)
        try:
            snapshot_for(repo=repo, job=pinned, store=store, record=FakeRecord())
        except SnapshotStoreCorrupted as exc:
            assert absent in str(exc)
        else:  # pragma: no cover - the assertion below reports the defect
            raise AssertionError("a missing pin must not return a value")


def test_t12_a_missing_pin_is_never_a_validation_failure_or_a_fresh_read() -> None:
    store = FakeStore()
    with repository(full_config()) as repo:
        pinned = job(repo, snapshot_hash="e" * 64)
        raised = None
        try:
            snapshot_for(repo=repo, job=pinned, store=store, record=FakeRecord())
        except SnapshotStoreCorrupted as exc:
            raised = exc
    assert isinstance(raised, SnapshotStoreCorrupted)
    assert isinstance(raised, PolicyError)
    assert store.activations == 0


def test_t16_an_already_pinned_job_appends_no_further_record_entry() -> None:
    store = FakeStore()
    record = FakeRecord()
    with repository(full_config()) as repo:
        first = snapshot_for(repo=repo, job=job(repo), store=store, record=record)
        pinned = job(repo, snapshot_hash=first.hash)
        snapshot_for(repo=repo, job=pinned, store=store, record=record)
        snapshot_for(repo=repo, job=pinned, store=store, record=record)
    assert len(record.appended) == 1


# -- T15, T17: the record is not optional on a first pin ----------------------


def test_the_first_pin_appends_one_snapshot_entry_with_the_documented_payload() -> None:
    store = FakeStore()
    record = FakeRecord()
    with repository(full_config()) as repo:
        snapshot = snapshot_for(repo=repo, job=job(repo), store=store, record=record)
    assert len(record.appended) == 1
    job_id, kind, payload = record.appended[0]
    assert job_id == "job-1"
    assert kind == "snapshot"
    assert kind in ENTRY_KINDS
    assert set(payload) == {"hash", "repo", "policy_version", "protocol_hash", "activated_at"}
    assert payload["hash"] == snapshot.hash
    assert payload["repo"] == repo
    assert payload["policy_version"] == "2026-09-01"
    assert payload["protocol_hash"] == snapshot.protocol_hash
    # The recorded snapshot is the one that was returned, for the job it pinned.
    stored = store.get(payload["hash"])
    assert stored is not None
    assert payload["activated_at"] == stored.activated_at.isoformat()


def test_an_admission_time_call_records_nothing(  # T7 step 7
) -> None:
    store = FakeStore()
    record = FakeRecord()
    with repository(full_config()) as repo:
        snapshot_for(repo=repo, job=None, store=store, record=record)
    assert record.appended == []


def test_t15_append_failed_propagates_and_no_snapshot_is_returned() -> None:
    store = FakeStore()
    record = FailingRecord()
    with repository(full_config()) as repo:
        raw = json.loads(pathlib.Path(repo, ".rqa", "config.json").read_text(encoding="utf-8"))
        raised = None
        try:
            snapshot_for(repo=repo, job=job(repo), store=store, record=record)
        except AppendFailed as exc:
            raised = exc
    assert isinstance(raised, AppendFailed)
    # The store was activated first — idempotent and harmless — but no entry exists.
    assert store.activations == 1
    assert store.get(digest_of(raw)) is not None
    assert record.appended == []


def test_t17_a_first_pin_without_a_record_writer_raises_policy_error() -> None:
    store = FakeStore()
    with repository(full_config()) as repo:
        raised = None
        try:
            snapshot_for(repo=repo, job=job(repo), store=store, record=None)
        except PolicyError as exc:
            raised = exc
    assert isinstance(raised, PolicyError)
    assert "RecordWriter" in str(raised)


def test_t17_no_unrecorded_job_snapshot_is_returned_even_when_the_config_is_valid() -> None:
    store = FakeStore()
    with repository(full_config()) as repo:
        outcome = None
        try:
            outcome = snapshot_for(repo=repo, job=job(repo), store=store, record=None)
        except PolicyError:
            pass
    assert outcome is None


def test_snapshot_for_is_the_edge_signature_character_for_character() -> None:
    """The seam rule: E-03's signature is `rqa.edges`' to declare and P-03's to
    implement, never to restate differently. Annotations are strings under
    `from __future__ import annotations`, so this compares the declared text too."""
    import inspect

    import rqa.edges as edges

    assert inspect.signature(snapshot_for) == inspect.signature(edges.snapshot_for)


# -- the hash covers the whole config, not just `policy` ----------------------


def test_the_hash_changes_when_a_non_policy_section_changes() -> None:
    store = FakeStore()
    with repository(full_config()) as repo:
        before = snapshot_for(repo=repo, job=None, store=store, record=None)
        edited = full_config()
        edited["budget"]["per_pr_tokens"] = 99
        write_config(repo, edited)
        after = snapshot_for(repo=repo, job=None, store=store, record=None)
    assert before.policy == after.policy
    assert before.hash != after.hash


def test_the_hash_is_sha256_over_the_canonical_whole_config() -> None:
    config = full_config()
    with repository(config) as repo:
        snapshot = snapshot_for(repo=repo, job=None, store=FakeStore(), record=None)
    assert snapshot.hash == digest_of(config)


def test_a_returned_snapshot_is_not_mutable_through_its_authority_mapping() -> None:
    with repository(full_config()) as repo:
        snapshot = snapshot_for(repo=repo, job=None, store=FakeStore(), record=None)
    from rqa.contracts import Activity

    try:
        snapshot.authority[Activity.MERGE] = True  # type: ignore[index]
    except TypeError:
        return
    raise AssertionError("a pinned snapshot's authority must not be writable")


def test_the_config_path_is_recomputed_from_repo_on_every_call() -> None:
    from rqa.policy.snapshot import config_path

    assert config_path("/tmp/one") != config_path("/tmp/two")
    assert config_path("/tmp/one").as_posix().endswith(".rqa/config.json")


def test_snapshot_for_is_keyword_only_exactly_as_the_edge_declares_it() -> None:
    import inspect

    parameters = inspect.signature(snapshot_for).parameters
    assert list(parameters) == ["repo", "job", "store", "record"]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values()
    )


def test_a_pinned_snapshot_is_returned_with_the_callers_repo_not_the_placeholder() -> None:
    store = FakeStore()
    record = FakeRecord()
    with repository(full_config()) as repo:
        first = snapshot_for(repo=repo, job=job(repo), store=store, record=record)
        stored = store.get(first.hash)
        assert stored is not None
        assert stored.snapshot.repo == ""
        pinned = snapshot_for(
            repo=repo, job=dataclasses.replace(job(repo), snapshot_hash=first.hash),
            store=store, record=record,
        )
    assert pinned.repo == repo
    assert pinned == dataclasses.replace(stored.snapshot, repo=repo)


def test_utcnow_is_timezone_aware_so_an_activation_time_round_trips() -> None:
    moment = utcnow()
    assert moment.tzinfo is not None
    assert moment.utcoffset().total_seconds() == 0
