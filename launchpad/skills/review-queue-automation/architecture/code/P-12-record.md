# P-12 Record — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-12 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Append every decision, action, finding and state change to one
append-only, hash-chained record per job — inside the same transaction as the change it describes —
and reconstruct any authoritative outcome from that record alone, contacting neither GitHub nor a
model.

**Depends on.** ADR-F ([#2159](https://github.com/launchpad-26/buzz/issues/2159), assumed) for
provenance integrity. It consumes no other part implementation or store.

## 1. Modules

```
rqa/record/
  __init__.py    re-exports: RecordWriter, RecordReader, Entry, RecordRow, EntryKind, AppendFailed,
                 RecordProgrammingError, UnknownEntryKind, PayloadNotSerializable, ENTRY_KINDS,
                 KeyStore, KeyStoreExplanationUnavailable, verify, VerifyResult, BreakKind, explain,
                 explain_job, resolve_job, ResolvedJob, NoRecord, AmbiguousHead, Explanation,
                 ExplanationUnavailable, ReuseResolutionError, migrate_legacy, MigrationSummary,
                 MigrationTableResult, LegacySource
  kinds.py       ENTRY_KINDS: the closed thirteen-kind set (§6)
  hashing.py     canonical_json(); compute_hash(); genesis and "legacy" prev_hash sentinels
  keychain.py    E-25 KeyStore implementation backed by the platform keychain command
  store.py       record_entries/record_heads DDL; serialization; ordered row reads
  writer.py      SQLiteRecordWriter: the RecordWriter implementation
  verify.py      verify(): chain and keyed-segment recomputation
  reader.py      SQLiteRecordReader plus resolve_job()
  explain.py     explain() / explain_job(): FR-012 reconstruction
  trace.py       jobs/<job>/trace.jsonl: non-authoritative milestone trace
  migrate.py     one-way legacy migration
```

No other module in RQA imports from `rqa.record` except through `__init__`. No module in
`rqa.record` imports from any other part's package, calls another part's `E-NN` contract, or reads
`jobs`, `snapshots`, `capabilities`, or any other table `container.md` §5 assigns to a different
writer. Every value that crosses into or out of this package — `payload` in, the fields of
`Explanation` out — is a plain JSON-safe type (`str`, `int`, `float`, `bool`, `None`, `list`, `dict`,
or a `tuple` of these) that this package defines the shape of itself; it never imports and never
instantiates `EvidenceState`, `Finding`, `JobStatus`, `Decision`, or any other part's dataclass or
enum. This is deliberate: P-12 is the one part every other part's durability depends on, so it is the
one part that must not be able to break because another part's type changed shape. `explain`'s
`evidence` and `findings` fields mirror `EvidenceState` and `Finding` by field-name and by-value
convention only.

Nothing in this package opens a socket, spawns `gh` or `git`, or invokes a model. `keychain.py`'s one
subprocess (`security`, macOS's local keychain CLI) is local-only and does not count as network
access; §8's T7 proves this behaviourally with a socket guard, not by this sentence alone.

## 2. Types

```python
# CONTRACTS.md §7 is the sole definition. rqa.record re-exports without varying shape.
from rqa.contracts import (
    AppendFailed, Entry, EntryKind, ENTRY_KINDS, RecordReader, RecordRow, RecordTrustFailureReason,
    RecordUntrusted, RecordWriter, VerifiedRecordPrefix,
)

assert ENTRY_KINDS == frozenset({
    "transition", "plan", "carry_over", "bundle", "attestation", "spend", "panel",
    "judgement", "grant", "action", "escalation", "decision", "legacy",
})
```
```python

class RecordProgrammingError(Exception):
    """Base class for this part's own programming errors — never a policy, availability or
    tamper finding. Never caught by Lifecycle's containment boundary (P-02); a caller passing an
    unknown kind or an unserializable payload is a defect in the caller, not a recorded outcome."""

class UnknownEntryKind(RecordProgrammingError):
    """`kind` is not one of the thirteen values in ENTRY_KINDS."""

class PayloadNotSerializable(RecordProgrammingError):
    """`payload` contains a value canonical_json() cannot render (anything other than str, int,
    float, bool, None, list, dict, or tuple of these — in particular, no Enum, no dataclass, no
    other part's type). The caller must convert its own values to plain JSON-safe data first."""
```

```python
# keychain.py — E-25 KeyStore is defined only in CONTRACTS.md §9 and imported here.
from rqa.contracts import KeyStore

class KeyStoreExplanationUnavailable(Exception):
    """The platform keychain command could not be invoked or queried. This differs from an absent
    item, for which `KeyStore.read()` returns None."""

class OSKeyStore:
    """Reads only `rqa-record-hmac` through the platform keychain command. It returns None only for
    that absent item and never writes, rotates, generates, or logs a key."""
    def read(self, name: str) -> bytes | None: ...
```

```python
# reader.py — shared values come from CONTRACTS.md §7.
class SQLiteRecordReader:
    """Immutable record reader. Basic reads make no trust claim."""
    def entries(self, job_id: str, kind: EntryKind | None = None) -> tuple[RecordRow, ...]: ...
    def latest(self, job_id: str, kind: EntryKind) -> RecordRow | None: ...
    def trusted_prefix(self, job_id: str) -> VerifiedRecordPrefix | RecordUntrusted: ...
```

`trusted_prefix` calls `verify` with the reader's key store. No rows returns `MISSING`; any chain/HMAC
break returns `INTEGRITY_BREAK`; any unverifiable segment returns `UNVERIFIABLE`; any legacy row
returns `LEGACY`. Only a complete, chain-valid, available-key HMAC-authenticated non-legacy history
returns `VerifiedRecordPrefix`; its `latest(kind)` searches only its immutable `rows`. Operational
consumers such as P-13 must use this method rather than treating `latest()` as authenticated.

```python
# verify.py
class BreakKind(str, Enum):
    HASH_MISMATCH = "hash_mismatch"     # a row's stored hash does not match its own recomputed content
    CHAIN_BREAK = "chain_break"         # a row's prev_hash does not match the previous real row's hash
    HMAC_MISMATCH = "hmac_mismatch"     # a keyed row does not authenticate under the available key

@dataclass(frozen=True)
class UnverifiableSegment:
    job_id: str
    first_seq: int
    last_seq: int
    reason: Literal["no key"] = "no key"

@dataclass(frozen=True)
class VerifyResult:
    job_id: str
    ok: bool
    bad_seq: int | None          # first seq verification stopped trusting; None iff ok
    kind: BreakKind | None       # None iff ok
    hmac_checked: bool           # True iff at least one keyed row was checked this run
    checked_through_seq: int     # last real (non-legacy) seq examined before stopping or finishing
    unverifiable: tuple[UnverifiableSegment, ...]  # unkeyed or unavailable-key segments; never breaks
```


```python
# reader.py
@dataclass(frozen=True)
class ResolvedJob:
    job_id: str

@dataclass(frozen=True)
class NoRecord:
    """No job's transition entries name this (repo, number)."""

@dataclass(frozen=True)
class AmbiguousHead:
    """More than one job matches (repo, number) and none names the other as its predecessor —
    resolve_job never guesses which is current."""
    candidates: tuple[str, ...]
```

```python
 # explain.py
@dataclass(frozen=True)
class Explanation:
    job_id: str
    repo: str
    number: int
    # The twelve RQA-FR-012 / CL-033 (AC06) elements, in fit-criterion order:
    pr_revision: str
    protocol_hash: str | None
    policy_version: str | None
    reviewer_identity: tuple[str, ...]
    reviewer_type: Literal["ai", "human", "none"]
    harness: tuple[str, ...]
    model: tuple[str, ...]
    provider: tuple[str, ...]
    evidence: Mapping[str, str]
    findings: tuple[Mapping[str, Any], ...]
    decision_basis: str | None
    disposition: str
    # Supporting trust/rendering fields:
    snapshot_hash: str | None
    verified: bool
    hmac_checked: bool
    unverifiable: tuple[UnverifiableSegment, ...]  # each has reason "no key"
    truncated_at: int | None
    legacy: bool

```

`ExplanationUnavailable` is the E-17 boundary result defined only in `CONTRACTS.md` §8.

```python
# migrate.py
class LegacySource(Protocol):
    """Read-only view of the pre-cutover tables, for the one-time migration. Not an ongoing
    dependency: nothing else in this part ever reads these tables, and this Protocol exists only
    so migrate_legacy can be tested against a fixture instead of a real pre-cutover database."""
    def ledger_entries(self) -> Iterator[Mapping[str, Any]]: ...
    def approval_decisions(self) -> Iterator[Mapping[str, Any]]: ...
    def cost_ledger(self) -> Iterator[Mapping[str, Any]]: ...

@dataclass(frozen=True)
class MigrationTableResult:
    migrated: int
    already_done: bool
@dataclass(frozen=True)
class MigrationSummary:
    ledger_entries: MigrationTableResult
    approval_decisions: MigrationTableResult
    cost_ledger: MigrationTableResult

class ReuseResolutionError(Exception):
    """A current judgement's `reused_from` chain cannot be resolved from trusted record rows:
    malformed/missing predecessor, missing source judgement or attestation, predecessor tamper before
    the cited evidence, or a cycle. It is a corrupt record reference, never a fabricated explanation."""
```

`Snapshot`, `Job`, `JobStatus`, `EvidenceState`, `Finding`, `Judgement`, `Decision`, `CarryOver`,
`Attempt`, `Attestation`, `Mutation`, `Plan` are other parts' types, never imported here. Where §6
below names a payload field after one of them, it means "the same value, JSON-safe, by field name" —
not the Python type.

## 3. Entry points — E-13 and E-17

P-12 provides two of the architecture's contracts: `append` (E-13, called by every other part except
P-04) and the `explain` half of the shared operator edge E-17 (`status` is P-02's, `decide` is
P-11's, `onboard` is P-03's — this contract covers `explain` alone). `verify` is not a separately
named `E-NN` edge; it is the mechanism `explain` calls, exposed publicly because tests, and an
operator who wants to check tamper-evidence without a full reconstruction, both need it directly.

### 3.1 `append` — E-13

```python
# `RecordWriter` and its E-13 method are defined verbatim in CONTRACTS.md §7:
# class RecordWriter(Protocol):
#     def append(self, job_id: str, kind: str, payload: Mapping) -> Entry: ...
#
# SQLiteRecordWriter is P-12's implementation. Its constructor-only dependencies are
# connection, clock=utcnow, and keystore=OSKeyStore(); they are not E-13 parameters.
```

The caller constructs (or is handed) a `RecordWriter` over the **same** `sqlite3.Connection` its own
state-changing statement is about to execute on, and calls `append` before that connection's
transaction commits. `append` never calls `connection.commit()` or `connection.rollback()` itself.

**Behaviour, in order. Every branch returns or raises.**

1. `kind not in ENTRY_KINDS` → raise `UnknownEntryKind`. Nothing is read or written.
2. `canonical_json(payload)` raises → raise `PayloadNotSerializable`. Nothing is written.
3. Read the highest-`seq` non-legacy row for `job_id`. None → `seq=1`, `prev_hash_for_hash=""`;
   found → `seq=found.seq+1`, `prev_hash_for_hash=found.hash`.
4. Set `at` from `clock()` as UTC ISO-8601 with microseconds and compute `hash` by §5.
5. `key = keystore.read("rqa-record-hmac")`:
   - returns `bytes` → `keyed=True`; `hmac` is `HMAC-SHA256(key, f"{job_id}|{seq}|{hash}")`, hex;
   - returns `None` → `keyed=False`; `hmac=NULL`. This is a successful, explicitly unkeyed append,
     not `AppendFailed`;
   - raises `KeyStoreExplanationUnavailable`, `OSError`, or a keychain-process error → raise
     `AppendFailed(job_id, kind, cause=exc)`. No row is inserted.
6. Insert one `record_entries` row with `job`, `seq`, `kind`, `at`, canonical `payload`,
   `prev_hash`, `hash`, `hmac`, and `keyed`. A `sqlite3.Error`/`OSError` → raise `AppendFailed`.
   No commit is issued.
7. Upsert `record_heads(job)=(seq, hash, hmac, keyed)` on the same connection. A
   `sqlite3.Error`/`OSError` → raise `AppendFailed`.
8. Return `Entry(seq, hash)`.

The explicit `keyed` bit and nullable `hmac` are part of every stored entry; an implementation MUST
NOT infer key absence from a missing head row. A `None` result opens an `unverifiable: no key` segment
at this sequence; consecutive unkeyed rows form one segment and a later keyed row closes it. The hash
chain still covers every entry, so this degradation does not create a chain break or a partial append.

**Guarantees.** `append` is deterministic for identical hashed inputs, re-reads its head on every
call, never inspects payload semantics, and is the only non-migration writer to `record_entries`.
The entry and head upsert are one caller-controlled transaction: either both persist on commit or an
`AppendFailed` propagates for the caller to roll back. An absent key is expressly not an error.

### 3.2 `verify` — chain and keyed-segment checks

```python
def verify(connection: sqlite3.Connection, job_id: str, *, keystore: KeyStore = OSKeyStore()) -> VerifyResult: ...
```

**Behaviour, in order. Every branch returns or raises.**

1. Read every row for `job_id`, ordered by `seq`. No rows → return `VerifyResult(ok=True,
   bad_seq=None, kind=None, hmac_checked=False, checked_through_seq=0, unverifiable=())`.
2. Walk non-legacy rows in sequence order, validating expected `prev_hash` and recomputed hash. The
   first wrong parent returns `CHAIN_BREAK`; the first wrong hash returns `HASH_MISMATCH`. Both set
   `bad_seq` to that row, preserve all accumulated `unverifiable` segments, and set
   `hmac_checked` only if a preceding keyed row was checked.
3. For each chain-valid row:
   - `keyed=False, hmac is NULL` → accumulate it into an `UnverifiableSegment(..., reason="no key")`;
     do not call the key store and do not mark the record broken.
   - `keyed=True, hmac` missing or malformed → return `HMAC_MISMATCH` at that row.
   - `keyed=True` → call `keystore.read("rqa-record-hmac")`. `None` makes that consecutive keyed
     run an `UnverifiableSegment(..., "no key")`; it is not a break. A `KeyStoreExplanationUnavailable` or
     platform/store read error does the same: verification remains readable and reports the run
     `unverifiable: no key`, rather than refusing the record.
   - keyed row and available key → recompute and constant-time compare the row HMAC. Mismatch returns
     `HMAC_MISMATCH` at that row; match sets `hmac_checked=True`.
4. A complete walk returns `ok=True`, `bad_seq=None`, `kind=None`, all accumulated segments, and the
   last examined sequence. Legacy-only rows return `ok=True`, no break and no keyed check.

`verify` never mutates either table, never reads the trace, and never raises for an integrity outcome.
Store read failures raise `sqlite3.Error`/`OSError`; all other branches above return `VerifyResult`.

### 3.3 `explain` / `explain_job` — E-17

```python
def resolve_job(connection: sqlite3.Connection, repo: str, number: int) -> ResolvedJob | NoRecord | AmbiguousHead: ...

def explain(connection: sqlite3.Connection, repo: str, number: int) -> Explanation | ExplanationUnavailable: ...

def explain_job(connection: sqlite3.Connection, job_id: str) -> Explanation | ExplanationUnavailable: ...
```

`resolve_job` reads every `transition`-kind row (§6) across the whole table, filters those whose
payload's `repo`/`number` match, and groups by `job`. Zero matches → `NoRecord`. One matching job
that no *other* matching job's `transition` payload names as its own `predecessor_job` → that job is
the head: `ResolvedJob(job_id)`. Zero or more-than-one such head → `AmbiguousHead(candidates)`; this
never guesses. `explain(connection, repo, number)` calls `resolve_job` and dispatches on the result;
`explain_job(connection, job_id)` is the same reconstruction with the job already named (matching the
CLI's `explain.py job <job-id>` precedent), and `explain` is defined in terms of it.

**Behaviour of `explain_job`, in order. Every branch returns or raises.**

1. Read the job's rows. None → return `ExplanationUnavailable(repo="", number=0, reason="no_record")`. Call
   `verify`; its bad sequence forms the trusted prefix. A bad row and all later rows contribute no
   element. Legacy rows remain readable but make their contribution unverified.
2. Reduce that prefix: the first/last `transition` supplies identity/disposition; the last `plan`
   supplies pins; harness-shaped `attestation` rows supply the ordered de-duplicated reviewer,
   harness, model, and provider values; the last `judgement` supplies obligations, findings,
   corroboration/blocking decorations, and decision basis; a terminal human `decision` overrides the
   reviewer identity/type exactly as before.
3. A judgement with `reused_from is None` uses only this job's rows. A judgement with
   `reused_from: str` is a materialised current judgement, not a pointer that may be ignored:
   - load and verify the named predecessor's trusted prefix, then obtain the predecessor judgement
     at the carried source sequence and its harness-shaped attestations;
   - merge the current judgement's own obligations/findings/basis with the predecessor attestations
     for the carried obligations, preserving predecessor attestation order and de-duplicating against
     local attestations. Thus the returned `Explanation` has all twelve elements even when this job
     has no `attestation` entry;
   - missing predecessor rows, no predecessor judgement at the referenced sequence, malformed
     `reused_from`, a predecessor integrity break before a referenced row, or a reuse cycle → raise
     `ReuseResolutionError`. `explain` must never guess, silently omit, or follow an untrusted
     predecessor tail.
4. No transition in the trusted prefix → `disposition="unknown"`. Every contribution from legacy rows
   sets `legacy=True`. `truncated_at` is `bad_seq` or None. `unverifiable` is the ordered union of
   current and predecessor `VerifyResult.unverifiable` segments, annotated with their job id; it
   renders each as `unverifiable: no key`, not as a hash/HMAC break.
5. `verified` is true only if every contributing current and predecessor prefix is chain-valid,
   non-legacy, and has no `unverifiable` segment. `hmac_checked` is true only if every keyed
   contributing row was checked with an available key. Return the assembled `Explanation`.

`explain(connection, repo, number)` dispatches `resolve_job`: `NoRecord` →
`ExplanationUnavailable(repo, number, "no_record")`; `AmbiguousHead` → `ExplanationUnavailable(repo, number,
"ambiguous_head")`; `ResolvedJob` → `explain_job` with the known identity filled in.

**Guarantees.** `explain` makes no GitHub, harness, model, network, trace-file, or other-part-store
call; never fabricates values; never presents a post-break row as authoritative; and is idempotent and
side-effect-free. Its only named reconstruction failure is `ReuseResolutionError` above; all ordinary
absence/ambiguity and integrity cases have the returned outcomes specified here.

## 4. Dependencies consumed — E-25 only

P-12 calls no other RQA part. Its sole cross-boundary dependency is **E-25**,
`KeyStore.read(name) -> bytes | None`, for the operator-held HMAC key; the platform keychain command
is local-only and RQA never writes the key. It also receives an injected wall clock and reads legacy
tables only through `LegacySource` during the one-way migration. It does not use GitHub, a harness, a
model, another part's store, or the trace as an authority source.

## 5. Store

```sql
CREATE TABLE record_entries (
  job       TEXT NOT NULL,
  seq       INTEGER NOT NULL,
  kind      TEXT NOT NULL,
  at        TEXT NOT NULL,
  payload   JSON NOT NULL,
  prev_hash TEXT,                         -- NULL genesis; 'legacy' migrated; otherwise parent hash
  hash      TEXT NOT NULL,
  hmac      TEXT,                         -- NULL exactly when keyed=0
  keyed     INTEGER NOT NULL CHECK (keyed IN (0, 1)),
  CHECK ((keyed = 1 AND hmac IS NOT NULL) OR (keyed = 0 AND hmac IS NULL)),
  UNIQUE (job, seq)
);
CREATE INDEX record_entries_by_job ON record_entries(job, seq);
CREATE INDEX record_entries_by_kind ON record_entries(kind);

CREATE TABLE record_heads (
  job TEXT PRIMARY KEY, seq INTEGER NOT NULL, hash TEXT NOT NULL,
  hmac TEXT, keyed INTEGER NOT NULL CHECK (keyed IN (0, 1))
);
```

**Hash formula** [ADR-F assumed]:
`sha256(f"{job}|{seq}|{kind}|{at}|{canonical_json(payload)}|{prev_hash_for_hash}")`, as UTF-8 hex.
`prev_hash_for_hash` is `""` for `NULL`, otherwise the stored value. `canonical_json` is
`json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)`.

**Read protocol.** `append` reads the last non-legacy row; `verify`, `SQLiteRecordReader.entries`,
and `explain_job` range-scan rows by `(job, seq)`; `SQLiteRecordReader.latest` reads the greatest
matching sequence or `None`; `resolve_job` scans transition rows. `verify` reads each row's `keyed`
and `hmac`, rather than treating `record_heads` as proof for a later unkeyed segment. The trace is
never read by any authoritative reconstruction.

**Retention: none.** U-DISPATCH-06 is binned — there is no delete, purge, vacuum, or compaction
statement anywhere in `rqa/record/`, and none is added by this contract. `record_entries`,
`record_heads`, and every `trace.jsonl` grow for the life of the state directory; `container.md` §5
records this as a deliberate, operator-carried cost, not a gap this part closes.

## 6. Record entries written

`append` executes the write for every kind below on behalf of the caller that names it; the calling
part chooses `kind` and builds `payload`, `append` does not validate payload content beyond §3.1
steps 1–2. P-12 itself calls `append` directly only for `kind="legacy"`-shaped rows during migration
(and, there, through `store.py`'s primitives rather than through `RecordWriter`, since migrated rows
carry a historical `at` and the fixed `"legacy"` `prev_hash` rather than the live clock and a followed
chain — §6's migration note).

| kind | written by | when | payload |
|---|---|---|---|
| `transition` | P-02 | every job-state change, including arrival (`None → queued`) | `from_state: str \| None`, `to_state: str`, `reason: str`, `repo: str`, `number: int`, `head_sha: str`, `base_sha: str`, `predecessor_job: str \| None` |
| `plan` | P-06 | step 5, once per job | all shared `Plan` fields, including `head_sha`, `snapshot_hash`, `protocol_hash`, and `policy_version`; this is the authoritative predecessor pin for P-13 |
| `carry_over` | P-13 | when a job supersedes a prior head (E-05) | `reused: [str]`, `regenerated: [str]`, `basis: str`, `source_job: str` |
| `bundle` | P-06 | before route selection, or on assembly failure | `status: "ready"\|"incomplete"`, `nonce`, `protocol_hash`, `manifest`, `reason` |
| `attestation` | P-06 (harness attempts) or P-08 (capability probes) | every harness attempt; every `probe()` | harness subject: `attempt_id: str`, `harness: str`, `model: str`, `provider: str`, `route_family: str`, `external: bool`, `effort: str`, `started_at: str`, `ended_at: str`, `exit_code: int`, `self_reported_identity: {...} \| None` (untrusted, marked as such). Capability subject (P-08's, verbatim): `login: str`, `capabilities: [str]`, `attested_not_proven: [str]`, `probed_at: str` |
| `spend` | P-05 | after each attempt (E-15) | `tokens: int`, `measured: bool`, `source: str`, `axis: str`, `route: {harness,model,provider} \| None`, `attempt_id: str \| None` |
| `panel` | P-06 | every normal `run()` return | `attempt_ids: [str]`, `complete: bool`, `incomplete_reason: str \| None`, `evidence_cutoff: str` captured after final attempt/consumption |
| `judgement` | P-07 | every `judge()` return, including carry-only step 5a | JSON-safe shared judgement fields plus `snapshot_hash`, `protocol_hash`, `facts_fetched_at`, `cutoff` (`panel.evidence_cutoff`), and `rendered_body`; carry-only materialises current state and retains predecessor provenance |
| `grant` | P-08 | every E-04 call | `activity: str`, `snapshot_hash: str`, `categories: [str] \| null`, `capability_proof_id: int \| null`, `decision: "grant"\|"deny"`, `reason/detail` |
| `action` | P-09 | every GitHub write (E-12) | `mutation_id: str`, `operation: "review_submit"\|"comment"\|"merge"\|"assignee_claim"\|"assignee_release"`, `outcome: str`, `accepted: bool`, `github_response: {...} \| None`, `grant_entry_seq: int \| None` |
| `escalation` | P-11 | `raise()` (E-11) | `cause: "unresolved_decision"\|"conflicting_judgement"\|"evidence_gap"\|"required_information"\|"authority_requirement"`, `question: str`, `substantiates: str \| None` |
| `decision` | P-11 | `resume()`/`rqa decide` (E-17, via P-11) | `actor: str`, `basis: str`, `substantiates: str \| None`, `outcome: "approved"\|"changes_requested"\|None` |
| `legacy` | P-12 (`migrate_legacy`, once) | migration of `ledger_entries` only | `source_table: "ledger_entries"`, `source_pk: int`, `legacy_kind: str` (the old 8-value kind), `entry_key: str`, `fields: {...original columns...}` |

**The `attestation` subjects are distinguished by shape, not by an added discriminator field**: a
`login` key marks a capability probe, a `harness` key marks a harness attempt. This is deliberate —
P-08's contract already fixes the capability-probe shape verbatim (`login`, `capabilities`,
`attested_not_proven`, `probed_at`), and this table does not require that already-written contract to
change.

P-08 capability probes share `attestation`; no separate capability kind exists. `bundle` and `panel`
are P-06-owned lifecycle evidence, not overloading attestation: the first can exist when assembly
fails before an attempt, and the second durably binds the post-attempt cutoff used by judgement.
`ENTRY_KINDS` is therefore the `CONTRACTS.md` §7 closed thirteen-kind set.

`judgement`'s writer is P-07, not P-02. P-02 supplies its transaction-bound `RecordWriter`, so the
append remains atomic with the transition and `AppendFailed` propagates. `append` is indifferent to
which caller supplies any closed-set kind.

**`transition`'s `repo`/`number`/`head_sha`/`base_sha`/`predecessor_job` fields are this contract's
own addition** (P12: identity fields) beyond `architecture.md` §10's sketch ("from-state, to-state,
reason"), carried on **every** transition row, not only the first. This is what makes `resolve_job`
possible without reading P-01's `jobs` table, which `container.md` §5 does not list P-12 as a reader
of: every job is fully self-describing from its own `record_entries` rows alone, matching how the
estate's own `ledger.py.revisions()` already resolves `(repo, number)` by scanning the ledger's own
`repo`/`number` columns rather than a separate jobs table. `plan`'s `protocol_hash` /
`policy_version` / `snapshot_hash` fields are the same kind of addition, needed so `explain` can
render RQA-FR-012's "protocol and policy in force" without reading P-03's `snapshots` table (also not
a P-12 read, per `container.md` §5).

**Migration mapping** (one-way, run once; `architecture.md` §14, `container.md` §5's "Migration, not
copy"). `approval_decisions` and `cost_ledger` do **not** produce `kind="legacy"` rows — they migrate
into their natural new kinds, so an ordinary `kind`-filtered query still finds them — but every
migrated row of any kind, including these, is written with `prev_hash="legacy"` and is therefore
**never** examined by `verify` (§3.2 step 2) and **never** `verified=True` from `explain` (§3.3 step
8), regardless of how well-formed its content is. Order: `ledger_entries`, then `approval_decisions`,
then `cost_ledger` — deterministic, and each table's migration is independently skippable on retry
(`MigrationTableResult.already_done`, checked by the presence of any `record_entries` row whose
payload already names that source table).

| source (columns per `scripts/common.py`) | target `kind` | payload additions | `job` key | `at` |
|---|---|---|---|---|
| `ledger_entries(id, job_id, repo, number, head_sha, recorded_at, kind, entry_key, payload, snapshot_hash, policy_version)` | `legacy` | old `kind` → `legacy_kind`; old `payload` → `fields`; `source_pk = id` | old `job_id` verbatim | old `recorded_at` |
| `approval_decisions(id, job_id, repo, number, head_sha, policy_hash, status, mode, risk_score, created_at, expires_at)` | `decision` | `actor="unknown"` (marked historical), `basis=f"migrated from approval_decisions: status={status}, mode={mode}"`, `substantiates=None`, `outcome` mapped from `status` | old `job_id` if not `NULL`, else `f"legacy:approval_decisions:{id}"` | old `created_at` |
| `cost_ledger(id, recorded_at, job_id, repo, number, model, provider_family, kind, tokens, latency_ms)` | `spend` | `measured=false`, `source="migrated"`, `axis="unknown"`, `route={"harness": null, "model": model, "provider": provider_family}` | old `job_id` verbatim | old `recorded_at` |

A migrated job's `job` key may or may not coincide with the value P-01's new deterministic hash
produces for the same `(repo, number, head_sha)` going forward; when it does not, the legacy segment
and any new entries for that same logical revision live under two different `job` keys. This is
consistent with Non-goal 8 (retrofitting continuity onto history is out of scope) and does not affect
`explain`'s reconstruction of jobs created after cutover.

**The non-authoritative trace.** `trace.py` appends one JSON object per orchestration milestone to
`jobs/<job>/trace.jsonl`, under an exclusive `flock` on a sidecar lock file for the duration of the
write — both for cross-process safety and for exclusive per-job attempt-number allocation
(U-RESILIENCE-08) — and writes the file's whole new content (old lines plus the one new line) to a
temp file in the same directory, `fsync`s, and renames over the original (U-RESILIENCE-14): a crash
between writes leaves the previous, complete file in place, never a torn line. `container.md` §5
attributes the same technique to P-03's `snapshots/<hash>.json`; the two are independent
implementations of one pattern, not a shared dependency — P-03 does not import `rqa.record.trace`,
and this part does not write a snapshot. This file is written by this part and read by nobody in
`rqa/record/`; it exists for an operator's or a future tool's inspection, never for a trust decision.

## 7. What P-12 does not do

- Does not decide a job's disposition. `explain`'s `disposition` field renders `flow-review-
  lifecycle.md` §4's closed 13-state → 6-value table against the latest recorded `transition` — a
  read-only copy of a table P-02 owns and decides, not a second decision.
- Does not validate another part's payload semantics: it enforces one of thirteen kinds and JSON-safe
  data. Each calling part owns its field contract.
- Does not read `jobs`, `pr_facts`, `leases`, `snapshots`, `capabilities`, `mutations`, `spend`,
  `breakers`, `human_requests`, or any other table `container.md` §5 assigns to a different writer.
- Does not read `jobs/<job>/trace.jsonl` for any purpose, including `explain`; the trace is written-
  only from this part and never authoritative (`architecture.md` §8).
- Does not retain, purge, compact, or vacuum anything; U-DISPATCH-06 is binned and no such path
  exists (§5).
- Does not generate, rotate, or write the operator's HMAC key into the OS keychain — only reads it
  (ADR-F: "the key is the operator's and never RQA's to write into the record").
- Does not contact GitHub, invoke a harness, or invoke a model anywhere in this package.
- Does not re-run a migration a prior run already completed for a given source table
  (`MigrationTableResult.already_done`), and does not invent a mapping for a table the migration
  doesn't name.
- Does not decide which finding blocks, which check is inherited, which activity is granted, or
  which cause an escalation names — it stores and, on request, replays exactly what the calling part
  decided, never re-deriving or second-guessing it.
- Does not catch `AppendFailed` anywhere inside `rqa.record`; every raise site in §3.1 lets it
  propagate to the caller unmodified.

## 8. Tests that prove it

Each is a unit test against a real (in-memory or temp-file) SQLite connection and a fake `KeyStore`;
none touches a real OS keychain or a real network.

| # | Given | Then |
|---|---|---|
| T1 | three chained entries for one job; row 2's stored `payload` edited in place, its `hash` left unchanged | `verify` returns `ok=False, bad_seq=2, kind=HASH_MISMATCH` |
| T2 | three chained entries; row 2 replaced with a new payload and a freshly, correctly recomputed own `hash`, but row 3's `prev_hash` left pointing at row 2's *original* hash | `verify` returns `ok=False, bad_seq=3, kind=CHAIN_BREAK` |
| T3 | row 2 and every downstream hash are consistently recomputed after a rewrite, but the original keyed HMAC remains on the rewritten head row | `verify` returns `ok=False, bad_seq=<head seq>, kind=HMAC_MISMATCH, hmac_checked=True` — a keyed entry catches the internally consistent rewrite |
| T4 | a connection with an open transaction: `append(job, "transition", ...)` succeeds (uncommitted), then the caller's own next statement fails and the caller rolls back | a fresh read of `record_entries` for that job returns zero rows |
| T5 | `append`'s `INSERT` raises `sqlite3.OperationalError` (monkeypatched) | `AppendFailed` is observed propagating out of the call at the test's own call site — nothing inside `rqa.record` caught it |
| T6 | a normal job with transition, plan, bundle, attestations, panel, judgement, action and terminal transition | `explain` returns all twelve fields and uses the recorded panel/judgement cutoff |
| T7 | socket calls patched to raise during T6 explain | unaffected; no network |
| T8 | integrity break at judgement | explanation truncates there and does not source later facts |
| T9 | a job with only migrated rows (`legacy`, `decision`, `spend`, all `prev_hash="legacy"`), zero real chained entries | `verify` returns `ok=True` (nothing chained to break); `explain_job` returns `legacy=True, verified=False` regardless — never `verified=True` |
| T10 | one fixture row from each of `ledger_entries`, `approval_decisions`, `cost_ledger` | `migrate_legacy` produces exactly: `kind="legacy"` with `legacy_kind`/`fields` set; `kind="decision"` with `actor="unknown"`; `kind="spend"` with `measured=False` — each with `prev_hash="legacy"` |
| T11 | three successive appends, including a final unkeyed append | `record_heads` has one latest `(seq, hash, hmac=NULL, keyed=0)` row, and each `record_entries` row carries its own correct keyed/HMAC state |
| T12 | `verify` on a job with zero rows | `ok=True, bad_seq=None, hmac_checked=False, checked_through_seq=0` |
| T16 | `KeyStore.read("rqa-record-hmac")` returns `None` during `append` | append returns `Entry`; its row has `keyed=False, hmac=NULL`; `verify` returns `ok=True` with an `unverifiable` segment whose reason is `no key`, not `HMAC_MISMATCH`; `explain` reports that segment `unverifiable: no key` |
| T14 | `append(job, "not_a_real_kind", {})` | raises `UnknownEntryKind`; `record_entries` for that job is unchanged (zero new rows) |
| T15 | `append(job, "spend", {"at": datetime.now()})` (a raw `datetime`, not a string) | raises `PayloadNotSerializable`; zero new rows |
| T20 | predecessor has a valid plan, harness attestations, and judgement; successor has no `attestation`, a materialised `judgement` with `reused_from=<predecessor job>`, and a transition | `explain_job(successor)` follows `reused_from`, returns all twelve elements, and obtains reviewer identity/harness/model/provider from the predecessor attestations |
| T17 | two payload dicts with identical key/value pairs built in different insertion order | `compute_hash` returns byte-identical results for both |
| T18 | a job with rows `[keyed real seq=1, legacy, unkeyed real seq=2 chained to seq=1]` | `verify` returns `ok=True` with the seq-2 `unverifiable: no key` segment; `explain_job` returns `legacy=True, verified=False` and reports that segment without calling it broken |
| T19 | a `judgement` row whose `findings` list contains three ids: one in both `blocking` and `corroborated`, one in `corroborated` only, one in neither | `explain_job`'s `findings` tuple marks the first `blocking=True, corroborated=True`, the second `blocking=False, corroborated=True`, the third `blocking=False, corroborated=False` — the three-way split RQA-BR-005/RQA-BR-008 need |
| T21 | append one minimal JSON-safe payload for each member of `ENTRY_KINDS` | all thirteen are accepted; any fourteenth string raises `UnknownEntryKind` |

Property that must hold across the suite: `grep -rn "INSERT INTO record_entries\|INSERT INTO
record_heads" rqa/ --include=*.py` returns hits only inside `rqa/record/store.py`. No other module —
not even inside `rqa/record/` — writes these tables directly; every write travels through
`RecordWriter.append` or, for the one-time migration, through `store.py`'s own primitives.

## 9. Requirements this part answers for

Accountable: RQA-BR-003, RQA-FR-012, RQA-NFR-022, RQA-NFR-028, RQA-NFR-032.

- **RQA-BR-003** — *"A review record shall establish who or what performed the review, which
  protocol was followed, and how the judgement was produced."* Fit criterion: **"Given any review
  record, a reader can name its performer, protocol, cutoff and judgement basis without asking the
  performer."** Served by the closed thirteen-kind schema (§6), especially `attestation`, `plan`,
  `panel`, and `judgement`, plus `explain`; T6, T21.
- **RQA-FR-012** — *"For any authoritative review outcome, a single command shall reconstruct the
  exact PR revision, the protocol and policy in force, reviewer identity and type, harness, model,
  provider, evidence examined, findings produced, decision basis and disposition."* Fit criterion:
  **"Running one command against an authoritative outcome returns each of the elements AC06 names …
  with none requiring a second lookup."** Served by `explain(repo, number)` returning one
  `Explanation` carrying all twelve fields from one call (§3.3); T6, T8.
- **RQA-NFR-022** — *"A provenance record shall never be writable by the reviewed content or by any
  model output, authenticated or not."* Fit criterion: **"Attempting to set any element … from PR
  content or from any model output is rejected rather than accepted into the record … whether the
  model response was authenticated or not."** Served by `append`'s closed `ENTRY_KINDS` gate and
  JSON-safety check (§3.1 steps 1–2), which admits only a plain, caller-constructed `Mapping` — never
  raw PR bytes or a harness's own output object — and by every calling part's own contract already
  isolating PR/model content behind its own types before it ever reaches `append`; a harness's
  self-reported identity is carried only as the clearly separate, marked `self_reported_identity`
  field of the `attestation` payload (§6), never as the `harness`/`model`/`provider` fields
  `explain` treats as attested; T14, T15.
- **RQA-NFR-028** — *"A provenance record shall be protected against forgery or alteration by any
  actor lacking authority to write it."* Fit criterion: **"… no element … can be created or altered
  by an actor lacking authority to write it and then be accepted as authentic and authoritative
  without detection; tamper-evidence satisfies this check … This row does not require the underlying
  storage bytes to be physically unalterable; it requires that an unauthorised alteration, if made,
  cannot pass as authentic … does not defend against a compromised operator machine."* Served by the
  hash chain plus the keyed HMAC on each keyed record entry (§5, §3.1) [ADR-F assumed]. `verify`
  detects an internally consistent rewrite as `HMAC_MISMATCH`; an unkeyed segment is instead honestly
  reported `unverifiable: no key`, never accepted as keyed-authentic. T1–T3 and T16 cover both paths.
- **RQA-NFR-032** — *"The authoritative provenance record shall be written by the system itself; a
  harness's or model's self-reported identity is input the system records, not a write of its own."*
  Fit criterion: **"Every element … is constructed and committed by the system itself. A harness or
  model may supply self-reported identity as input for the system to record, but cannot directly
  create or alter an authoritative provenance element …"** Served by `append` being the sole
  `INSERT INTO record_entries` path in RQA (§8's closing property) and by the `attestation` payload's
  separation of RQA's own attested `harness`/`model`/`provider` from the harness's untrusted
  `self_reported_identity` (§6); T6.

**Contributing** (per `components.md` §5, not accountable but served incidentally by mechanisms
above): RQA-BR-001 (auditability limb, via FR-012/NFR-022/NFR-028), RQA-BR-005/RQA-BR-008/
RQA-BR-014 (the per-finding `blocking`/`corroborated` markers `explain_job` computes from the
judgement's own id sets, §3.3 step 4; T19),
RQA-BR-011/RQA-FR-013 (the `decision` kind's `actor`/`basis`/`substantiates` fields, §6),
RQA-FR-007/RQA-FR-015/RQA-FR-020 (the `carry_over`/`judgement` kinds make reused/regenerated and
inherited-check state inspectable, §6), RQA-FR-016 (the closed disposition-rendering table, §3.3
step 4), RQA-FR-021/RQA-FR-038 (the `spend` kind's `measured` flag; a `transition` to `stopped` is
recordable and resumable like any other, §6), RQA-NFR-006 (nothing here requires anything beyond one
local SQLite file and one local keychain call), RQA-NFR-010 (`append`'s all-or-nothing transaction
contract and `AppendFailed`'s uncaught propagation, §3.1, are exactly the "no partially authoritative
outcome" mechanism U-DISPATCH-20/21 name).
