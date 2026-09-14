#!/usr/bin/env python3
"""Task #2216 — ADR-0063's executable half: a hand-tampered row is an integrity
break, a reuse attempt against that predecessor regenerates every obligation, and
an absent key degrades the append instead of blocking it (AC03, RQA-NFR-028).

ADR-0063, verbatim: "A missing key degrades, it never blocks. An append with no key
available succeeds and records itself as explicitly unkeyed; `verify` and `explain`
then report that span as `unverifiable: no key` — never as a hash or HMAC break, and
never as a stopped review."

The absent-key tests assert the behaviour the ADR requires *for the absent-key
case the key store can express* (`read()` returning `None`). What they deliberately
do NOT pin: #2272's platform behaviour, where on every non-darwin platform
`OSKeyStore.read` cannot answer "absent" at all and the append blocks — that is a
decided-ADR contradiction recorded as evidence in `TESTING.md` Part 2 §11.3, not a
property a test may encode in either direction.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from lifecycle_cascade_bench import (  # noqa: E402
    NoKeyStore,
    bench,
    make_facts,
    make_job,
    make_snapshot,
)

from rqa.contracts import RecordTrustFailureReason, RecordUntrusted, VerifiedRecordPrefix  # noqa: E402
from rqa.record.reader import SQLiteRecordReader  # noqa: E402
from rqa.record.verify import BreakKind, verify  # noqa: E402
from rqa.reuse import carry_over  # noqa: E402


def _recorded_history(connection, record, job) -> None:
    """A small real history: enough rows for a chain, a judgement for reuse to find."""
    record.append(job.id, "transition", {"from_state": None, "to_state": "queued"})
    record.append(job.id, "grant", {"activity": "review", "decision": "denied"})
    record.append(job.id, "judgement", {"obligations": {"ob-1": "verified"},
                                        "disposition": "approve", "findings": []})
    connection.commit()


def _tamper(connection, job_id: str, seq: int) -> None:
    """The AC03 mutation: edit one payload in place, without recomputing the chain."""
    payload = json.loads(connection.execute(
        "SELECT payload FROM record_entries WHERE job=? AND seq=?", (job_id, seq)
    ).fetchone()[0])
    payload["decision"] = "granted"
    connection.execute(
        "UPDATE record_entries SET payload=? WHERE job=? AND seq=?",
        (json.dumps(payload), job_id, seq),
    )
    connection.commit()


def test_adr0063_an_absent_key_degrades_the_append_instead_of_blocking_it() -> None:
    """The append succeeds, records itself explicitly unkeyed, and verify reports the
    span `unverifiable: no key` — never a break, never a stopped review."""
    connection, record, job = bench()
    entry = record.append(job.id, "transition", {"from_state": None, "to_state": "queued"})
    connection.commit()
    assert entry.seq == 1 and entry.hash
    keyed, hmac = connection.execute(
        "SELECT keyed, hmac FROM record_entries WHERE job=? AND seq=1", (job.id,)
    ).fetchone()
    assert keyed == 0 and hmac is None, "explicitly unkeyed: keyed=0, hmac=NULL"

    result = verify(connection, job.id, keystore=NoKeyStore())
    assert result.ok, "an unkeyed span is not a break"
    assert result.bad_seq is None and result.kind is None
    assert [segment.reason for segment in result.unverifiable] == ["no key"]


def test_adr0063_a_hand_tampered_row_is_reported_as_an_integrity_break() -> None:
    """AC03: an edited payload whose author did not recompute the chain is detected,
    named (`hash_mismatch`, at its seq), and never accepted as authoritative."""
    connection, record, job = bench()
    _recorded_history(connection, record, job)
    _tamper(connection, job.id, seq=2)

    result = verify(connection, job.id, keystore=NoKeyStore())
    assert not result.ok
    assert result.kind is BreakKind.HASH_MISMATCH
    assert result.bad_seq == 2

    prefix = SQLiteRecordReader(connection, keystore=NoKeyStore()).trusted_prefix(job.id)
    assert isinstance(prefix, RecordUntrusted)
    assert prefix.reason is RecordTrustFailureReason.INTEGRITY_BREAK
    assert "seq 2" in prefix.detail


def test_adr0063_reuse_against_a_tampered_predecessor_regenerates_every_obligation() -> None:
    """AC03's reuse half: the successor carries nothing over from a predecessor whose
    record cannot be trusted — every current obligation regenerates, and the decision
    is durably recorded as a `carry_over` entry naming its reason."""
    prior_connection, prior_record, prior_job = bench()
    _recorded_history(prior_connection, prior_record, prior_job)
    _tamper(prior_connection, prior_job.id, seq=2)
    prior = SQLiteRecordReader(prior_connection, keystore=NoKeyStore())

    connection, record, _ = bench()
    successor = make_job(job_id="successor-1", predecessor_job=prior_job.id)
    snapshot = make_snapshot()
    carry = carry_over(
        job=successor,
        prior=prior,
        facts=make_facts(job=successor),
        snapshot=snapshot,
        record=record,
    )
    connection.commit()

    assert carry.reused == ()
    assert carry.regenerated == tuple(o.id for o in snapshot.policy.obligations)
    assert set(carry.reasons.values()) == {"untrusted_predecessor"}

    recorded = json.loads(connection.execute(
        "SELECT payload FROM record_entries WHERE job=? AND kind='carry_over'",
        (successor.id,),
    ).fetchone()[0])
    assert recorded["reused"] == []
    assert recorded["reasons"] == {"ob-1": "untrusted_predecessor"}
    assert recorded["source_job"] == prior_job.id


def test_adr0063_an_intact_predecessor_is_not_reported_as_a_break() -> None:
    """The detector's other half — without the tamper, the same history verifies
    clean and `trusted_prefix` returns a real prefix. If this ever fails while the
    tampered twin passes, the detector is firing on something other than the tamper."""
    connection, record, job = bench()
    _recorded_history(connection, record, job)

    result = verify(connection, job.id, keystore=NoKeyStore())
    assert result.ok and result.bad_seq is None

    prefix = SQLiteRecordReader(connection, keystore=NoKeyStore()).trusted_prefix(job.id)
    # An unkeyed span is UNVERIFIABLE (a degrade), never INTEGRITY_BREAK (an accusation).
    if isinstance(prefix, RecordUntrusted):
        assert prefix.reason is RecordTrustFailureReason.UNVERIFIABLE
    else:
        assert isinstance(prefix, VerifiedRecordPrefix)
