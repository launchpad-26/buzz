"""Offline reconstruction uses recorded pins and keyless chain integrity."""

import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.record.explain import explain_job
from rqa.record.writer import SQLiteRecordWriter


def test_snapshot_pins_are_reconstructed_before_a_plan_exists():
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    writer.append("job", "snapshot", {"hash": "snapshot-pin", "protocol_hash": "protocol-pin", "policy_version": "v1"})
    result = explain_job(connection, "job")
    assert (result.snapshot_hash, result.protocol_hash, result.policy_version) == ("snapshot-pin", "protocol-pin", "v1")
    assert result.verified
    connection.close()


def test_chain_integrity_distinguishes_tampering_from_intact_records():
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    writer.append("job", "snapshot", {"hash": "snapshot-pin", "protocol_hash": "protocol-pin", "policy_version": "v1"})
    assert explain_job(connection, "job").verified
    connection.execute("UPDATE record_entries SET payload = '{}' WHERE job = 'job'")
    result = explain_job(connection, "job")
    assert not result.verified
    assert result.truncated_at is not None
    assert result.snapshot_hash is None
    connection.close()


def test_human_decision_basis_is_reconstructed_from_the_decision_entry():
    connection = sqlite3.connect(":memory:")
    writer = SQLiteRecordWriter(connection)
    writer.append("job", "decision", {"actor": "fixture-human", "basis": "checked the cited evidence"})
    result = explain_job(connection, "job")
    assert result.reviewer_identity == ("fixture-human",)
    assert result.decision_basis == "checked the cited evidence"
    connection.close()
