"""`rqa.record` — P-12, `architecture/code/P-12-record.md`.

Appends every decision, action, finding and state change to one append-only,
hash-chained record per job — inside the same transaction as the change it describes —
and reconstructs any authoritative outcome from that record alone, contacting neither
GitHub nor a model.

No other module in RQA imports from `rqa.record` except through this file (§1). The
public surface is §1's re-export list plus the concrete collaborators callers must
construct: `SQLiteRecordWriter` and `SQLiteRecordReader`, plus `append_trace`, which
lifecycle uses to emit P-12's non-authoritative orchestration milestones.

**Why those names are surface.** Every part that appends takes its `RecordWriter` as a
parameter and nothing inside `rqa/record/` constructs one, so something outside this
package always must, and the operator CLI's composition root (#2211) is the first
module in RQA whose job is exactly that. Withholding it while forbidding a reach past
`__init__` left no conforming way to build the writer: the clause was unfalsifiable only
until a composition root existed. P-02 likewise constructs `SQLiteRecordReader` over
its injected connection when it reads a predecessor.

**ADR-0066 removed the key.** `OSKeyStore`, `KeyStore`, `KeyStoreExplanationUnavailable`
and `UnverifiableSegment` were part of this surface while the record carried an
operator-held HMAC. There is no key now, so there is no key store to construct and no
unverifiable-for-want-of-a-key segment to report.

The shared record vocabulary — `Entry`, `EntryKind`, `ENTRY_KINDS`, `AppendFailed`,
`RecordWriter`, `RecordReader`, `RecordRow` — is imported from
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
    RecordReader,
    RecordRow,
    RecordWriter,
)
from rqa.record.anchor import (
    Anchor,
    AnchorPublisher,
    AnchorConflict,
    AnchorResult,
    PublishFailed,
    anchor_job,
    recover_external_anchors,
)
from rqa.record.explain import Explanation, ReuseResolutionError, explain, explain_job
from rqa.record.hashing import PayloadNotSerializable
from rqa.record.kinds import RecordProgrammingError, UnknownEntryKind
from rqa.record.migrate import LegacySource, MigrationSummary, MigrationTableResult, migrate_legacy
from rqa.record.reader import AmbiguousHead, NoRecord, ResolvedJob, SQLiteRecordReader, resolve_job
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
    "verify",
    "VerifyResult",
    "BreakKind",
    "Anchor",
    "AnchorPublisher",
    "AnchorResult",
    "AnchorConflict",
    "PublishFailed",
    "anchor_job",
    "recover_external_anchors",
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
    "SQLiteRecordReader",
    "append_trace",
]
