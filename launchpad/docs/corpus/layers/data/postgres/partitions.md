---
id: layers-data-postgres-partitions
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
  - statement: "node.schema.json's type enum has no `datastore` member (its 13 values are architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion), so this node uses type: layers rather than the `templates/datastore.md` worked example's own type choice, per this batch's established precedent for every layers/data/... document."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node's body is shaped from templates/datastore.md's required-sections list (purpose/scope, schema/namespace inventory, migration mechanism, access-pattern summary, operational characteristics, scope and omissions), narrowed to one cross-cutting storage-layout mechanism (monthly range partitioning of two tables) rather than templates/datastore.md's own broader subject of one whole running technology instance, because the issue's own Definition of Done asks specifically what a store is (authoritative/derived/cache/transport), what it owns, its lifecycle/retention and consistency semantics, its tenancy/security boundary and failure behavior, and to link schema/migrations/code/tests rather than copy DDL -- the same axes templates/datastore.md's required sections cover, at partition scope rather than instance scope."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/launchpad-26/buzz/issues/1085"
      - "launchpad/docs/corpus/templates/datastore.md"
    confidence: 0.85
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md exists on origin/launchpad with id architecture-containers-postgres and type: architecture, documenting the Postgres container as a whole (buzz-db as its data-access component, its design invariants) at one line of depth, which this node zooms into for the partitioning mechanism specifically."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "No layers/data/postgres/* sibling document exists on origin/launchpad at the recorded revision, confirmed by listing that tree, so this node declares no relationships to any such sibling."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/layers') -> empty"
  - statement: "buzz-db's crate-level doc comment states two of its own design invariants verbatim: \"Events table is partitioned by month on created_at\" and \"No FK references to partitioned tables.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:8"
      - "crates/buzz-db/src/lib.rs:9"
  - statement: "The events table is declared PARTITION BY RANGE (created_at) with primary key (community_id, created_at, id), and migration 0001 creates seven initial monthly range partitions (events_p_past, events_p2026_01 through events_p2026_06, events_p_future) each with an explicit FOR VALUES FROM/TO bound."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190"
      - "migrations/0001_initial_schema.sql:235"
      - "migrations/0001_initial_schema.sql:237-252"
  - statement: "The delivery_log table is declared PARTITION BY RANGE (delivered_at) with primary key (delivered_at, id), and migration 0001 creates six initial monthly range partitions (delivery_log_p_past, delivery_log_p2026_03 through delivery_log_p2026_06, delivery_log_p_future)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:329-341"
      - "migrations/0001_initial_schema.sql:343-354"
  - statement: "crates/buzz-db/src/partition.rs's PARTITIONED_TABLES constant names exactly events and delivery_log as the only tables the runtime partition manager will act on, and its own doc comment states this allowlist \"prevents DDL injection\" because partition DDL identifiers cannot be parameterized."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/partition.rs:11-12"
  - statement: "ensure_future_partitions computes, for each of the next N months (N given by the caller), a monthly [start, end) date range and a suffix, validates the target table against the allowlist and the suffix/date strings against strict character-class regexes (validate_partition_suffix, validate_date_str) before interpolating them into a CREATE TABLE .. PARTITION OF .. FOR VALUES FROM .. TO .. statement, and treats a Postgres 42P17 \"would overlap partition\" error as success rather than failure, on the stated grounds that a fresh schema's catch-all *_p_future partition may already cover the requested month."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/partition.rs:15-56"
      - "crates/buzz-db/src/partition.rs:74-150"
  - statement: "crates/buzz-relay/src/main.rs calls db.ensure_future_partitions(3) once at relay startup (unconditionally, not gated on BUZZ_AUTO_MIGRATE), and the module's own doc comment states it is additionally intended to run monthly via cron, though no cron invocation was found in this repository at the recorded revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:200-202"
      - "crates/buzz-db/src/partition.rs:3"
  - statement: "A repository-wide search for partition retention or removal logic (grep for \"detach partition\", \"drop.*partition\", \"retention\" across .rs and .sql files) found no code path that ever drops, detaches, or archives an old partition; ensure_future_partitions only ever creates partitions for future months, never removes past ones."
    entry_class: FACT
    evidence:
      - "grep(pattern='detach partition|drop.*partition|retention', paths=['**/*.rs','**/*.sql']) -> no partition-removal call site found"
  - statement: "Because no partition-drop or archival mechanism exists in this codebase, the events and delivery_log partition sets grow monotonically for as long as a deployment runs, and any pruning of old partitions today would have to happen as an out-of-band, unreviewed operator action rather than through code this node can cite."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/partition.rs:15-150"
      - "grep(pattern='detach partition|drop.*partition|retention', paths=['**/*.rs','**/*.sql']) -> no partition-removal call site found"
    confidence: 0.85
  - statement: "Migration 0021 creates a DEFERRABLE INITIALLY DEFERRED constraint trigger (events_created_at_floor, function events_created_at_floor_guard) on the events table that re-evaluates clock_timestamp() at COMMIT and rejects a channel-bearing row whose created_at is older than a session-scoped buzz.created_at_floor GUC (seconds), and its own comment states this exists to make the ingest-time created_at envelope a commit-time storage invariant so that cursor pages served from a read replica behind a fence timestamp cannot miss a row."
    entry_class: FACT
    evidence:
      - "migrations/0021_created_at_fence_floor.sql:1-17"
      - "migrations/0021_created_at_fence_floor.sql:44-74"
  - statement: "Migration 0021's own comment states that because the constraint trigger is created on the partitioned events parent, PostgreSQL's CREATE TABLE .. PARTITION OF clones it onto every existing partition and onto partitions created later, so partition rotation (ensure_future_partitions creating a new monthly child) keeps the guard without any additional code."
    entry_class: FACT
    evidence:
      - "migrations/0021_created_at_fence_floor.sql:38-42"
  - statement: "crates/buzz-db/src/replica_fence.rs's verify_floor_guard_catalog function queries pg_inherits for every partition child of events (UNION ALL with the events parent itself) and asserts, per relation, that a correctly-shaped events_created_at_floor trigger (right function, DEFERRABLE, INITIALLY DEFERRED, row-level, AFTER not BEFORE, firing on both INSERT and UPDATE) exists; any relation missing it is collected and returned as an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/replica_fence.rs:312-360"
  - statement: "crates/buzz-db/src/migration.rs's run_migrations_locked calls verify_floor_guard_catalog immediately after running the embedded SQLx migrator, and its own comment states migration \"fails closed if any is missing\" -- a partition attached by any path that escapes trigger inheritance (an ATTACH PARTITION or an older code path, per the comment) causes the whole migration run to return an error rather than complete."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/migration.rs:35-47"
  - statement: "Db::spawn_fence_probe's own doc comment states that on any floor-guard verification failure (catalog shape or observed behavior) the background replica-fence probe is never spawned and the fence stays closed, so every cursor page routes to the writer pool -- described in the comment as \"the relay keeps serving -- degraded capacity, never holes.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs:850-873"
  - statement: "crates/buzz-relay/src/main.rs treats a failure of ensure_future_partitions itself (the monthly-partition-creation call, not the floor-guard verification) as non-fatal: the error is logged and relay startup continues, unlike auto-migration failure and deletion-serving-fence validation failure in the same function, both of which abort startup via `?`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:190-202"
  - statement: "If ensure_future_partitions fails to create an upcoming month's partition and no partition covers a given INSERT's created_at (or delivered_at) value, Postgres itself rejects that INSERT with a \"no partition of relation ... found for row\" error at write time -- this exact error text is independently named in scripts/attach-schema-partitions.sql's own comment describing the failure a mis-attached partition produces -- rather than the write silently succeeding into the wrong partition or being dropped."
    entry_class: INFERENCE
    evidence:
      - "scripts/attach-schema-partitions.sql:5-8"
      - "crates/buzz-db/src/partition.rs:15-56"
    confidence: 0.8
  - statement: "Migration 0029's attach_community_write_fence function attaches the community_write_fence_<table> row-level trigger (enforce_community_write_fence, which rejects an INSERT/UPDATE/DELETE naming a non-active community) only to relations for which pg_class.relispartition is false, i.e. to the events and delivery_log partitioned parents, never directly to their partition children; delivery_log is named explicitly in the migration's own list of tables the fence is attached to."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:475-516"
      - "migrations/0029_community_deletion.sql:552"
  - statement: "Because the community write-fence trigger is attached only to the partitioned parent and Postgres clones row-level triggers from a partitioned parent onto its partition children (the same inheritance mechanism migration 0021's comment states for the floor guard), every partition child of events and delivery_log inherits the same community-scoped write fence as its parent without a separate per-partition attach call -- partitioning does not create or widen a tenancy boundary of its own; it inherits the parent table's."
    entry_class: INFERENCE
    evidence:
      - "migrations/0029_community_deletion.sql:475-516"
      - "migrations/0021_created_at_fence_floor.sql:38-42"
    confidence: 0.8
  - statement: "scripts/attach-schema-partitions.sql's own comment states that when pgschema (rather than raw schema.sql) creates a fresh schema, it emits existing partition children as standalone CREATE TABLE statements not yet attached to their parent, and that pgschema also copies the parent's triggers onto those standalone children -- so the repair script must DROP each copied trigger (including community_write_fence_events, community_write_fence_delivery_log, and events_created_at_floor) from every partition child before ALTER TABLE .. ATTACH PARTITION, because PostgreSQL recreates the inherited parent trigger on attach and rejects a same-named trigger already present on the child."
    entry_class: FACT
    evidence:
      - "scripts/attach-schema-partitions.sql:1-27"
  - statement: "The events table's stored columns (id, pubkey, created_at, kind, tags, content, sig, and more) are the full signed Nostr event, and buzz-db's crate-level invariants state that ephemeral events (kinds 20000-29999) are never persisted at all and AUTH events (kind 22242) are never stored because they carry bearer tokens -- so a row that is persisted in the partitioned events table is this repository's durable, canonical copy of that event, not a cache or projection of a copy held authoritatively elsewhere."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:190-235"
      - "crates/buzz-db/src/lib.rs:8-9"
  - statement: "The partitioned events and delivery_log tables are this repository's authoritative store for the data they hold (persisted Nostr events and subscription delivery attempts, respectively), not a derived, cache, or transport layer -- partitioning is a physical storage-layout strategy applied to that authoritative data, not a separate store in its own right."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql:190-235"
      - "migrations/0001_initial_schema.sql:329-341"
      - "crates/buzz-db/src/lib.rs:8-9"
    confidence: 0.8
  - statement: "crates/buzz-db/src/partition.rs's own unit test module asserts validate_partition_suffix and validate_date_str reject SQL-injection-shaped inputs (e.g. \"2026_03; DROP TABLE events--\", \"2026-03-01; DROP TABLE events--\") and that PARTITIONED_TABLES contains events and delivery_log but not api_tokens or users."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/partition.rs:152-182"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Postgres table partitioning: `events` and `delivery_log`

## Scope and authority

**This node covers** the monthly range-partitioning scheme applied to two tables in
Buzz's Postgres instance -- `events` and `delivery_log` -- as a cross-cutting physical
storage-layout mechanism: which tables are partitioned and on what key, how new
partitions come into existence, how the mechanism interacts with two other invariants
built on top of it (the replica-fence floor guard and the per-community write fence),
what happens when the mechanism fails, and what it does not do (retire old partitions).

**This node does not cover** the Postgres container's own identity, technology version,
or its full data-access surface -- that is `architecture-containers-postgres`
(`launchpad/docs/corpus/architecture/containers/postgres.md`), already merged, which
this node is `part-of`. It also does not cover the domain meaning of an `events` or
`delivery_log` row (what a Nostr event or a delivery attempt *is*) -- that is a
data-entity concern, out of scope here. It does not cover per-environment operational
facts (replica count, whether an environment actually sets `buzz.created_at_floor`) --
those are deployment facts, not partitioning facts, per the same practical test
`templates/datastore.md` states for its own operational-characteristics section: would
this fact still be true regardless of which environment is being described? Everything
in this node is.

| For | Read |
|---|---|
| The Postgres container's identity and technology | `launchpad/docs/corpus/architecture/containers/postgres.md` |
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Required-sections shape this node adapts | `launchpad/docs/corpus/templates/datastore.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |

## Authoritative, derived, cache, or transport

The partitioned `events` table stores the full signed Nostr event (id, pubkey,
`created_at`, kind, tags, content, `sig`, and more), and `buzz-db`'s own crate-level
invariants state that ephemeral events (kinds 20000-29999) are never persisted at all
and AUTH events (kind 22242) are never stored because they carry bearer tokens. A row
that does land in `events` is this repository's durable, canonical copy of that event --
not a cache or a projection of a copy held authoritatively somewhere else. The same
holds for `delivery_log`: it is the record of a subscription delivery attempt, not a
copy of one recorded elsewhere. **Both tables are authoritative stores for the data
they hold.** Partitioning is a physical storage-layout strategy applied on top of that
authoritative data; it is not itself a second store, and it does not change either
table's authoritative status.

## Owned data and partition topology

| Table | Partition key | Primary key | Initial partitions (migration 0001) |
|---|---|---|---|
| `events` | `RANGE (created_at)` | `(community_id, created_at, id)` | `events_p_past`, `events_p2026_01` .. `events_p2026_06`, `events_p_future` |
| `delivery_log` | `RANGE (delivered_at)` | `(delivered_at, id)` | `delivery_log_p_past`, `delivery_log_p2026_03` .. `delivery_log_p2026_06`, `delivery_log_p_future` |

Each initial partition is a Postgres range partition with an explicit
`FOR VALUES FROM (...) TO (...)` bound, declared directly in
`migrations/0001_initial_schema.sql`. `buzz-db`'s crate-level doc comment states this
as one of its own design invariants: "Events table is partitioned by month on
`created_at`" and "No FK references to partitioned tables" -- the second because
Postgres does not allow a foreign key to target a partitioned table the way it targets
an ordinary one, so nothing in this schema references `events` or `delivery_log` by FK.

Schema and column detail is not repeated here -- see `migrations/0001_initial_schema.sql`
for the authoritative `CREATE TABLE` statements for both tables.

## Partition creation mechanism

New monthly partitions are created by `crates/buzz-db/src/partition.rs`'s
`ensure_future_partitions(pool, months_ahead)`, which:

1. Is restricted to an explicit allowlist, `PARTITIONED_TABLES = ["events",
   "delivery_log"]` -- the module's own doc comment states this "prevents DDL
   injection," because a partition's table name and bounds cannot be supplied as
   query parameters and must instead be interpolated into DDL text.
2. Validates every interpolated value with a strict character-class check before use:
   `validate_partition_suffix` (digits and underscores only) and `validate_date_str`
   (`YYYY-MM-DD` only) -- both are unit-tested against SQL-injection-shaped inputs.
3. Checks the Postgres catalog (`pg_class`/`pg_namespace`) for an existing partition
   of that name before creating one, so the operation is idempotent.
4. Treats Postgres error `42P17` ("would overlap partition") as success rather than
   failure, because a fresh schema's catch-all `*_p_future` partition may already
   cover the requested month -- this is a deliberate design choice recorded in the
   function's own comment, not an unhandled edge case.

`crates/buzz-relay/src/main.rs` calls `db.ensure_future_partitions(3)` once, at every
relay startup, unconditionally (not gated on `BUZZ_AUTO_MIGRATE`). The module's own
doc comment additionally states it is meant to run monthly via cron; no cron
invocation was found anywhere in this repository at the recorded revision --
named here as a gap rather than assumed to exist.

## Lifecycle and retention

**Partitions are only ever created, never removed, by any code path in this
repository.** A repository-wide search for partition retention, detachment, or drop
logic found no call site. `ensure_future_partitions` only ever creates partitions for
upcoming months. Consequently the `events` and `delivery_log` partition sets grow
monotonically for the life of a deployment; pruning an old partition today would have
to be an out-of-band operator action outside any code this node can cite, not a
scheduled or automated one. This is stated as a gap, not resolved.

## Consistency semantics: partitioning and the replica-fence floor guard

Migration 0021 attaches a `DEFERRABLE INITIALLY DEFERRED` constraint trigger
(`events_created_at_floor`, backed by `events_created_at_floor_guard()`) to the
`events` parent table, re-evaluated at `COMMIT` via `clock_timestamp()`, that rejects
a channel-bearing row whose `created_at` is older than a session-scoped
`buzz.created_at_floor` GUC. Its purpose, per the migration's own comment, is to make
the ingest-time `created_at` envelope a commit-time storage invariant, so that a
cursor page served from a read replica behind a sampled fence timestamp can never miss
a row that should have been visible.

**Partition rotation must preserve this guard on every partition, and the codebase
verifies that it does.** Because the trigger is declared on the partitioned parent,
`CREATE TABLE .. PARTITION OF` clones it onto every partition automatically --
migration 0021's own comment states this explicitly. `crates/buzz-db/src/replica_fence.rs`'s
`verify_floor_guard_catalog` independently re-checks this at runtime: it walks
`pg_inherits` for every child of `events` and asserts a correctly shaped copy of the
trigger exists on each one.

## Tenancy and security boundary

Migration 0029's per-community write fence (`enforce_community_write_fence`, which
rejects a write naming a non-active community) is attached, via
`attach_community_write_fence`, only to relations where `pg_class.relispartition` is
false -- i.e. to the `events` and `delivery_log` partitioned *parents*, never directly
to a partition child. Because Postgres clones row-level triggers from a partitioned
parent onto its children (the same inheritance mechanism the floor guard relies on,
above), every partition of `events` and `delivery_log` inherits the same
community-scoped write fence as its parent automatically. **Partitioning does not
create or widen a tenancy boundary of its own; it inherits the parent table's, and
that inheritance is load-bearing for both invariants documented in this node.**

## Failure behavior

Three distinct failure modes exist, and they are not treated identically:

1. **`ensure_future_partitions` itself fails at startup** (e.g. the database is
   briefly unreachable). `crates/buzz-relay/src/main.rs` logs the error and continues
   starting the relay -- non-fatal, unlike auto-migration failure and deletion-serving
   fence validation failure in the same function, both of which abort startup.
2. **A write lands outside every existing partition's range** (the consequence of
   failure mode 1 persisting long enough that an upcoming month has no partition).
   Postgres itself rejects the `INSERT` with a "no partition of relation ... found for
   row" error at write time -- this exact error text is independently named in
   `scripts/attach-schema-partitions.sql`'s own comment, describing the failure a
   mis-attached partition produces.
3. **The replica-fence floor guard is missing or mis-shaped on any partition.**
   `crates/buzz-db/src/migration.rs`'s `run_migrations_locked` re-checks the guard
   immediately after running migrations and fails the entire migration run closed if
   any partition (parent or child) is missing it -- the function's own comment states
   this explicitly. Separately, `Db::spawn_fence_probe`'s own doc comment states that
   if this same verification fails outside a migration run, the background
   replica-fence probe is never spawned and the fence stays permanently closed: every
   cursor page routes to the writer pool, described in the comment as "the relay keeps
   serving -- degraded capacity, never holes." Partition topology and this guard's
   correctness are directly coupled: an incorrectly rotated partition degrades read
   capacity rather than corrupting a served page.

Separately, the pgschema-vs-raw-SQL repair path in `scripts/attach-schema-partitions.sql`
exists because pgschema-applied schemas emit existing partition children as standalone
tables that also carry copies of the parent's triggers; attaching them without first
dropping those copies fails, because Postgres recreates the inherited trigger on
attach and rejects a same-named trigger already present on the child.

## Verification

`crates/buzz-db/src/partition.rs`'s own unit tests (`suffix_validation`,
`date_str_validation`, `table_allowlist`) assert the injection-guard regexes reject
SQL-injection-shaped inputs and that the allowlist contains exactly `events` and
`delivery_log`. `crates/buzz-db/src/replica_fence.rs`'s `verify_floor_guard_catalog`
is itself a runtime verification of partition-guard coverage, re-run on every startup
and every migration.

## Scope and omissions

**Not covered here, and owned elsewhere:** the Postgres container's own identity and
technology version (`architecture-containers-postgres`); the domain meaning of an
`events` or `delivery_log` row; per-environment operational facts such as replica
count or whether `buzz.created_at_floor` is actually set anywhere (deployment
concerns); Redis or the S3-compatible object store's own partitioning or lack of it
(out of scope for this node, which is Postgres-only).

**Expected but not verified while drafting this node:**

- Whether any monitoring or alerting exists for the case where `ensure_future_partitions`
  fails repeatedly and a write-time "no partition of relation" error becomes likely --
  not found in this repository at the recorded revision, and not ruled out either.
- Whether an operator runbook exists for manually dropping or archiving an old
  partition, given that no code path does this -- not found, and named as a gap in
  the *Lifecycle and retention* section above rather than assumed absent from
  operational practice entirely.
