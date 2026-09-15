"""`rqa.record` — P-12, `architecture/code/P-12-record.md`.

Appends every decision, action, finding and state change to one append-only,
hash-chained record per job — inside the same transaction as the change it describes —
and reconstructs any authoritative outcome from that record alone, contacting neither
GitHub nor a model.

No other module in RQA imports from `rqa.record` except through this file (§1). The
public surface is §1's twenty-eight-name re-export list plus the two concrete
collaborators a composition root must construct: `SQLiteRecordWriter` (the one
implementation of the `RecordWriter` seam every other part is handed) and `OSKeyStore`
(the one implementation of `KeyStore`), plus `append_trace`, which lifecycle uses to
emit P-12's non-authoritative orchestration milestones. `SQLiteRecordReader` and `UnverifiableSegment`
stay module names (`rqa.record.reader`, `.verify`).

**Why those two are surface.** Every part that appends takes its `RecordWriter` as a
parameter and nothing inside `rqa/record/` constructs one, so something outside this
package always must, and the operator CLI's composition root (#2211) is the first
module in RQA whose job is exactly that. Withholding them while forbidding a reach past
`__init__` left no conforming way to build the writer: the clause was unfalsifiable only
until a composition root existed. Publishing `OSKeyStore` re-exports the same class
under a second name; it widens no capability — the keychain read, its `KEY_NAME` and its
refusal to carry a credential into an explanation are unchanged and still tested in
`tests/test_rqa_record_keychain.py`.

The shared record vocabulary — `Entry`, `EntryKind`, `ENTRY_KINDS`, `AppendFailed`,
`RecordWriter`, `RecordReader`, `RecordRow`, `KeyStore` — is imported from
`rqa.contracts` (`CONTRACTS.md` §7 and §9 are its one definition) and re-exported here
so a consumer can import the whole answer from one module. An import is not a
declaration: this file defines nothing.
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
from rqa.record.keychain import KeyStoreExplanationUnavailable, OSKeyStore
from rqa.record.kinds import RecordProgrammingError, UnknownEntryKind
from rqa.record.migrate import LegacySource, MigrationSummary, MigrationTableResult, migrate_legacy
from rqa.record.reader import AmbiguousHead, NoRecord, ResolvedJob, resolve_job
from rqa.record.trace import append_trace
from rqa.record.verify import BreakKind, VerifyResult, verify
from rqa.record.writer import SQLiteRecordWriter

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
    "SQLiteRecordWriter",
    "OSKeyStore",
    "append_trace",
]
