#!/usr/bin/env python3
"""`verify` — `code/P-12-record.md` §3.2 and §8 rows T1, T2, T3, T12, T16 and T9's
verify half.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Each test writes a real chain through `append`, then edits the stored rows with direct
SQL the way an actor with database access would, and asks `verify` what it makes of the
result. The key is a fake `KeyStore`'s bytes, chosen here; no real OS keychain is
touched (§8).

**What `verify` claims.** It detects an altered row, a re-parented row, and a keyed row
that no longer authenticates. It does **not** detect a removed tail — the walk starts at
the first row and stops at the first row it stops trusting, so a shortened but
internally consistent chain verifies. `test_a_removed_tail_is_not_detected_and_the_claim_is_not_made`
pins that limit deliberately (issue #2220): `bad_seq` is the first seq verification
stopped trusting, never proof that rows were removed.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.record import BreakKind, verify  # noqa: E402
from rqa.record.hashing import LEGACY_PREV_HASH, compute_hash, compute_hmac  # noqa: E402
from rqa.record.keychain import KeyStoreExplanationUnavailable  # noqa: E402
from rqa.record.store import StoredEntry, insert_entry  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

KEY = b"a-test-key-that-never-leaves-this-process"


class FakeKeyStore:
    """§8's fake `KeyStore`. No real keychain, no subprocess, no key on this machine."""

    def __init__(self, *, key: bytes | None = KEY, error: BaseException | None = None):
        self.key = key
        self.error = error
        self.reads = 0

    def read(self, name: str) -> bytes | None:
        self.reads += 1
        if self.error is not None:
            raise self.error
        return self.key


def chained(job: str = "job-1", *, entries: int = 3, keystore: FakeKeyStore | None = None):
    """A real job with `entries` chained rows, written through `append`."""
    keystore = keystore or FakeKeyStore()
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, keystore=keystore)
    for index in range(entries):
        writer.append(job, "transition", {"to_state": f"state-{index}", "step": index})
    return connection, keystore


def row(connection: sqlite3.Connection, job: str, seq: int) -> tuple:
    return tuple(
        connection.execute(
            "SELECT kind, at, payload, prev_hash, hash, hmac, keyed FROM record_entries "
            "WHERE job = ? AND seq = ?",
            (job, seq),
        ).fetchone()
    )


def rewrite(connection: sqlite3.Connection, job: str, seq: int, **columns) -> None:
    assignments = ", ".join(f"{name} = ?" for name in columns)
    connection.execute(
        f"UPDATE record_entries SET {assignments} WHERE job = ? AND seq = ?",
        (*columns.values(), job, seq),
    )


# -- §3.2 step 1: nothing to verify -------------------------------------------


def test_t12_a_job_with_no_rows_verifies_vacuously() -> None:
    """T12: `verify` on a job with zero rows → `ok=True, bad_seq=None,
    hmac_checked=False, checked_through_seq=0`."""
    connection, keystore = chained("job-1", entries=1)
    result = verify(connection, "job-with-nothing-in-it", keystore=keystore)
    assert (result.ok, result.bad_seq, result.kind) == (True, None, None)
    assert result.hmac_checked is False
    assert result.checked_through_seq == 0
    assert result.unverifiable == ()
    assert result.job_id == "job-with-nothing-in-it"


def test_an_intact_chain_verifies_and_reports_how_far_it_got() -> None:
    connection, keystore = chained(entries=3)
    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is True
    assert (result.bad_seq, result.kind) == (None, None)
    assert result.hmac_checked is True
    assert result.checked_through_seq == 3
    assert result.unverifiable == ()


# -- §3.2 step 2: the chain ----------------------------------------------------


def test_t1_an_edited_payload_with_its_old_hash_is_a_hash_mismatch() -> None:
    """T1: three chained entries for one job; row 2's stored `payload` edited in place,
    its `hash` left unchanged → `verify` returns `ok=False, bad_seq=2,
    kind=HASH_MISMATCH`."""
    connection, keystore = chained(entries=3)
    rewrite(connection, "job-1", 2, payload=json.dumps({"to_state": "approved", "step": 1}))

    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is False
    assert result.bad_seq == 2
    assert result.kind is BreakKind.HASH_MISMATCH
    assert result.checked_through_seq == 1, "row 1 was examined; row 2 stopped the walk"


def test_a_payload_that_no_longer_parses_is_a_hash_mismatch_not_an_exception() -> None:
    """§3.2: "never raises for an integrity outcome"."""
    connection, keystore = chained(entries=2)
    rewrite(connection, "job-1", 1, payload="{not json at all")
    result = verify(connection, "job-1", keystore=keystore)
    assert (result.ok, result.bad_seq, result.kind) == (False, 1, BreakKind.HASH_MISMATCH)


def test_t2_a_stale_parent_pointer_is_a_chain_break_at_the_child() -> None:
    """T2: three chained entries; row 2 replaced with a new payload and a freshly,
    correctly recomputed own `hash`, but row 3's `prev_hash` left pointing at row 2's
    *original* hash → `verify` returns `ok=False, bad_seq=3, kind=CHAIN_BREAK`."""
    connection, keystore = chained(entries=3)
    kind, at, _payload, prev_hash, _hash, _hmac, _keyed = row(connection, "job-1", 2)
    replacement = {"to_state": "approved", "step": 1}
    recomputed = compute_hash(
        job="job-1", seq=2, kind=kind, at=at, payload=replacement, prev_hash=prev_hash
    )
    rewrite(
        connection,
        "job-1",
        2,
        payload=json.dumps(replacement),
        hash=recomputed,
        hmac=compute_hmac(key=KEY, job="job-1", seq=2, hash=recomputed),
    )

    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is False
    assert result.bad_seq == 3
    assert result.kind is BreakKind.CHAIN_BREAK
    assert result.checked_through_seq == 2


def test_a_genesis_row_that_claims_a_parent_is_a_chain_break() -> None:
    """The first real row's parent is NULL; anything else is a row spliced in front."""
    connection, keystore = chained(entries=2)
    rewrite(connection, "job-1", 1, prev_hash="b" * 64)
    result = verify(connection, "job-1", keystore=keystore)
    assert (result.ok, result.bad_seq, result.kind) == (False, 1, BreakKind.CHAIN_BREAK)
    assert result.checked_through_seq == 0


# -- §3.2 step 3: the keyed bit ------------------------------------------------


def test_t3_an_internally_consistent_rewrite_of_the_head_fails_its_hmac() -> None:
    """T3: row 2 and every downstream hash are consistently recomputed after a rewrite,
    but the original keyed HMAC remains on the rewritten head row → `verify` returns
    `ok=False, bad_seq=<head seq>, kind=HMAC_MISMATCH, hmac_checked=True` — a keyed
    entry catches the internally consistent rewrite.

    Here the rewritten row *is* the head, so "every downstream hash" is vacuous and the
    chain is perfectly consistent: only the key catches it.
    """
    connection, keystore = chained(entries=3)
    kind, at, _payload, prev_hash, _hash, original_hmac, _keyed = row(connection, "job-1", 3)
    replacement = {"to_state": "merged", "step": 2}
    recomputed = compute_hash(
        job="job-1", seq=3, kind=kind, at=at, payload=replacement, prev_hash=prev_hash
    )
    rewrite(connection, "job-1", 3, payload=json.dumps(replacement), hash=recomputed)
    assert row(connection, "job-1", 3)[5] == original_hmac, "the old HMAC stays put"

    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is False
    assert result.bad_seq == 3
    assert result.kind is BreakKind.HMAC_MISMATCH
    assert result.hmac_checked is True, "rows 1 and 2 authenticated before the break"


def test_a_mid_chain_rewrite_with_every_downstream_hash_repaired_still_fails_its_hmac() -> None:
    """The same property where the rewrite is not at the head: an actor without the key
    can repair every hash in the chain and still cannot repair one HMAC."""
    connection, keystore = chained(entries=3)
    kind, at, _payload, prev_hash, _hash, _hmac, _keyed = row(connection, "job-1", 2)
    replacement = {"to_state": "approved", "step": 1}
    repaired_two = compute_hash(
        job="job-1", seq=2, kind=kind, at=at, payload=replacement, prev_hash=prev_hash
    )
    rewrite(connection, "job-1", 2, payload=json.dumps(replacement), hash=repaired_two)

    kind3, at3, payload3, _prev3, _hash3, _hmac3, _keyed3 = row(connection, "job-1", 3)
    repaired_three = compute_hash(
        job="job-1",
        seq=3,
        kind=kind3,
        at=at3,
        payload=json.loads(payload3),
        prev_hash=repaired_two,
    )
    rewrite(connection, "job-1", 3, prev_hash=repaired_two, hash=repaired_three)

    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is False
    assert result.bad_seq == 2, "the first row whose HMAC no longer authenticates"
    assert result.kind is BreakKind.HMAC_MISMATCH
    assert result.hmac_checked is True


def test_a_keyed_row_whose_hmac_is_missing_or_malformed_is_an_hmac_mismatch() -> None:
    """§3.2 step 3: "keyed=True, hmac missing or malformed → return HMAC_MISMATCH at
    that row" — a claim to be keyed that carries no usable HMAC is not an unverifiable
    segment, it is a broken row."""
    connection, keystore = chained(entries=2)
    # The store's CHECK forbids keyed=1 with a NULL hmac, so malformed is the reachable
    # shape of this branch: something that is not a SHA-256 hex digest.
    rewrite(connection, "job-1", 2, hmac="not-a-digest")
    result = verify(connection, "job-1", keystore=keystore)
    assert (result.ok, result.bad_seq, result.kind) == (False, 2, BreakKind.HMAC_MISMATCH)


def test_t16_unkeyed_rows_form_one_unverifiable_segment_closed_by_a_keyed_row() -> None:
    """T16 (verify half) and §3.1: "consecutive unkeyed rows form one segment and a
    later keyed row closes it"."""

    class KeyComesBack(FakeKeyStore):
        def read(self, name: str) -> bytes | None:
            self.reads += 1
            return None if self.reads in (2, 3) else KEY

    keystore = KeyComesBack()
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, keystore=keystore)
    for index in range(4):
        writer.append("job-1", "transition", {"step": index})

    result = verify(connection, "job-1", keystore=FakeKeyStore())
    assert result.ok is True, "an unkeyed run is not a break"
    assert result.kind is None and result.bad_seq is None
    assert [(s.first_seq, s.last_seq, s.reason) for s in result.unverifiable] == [
        (2, 3, "no key")
    ]
    assert result.unverifiable[0].job_id == "job-1"
    assert result.hmac_checked is True, "rows 1 and 4 were keyed and did authenticate"
    assert result.checked_through_seq == 4


def test_an_unavailable_key_store_makes_a_keyed_run_unverifiable_not_broken() -> None:
    """§3.2 step 3: "A `KeyStoreExplanationUnavailable` or platform/store read error does
    the same: verification remains readable and reports the run `unverifiable: no key`,
    rather than refusing the record." The same run in `append` would be `AppendFailed`;
    the two outcomes are deliberately not unified."""
    connection, _keystore = chained(entries=2)
    result = verify(
        connection,
        "job-1",
        keystore=FakeKeyStore(error=KeyStoreExplanationUnavailable("no keychain here")),
    )
    assert result.ok is True
    assert result.kind is None
    assert [(s.first_seq, s.last_seq, s.reason) for s in result.unverifiable] == [
        (1, 2, "no key")
    ]
    assert result.hmac_checked is False


def test_an_absent_key_makes_every_keyed_row_unverifiable_and_never_a_break() -> None:
    """ADR-0063, stated as a property rather than as a branch: with no key at all,
    nothing about this record is reported as tampering."""
    connection, _keystore = chained(entries=3)
    result = verify(connection, "job-1", keystore=FakeKeyStore(key=None))
    assert result.ok is True
    assert result.kind is None
    assert [(s.first_seq, s.last_seq) for s in result.unverifiable] == [(1, 3)]
    assert result.hmac_checked is False


# -- §3.2 step 4 and §6: migrated rows ----------------------------------------


def migrated_row(connection: sqlite3.Connection, job: str, seq: int, kind: str) -> None:
    payload = {"source_table": "ledger_entries", "source_pk": seq, "legacy_kind": "decision"}
    insert_entry(
        connection=connection,
        entry=StoredEntry(
            job=job,
            seq=seq,
            kind=kind,
            at="2025-03-04T05:06:07.000000+00:00",
            payload=json.dumps(payload),
            prev_hash=LEGACY_PREV_HASH,
            hash="d" * 64,
            hmac=None,
            keyed=False,
        ),
    )


def test_t9_a_job_of_only_migrated_rows_verifies_because_nothing_is_chained() -> None:
    """T9 (verify half): a job with only migrated rows (`legacy`, `decision`, `spend`,
    all `prev_hash="legacy"`), zero real chained entries → `verify` returns `ok=True`
    (nothing chained to break).

    T9's `explain_job` half — `legacy=True, verified=False` regardless — belongs to the
    sibling lane.
    """
    connection = sqlite3.connect(":memory:")
    SQLiteRecordWriter(connection, keystore=FakeKeyStore())
    for seq, kind in enumerate(("legacy", "decision", "spend"), start=1):
        migrated_row(connection, "job-legacy", seq, kind)

    result = verify(connection, "job-legacy", keystore=FakeKeyStore())
    assert result.ok is True
    assert (result.bad_seq, result.kind) == (None, None)
    assert result.hmac_checked is False
    assert result.checked_through_seq == 0, "no real row was examined"
    assert result.unverifiable == (), "a migrated row is not an unverifiable segment"


def test_migrated_rows_are_skipped_without_breaking_a_live_chain_around_them() -> None:
    """§6: a migrated row is "never examined by `verify`" — including when it sits in
    the middle of a job's sequence, where a naive walk would call it a chain break."""
    keystore = FakeKeyStore()
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, keystore=keystore)
    writer.append("job-1", "transition", {"step": 0})
    writer.append("job-1", "transition", {"step": 1})
    migrated_row(connection, "job-1", 3, "decision")

    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is True
    assert result.checked_through_seq == 2
    assert result.unverifiable == ()


def test_t18_a_keyed_row_a_migrated_row_and_an_unkeyed_row_verify_together() -> None:
    """T18 (verify half): a job with rows `[keyed real seq=1, legacy, unkeyed real
    seq=2 chained to seq=1]` → `verify` returns `ok=True` with the seq-2
    `unverifiable: no key` segment.

    T18's `explain_job` half — `legacy=True, verified=False`, reporting that segment
    without calling it broken — belongs to the sibling lane. The migrated row takes a
    sequence of its own because `(job, seq)` is unique; where it sorts changes nothing,
    since `verify` never examines it.
    """

    class KeyRunsOut(FakeKeyStore):
        def read(self, name: str) -> bytes | None:
            self.reads += 1
            return KEY if self.reads == 1 else None

    keystore = KeyRunsOut()
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection, keystore=keystore)
    writer.append("job-1", "transition", {"step": 0})
    writer.append("job-1", "transition", {"step": 1})
    migrated_row(connection, "job-1", 3, "legacy")

    stored = connection.execute(
        "SELECT seq, keyed, prev_hash FROM record_entries WHERE job = ? ORDER BY seq",
        ("job-1",),
    ).fetchall()
    assert [(row[0], row[1]) for row in stored] == [(1, 1), (2, 0), (3, 0)]
    assert stored[1][2] is not None and stored[1][2] != LEGACY_PREV_HASH

    result = verify(connection, "job-1", keystore=FakeKeyStore())
    assert result.ok is True
    assert (result.bad_seq, result.kind) == (None, None)
    assert [(s.first_seq, s.last_seq, s.reason) for s in result.unverifiable] == [
        (2, 2, "no key")
    ]
    assert result.hmac_checked is True, "seq 1 was keyed and did authenticate"


# -- the limit of the claim, pinned on purpose (issue #2220) -------------------


def test_a_removed_tail_is_not_detected_and_the_claim_is_not_made() -> None:
    """§3.2 walks from the first row and stops at the first bad row, so deleting the
    *last* rows leaves a shorter, internally consistent chain that verifies.

    ADR-0063 and ADR-F claimed a truncation detection this mechanism does not provide.
    This test exists so the limit is recorded as behaviour rather than as prose, and so
    a future change that claims truncation detection has to face it.
    """
    connection, keystore = chained(entries=4)
    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq > ?", ("job-1", 2))

    result = verify(connection, "job-1", keystore=keystore)
    assert result.ok is True
    assert result.bad_seq is None
    assert result.checked_through_seq == 2


def test_the_head_row_is_not_treated_as_proof_about_an_entry() -> None:
    """§5's read protocol: "`verify` reads each row's `keyed` and `hmac`, rather than
    treating `record_heads` as proof for a later unkeyed segment." Deleting the head
    row changes no verification outcome."""
    connection, keystore = chained(entries=3)
    before = verify(connection, "job-1", keystore=keystore)
    connection.execute("DELETE FROM record_heads WHERE job = ?", ("job-1",))
    after = verify(connection, "job-1", keystore=keystore)
    assert before == after
    assert after.ok is True


def test_verify_mutates_neither_table() -> None:
    """§3.2: "never mutates either table"."""
    connection, keystore = chained(entries=3)
    snapshot = (
        connection.execute("SELECT * FROM record_entries ORDER BY job, seq").fetchall(),
        connection.execute("SELECT * FROM record_heads ORDER BY job").fetchall(),
    )
    verify(connection, "job-1", keystore=keystore)
    assert snapshot == (
        connection.execute("SELECT * FROM record_entries ORDER BY job, seq").fetchall(),
        connection.execute("SELECT * FROM record_heads ORDER BY job").fetchall(),
    )


def test_verify_is_the_positional_signature_its_contract_states() -> None:
    """§3.2 states `verify(connection, job_id, *, keystore=OSKeyStore())` with the first
    two parameters positional; the keyword-only convention does not override it."""
    import inspect

    from rqa.record.keychain import OSKeyStore

    parameters = list(inspect.signature(verify).parameters.values())
    assert [p.name for p in parameters] == ["connection", "job_id", "keystore"]
    assert [p.kind for p in parameters[:2]] == [inspect.Parameter.POSITIONAL_OR_KEYWORD] * 2
    assert parameters[2].kind is inspect.Parameter.KEYWORD_ONLY
    assert isinstance(parameters[2].default, OSKeyStore)
