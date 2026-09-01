---
id: layers-data-postgres-audit-tables
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion) with no `data` member; a node whose path lives under `layers/` takes `type: layers`, the same choice the merged/open siblings under `layers/data/object-storage/` (media-objects, minio, on open PR #1874) already made over `templates/datastore.md`'s own `type: architecture` suggestion, disclosed as a tension in each of their own evidence ledgers."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1075 assigns this document the path launchpad/docs/corpus/layers/data/postgres/audit-tables.md directly via its own corpus-plan:v2 alias header comment and Objective sentence, and describes the subject as 'the single canonical data entity node for audit tables.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1075, read directly via gh issue view"
  - statement: "Issue #1075's Definition of Done requires this document to define identity/key and semantic ownership; summarize fields by meaning without duplicating generated schema detail; define relationships, lifecycle and invariants; and link authoritative migration/schema and read/write code paths rather than copying DDL — distinct in wording from sibling issue #1070's (media-objects) Definition of Done, which instead requires stating whether the store is authoritative/derived/cache/transport and describing lifecycle/retention/tenancy/failure. #1075's wording maps onto templates/data-entity.md's required sections (Identity, Attributes and shape, Invariants, Relationships, Provenance, Storage pointer); #1070's maps onto templates/datastore.md's sections instead. This document follows data-entity.md's shape for that reason, checked by reading both issue bodies directly rather than assumed from a shared batch template."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1075 and launchpad-26/buzz#1070 definitions of done, read directly via gh issue view"
  - statement: "architecture-containers-postgres is a merged, validated node on origin/launchpad (confirmed via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus) whose own body names audit_log as one of the relational tables Postgres holds ('the relational tables for communities, channels, membership, moderation, workflows, push state, and audit') and documents the 5-connection, BUZZ_AUDIT_ENABLED-gated audit pool buzz-relay opens directly against the same database, distinct from buzz-db's own pool."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "migrations/0001_initial_schema.sql defines audit_log with columns community_id (UUID NOT NULL REFERENCES communities(id)), seq (BIGINT NOT NULL), hash (BYTEA NOT NULL), prev_hash (BYTEA, nullable), action (VARCHAR(64) NOT NULL), actor_pubkey (BYTEA, nullable), object_id (TEXT, nullable), detail (JSONB, nullable) and created_at (TIMESTAMPTZ NOT NULL DEFAULT NOW()), with PRIMARY KEY (community_id, seq) and a separate UNIQUE INDEX idx_audit_log_hash ON audit_log (community_id, hash); the migration's own comment states 'Per-community hash chain: uniqueness (community_id, seq) and (community_id, hash). One chain per tenant.'"
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "crates/buzz-audit/src/lib.rs's own module doc comment states the crate implements a 'Tamper-evident, per-community hash-chain audit log', that 'the audit_log table is owned by the consolidated 0001 migration — this crate is pure chain logic and ships no DDL', that community_id is folded into the hash so 'a row lifted out of one community's chain can never verify inside another's', and that writes for a given community are serialized by a per-community Postgres advisory lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/lib.rs"
  - statement: "crates/buzz-audit/src/entry.rs's AuditEntry doc comments state seq is 'monotonic within one community' and prev_hash 'chains to the previous entry of the same community', that community_id 'leads the primary key', that object_id is 'a generic identifier of the object acted upon (event id hex, channel UUID, media sha256, ...)' resolved by the relay under community_id, and that detail is 'arbitrary JSON context. Included in the hash (serialized with sorted keys for determinism) so tampering with it is detectable.' NewAuditEntry's own comment states community_id is 'the server-resolved tenant (from the request's TenantContext), never a client-supplied value', typed as CommunityId rather than a raw Uuid 'so the provenance rule is visible in the signature', and that detail 'must not' carry bearer-token material."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/entry.rs"
  - statement: "crates/buzz-audit/src/action.rs's AuditAction enum has exactly eleven variants (EventCreated, EventDeleted, ChannelCreated, ChannelUpdated, ChannelDeleted, MemberAdded, MemberRemoved, AuthSuccess, AuthFailure, RateLimitExceeded, MediaUploaded), each with a stable snake_case as_str() string ('event_created', 'event_deleted', ... 'media_uploaded') used identically for hash computation and for the stored `action` column value; FromStr rejects any string outside that set with an explicit 'unknown audit action' error rather than silently defaulting."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/action.rs"
  - statement: "crates/buzz-audit/src/hash.rs's compute_hash function computes SHA-256 over a fixed field order — community_id first (as raw bytes), then seq (big-endian i64), then created_at (RFC3339 string, normalized through to_storage_precision), then action.as_str(), then a presence-tagged actor_pubkey, then a presence-tagged object_id, then canonical_json(detail) (BTreeMap-sorted keys for deterministic serialization across machines), then prev_hash or the 32-byte all-zero GENESIS_HASH sentinel when prev_hash is None — and its own doc comment states 'Field order is fixed — changing it invalidates all existing chains' and 'The community_id is hashed first so chain identity carries the tenant: an entry cannot be lifted out of one community's chain and re-verified inside another.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs"
  - statement: "hash.rs's to_storage_precision truncates a DateTime<Utc> to microsecond resolution before it is hashed, and its own doc comment explains why: audit_log.created_at is a Postgres TIMESTAMPTZ (microsecond resolution), chrono's to_rfc3339() emits a variable digit count (0/3/6/9 fractional digits) depending on the value's own precision, so hashing an untruncated nanosecond timestamp produces a digest 'that can never be recomputed from the stored row'; compute_hash calls to_storage_precision itself as the single enforcement point so no future write path can reintroduce the write/read preimage split by forgetting to truncate first. hash.rs's own test suite (rfc3339_sub_second_width_follows_the_value, compute_hash_normalizes_sub_microsecond_timestamps, storage_precision_timestamps_survive_a_database_round_trip) pins this behavior directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs"
  - statement: "crates/buzz-audit/src/service.rs's AuditService::log acquires a per-community Postgres advisory lock (pg_advisory_lock(hashtextextended($1, 0)) keyed on a 'buzz_audit:{community_id}' namespaced string) before appending, wraps the append in a transaction, and releases the advisory lock afterward regardless of outcome (including on panic, via catch_unwind); its own comment states this serializes writes 'so the chain stays consistent across relay processes' while 'different communities proceed in parallel' rather than contending on one global lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
  - statement: "service.rs's log_inner reads the calling community's current chain head with 'SELECT seq, hash FROM audit_log WHERE community_id = $1 ORDER BY seq DESC LIMIT 1' inside the same transaction as the insert, sets seq = prev_seq + 1 (or seq = 1, prev_hash = NULL for a community's first entry when no head row exists), computes the new row's hash, and inserts all nine columns in one INSERT before committing — the write path that establishes the chain's per-community monotonic seq and linkage."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
  - statement: "service.rs's verify_chain reads exactly one community's rows in a seq range ('WHERE community_id = $1 AND seq BETWEEN $2 AND $3 ORDER BY seq ASC'), recomputes each row's hash from its stored fields, checks each entry's stored prev_hash against the immediately preceding entry's recomputed hash, and returns AuditError::ChainViolation{seq} or AuditError::HashMismatch{seq} naming the first offending seq on failure, Ok(false) for an empty range, and Ok(true) when the segment is internally consistent; get_entries performs the equivalent community-scoped, seq-ordered, limited read without verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
  - statement: "service.rs's own #[cfg(test)] suite (community_chain_starts_at_seq_1_with_null_prev, chain_links_within_one_community, chains_are_independent_per_community, verify_detects_tampering_within_a_community, cross_community_row_does_not_verify, verify_empty_range_is_false) is #[ignore]-gated on a live Postgres and directly exercises the invariants above: a community's chain starts at seq 1 with a NULL prev_hash; two communities' chains never link to each other even when writes interleave; tampering with a stored column (actor_pubkey) after the fact is caught by verify_chain as a HashMismatch at the tampered seq; and a row forged with another community's stored hash at seq 1 fails verification under the forged community's own id, because community_id is folded into the hash and recomputing it under a different id changes the digest."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
  - statement: "migrations/0029_community_deletion.sql's attach_community_write_fence('audit_log') call (line 548) attaches the enforce_community_write_fence() BEFORE INSERT/UPDATE/DELETE trigger to audit_log, alongside events, channels, and every other community-scoped table this migration lists; that trigger function calls assert_community_write_allowed(community_id) for the row's community_id, and assert_community_write_allowed raises 'community write fenced: community % generation %' (SQLSTATE object_not_in_prerequisite_state) when that community's lifecycle is not 'active' — so once a community's deletion lifecycle leaves 'active', new audit_log rows for it are rejected at the database level, not merely by application-level checks."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-relay/src/main.rs constructs the audit pool only when config.audit_enabled is true (parsed from BUZZ_AUDIT_ENABLED, default true, per crates/buzz-relay/src/config.rs's parse_bool call and its own doc comment 'Set BUZZ_AUDIT_ENABLED=false for deployments that do not require it'), opening a dedicated sqlx::postgres::PgPoolOptions pool (max_connections(5), min_connections(1)) against the same database_url buzz-db's own pool uses, independently of buzz_db::Db, and logs 'Audit service ready' or 'Audit logging disabled by BUZZ_AUDIT_ENABLED' accordingly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "AuditAction::EventCreated is constructed as a literal audit-log action at crates/buzz-relay/src/handlers/event.rs:583, one of thirteen files across crates/buzz-relay/src that reference AuditService or an audit_service field/variable (api/admin/mod.rs, api/bridge.rs, api/git/policy.rs, api/git/transport.rs, api/invites.rs, api/media.rs, api/operator.rs, handlers/event.rs, handlers/identity_archive.rs, handlers/relay_admin.rs, main.rs, state.rs, workflow_sink.rs) — the write side of audit_log is exercised broadly across the relay's own request handlers, not confined to one code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/state.rs"
  - statement: "The only call sites found in this repository for AuditService::verify_chain and AuditService::get_entries — the log's own read/verification methods — are inside a #[cfg(test)] module in crates/buzz-relay/src/handlers/event.rs (around lines 1939-1990), asserting cross-community isolation in a test; no production (non-test) code path in buzz-relay, buzz-cli, or buzz-admin was found calling either method. Read access to audit_log's own chain-verification guarantee is exercised by tests today, not by any operator-facing feature this task located."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
    confidence: 0.75
  - statement: "crates/buzz-db/src/store/deletion.rs's EXPECTED_SCOPED_TABLES constant (the exact set of community-scoped tables the whole-community deletion inventory checks before approving a deletion) and its PURGE_SCOPED_TABLES constant (the foreign-key-safe child-before-parent purge order) both include audit_log; the module's own doc comment describes the module as owning the 'durable whole-community deletion lifecycle,' and DeletionStage's fixed, forward-only stage order names PostgresPurged as the stage in which all EXPECTED_SCOPED_TABLES rows, audit_log included, are physically deleted. Audit rows are therefore not retained independently of the community that produced them — a permanently deleted community's audit_log rows are purged along with its other tenant-scoped data, not kept as a standing record outside the community's own lifecycle."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "migrations/0006_moderation.sql defines a separate moderation_actions table (community_id, id, actor_pubkey, action, target_pubkey, target_event_id, channel_id, reason_code, public_reason, private_reason, matched_principal, created_at; PRIMARY KEY (community_id, id)) under its own '── Moderation audit ──' section comment, distinct from audit_log's hash-chain schema and primary key shape; issue #1084 ('task: document layers/data/postgres/moderation-tables.md') is the separate task naming that table as its own subject, confirmed by reading both the issue title and the migration's DDL directly rather than assumed."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1084, read directly via gh issue list; migrations/0006_moderation.sql read directly"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Data entity: the `audit_log` hash chain

The **`audit_log` table** is Buzz's tamper-evident, per-community record of
actions the relay performed or observed. This document is a **data-entity**
view of it: its identity and key, what each field means, the invariants that
must hold about any row in it, its relationships to other rows and tables, and
where it is stored — not a restatement of `architecture-containers-postgres`'s
job (that Postgres exists, its connection pools, and its migration mechanism,
linked below via `part-of`) and not `moderation-tables.md`'s job (issue
#1084, not yet drafted at this node's authoring time): `moderation_actions`
is a structurally distinct table (its own primary key is `(community_id,
id)`, not a hash chain) recording moderator decisions, defined in its own
`migrations/0006_moderation.sql` section, and is out of scope here.

## Identity

A row's identity is the pair **`(community_id, seq)`** — `audit_log`'s
declared primary key in `migrations/0001_initial_schema.sql`. `seq` is a
`BIGINT`, monotonic **within one community only**: `AuditService::log_inner`
reads the calling community's current head (`SELECT seq, hash FROM audit_log
WHERE community_id = $1 ORDER BY seq DESC LIMIT 1`) inside the same
transaction as the insert, and assigns `seq = prev_seq + 1` (or `seq = 1`
for a community's first entry). Two different communities' chains both start
at `seq = 1` and number independently — `seq` alone never identifies a row
across communities, only `(community_id, seq)` together does.

A second, independent uniqueness constraint holds per community:
**`(community_id, hash)`** is enforced by `idx_audit_log_hash`, a `UNIQUE
INDEX`, separate from the primary key. `hash` is the row's own SHA-256
digest (see *Invariants*), so this index additionally guarantees no two
rows in one community's chain ever collide on their content hash.

**Semantic ownership.** `audit_log` is owned end-to-end by
`crates/buzz-audit`: the crate's own module doc states plainly that "the
`audit_log` table is owned by the consolidated `0001` migration — this
crate is pure chain logic and ships no DDL." No other crate defines or
alters this table's shape; `crates/buzz-relay` calls into `buzz-audit`'s
`AuditService` rather than writing to the table directly.

## Attributes and shape

Not JSON Schema — `audit_log` is a relational projection with one JSON-typed
column (`detail`), the same treatment `data-entity.md`'s own worked
`thread_metadata` illustration gives a relational table. Each row, per
`migrations/0001_initial_schema.sql` and `crates/buzz-audit/src/entry.rs`:

| Column | Type | Meaning |
|---|---|---|
| `community_id` | `UUID NOT NULL REFERENCES communities(id)` | Server-resolved tenant this entry belongs to; leads the primary key and the hash. |
| `seq` | `BIGINT NOT NULL` | Per-community monotonic sequence number, starting at 1. |
| `hash` | `BYTEA NOT NULL` | SHA-256 of this entry's own fields (see *Invariants*). |
| `prev_hash` | `BYTEA`, nullable | The previous entry's `hash` in *this community's* chain; `NULL` only for a community's first entry. |
| `action` | `VARCHAR(64) NOT NULL` | One of `AuditAction`'s eleven stable snake_case strings (`event_created`, `event_deleted`, `channel_created`, `channel_updated`, `channel_deleted`, `member_added`, `member_removed`, `auth_success`, `auth_failure`, `rate_limit_exceeded`, `media_uploaded`). `FromStr` rejects any other value. |
| `actor_pubkey` | `BYTEA`, nullable | Raw bytes of the Nostr pubkey that performed the action, when the action has one. |
| `object_id` | `TEXT`, nullable | A generic identifier of the object acted upon (event id hex, channel UUID, media sha256, …), per `entry.rs`'s doc comment — "the relay resolves it under `community_id`; it never names an object in another community." |
| `detail` | `JSONB`, nullable | Arbitrary structured context. **Included in the hash** (canonicalized with sorted keys) so tampering with it is detectable; `entry.rs`'s doc comment states this field "must not" carry bearer-token or other secret material. |
| `created_at` | `TIMESTAMPTZ NOT NULL DEFAULT NOW()` | When the row was written. Stored (and hashed) at microsecond precision — see *Invariants*. |

`NewAuditEntry` (the crate's write-side input type, not itself persisted as
a whole) types `community_id` as `CommunityId` rather than a raw `Uuid`
specifically so a client-supplied value can never reach it — `entry.rs`'s
own doc comment: "the only ways to obtain one are host resolution or a
server-scoped DB row — never a value parsed from client input."

## Invariants

- **Hash-chain integrity.** `hash.rs::compute_hash` digests a **fixed field
  order** — `community_id`, `seq`, `created_at`, `action`, a
  presence-tagged `actor_pubkey`, a presence-tagged `object_id`,
  canonicalized `detail`, then `prev_hash` (or the 32-byte all-zero
  `GENESIS_HASH` sentinel for a chain's first entry) — and the function's
  own doc comment states "changing it invalidates all existing chains."
  `service.rs::verify_chain` recomputes this digest per row and compares it
  against the stored `hash`, and separately checks that each row's
  `prev_hash` equals the immediately preceding row's recomputed `hash`;
  `service.rs`'s own `verify_detects_tampering_within_a_community` test
  proves a single tampered column (`actor_pubkey`) is caught as a
  `HashMismatch` at the tampered `seq`.
- **Tenant binding is part of the hash, not just the schema.**
  `compute_hash` hashes `community_id` first, and `hash.rs`'s own doc
  comment states this is deliberate: "an entry cannot be lifted out of one
  community's chain and re-verified inside another's." `service.rs`'s
  `cross_community_row_does_not_verify` test proves this directly: a row
  forged with community A's stored hash, inserted into community B's
  chain, fails `verify_chain` under B's id because recomputing the hash
  with `community_id = B` no longer matches the digest that was computed
  with `community_id = A`.
- **`created_at` is normalized before it is hashed.** `hash.rs::compute_hash`
  passes `created_at` through `to_storage_precision` (truncating to
  microsecond resolution) before hashing, because `audit_log.created_at` is
  a `TIMESTAMPTZ` (microsecond-precision storage) while an in-process
  timestamp may carry nanosecond digits; the function's own doc comment
  states an untruncated timestamp "hashes to a digest that can never be
  recomputed from the stored row." `service.rs::log_timestamp` truncates
  before storing for the same reason, and `hash.rs`'s own test suite pins
  this failure mode by name.
- **Community write-fence.** `migrations/0029_community_deletion.sql`
  attaches `enforce_community_write_fence()` to `audit_log` (line 548,
  alongside `events`, `channels`, and the rest of this migration's
  community-scoped table list). That trigger calls
  `assert_community_write_allowed(community_id)`, which raises `community
  write fenced: community % generation %` (SQLSTATE
  `object_not_in_prerequisite_state`) whenever the row's community's
  deletion lifecycle is not `'active'`. A community leaving `'active'`
  therefore stops new `audit_log` writes for it at the database level, not
  only through application-level checks.
- **Per-community write serialization.** `AuditService::log` takes a
  Postgres advisory lock keyed on a `buzz_audit:{community_id}`-namespaced
  string (`pg_advisory_lock(hashtextextended($1, 0))`) before reading the
  chain head and appending, releasing it afterward on every path including
  panic (via `catch_unwind`). This is what keeps the monotonic-`seq`
  invariant sound under concurrent writers to the same community's chain
  across relay processes; different communities' locks are independent, so
  writes to separate chains proceed in parallel.

## Lifecycle

`audit_log` rows are append-only for the life of the community they belong
to — nothing in `crates/buzz-audit` or in the schema updates or deletes an
existing row (the only mutation path this task found is the test suite's
own deliberate tampering, used to prove `verify_chain` detects it). That
lifespan is bounded by the **community's** own lifecycle, not treated as
permanent independently of it: `crates/buzz-db/src/store/deletion.rs`'s
whole-community deletion module lists `audit_log` in both
`EXPECTED_SCOPED_TABLES` (the community-scoped tables its pre-deletion
inventory checks) and `PURGE_SCOPED_TABLES` (the child-before-parent
physical-purge order), and its `DeletionStage` enum's fixed, forward-only
stage sequence reaches `PostgresPurged` — the stage at which those tables'
rows, `audit_log` included, are physically deleted. A permanently deleted
community's audit history is deleted with it; the hash chain guarantees
tamper-evidence for a chain that exists, not indefinite retention of that
chain once its community is gone.

## Relationships

- **Foreign key.** `community_id` carries `REFERENCES communities(id)` in
  the table's own DDL — a row cannot name a community that does not exist.
  This is a row-to-row relationship in code, not (yet) a corpus
  `relationships` edge, because no `communities`-entity corpus node is
  merged on `origin/launchpad` today.
- **Corpus-level.** This node declares one `relationships` entry:
  `part-of` → `architecture-containers-postgres` (merged), naming that
  `audit_log` is one of the tables the Postgres container document already
  lists. No `references` edge is declared toward any `layers/data/postgres/*`
  sibling (`moderation-tables`, `events-table`, `channels-table`, and the
  rest) — none is merged on `origin/launchpad` at this node's authoring
  time, and a `relationships.target` naming an unmerged id is a hard
  validation error on the branch this document is merging into, per
  `AGENTS.md`'s step 9.

## Provenance

`audit_log` is a **purely server-derived projection with no Nostr event of
its own** — `crates/buzz-audit/src/lib.rs`'s own module doc states plainly
that the crate "is pure chain logic and ships no DDL" and describes no
event-kind mapping anywhere in the crate. A row is written whenever relay
code on one of thirteen call sites across `crates/buzz-relay/src`
(`handlers/event.rs`, `handlers/identity_archive.rs`,
`handlers/relay_admin.rs`, several files under `api/`, `state.rs`,
`workflow_sink.rs`, and `main.rs` itself for wiring) constructs a
`NewAuditEntry` and calls `AuditService::log` — reacting to relay-internal
actions (an event being created or deleted, a channel changing, a client
authenticating, a rate limit firing, a media upload completing — the eleven
`AuditAction` variants), not to any one Nostr event kind's own tag or
content shape the way an entity documented by the event-kind template
would be.

## Storage pointer

Postgres, table `audit_log`, one row per hash-chain entry across every
community. `architecture-containers-postgres` (linked above via `part-of`)
is the node for the container's own facts — connection pooling, the
`BUZZ_AUTO_MIGRATE` gate, partitioning — and already states that
`buzz-relay`'s own `main.rs` opens a dedicated 5-connection pool for this
table (`max_connections(5)`, `min_connections(1)`), gated on
`BUZZ_AUDIT_ENABLED` (default `true`, per `crates/buzz-relay/src/config.rs`'s
`parse_bool` call), independently of `buzz-db`'s own connection pool. That
gating, pool-sizing, and migration-ordering detail is not repeated here —
this node names the table `audit_log` lives in and links out, per
`AGENTS.md`'s links-instead-of-duplicating rule.

## Scope and omissions

**This document covers** `audit_log`'s identity and key, its column shape
and field meanings, the invariants its hash-chain and write-fence
mechanisms enforce, its append-only-until-community-deletion lifecycle,
its relationships to `communities` and to the
`architecture-containers-postgres` container node, its provenance as a
server-derived (not event-sourced) table, and where it is physically
stored.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `moderation_actions` — a structurally distinct table (own primary key, no hash chain) recording moderator decisions | `moderation-tables.md`, issue #1084, not yet drafted at this node's authoring time |
| Postgres's own connection pooling, migration mechanism, and deployment/partitioning facts | `architecture-containers-postgres` (merged), linked above via `part-of` |
| The full set of `_operator_global_tables` and other tables `migrations/0001_initial_schema.sql` defines | Future `layers/data/postgres/*` corpus nodes, not this one |
| Whether any staging/production deployment sets `BUZZ_AUDIT_ENABLED=false` | Not established here — `architecture-containers-postgres` itself names the identical gap for `BUZZ_AUTO_MIGRATE`; this repository's deployment pipelines live in separate private repositories this task did not open |

**Expected but not verified when this node was written:**

- **Whether `AuditService::verify_chain`/`get_entries` having no production
  caller is deliberate or incomplete was not established.** The only call
  sites found for either method are inside a `#[cfg(test)]` module in
  `crates/buzz-relay/src/handlers/event.rs` (asserting cross-community
  isolation). No operator-facing endpoint, CLI subcommand, or scheduled job
  invoking either method was found in `buzz-relay`, `buzz-cli`, or
  `buzz-admin`. This is recorded as a checked gap, not resolved either way.
- **Whether the eleven `AuditAction` variants are a complete or intended-
  to-grow set was not evaluated.** The write side is exercised across
  thirteen files in `crates/buzz-relay/src`, but whether every
  auditable relay action is covered, versus some actions deliberately
  going unlogged, was not established from the repository alone.
- **Production/staging `BUZZ_AUDIT_ENABLED` and connection-pool topology**
  were not checked — those pipelines (`squareup/block-coder-tf-stacks`,
  `squareup/sprout-oss`) live in separate private repositories this task
  did not open, the same limitation `architecture-containers-postgres`
  records for the identical class of question about `BUZZ_AUTO_MIGRATE`.
- **Cross-model review was not run.** This task's own instructions scope
  this session to isolate/plan/build/verify/commit only, with the batch
  owner's later bundling step responsible for adjudication and any
  cross-model pass.
