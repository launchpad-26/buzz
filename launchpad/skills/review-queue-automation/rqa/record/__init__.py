"""`rqa.record` — P-12, `architecture/code/P-12-record.md`.

Appends every decision, action, finding and state change to one append-only,
hash-chained record per job — inside the same transaction as the change it describes —
and reconstructs any authoritative outcome from that record alone, contacting neither
GitHub nor a model.

No other module in RQA imports from `rqa.record` except through this file (§1). The
public surface is exactly §1's re-export list and nothing more: `SQLiteRecordWriter`,
`SQLiteRecordReader`, `OSKeyStore` and `UnverifiableSegment` are deliberately **not**
re-exported and stay module names (`rqa.record.writer`, `.reader`, `.keychain`,
`.verify`), the same way `rqa.policy` keeps `SnapshotStore` a `rqa.policy.store` name.
The shared record vocabulary — `Entry`, `EntryKind`, `ENTRY_KINDS`, `AppendFailed`,
`RecordWriter`, `RecordReader`, `RecordRow`, `KeyStore` — is imported from
`rqa.contracts` (`CONTRACTS.md` §7 and §9 are its one definition) and re-exported here
so a consumer can import the whole answer from one module. An import is not a
declaration: this file defines nothing.

§1 lists eleven modules and twenty-eight re-exports; this is the finished package.
"""

from __future__ import annotations

from rqa.contracts import (
    ENTRY_KINDS,
    AppendFailed,
    Entry,
    EntryKind,
    ExplanationUnavailable,
    KeyStore,
    RecordReader,
    RecordRow,
    RecordWriter,
)
from rqa.record.explain import Explanation, ReuseResolutionError, explain, explain_job
from rqa.record.hashing import PayloadNotSerializable
from rqa.record.keychain import KeyStoreExplanationUnavailable
from rqa.record.kinds import RecordProgrammingError, UnknownEntryKind
from rqa.record.migrate import LegacySource, MigrationSummary, MigrationTableResult, migrate_legacy
from rqa.record.reader import AmbiguousHead, NoRecord, ResolvedJob, resolve_job
from rqa.record.verify import BreakKind, VerifyResult, verify

__all__ = [
    "RecordWriter",
    "RecordReader",
    "Entry",
    "RecordRow",
    "EntryKind",
    "AppendFailed",
    "RecordProgrammingError",
    "UnknownEntryKind",
    "PayloadNotSerializable",
    "ENTRY_KINDS",
    "KeyStore",
    "KeyStoreExplanationUnavailable",
    "verify",
    "VerifyResult",
    "BreakKind",
    "explain",
    "explain_job",
    "resolve_job",
    "ResolvedJob",
    "NoRecord",
    "AmbiguousHead",
    "Explanation",
    "ExplanationUnavailable",
    "ReuseResolutionError",
    "migrate_legacy",
    "MigrationSummary",
    "MigrationTableResult",
    "LegacySource",
]
