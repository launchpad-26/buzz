---
id: layers-observability-audit-log
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
relationships:
  - type: references
    target: architecture-flows-event-ingestion
  - type: depends-on
    target: architecture-principles-community-is-security-boundary
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "buzz-audit's own crate doc comment describes it as a tamper-evident, per-community hash-chain audit log: each community owns an independent chain, rows are keyed (community_id, seq), seq is monotonic within a community, and each entry chains to the previous entry of the same community via SHA-256, with community_id folded into the hash so a row lifted out of one community's chain can never verify inside another's."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/lib.rs:1-18"
  - statement: "compute_hash hashes a fixed field order over community_id, seq (big-endian bytes), created_at (normalized through to_storage_precision then rendered via to_rfc3339), action.as_str(), actor_pubkey (with a presence tag byte distinguishing Some(empty) from None), object_id (same presence-tag treatment), detail serialized through canonical_json, and finally prev_hash (or the all-zero GENESIS_HASH sentinel for a community's first entry) -- changing this field order would invalidate every existing chain."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs:26-73"
  - statement: "to_storage_precision truncates a timestamp to microsecond precision (trunc_subsecs(6)) before it is hashed, because chrono's to_rfc3339 emits a variable fractional-digit count (0, 3, 6 or 9 digits) depending on the value, so a nanosecond-precision preimage would hash to a digest that can never be recomputed from the microsecond-precision TIMESTAMPTZ row Postgres round-trips; the crate's own tests (rfc3339_sub_second_width_follows_the_value, storage_precision_timestamps_survive_a_database_round_trip) pin exactly this failure mode as the reason the normalization exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs:11-24"
      - "crates/buzz-audit/src/hash.rs:167-214"
  - statement: "canonical_json recursively serializes a JSON value with object keys sorted into a BTreeMap before hashing, so the digest is deterministic regardless of the source object's key insertion order; the canonical_json_key_order_is_stable test asserts two objects built with the same keys in different insertion order canonical-serialize identically."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs:80-116"
      - "crates/buzz-audit/src/hash.rs:267-271"
  - statement: "AuditService::log acquires a per-community Postgres advisory lock (pg_advisory_lock(hashtextextended(lock_key, 0)), where lock_key namespaces the community UUID under \"buzz_audit:\") before appending, and releases it afterward via pg_advisory_unlock even if the append panics -- the panic is caught with std::panic::AssertUnwindSafe(..).catch_unwind() so the unlock query still runs, then the panic is resumed via std::panic::resume_unwind so it still propagates. This serializes writes within one community while different communities' locks never contend."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:26-30"
      - "crates/buzz-audit/src/service.rs:53-85"
  - statement: "log_inner reads the current head row (MAX seq) scoped to community_id inside a transaction, computes the next seq as prev_seq + 1 (or seq 1 with prev_hash = None for a community's first entry), computes the entry's hash, inserts the row, and commits -- all before the advisory lock taken in log() is released."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:87-157"
  - statement: "verify_chain re-reads one community's rows over an inclusive [from_seq, to_seq] range ordered by seq, recomputes each row's hash and compares it to the stored hash (returning AuditError::HashMismatch{seq} on mismatch), and checks that each row's prev_hash equals the immediately preceding row's stored hash (returning AuditError::ChainViolation{seq} on mismatch); it returns Ok(false) for an empty range rather than treating 'no rows' as vacuously verified."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:159-215"
  - statement: "The audit_log table (migrations/0001_initial_schema.sql) has PRIMARY KEY (community_id, seq) and a separate UNIQUE INDEX idx_audit_log_hash on (community_id, hash); migrations/0029_community_deletion.sql later calls attach_community_write_fence('audit_log'), the same tenant-scoping enforcement mechanism this repository's migration-lint harness applies to other per-community tables, and audit_log is not listed in the 0001 migration's _operator_global_tables allowlist of deliberately non-tenant-scoped tables."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:606-619"
      - "migrations/0001_initial_schema.sql:628-636"
      - "migrations/0029_community_deletion.sql:548"
  - statement: "crates/buzz-relay/src/state.rs wires AuditService behind a bounded (capacity 1000) tokio mpsc channel (audit_tx/audit_rx) served by exactly one spawned worker task that calls log_audit_entry serially as entries arrive; on cancellation the worker closes the receiver (rejecting further sends) and drains every already-buffered entry before exiting, and AuditShutdownHandle::drain triggers that cancellation and waits up to a caller-supplied timeout for the worker to finish."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:697"
      - "crates/buzz-relay/src/state.rs:799-835"
      - "crates/buzz-relay/src/state.rs:1325-1355"
  - statement: "Both production call sites that enqueue an audit entry -- enqueue_event_created_audit in handlers/event.rs and the media-upload handler in api/media.rs -- use audit_tx.send(...).await (backpressure-propagating), not try_send; a comment beside the event.rs call site states this is deliberate, because the advisory lock already limits the audit DB to one in-flight write per community, so a full queue signals genuine audit-DB overload the relay should slow down for, rather than silently dropping the entry or growing unbounded in-memory state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:563-601"
      - "crates/buzz-relay/src/api/media.rs:458-475"
  - statement: "Grepping crates/ for the literal pattern AuditAction:: shows only two of the AuditAction enum's eleven variants are ever constructed outside buzz-audit's own crate: EventCreated (handlers/event.rs) and MediaUploaded (api/media.rs). The other nine variants defined in the enum -- EventDeleted, ChannelCreated, ChannelUpdated, ChannelDeleted, MemberAdded, MemberRemoved, AuthSuccess, AuthFailure, RateLimitExceeded -- have no production call site found anywhere in the crates/ tree at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/action.rs:8-31"
      - "crates/buzz-relay/src/handlers/event.rs:583"
      - "crates/buzz-relay/src/api/media.rs:464"
  - statement: "AuditService::verify_chain and AuditService::get_entries are called nowhere in crates/buzz-relay/src outside a #[cfg(test)] module: the only call sites found are inside handlers/event.rs's tenant-isolation test, which constructs its own AuditService::new(pool.clone()) directly rather than reading it through any HTTP handler or CLI subcommand. No production HTTP endpoint or buzz-cli/buzz-admin subcommand invokes either method at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:1936-1989"
  - statement: "crates/buzz-relay/src/config.rs's audit_enabled field defaults to true (parse_bool(\"BUZZ_AUDIT_ENABLED\", true)), and its doc comment states explicitly that the flag 'does not control the separate moderation_actions audit trail' -- a distinct table maintained by buzz-db (crates/buzz-db/src/store/moderation.rs), outside buzz-audit's scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:302-305"
      - "crates/buzz-relay/src/config.rs:1019"
  - statement: "crates/buzz-relay/src/main.rs constructs a dedicated Postgres connection pool (max 5, min 1 connections) for the audit service only when config.audit_enabled is true, separate from the relay's primary database pool, and logs 'Audit logging disabled by BUZZ_AUDIT_ENABLED' when the flag is false, rather than constructing a service that then silently no-ops."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:367-380"
  - statement: "buzz-audit's own lib.rs doc comment ties this crate's per-community chains to a formal model: 'the audit half of the non-interference floor (auditHeads[c] in MultiTenantRelay.tla)'. docs/spec/MultiTenantRelay.tla declares auditHeads as a state variable annotated 'function: community -> current audit head' and threads it through the spec's state predicates."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/lib.rs:9-11"
      - "docs/spec/MultiTenantRelay.tla:168"
  - statement: "buzz-audit's test suite includes #[ignore = \"requires Postgres\"] integration tests exercising per-community chain start/linking, cross-community isolation (chains_are_independent_per_community), tamper detection (verify_detects_tampering_within_a_community), and cross-community forgery rejection (cross_community_row_does_not_verify) -- alongside always-run unit tests (no #[ignore]) covering hash determinism and the timestamp-precision invariant, so the timestamp/hash-determinism guarantees are checked by just test-unit while the full chain-isolation and tamper-detection guarantees require just test's Postgres fixture."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs:296-539"
      - "crates/buzz-audit/src/hash.rs:118-272"
  - statement: "AuditError's variants carry no community_id or Postgres constraint/table name in their Display text -- only a per-community, chain-meaningless-alone seq -- and the crate's own test (audit_error_text_carries_no_community_id_or_constraint) asserts this directly by constructing each domain-error variant and checking its rendered text against a concrete community id and a list of schema-revealing substrings."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/error.rs:1-41"
      - "crates/buzz-audit/src/error.rs:58-107"
  - statement: "Issue #1135's dispatch brief (the batch run for parent Feature #611) names #1139 (logging) and #1144 (structured-logging) as sibling tasks documenting general application logging, and instructs this node to stay scoped to buzz-audit's hash-chain audit logging specifically rather than general application logging or tracing/metrics."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1135 task dispatch brief (corpus-batch-author, Feature #611 batch run)"
---

# Audit log

## Definition

The **audit log**, in Buzz, is a tamper-evident, **per-community** SHA-256 hash chain
recording security- and compliance-relevant actions -- implemented entirely in the
`buzz-audit` crate and backed by the single `audit_log` Postgres table. It is a distinct
concept from Buzz's general application logging (the `tracing`-based diagnostic output
covered by other nodes in this `layers/observability/` family): where general logging is
for developers debugging behavior, the audit log is an append-only, cryptographically
chained record built specifically so that a tampered or replayed entry can be detected
after the fact.

Each community owns its own independent chain. Rows are keyed `(community_id, seq)`,
`seq` is monotonic *within a community*, and each entry's hash is computed over a fixed
field order that hashes `community_id` first -- so a row copied out of one community's
chain and reinserted into another's can never re-verify, because recomputing its hash
under the new `community_id` produces a different digest. This mirrors, and is explicitly
tied by the crate's own doc comment to, `auditHeads[c]` in the repository's
`MultiTenantRelay.tla` formal spec: an audit observation reveals only its own community's
head.

## How an entry is chained

`compute_hash` (in `hash.rs`) hashes, in this fixed order: `community_id`, `seq` (as
big-endian bytes), a storage-precision-normalized `created_at`, the action string,
`actor_pubkey` and `object_id` (each with a one-byte presence tag distinguishing
`Some(empty)` from `None`), the `detail` JSON payload (via a canonical, sorted-key
serialization so the digest doesn't depend on key insertion order), and finally
`prev_hash` -- or an all-zero `GENESIS_HASH` sentinel for a community's first entry. This
order is fixed by design: changing it would invalidate every chain already written.

A normalization step exists specifically to keep this hash reproducible: Postgres'
`TIMESTAMPTZ` column stores microsecond precision, but a wall-clock timestamp
(`Utc::now()`) can carry nanosecond precision, and `chrono`'s RFC-3339 rendering emits a
variable number of fractional digits depending on the value. Left unnormalized, an entry
would be hashed against one string and later recomputed against a different one read back
from the database -- silently failing every `verify_chain` call with `HashMismatch`. The
crate truncates every `created_at` to microsecond precision (`to_storage_precision`)
*before* hashing, and the crate's own tests pin this exact failure mode as the reason the
truncation exists.

## Writing an entry

`AuditService::log` appends to the calling community's chain under a **per-community
Postgres advisory lock** (`pg_advisory_lock`, keyed by a hash of the community UUID), so
writes to one community's chain serialize while different communities' writes proceed
independently -- a global lock across every tenant would be both a throughput bottleneck
and a cross-tenant timing side channel. Inside the lock, `log_inner` reads the community's
current head row, computes the next `seq` and hash, inserts the row, and commits, all in
one transaction; the advisory lock is released afterward regardless of outcome (even a
panic during the append is caught, the lock released, and the panic then re-raised, so a
crash never leaves the lock held).

The relay does not call `AuditService::log` synchronously from request handlers. Instead,
`AppState` wires a bounded (capacity 1000) `tokio::mpsc` channel with exactly one
dedicated worker task consuming it and calling the append serially. The two production
call sites that produce entries today -- `enqueue_event_created_audit` in
`handlers/event.rs` (for `EventCreated`) and the media-upload handler in `api/media.rs`
(for `MediaUploaded`) -- both use `.send(...).await`, not `try_send`, so a full channel
propagates backpressure to the caller instead of silently dropping the entry. This is a
deliberate choice recorded in a comment beside the event.rs call site: because the
advisory lock already limits the audit database to one in-flight write per community, a
full queue means the audit DB is genuinely overloaded, and the relay slowing its ingest
rate is the intended response -- not accumulating unbounded in-memory entries.

On shutdown, `AuditShutdownHandle::drain` cancels the worker and waits (up to a
caller-given timeout) for it to flush every entry already buffered in the channel before
exiting, rather than dropping in-flight entries at process exit.

## Reading and verifying a chain

`AuditService::get_entries` returns up to `limit` rows for one community starting at a
given `seq`, and `AuditService::verify_chain` re-reads a community's rows over an
inclusive `[from_seq, to_seq]` range, recomputes each row's hash, and checks that each
row's `prev_hash` matches the *stored* hash of the row immediately before it -- surfacing
`AuditError::HashMismatch` (recomputed hash disagrees with the stored one) or
`AuditError::ChainViolation` (the link between two rows is broken) as distinct, precisely
attributed error variants. An empty range returns `Ok(false)` rather than being treated as
vacuously verified.

Both methods are exercised thoroughly by the crate's own test suite -- including
integration tests (gated behind `#[ignore = "requires Postgres"]`, so they run under
`just test` but not `just test-unit`) that plant a tampered row or forge a cross-community
replay and assert the specific error each produces. **At this revision, however, neither
method has a production caller.** The only call sites in `crates/buzz-relay/src` for
either method are inside a `#[cfg(test)]` tenant-isolation test in `handlers/event.rs`,
which constructs its own `AuditService` directly rather than going through any HTTP
handler or CLI subcommand. There is currently no operator-facing way -- no HTTP endpoint,
no `buzz-cli` or `buzz-admin` subcommand -- to actually read back or verify a community's
audit chain in a running relay; the read/verify capability exists and is tested, but is
not yet wired to any surface an operator can reach.

## Enablement

Audit logging is controlled by the `audit_enabled` config field (`BUZZ_AUDIT_ENABLED`
environment variable, **default `true`**). When enabled, `main.rs` opens a small,
dedicated Postgres connection pool (max 5, min 1 connections) specifically for the audit
service, separate from the relay's primary database pool. When disabled, no `AuditService`
is constructed at all and the relay logs that audit logging is disabled, rather than
constructing a service that silently no-ops. `BUZZ_AUDIT_ENABLED` is not documented in
`.env.example` at this revision.

## Use cases

A reader reaches for this node when they need to know: what guarantees the audit chain
actually provides (per-community isolation, tamper-evidence, not confidentiality --
`community_id` is hashed in, not encrypted), which actions are actually recorded in
practice today versus merely defined as possible actions, whether audit writes can block
or drop under load (they backpressure, they don't silently drop), and whether a chain can
currently be verified or read back from a running relay (not yet, outside tests).

## Boundaries and non-goals

This node does **not** cover:

- **General application logging** -- the `tracing`-based diagnostic output covered by
  sibling nodes in this `layers/observability/` family (general logging, structured-field
  logging). The audit log's `tracing::debug!`/`tracing::error!` calls around its own
  operations are themselves an example of that general logging, not the audit log itself.
- **The `moderation_actions` operator-action trail.** This is a **separate table**,
  maintained by `buzz-db` (`crates/buzz-db/src/store/moderation.rs`), not `buzz-audit`.
  `crates/buzz-relay/src/config.rs`'s own doc comment on `audit_enabled` states directly
  that this flag does not control that separate trail. This node's `buzz-audit` scope and
  that system are two different audit surfaces in this codebase; do not conflate them.
- **Tracing spans and metrics.** `AuditService`'s methods are instrumented with
  `#[datastore_span(...)]` (from `buzz-datastore-tracing`) and emit
  `buzz_audit_log_errors_total` / `buzz_audit_log_seconds` metrics -- but the
  instrumentation mechanics themselves belong to the datastore-tracing and metrics nodes,
  not this one.
- **A full enumeration of `AuditAction`'s eleven variants' intended future call sites.**
  This node records, as a fact found while researching it, that only two variants
  (`EventCreated`, `MediaUploaded`) have a production call site today; it does not assert
  why the other nine are unwired, or when (if ever) they will be.

## Scope and omissions

**This document covers** the hash-chain mechanics, per-community isolation guarantee,
write-path design (advisory lock, bounded async channel, backpressure, graceful drain),
read/verify-path mechanics and their current lack of a production caller, and the
`BUZZ_AUDIT_ENABLED` enablement switch, all as implemented in `buzz-audit` and wired into
`buzz-relay` at the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| General `tracing`-based application logging | Sibling `layers/observability/` logging nodes (#1139, #1144) |
| The separate `moderation_actions` operator-action trail | Not this node's scope; a different `buzz-db` table |
| Datastore-tracing instrumentation mechanics (`#[datastore_span]`) | #1136 (datastore-tracing), not yet a merged corpus node at this revision |
| Metrics emitted alongside audit writes (`buzz_audit_log_*`) | Not investigated for this node |

**Expected but not verified when this node was written:**

- **Whether the nine unwired `AuditAction` variants are an intentional incremental
  rollout or an oversight.** This node found, by direct grep, that only `EventCreated` and
  `MediaUploaded` are ever constructed in production code; it does not know, and does not
  assert, why `ChannelCreated`, `MemberAdded`, `AuthFailure`, and the rest remain unwired.
  - **Candidate follow-up** (not filed as part of this task, per the batch-run instruction
    to note rather than file it): confirm with whoever owns the audit-log rollout whether
    the remaining `AuditAction` variants are planned, and if so, track wiring them as their
    own implementation work.
- **Whether an operator-facing surface for `verify_chain`/`get_entries` is planned.** Both
  methods are implemented and tested, but neither is reachable from any HTTP endpoint or
  CLI subcommand today -- this node records that gap without asserting whether closing it
  is in scope for any existing tracked work.
- **`.env.example` does not document `BUZZ_AUDIT_ENABLED`**, unlike several other
  environment variables covered by sibling observability nodes; whether that is an
  intentional omission (the default is `true` and most deployments want it on) was not
  established.
