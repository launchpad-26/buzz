#!/usr/bin/env python3
"""`verify` — `code/P-12-record.md` §3.2 and §8 rows T1, T2, T3, T12, T16 and T9's
verify half.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Each test writes a real chain through `append`, then edits the stored rows with direct
SQL the way an actor with database access would, and asks `verify` what it makes of the
result. ADR-0066 removed the credential-store dependency, so no real OS keychain is
touched (§8).

**What `verify` claims.** It detects an altered row and a re-parented row. It does
**not** detect a removed tail — the walk starts at
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
from rqa.record.hashing import LEGACY_PREV_HASH, compute_hash  # noqa: E402
from rqa.record.store import StoredEntry, insert_entry  # noqa: E402
from rqa.record.writer import SQLiteRecordWriter  # noqa: E402

KEY = b"a-key-from-a-record-written-before-ADR-0066"


def chained(job: str = "job-1", *, entries: int = 3):
    """A real job with `entries` chained rows, written through `append`.

    ADR-0066: `append` takes no key store, so every row is unkeyed. The second
    element of the tuple is `None` and is kept only so the many
    `connection, _ = chained()` call sites keep their shape.
    """
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    for index in range(entries):
        writer.append(job, "transition", {"to_state": f"state-{index}", "step": index})
    return connection, None


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
    checked_through_seq=0`."""
    connection, _keystore = chained("job-1", entries=1)
    result = verify(connection, "job-with-nothing-in-it")
    assert (result.ok, result.bad_seq, result.kind) == (True, None, None)
    assert result.checked_through_seq == 0
    assert result.job_id == "job-with-nothing-in-it"


def test_an_intact_chain_verifies_and_reports_how_far_it_got() -> None:
    connection, _keystore = chained(entries=3)
    result = verify(connection, "job-1")
    assert result.ok is True
    assert (result.bad_seq, result.kind) == (None, None)
    assert result.checked_through_seq == 3


# -- §3.2 step 2: the chain ----------------------------------------------------


def test_t1_an_edited_payload_with_its_old_hash_is_a_hash_mismatch() -> None:
    """T1: three chained entries for one job; row 2's stored `payload` edited in place,
    its `hash` left unchanged → `verify` returns `ok=False, bad_seq=2,
    kind=HASH_MISMATCH`."""
    connection, _keystore = chained(entries=3)
    rewrite(connection, "job-1", 2, payload=json.dumps({"to_state": "approved", "step": 1}))

    result = verify(connection, "job-1")
    assert result.ok is False
    assert result.bad_seq == 2
    assert result.kind is BreakKind.HASH_MISMATCH
    assert result.checked_through_seq == 1, "row 1 was examined; row 2 stopped the walk"


def test_a_payload_that_no_longer_parses_is_a_hash_mismatch_not_an_exception() -> None:
    """§3.2: "never raises for an integrity outcome"."""
    connection, _keystore = chained(entries=2)
    rewrite(connection, "job-1", 1, payload="{not json at all")
    result = verify(connection, "job-1")
    assert (result.ok, result.bad_seq, result.kind) == (False, 1, BreakKind.HASH_MISMATCH)


def test_t2_a_stale_parent_pointer_is_a_chain_break_at_the_child() -> None:
    """T2: three chained entries; row 2 replaced with a new payload and a freshly,
    correctly recomputed own `hash`, but row 3's `prev_hash` left pointing at row 2's
    *original* hash → `verify` returns `ok=False, bad_seq=3, kind=CHAIN_BREAK`."""
    connection, _keystore = chained(entries=3)
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
    )

    result = verify(connection, "job-1")
    assert result.ok is False
    assert result.bad_seq == 3
    assert result.kind is BreakKind.CHAIN_BREAK
    assert result.checked_through_seq == 2


def test_a_genesis_row_that_claims_a_parent_is_a_chain_break() -> None:
    """The first real row's parent is NULL; anything else is a row spliced in front."""
    connection, _keystore = chained(entries=2)
    rewrite(connection, "job-1", 1, prev_hash="b" * 64)
    result = verify(connection, "job-1")
    assert (result.ok, result.bad_seq, result.kind) == (False, 1, BreakKind.CHAIN_BREAK)
    assert result.checked_through_seq == 0


# -- §3.2 step 3: the keyed bit ------------------------------------------------


def test_an_internally_consistent_rewrite_is_not_detected_and_the_claim_is_not_made() -> None:
    """ADR-0066, stated as a test rather than left as prose.

    Under ADR-0063 a rewritten row still failed its HMAC, because the actor could not
    forge one without the operator's key. There is no key now, so an actor who
    rewrites a row *and* recomputes every downstream hash produces a chain that
    verifies clean. That is the margin ADR-0066 deliberately gave up, on the grounds
    that the actor it defended against — one running with the operator's own
    authority — could read the key anyway.

    This test exists so the gap is asserted rather than assumed. #2300's externally
    anchored chain head is what closes it; nothing in this module does.
    """
    connection, _ = chained(entries=3)
    kind, at, _payload, prev_hash, _hash, _hmac, _keyed = row(connection, "job-1", 3)
    replacement = {"to_state": "merged", "step": 2}
    recomputed = compute_hash(
        job="job-1", seq=3, kind=kind, at=at, payload=replacement, prev_hash=prev_hash
    )
    rewrite(connection, "job-1", 3, payload=json.dumps(replacement), hash=recomputed)

    result = verify(connection, "job-1")
    assert result.ok is True, "ADR-0066 accepts this; #2300 is what detects it"
    assert result.kind is None and result.bad_seq is None


def test_a_historical_keyed_row_verifies_by_its_chain_and_is_never_a_break() -> None:
    """The load-bearing compatibility property of #2299.

    A record written under ADR-0063 carries `keyed = 1` rows with real HMACs. After
    the key is removed, those rows must still verify — by their hash and their parent
    link, exactly as any other row — and must never be reported as tampered with
    merely because nothing can check their HMAC any more.
    """
    import hashlib
    import hmac as hmac_module

    connection, _ = chained(entries=3)
    # Retro-fit rows 1 and 2 into the pre-ADR-0066 shape: keyed, with a genuine HMAC
    # over the same material `compute_hmac` used to produce.
    for seq in (1, 2):
        entry_hash = row(connection, "job-1", seq)[4]
        digest = hmac_module.new(
            KEY, f"job-1|{seq}|{entry_hash}".encode("utf-8"), hashlib.sha256
        ).hexdigest()
        rewrite(connection, "job-1", seq, hmac=digest, keyed=1)

    assert [row(connection, "job-1", seq)[6] for seq in (1, 2, 3)] == [1, 1, 0]

    result = verify(connection, "job-1")
    assert result.ok is True, "a pre-ADR-0066 record must not read as broken"
    assert result.kind is None and result.bad_seq is None
    assert result.checked_through_seq == 3


def test_a_historical_keyed_row_with_a_malformed_hmac_is_still_not_a_break() -> None:
    """The stored HMAC is not read at all now, so its shape cannot fail anything.

    Under ADR-0063 a `keyed = 1` row whose `hmac` was not a SHA-256 digest was an
    immediate `HMAC_MISMATCH`. That branch is gone with the key: the column is inert
    data, and only the chain decides.
    """
    connection, _ = chained(entries=2)
    rewrite(connection, "job-1", 2, hmac="not-a-digest", keyed=1)
    result = verify(connection, "job-1")
    assert (result.ok, result.bad_seq, result.kind) == (True, None, None)


def test_verify_reads_no_key_and_names_no_credential_command() -> None:
    """Belt and braces on the removal: the module cannot reach a credential store."""
    source = pathlib.Path(
        pathlib.Path(__file__).resolve().parent.parent / "rqa" / "record" / "verify.py"
    ).read_text(encoding="utf-8")
    for forbidden in ("keychain", "KeyStore", "compute_hmac", "hmac_matches", "security", "secret-tool"):
        assert forbidden not in source, f"{forbidden!r} survives in verify.py"


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
    SQLiteRecordWriter(connection)
    for seq, kind in enumerate(("legacy", "decision", "spend"), start=1):
        migrated_row(connection, "job-legacy", seq, kind)

    result = verify(connection, "job-legacy")
    assert result.ok is True
    assert (result.bad_seq, result.kind) == (None, None)
    assert result.checked_through_seq == 0, "no real row was examined"


def test_migrated_rows_are_skipped_without_breaking_a_live_chain_around_them() -> None:
    """§6: a migrated row is "never examined by `verify`" — including when it sits in
    the middle of a job's sequence, where a naive walk would call it a chain break."""
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"step": 0})
    writer.append("job-1", "transition", {"step": 1})
    migrated_row(connection, "job-1", 3, "decision")

    result = verify(connection, "job-1")
    assert result.ok is True
    assert result.checked_through_seq == 2


def test_t18_a_real_row_a_migrated_row_and_a_later_real_row_verify_together() -> None:
    """T18 (verify half), restated for ADR-0066: a job holding `[real seq=1, real
    seq=2 chained to seq=1, legacy seq=3]` verifies `ok=True`.

    The migrated row takes a sequence of its own because `(job, seq)` is unique;
    where it sorts changes nothing, since `verify` never examines it. Under ADR-0063
    the seq-2 row opened an `unverifiable: no key` segment; there is no such segment
    now, because there is no key any row could have been measured against.
    """
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    writer.append("job-1", "transition", {"step": 0})
    writer.append("job-1", "transition", {"step": 1})
    migrated_row(connection, "job-1", 3, "legacy")

    stored = connection.execute(
        "SELECT seq, keyed, prev_hash FROM record_entries WHERE job = ? ORDER BY seq",
        ("job-1",),
    ).fetchall()
    assert [(row[0], row[1]) for row in stored] == [(1, 0), (2, 0), (3, 0)]
    assert stored[1][2] is not None and stored[1][2] != LEGACY_PREV_HASH

    result = verify(connection, "job-1")
    assert result.ok is True
    assert (result.bad_seq, result.kind) == (None, None)
    assert result.checked_through_seq == 2


# -- the limit of the claim, pinned on purpose (issue #2220) -------------------


def test_a_removed_tail_is_not_detected_and_the_claim_is_not_made() -> None:
    """§3.2 walks from the first row and stops at the first bad row, so deleting the
    *last* rows leaves a shorter, internally consistent chain that verifies.

    ADR-0063 and ADR-F claimed a truncation detection this mechanism does not provide.
    This test exists so the limit is recorded as behaviour rather than as prose, and so
    a future change that claims truncation detection has to face it.
    """
    connection, _keystore = chained(entries=4)
    connection.execute("DELETE FROM record_entries WHERE job = ? AND seq > ?", ("job-1", 2))

    result = verify(connection, "job-1")
    assert result.ok is True
    assert result.bad_seq is None
    assert result.checked_through_seq == 2


def test_the_head_row_is_not_treated_as_proof_about_an_entry() -> None:
    """§5's read protocol: "`verify` reads each row's `keyed` and `hmac`, rather than
    treating `record_heads` as proof for a later unkeyed segment." Deleting the head
    row changes no verification outcome."""
    connection, _keystore = chained(entries=3)
    before = verify(connection, "job-1")
    connection.execute("DELETE FROM record_heads WHERE job = ?", ("job-1",))
    after = verify(connection, "job-1")
    assert before == after
    assert after.ok is True


def test_verify_mutates_neither_table() -> None:
    """§3.2: "never mutates either table"."""
    connection, _keystore = chained(entries=3)
    snapshot = (
        connection.execute("SELECT * FROM record_entries ORDER BY job, seq").fetchall(),
        connection.execute("SELECT * FROM record_heads ORDER BY job").fetchall(),
    )
    verify(connection, "job-1")
    assert snapshot == (
        connection.execute("SELECT * FROM record_entries ORDER BY job, seq").fetchall(),
        connection.execute("SELECT * FROM record_heads ORDER BY job").fetchall(),
    )


def test_verify_is_the_positional_signature_its_contract_states() -> None:
    """ADR-0066: `verify(connection, job_id)`. The `keystore` keyword is gone, not
    defaulted — there is nothing for a caller to substitute."""
    import inspect

    parameters = list(inspect.signature(verify).parameters.values())
    assert [p.name for p in parameters] == ["connection", "job_id"]
    assert [p.kind for p in parameters] == [inspect.Parameter.POSITIONAL_OR_KEYWORD] * 2
