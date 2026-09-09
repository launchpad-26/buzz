# P-13 Revision reuse — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-13 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.
Shared types and edge signatures are defined only in [`CONTRACTS.md`](CONTRACTS.md).

**Responsibility, in one sentence.** Given a successor's facts, pinned snapshot, and predecessor
judgement, determine exactly which current obligations remain valid, carry their verified evidence
and provenance forward, and record every reuse or regeneration reason.

**Depends on.** P-12's read-only record view for the predecessor's `judgement` and `carry_over`
entries, and P-04's canonical path matcher. P-13 neither reads GitHub nor fetches a diff: P-02 passes
the E-23 `Facts` value to E-05.

## 1. Modules

```
rqa/reuse/
  __init__.py        re-exports: carry_over, Reason, ReuseError
  obligations.py     per-obligation classification and carried-evidence construction
  pin.py             protocol/policy pin lookup from a predecessor carry_over entry
  reuse.py           carry_over(): the E-05 entry point
```

No module outside `rqa.reuse` imports its internals. `rqa.reuse` imports the shared contracts from
their owners and invokes path matching only as `rqa.protocol.paths.matches(path, pattern)`.

## 2. Types

`CarryOver` and `CarriedEvidence` are defined by [`CONTRACTS.md`](CONTRACTS.md) §6 and are used
unchanged:

```python
# CONTRACTS.md §6
CarryOver.reused: tuple[CarriedEvidence, ...]
CarriedEvidence: obligation_id, state, source_job, source_judgement_seq, source_attestations
CarryOver.regenerated: tuple[str, ...]
CarryOver.reasons: Mapping[str, str]
CarryOver.source_job: str | None
```

For each reused item, `state is EvidenceState.VERIFIED`; it is not merely a reused id. `reused` and
`regenerated` preserve `snapshot.policy.obligations` order.

```python
# P-13-local
class Reason(str, Enum):
    PATH_TOUCHED = "path_touched"
    PIN_CHANGED = "pin_changed"
    NOT_VERIFIED = "not_verified"
    NEW_OBLIGATION = "new_obligation"
    NO_PRIOR_JUDGEMENT = "no_prior_judgement"
    NO_PREDECESSOR = "no_predecessor"
    UNTRUSTED_PREDECESSOR = "untrusted_predecessor"
    UNCHANGED_VERIFIED = "unchanged_verified"

class ReuseError(Exception):
    """Programming error or malformed predecessor record: no trustworthy CarryOver can be made."""
```

`Job`, `Facts`, `Snapshot`, `Obligation`, `EvidenceState`, `RecordReader`, `VerifiedRecordPrefix`,
`RecordUntrusted`, `RecordWriter`, `RecordRow`, `AppendFailed`, `CarryOver`, and `CarriedEvidence`
are shared types in `CONTRACTS.md` §§1–7; P-13 does not redefine them.
It reads only `job.id`, `job.repo`, `job.predecessor_job`, `snapshot.repo`,
`snapshot.protocol_hash`, `snapshot.policy.version`, `snapshot.policy.obligations`, and
`facts.revision_changed_paths`.

## 3. Entry point — E-05

```python
def carry_over(*, job: Job, prior: RecordReader, facts: Facts, snapshot: Snapshot, record: RecordWriter) -> CarryOver: ...
```

**Behaviour, in order.** Every normal branch appends exactly one `carry_over` entry and returns its
matching `CarryOver`; `AppendFailed` propagates.

1. If `job.repo != snapshot.repo`, raise `ReuseError`; do not append. This is a caller programming
   error.
2. Build `obligations` in current snapshot order. If `job.predecessor_job is None`, set
   `source_job = None`, classify every obligation `NO_PREDECESSOR`, and skip all `prior` reads.
3. Otherwise set `source_job = job.predecessor_job` and call `prior.trusted_prefix(source_job)`
   exactly once. `RecordUntrusted` classifies every obligation `UNTRUSTED_PREDECESSOR`; P-13 reads
   no row from that predecessor. From a `VerifiedRecordPrefix`, read its latest `judgement` and
   `plan` rows only. A missing judgement is normal: classify every obligation
   `NO_PRIOR_JUDGEMENT`. A missing plan classifies every obligation `PIN_CHANGED`; malformed present
   judgement or plan raises `ReuseError`.
4. If the predecessor plan's `(protocol_hash, policy_version)` differs from
   `(snapshot.protocol_hash, snapshot.policy.version)`, classify every obligation `PIN_CHANGED`.
5. Otherwise decode `prior_states` from the trusted `judgement_row.payload["obligations"]`. For each
   current obligation, in order:
   - absent from `prior_states` → `NEW_OBLIGATION`;
   - state other than `EvidenceState.VERIFIED` → `NOT_VERIFIED`;
   - `any(rqa.protocol.paths.matches(path, pattern) for path in facts.revision_changed_paths for pattern in ob.paths)`
     → `PATH_TOUCHED`;
   - otherwise → `UNCHANGED_VERIFIED`.
6. For every `UNCHANGED_VERIFIED` obligation, construct one `CarriedEvidence` from the same
   `judgement_row`: `obligation_id=ob.id`, `state=EvidenceState.VERIFIED`,
   `source_job=source_job`, `source_judgement_seq=judgement_row.seq`, and
   `source_attestations` from that judgement payload's per-obligation contributing-attempt-id list:
   `tuple(judgement_row.payload["contributing_attempts"][ob.id])`. The list must be a sequence of
   non-empty strings; a missing, malformed, or non-string entry raises `ReuseError`, rather than
   returning unproven carried evidence.
7. Set `regenerated` to every non-reused current id, in order. `reasons` maps every current
   obligation id to its `Reason` string value. Append and return the `CarryOver` described in §6.

Thus every normal input has a total result: each current obligation is reused or regenerated exactly
once. The only exceptional branches are the named `ReuseError` cases above and `AppendFailed`.

## 4. Dependencies consumed

P-13 calls `prior.trusted_prefix(source_job)` once and never calls the unauthenticated
`RecordReader.entries/latest` methods. Without a predecessor it makes no reader call. A
`RecordUntrusted` result causes complete regeneration; P-13 never walks farther than one predecessor.

The source judgement entry is P-07/P-12's durable provenance boundary only when it lies in the
`VerifiedRecordPrefix`. Its payload supplies both `obligations` (id → `EvidenceState`) and
`contributing_attempts` (obligation id → contributing attempt ids). P-13 reads those fields only
through `prefix.latest("judgement")`; it never reads attestation entries to infer or replace them.

`prior_pin(prefix)` reads the trusted predecessor prefix's latest `plan` payload and returns its
required `(protocol_hash, policy_version)`, returns `None` when no plan exists (forcing
`PIN_CHANGED`), or raises `ReuseError` for malformed values.

## 5. Store

None. P-13 owns no database table, file, cache, or mutable module state. Its only durable output is
the P-12 `carry_over` entry described below.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `carry_over` | every normal E-05 return, before it returns | `source_job` (`null` with no predecessor), `reused` (serialized `CarriedEvidence`: obligation id, `verified`, source job, source judgement seq, source attestation ids), `regenerated` (ids), `reasons` (every current id → reason string), `protocol_hash`, `policy_version` |

P-13 writes no other kind. `reasons` is complete over current snapshot obligations, and the
serialized carried evidence has the exact provenance P-07 consumes from `carry.reused`.

P-13 does not judge and makes no assertion about whether P-06 was called. P-07 consumes
`carry.reused`; when all work is carried it records the current job's `judgement` with `reused_from`.
The proof of zero reviewer calls is that P-07 `judgement` entry together with no `attestation` entry
on the current job, owned by P-02/P-07/P-12 rather than P-13.

## 7. What P-13 does not do

- Does not decide whether E-05 is called, select work for a harness, invoke a harness, or decide a
  job transition; P-02 and P-06 own those operations.
- Does not assign a current evidence state, corroborate findings, calculate assurance, or choose a
  disposition. P-07 receives and consumes `carry.reused`.
- Does not fetch facts, diffs, or GitHub data. It reads changed paths only from `facts.changed_paths`.
- Does not validate path-glob grammar or implement matching. It calls only
  `rqa.protocol.paths.matches(path, pattern)`.
- Does not inspect predecessor attestation entries; the predecessor judgement payload supplies the
  contributing attempt ids carried as provenance.
- Does not mutate `jobs.status`, make GitHub mutations, reserve budget, remediate, or escalate.

## 8. Tests that prove it

Each is a unit test with frozen shared-contract values, a fake `RecordReader` whose
`trusted_prefix()` returns the named result, and a fake `RecordWriter`.

| # | Given | Then |
|---|---|---|
| T1 | authenticated non-legacy predecessor prefix; `judgement` verifies every obligation with contribution ids and `plan` has matching pins; revision path set empty | every obligation is carried with trusted provenance |
| T2 | verified A/B/C have distinct globs; predecessor-to-current revision paths match only A although the PR-wide path set also contains B | only A regenerates with `path_touched`; B/C carry their own provenance |
| T3 | predecessor plan changes either policy version or protocol hash, or is absent | every obligation regenerates with `pin_changed` |
| T4 | one predecessor obligation is non-verified; another is verified and untouched | the non-verified obligation regenerates with `not_verified`; the verified obligation becomes `CarriedEvidence` |
| T5 | a current obligation is absent from predecessor `judgement.payload["obligations"]` | it regenerates with `new_obligation` |
| T6 | predecessor judgement is absent | every obligation regenerates with `no_prior_judgement`; no carried evidence is constructed |
| T7 | `job.predecessor_job is None` | every obligation regenerates with `no_predecessor`, `source_job is None`, and no reader call occurs |
| T8 | a predecessor judgement has an unchanged verified obligation but omits/malforms its `contributing_attempts[obligation_id]` | `ReuseError`; no `carry_over` entry is appended |
| T9 | any mix of reuse and regeneration | recorded `reused` serializes the full `CarriedEvidence`; `regenerated` and `reasons` cover every current obligation exactly once |
| T10 | malformed judgement or plan pin inside a trusted prefix | `ReuseError`; no `carry_over` entry is appended |
| T11 | `record.append` raises `AppendFailed` | exception propagates and no result is returned |
| T12 | repository/snapshot mismatch | `ReuseError`; reader and writer are untouched |
| T13 | identical facts and immutable trusted prefix twice | byte-identical results and equivalent payloads |
| T14 | predecessor has a chain/HMAC break, an unavailable-key/unkeyed segment, legacy rows, or no rows | every obligation regenerates as `untrusted_predecessor`; no judgement/pin row is read |

## 9. Requirements this part answers for

Accountable: RQA-FR-005, RQA-FR-006, RQA-FR-007, RQA-FR-018, RQA-FR-020.

- **RQA-FR-005** → an unchanged verified result becomes `CarriedEvidence`; P-07, not P-13, materialises
  the current judgement and P-02/P-06 enforce the no-harness path. T1.
- **RQA-FR-006** → each current obligation is invalidated only when
  `rqa.protocol.paths.matches()` matches one of `facts.changed_paths`. T2.
- **RQA-FR-007** → the complete reused evidence, regenerated ids, and one reason per current
  obligation are recorded. T9.
- **RQA-FR-018** → the same path-and-pin rules apply to every predecessor, including a remediation
  successor; no special case broadens invalidation. T2.
- **RQA-FR-020** → every trustworthy unchanged `VERIFIED` predecessor result is carried with durable
  authenticated judgement and attempt provenance; an untrusted predecessor safely regenerates. T1, T4, T14.
