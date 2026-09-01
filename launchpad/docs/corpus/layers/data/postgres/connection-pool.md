---
id: layers-data-postgres-connection-pool
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
  - statement: "node.schema.json's type enum is architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion, and contains no data or datastore value -- a node whose path lives under layers/ takes type: layers."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real datastore instance (architecture, at confidence 0.6), for the same reason five other documents in this same overnight batch already chose it (PR #1875, unmerged at the recorded revision: audit-tables.md, backup-boundary.md, channel-members-table.md, channels-table.md, communities-table.md): the issue's own directory assignment (launchpad/docs/corpus/layers/data/postgres/connection-pool.md, from issue #1080's corpus-plan:v2 alias header) and Feature #610's title ('data and storage layer corpus exists') both point at layers as the intended surface. Per standards/taxonomy.md's step-4 rule (disclose an imperfect fit rather than silently resolve it), this tension is named here rather than picked unilaterally."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.65
  - statement: "PR #1875's backup-boundary.md (unmerged at the recorded revision) documents a different operational facet of the same architecture-containers-postgres container -- what must be backed up -- using the identical shape this node follows: a datastore.md-adapted document that is part-of architecture-containers-postgres rather than a table/domain-entity node, with the type: layers tension disclosed the same way."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1875 (open PR, unmerged), read directly via gh pr diff"
  - statement: "architecture-containers-postgres.md (merged on origin/launchpad) states buzz-db owns the schema-facing contract including connection pooling and lifecycle (Db::new, DbConfig), and that buzz-relay is the sole crate that builds a DbConfig and calls Db::new at process startup, separately opening two more independent Postgres pools of its own for the audit and search subsystems. This node zooms into that connection-pool facet specifically, without repeating the container node's migration or partitioning detail."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "crates/buzz-db/Cargo.toml describes buzz-db as 'Postgres event store and data access layer for Buzz'; crates/buzz-db/src/lib.rs's DbConfig struct and its Default impl set the writer pool to max_connections: 20, min_connections: 2, acquire_timeout_secs: 3, max_lifetime_secs: 1800, idle_timeout_secs: 600, with a doc comment stating this is 'sized for a single relay pod against PG max_connections=100' and that 'staging measured 51 idle + 1 active out of 50 -- most connections sat unused.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-db/src/lib.rs"
  - statement: "Db::connect_pool (the writer pool constructor) registers a single after_connect hook on every connection that runs SELECT set_config('buzz.created_at_floor', $1, false) with replica_fence::CREATED_AT_FLOOR_SECS, then queries SHOW transaction_isolation and returns sqlx::Error::Configuration -- refusing the connection -- if the value is not exactly 'read committed'; the function's own doc comment states 'SQLx stores one after_connect hook, so the floor guard and transaction isolation assertion must remain in this single closure. Registering a second hook replaces the first and silently disarms the floor trigger.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Db::connect_read_pool builds the optional read-replica pool with connect_lazy (no connection attempted at construction) and min_connections pinned to 0 explicitly; its doc comment states the 0 pin is deliberate because 'sqlx's lazy pool still spawns an eager background connect task to satisfy a nonzero minimum, which would reintroduce boot-time reader dial attempts,' and that the reader pool carries 'no floor guard or writer-isolation assertion' because replica sessions are read-only and the commit-time trigger from migration 0021 never fires there."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Db::READER_ACQUIRE_TIMEOUT is a const Duration::from_millis(150), deliberately far below the writer's seconds-denominated acquire_timeout_secs; its doc comment states 'failing closed to the writer must be fast: a saturated reader pool that made routed reads wait the full writer-style timeout would add dead latency during exactly the load spike the offload exists for.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Db::spawn_read_pool_boot_ping spawns a one-shot, warn-only reachability probe against the read pool at startup; its doc comment states it 'must never gate startup or Db::spawn_fence_probe' and exists only because a lazy pool with min_connections(0) dials nothing until the first routed read, so a misconfigured READ_DATABASE_URL would otherwise be invisible until traffic arrives."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Db::proved_reader acquires one connection from the read pool per routed read and treats every non-Ok outcome as fail-closed to the writer: a sqlx::Error::PoolTimedOut on acquire or on beginning the 'BEGIN ISOLATION LEVEL REPEATABLE READ, READ ONLY' transaction returns Err(\"reader_acquire_timeout\"), logged as a warning ('reader pool acquire timed out; routing to writer'); a code comment states the reason 'names the mechanism, not a diagnosis' and that buzz_db_route_decision{decision=\"writer\",reason=\"reader_acquire_timeout\"} is 'the operator's alert signal for a struggling reader pool.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "replica_fence.rs defines CREATED_AT_FLOOR_SECS: i64 = 960 (the GUC value the writer pool's after_connect hook arms on every connection) and FENCE_STALENESS: Duration = Duration::from_secs(30); DbConfig::replica_read_max_age_ms's own doc comment states '0 disables bounded-staleness routing -- the rollout default' and that values above FENCE_STALENESS 'are clamped to it,' which lib.rs's read_budget_from_ms function implements directly (ms => Some(Duration::from_millis(ms).min(replica_fence::FENCE_STALENESS)))."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/replica_fence.rs"
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-relay/src/config.rs's Config struct fields db_pool_size (u32) and db_read_pool_size (Option<u32>) are parsed from BUZZ_DB_POOL_SIZE (env var parsed as u32, filtered to v > 0, default 50) and BUZZ_DB_READ_POOL_SIZE (same parsing, no default -- None when unset or invalid); a doc comment on db_pool_size states buzz-db's own crate default of 20 'was sized for a handful of pods against max_connections=100. Against Aurora (~5,000 connections) that cap is the binding constraint.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "crates/buzz-relay/src/main.rs constructs DbConfig from Config as { database_url, read_database_url, replica_read_max_age_ms, max_connections: config.db_pool_size, read_max_connections: config.db_read_pool_size, ..DbConfig::default() } -- overriding only max_connections/read_max_connections/the two URLs/replica_read_max_age_ms from environment-derived Config, while min_connections, acquire_timeout_secs, max_lifetime_secs and idle_timeout_secs are inherited unchanged from buzz-db's own DbConfig::default() (2, 3s, 1800s, 600s respectively) because Config carries no fields for them. A failed Db::new call is mapped to an anyhow error and propagated with ?, which is fatal to relay startup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "crates/buzz-relay/src/main.rs opens two further, independent Postgres pools with sqlx::postgres::PgPoolOptions directly (not via buzz_db::Db): an audit pool (.max_connections(5).min_connections(1), eager .connect(&config.database_url)) built only when config.audit_enabled is set (BUZZ_AUDIT_ENABLED), and a search pool (no explicit max/min_connections override, eager .connect()) that connects to config.read_database_url when set, falling back to config.database_url otherwise. Both propagate a connection failure with ? as a fatal anyhow error, identical in failure shape to the writer pool."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Db exposes has_read_pool() -> bool, pool_stats() -> DbPoolStats and read_pool_stats() -> Option<DbPoolStats>, where DbPoolStats { size, idle, max } is documented as a 'Snapshot of Postgres connection pool utilisation'; crates/buzz-relay/src/main.rs polls both on a periodic background task (interval from BUZZ_POOL_METRICS_INTERVAL_SECS, parsed as u64 and floored at 1 second via .max(1) with the comment 'tokio::time::interval panics on Duration::ZERO', default 10) and exports them as the Prometheus gauges buzz_db_pool_size/_idle/_active/_max and, when a read pool exists, buzz_db_read_pool_size/_idle/_active/_max."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: ".env.example documents DATABASE_URL (the writer/default connection string), a commented-out READ_DATABASE_URL with the comment 'Optional read-replica URL; unset/blank keeps all reads on the writer,' and a commented-out BUZZ_DB_POOL_SIZE=50 under the comment 'Max connections in each of the relay's Postgres pools -- writer and, when READ_DATABASE_URL is set, reader (default 50).' It does not document BUZZ_DB_READ_POOL_SIZE or BUZZ_REPLICA_READ_MAX_AGE_MS anywhere -- a targeted grep of the file for both names returned no match -- even though crates/buzz-relay/src/config.rs reads both from the environment."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
  - statement: "migrations/0021_created_at_fence_floor.sql exists in the repository at the recorded revision and is the migration replica_fence.rs's doc comments and the writer pool's after_connect hook both depend on for the commit-time created_at floor trigger."
    entry_class: FACT
    evidence:
      - "migrations/0021_created_at_fence_floor.sql"
  - statement: "migrations/0001_initial_schema.sql gives every tenant-scoped table a NOT NULL community_id, and architecture-containers-postgres.md records this as the schema's row-zero invariant: cross-community isolation is enforced in the schema and in buzz-db's query construction, never in the connection or pool layer. None of DbConfig, PgPoolOptions, or the after_connect hook examined in this node's own evidence above references community_id, a tenant identifier, or any per-community connection routing -- a connection checked out of any of the four pools this node documents can serve a query against any community; tenancy is enforced by the query, not by which physical connection served it."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "crates/buzz-db/src/lib.rs"
    confidence: 0.8
  - statement: "Issue #1080's definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1080 definition of done"
  - statement: "Issue #1092 (the sibling task in this same overnight batch, not yet started at the time this node was written) is scoped by its own issue body's corpus-plan:v2 alias header to launchpad/docs/corpus/layers/data/redis/connection-pool.md, a structurally distinct pool built with deadpool_redis rather than sqlx::postgres::PgPoolOptions -- confirmed by reading crates/buzz-relay/src/main.rs's own redis_pool construction, which uses deadpool_redis::Config/PoolConfig, not PgPoolOptions."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1092, opened directly via gh issue view"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Postgres: connection pool

How Buzz's Postgres connection pools are configured, who owns each of them, what
consistency guarantee they do and do not provide, and how each one fails. This
document zooms into one operational facet of the container
`architecture-containers-postgres` already inventories -- Postgres's existence,
technology, and the crates that own its connections -- without repeating that
node's schema, migration, or partitioning detail.

## Purpose and scope

This node answers: **what connection pools exist between Buzz's code and Postgres,
how is each one sized and configured, what does each one guarantee about the
freshness of what it reads, and what happens when one of them cannot get a
connection?** It is not a schema document (table/DDL contents belong to a future
data-entity or datastore instance node, not here), not the migration mechanism
(already owned by `architecture-containers-postgres.md`), and not the Redis pool
(a structurally distinct `deadpool_redis`-backed pool, the subject of the sibling
issue #1092, not this one).

## Store classification: transport to an authoritative store, not a store itself

A connection pool holds no rows and makes no data authoritative, derived, cache, or
transport *by itself* -- it is the mechanism through which application code reaches
whichever role the underlying datastore plays. `architecture-containers-postgres.md`
already establishes that role for the datastore these pools connect to: Postgres is
Buzz's single system of record, "the durable event store behind every Nostr event
the relay accepts, plus the relational tables for communities, channels, membership,
moderation, workflows, push state, and audit." Every pool this node documents is a
**transport** connecting application code to that one authoritative store -- none of
the four pools below is itself a cache or a derived copy of anything. The one
exception worth naming explicitly: the lazy reader pool connects to a *read replica*
when `READ_DATABASE_URL` is configured, which is itself a derived, lag-bounded copy
of the writer's data -- but the pool is still transport; the replica's derivation is
a fact about the datastore it reaches, not about the pooling mechanism itself. See
*Consistency semantics*, below, for how that lag is bounded before a routed read is
allowed to use it.

## The pools that exist, and who owns each

Four independent Postgres connection pools exist in this repository at the recorded
revision, all `sqlx::postgres::PgPoolOptions`-backed, but not all built the same way
or owned by the same crate:

| Pool | Built by | Sizing | Connects |
|---|---|---|---|
| Writer | `buzz_db::Db::connect_pool`, via `buzz-relay`'s `DbConfig` | `max_connections` from `BUZZ_DB_POOL_SIZE` (default 50 at the relay layer; `buzz-db`'s own crate default is 20), `min_connections: 2`, `acquire_timeout_secs: 3`, `max_lifetime_secs: 1800`, `idle_timeout_secs: 600` | `DATABASE_URL`, eagerly at startup |
| Reader (optional) | `buzz_db::Db::connect_read_pool`, via the same `DbConfig` | `max_connections` from `BUZZ_DB_READ_POOL_SIZE` (defaults to the writer's size when unset), `min_connections: 0` (pinned, not configurable), `150ms` acquire timeout, same `max_lifetime`/`idle_timeout` as the writer | `READ_DATABASE_URL`, lazily -- only when that variable is set, and no connection is dialed until first use |
| Audit | `crates/buzz-relay/src/main.rs`, direct `PgPoolOptions`, not via `buzz_db::Db` | `max_connections: 5`, `min_connections: 1` | `DATABASE_URL`, eagerly, only when `BUZZ_AUDIT_ENABLED` is set |
| Search | `crates/buzz-relay/src/main.rs`, direct `PgPoolOptions`, not via `buzz_db::Db` | No explicit `max_connections`/`min_connections` override in this repository's own construction call | `READ_DATABASE_URL` when set, else `DATABASE_URL`, eagerly |

Only the writer and reader pools go through `buzz_db::Db` and its typed data-access
modules. The audit pool backs `buzz-audit`'s hash-chain log; the search pool backs
`buzz-search`'s Postgres full-text search over the same `events` rows the writer
pool populates -- `architecture-containers-postgres.md` already names both as
separate, direct connections `buzz-relay` opens on its own, and this table adds only
the pool-construction detail that node's own inbound-interfaces summary does not
carry.

`crates/buzz-admin` (operator CLI) and `crates/buzz-deletion` (whole-community
deletion) reach Postgres exclusively through `buzz_db::Db`, i.e. through the writer
(and, when configured, reader) pool above -- neither opens a pool of its own.

## Owned data, access patterns, and lifecycle

A connection pool owns no rows -- what it "owns," in the sense this section
addresses, is connection lifetime and reuse, not data. The writer and reader pools
share the same lifecycle knobs (`max_lifetime_secs: 1800`, `idle_timeout_secs: 600`,
inherited from `buzz-db`'s own `DbConfig::default()` because `buzz-relay`'s
`Config`-to-`DbConfig` construction overrides only `max_connections`,
`read_max_connections`, the two URLs, and `replica_read_max_age_ms`): a pooled
connection is recycled after 30 minutes regardless of use, and an idle connection
above `min_connections` is closed after 10 minutes. The writer additionally
maintains a floor of 2 always-open connections (`min_connections: 2`); the reader
maintains none (`min_connections: 0`, pinned in code rather than configurable) so
that a reader with no `READ_DATABASE_URL` traffic yet does not hold connections open
against a replica that may not exist.

**Access pattern**, restated from the table above at the level this node owns: the
writer pool serves every write and every read that is not explicitly routed to the
replica; the reader pool serves only reads that pass `Db::proved_reader`'s fence
proof (see below); the audit and search pools are single-purpose, opened once at
startup for exactly the subsystem each backs, and never shared with the writer or
reader pool's own callers.

**Retention**, in the sense this section can speak to, is about connections, not
rows: sqlx's pool reaper recycles connections past `max_lifetime_secs` and closes
idle ones past `idle_timeout_secs`. Row-level retention (partitioning, whole-
community deletion) is `architecture-containers-postgres.md`'s subject, not this
pool-configuration node's.

## Consistency semantics: the floor guard, replica fence, and bounded staleness

The writer pool's `after_connect` hook is what makes a bounded-staleness guarantee
possible for routed reads at all. On every writer connection it runs `SELECT
set_config('buzz.created_at_floor', $1, false)` with the value
`replica_fence::CREATED_AT_FLOOR_SECS` (960), then asserts `SHOW
transaction_isolation` is exactly `"read committed"` -- refusing the connection
outright if it is not. `Db::connect_pool`'s own doc comment states this hook must
stay a single closure because "SQLx stores one `after_connect` hook ... registering
a second hook replaces the first and silently disarms the floor trigger." This is
what pairs with the commit-time floor trigger added by
`migrations/0021_created_at_fence_floor.sql` to give the replica-freshness fence
(`replica_fence.rs`) a sound premise to reason from.

The reader pool carries **no such guarantee of its own** -- its own code comment
states plainly that replica sessions are read-only, so the commit-time trigger
"never fires here." Every routed read instead goes through `Db::proved_reader`,
which opens a `BEGIN ISOLATION LEVEL REPEATABLE READ, READ ONLY` transaction and
resolves the freshest heartbeat token the fence has retained. `FENCE_STALENESS`
(30 seconds) bounds how old a retained entry may be and still count as proof;
`DbConfig::replica_read_max_age_ms` (env `BUZZ_REPLICA_READ_MAX_AGE_MS`) is an
additional, narrower per-request budget that `read_budget_from_ms` clamps to
`FENCE_STALENESS` -- a caller cannot ask for a looser bound than the fence itself
allows. The field's own doc comment states `0` "disables bounded-staleness routing
-- the rollout default," meaning this repository ships with routed reads off by
default even when a replica is configured; enabling it is an explicit, separate
opt-in.

**What this means for a caller of any of the four pools:** a query against the
writer pool sees read-committed, always-current data. A query that clears the fence
and lands on the reader pool sees data no more than `min(BUZZ_REPLICA_READ_MAX_AGE_MS,
30s)` stale relative to a proven commit. A query that fails the fence proof (acquire
timeout, begin failure, missing or stale heartbeat) is **not** served a stale answer
-- it falls back to the writer pool instead, per *Failure behavior* below. The audit
and search pools carry no fence logic of their own; the search pool's own connection
string selection (`READ_DATABASE_URL` when set, else `DATABASE_URL`) is a
lag-tolerant design choice `architecture-containers-postgres.md` already records
("described in code as lag-tolerant"), not a fenced guarantee -- an unfenced,
best-effort staleness tolerance, distinct from the writer/reader pair's proven
bound.

## Tenancy and security boundaries

**None of the four pools is community-scoped.** `migrations/0001_initial_schema.sql`
gives every tenant-scoped table a `NOT NULL community_id`, and
`architecture-containers-postgres.md` records this as the schema's row-zero
invariant -- but that invariant is enforced in the schema and in `buzz-db`'s query
construction, not in which physical connection a query happens to use. Neither
`DbConfig`, `PgPoolOptions`, nor the writer's `after_connect` hook examined for this
node references a community or tenant identifier anywhere; a connection checked out
of any pool can serve a query against any community, and the security boundary
between communities lives entirely above the connection layer, in the query code
`architecture-containers-postgres.md` already inventories. This is the same
pool-is-tenant-blind shape `backup-boundary.md` (unmerged, PR #1875) records for a
whole-database backup or restore operation, applied here to connection acquisition
instead.

**Credentials are externalized, not embedded.** Every pool in this node connects
through an environment-sourced URL (`DATABASE_URL`, `READ_DATABASE_URL`) rather than
a hardcoded value -- the same config-attachment shape `.env.example` documents for
local development and that `templates/datastore.md`'s own adaptation of the
Twelve-Factor App's Backing Services factor describes generally. This node does not
document what those URLs' actual values are in staging or production; that is
deployment's fact, not this pool-configuration node's, per the same boundary
`architecture-containers-postgres.md` already draws for provisioning generally.

## Failure behavior

**Writer pool connection failure at startup is fatal.** `Db::new`'s failure is
mapped to an `anyhow` error and propagated with `?` in `crates/buzz-relay/src/main.rs`
-- the relay does not start without a writer connection. The audit and search pools
share this same fatal-on-connect-failure shape: each is built with a direct
`PgPoolOptions::new()...connect(...).await.map_err(...)?` call, so a database
outage at boot fails relay startup through either of those two pools exactly as it
would through the writer, whenever the audit pool's `BUZZ_AUDIT_ENABLED` gate is on.

**Reader pool connection failure at startup is explicitly non-fatal.**
`connect_read_pool` uses `connect_lazy`, which dials nothing at construction time --
"a reader that is down at boot cannot crash the relay," per the constructor's own
doc comment. `Db::spawn_read_pool_boot_ping` provides the only boot-time visibility
into an unreachable replica: a one-shot probe that logs and warns but "must never
gate startup." A misconfigured or unreachable `READ_DATABASE_URL` is therefore
silent at boot beyond that one warning, and does not block the relay from serving
traffic on the writer pool alone.

**A saturated or slow-to-respond reader pool at runtime fails closed to the writer,
fast.** `Db::READER_ACQUIRE_TIMEOUT` (150ms) is deliberately far below the writer's
multi-second `acquire_timeout_secs`, so that a struggling reader adds at most 150ms
of dead latency to a routed read before falling back, rather than stalling the
request for the writer's own longer budget. `Db::proved_reader` reports this
specific failure as the reason code `reader_acquire_timeout` -- named, per its own
code comment, for "the mechanism, not a diagnosis," because a `PoolTimedOut` proves
only that no connection was handed out within budget, not whether the cause was
connection-establishment latency or genuine contention.

## Configuration surface

| Variable | Read by | Effect |
|---|---|---|
| `DATABASE_URL` | `crates/buzz-relay/src/config.rs` | Writer pool's connection string; also the audit pool's and (when `READ_DATABASE_URL` is unset) the search pool's |
| `READ_DATABASE_URL` | `crates/buzz-relay/src/config.rs` | Reader pool's connection string, and the search pool's preferred connection string when set; unset disables replica routing entirely |
| `BUZZ_DB_POOL_SIZE` | `crates/buzz-relay/src/config.rs` | Writer (and, absent an override, reader) pool `max_connections`; default 50 at the relay layer |
| `BUZZ_DB_READ_POOL_SIZE` | `crates/buzz-relay/src/config.rs` | Reader pool `max_connections` override; defaults to the writer's size when unset -- **not documented in `.env.example`**, a real gap named here rather than silently corrected |
| `BUZZ_REPLICA_READ_MAX_AGE_MS` | `crates/buzz-relay/src/config.rs` (via `DbConfig::replica_read_max_age_ms`) | Per-request staleness budget for routed reads, clamped to `FENCE_STALENESS` (30s); `0` (the rollout default) disables bounded-staleness routing entirely -- **also not documented in `.env.example`** |
| `BUZZ_AUDIT_ENABLED` | `crates/buzz-relay/src/main.rs` | Gates whether the audit pool is constructed at all |
| `BUZZ_POOL_METRICS_INTERVAL_SECS` | `crates/buzz-relay/src/main.rs` | How often the pool-metrics background task polls `pool_stats()`/`read_pool_stats()`; default 10s, floored at 1s |

## Implementation, schema, and test references

- `crates/buzz-db/src/lib.rs` -- `DbConfig`, `Db::new`, `Db::connect_pool`,
  `Db::connect_read_pool`, `Db::READER_ACQUIRE_TIMEOUT`,
  `Db::spawn_read_pool_boot_ping`, `Db::proved_reader`, `DbPoolStats`,
  `Db::has_read_pool`, `Db::pool_stats`, `Db::read_pool_stats`. This is the primary
  source for every sizing default and failure path this node describes.
- `crates/buzz-db/src/runtime/replica_fence.rs` -- `CREATED_AT_FLOOR_SECS`,
  `FENCE_STALENESS`, `read_budget_from_ms`, and the fence proof `proved_reader`
  resolves against. This node does not restate the fence's full correctness proof;
  `architecture-containers-postgres.md` already defers that to this same file.
- `crates/buzz-relay/src/config.rs` -- `Config::db_pool_size`,
  `Config::db_read_pool_size` environment parsing, including the tests at
  `db_pool_size_env_override_and_invalid_fallback` and
  `db_read_pool_size_env_override_and_invalid_fallback`.
- `crates/buzz-relay/src/main.rs` -- `DbConfig` construction from `Config`, the
  audit and search pool construction, and the periodic pool-metrics task.
- `migrations/0021_created_at_fence_floor.sql` -- the commit-time floor trigger the
  writer pool's `after_connect` hook and the fence proof both depend on.
- `.env.example` -- the documented (and, per *Configuration surface* above, the
  undocumented) connection-pool environment variables.
- `launchpad/docs/corpus/architecture/containers/postgres.md` -- the container-level
  node this document is `part-of`; schema, migration ordering, and partitioning
  detail live there, not here.

This document does not restate any of those files' full contents -- read them
directly for the detail; this node exists to state the connection-pool shape and
its consequences, not to duplicate the sources that establish it.

## Scope and omissions

**This node covers** which Postgres connection pools exist in this repository, how
each is sized and configured, what consistency guarantee (if any) each provides to
its callers, the tenancy and credential boundaries each pool does and does not
enforce, and how each pool behaves when it cannot get a connection.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres's own existence, technology, ownership boundary, and inbound-interface inventory | `architecture-containers-postgres.md` |
| Migration ordering, the schema-destruction lock, and partitioning | `architecture-containers-postgres.md` |
| Table-by-table schema contents and the multi-tenant conformance contract | `migrations/0001_initial_schema.sql`, `docs/multi-tenant-conformance.md` |
| Backup and restore of the datastore these pools connect to | `backup-boundary.md` (unmerged, PR #1875) |
| The replica-freshness fence's full correctness proof | `crates/buzz-db/src/runtime/replica_fence.rs` |
| The Redis connection pool (`deadpool_redis`-backed, structurally distinct) | `layers/data/redis/connection-pool.md` (issue #1092, not yet drafted) |
| Production/staging Postgres provisioning, topology, and the actual value of `DATABASE_URL`/`READ_DATABASE_URL` per environment | `squareup/block-coder-tf-stacks` (private, not opened by this task) |

**No relationships to sibling `layers/data/postgres/*` documents from this same
overnight batch** (audit-tables, backup-boundary, channel-members-table,
channels-table, communities-table, and the rest). None are merged on
`origin/launchpad` at the recorded revision -- each exists, if at all, only on an
unmerged sibling worktree/branch (PR #1875) -- and `AGENTS.md`'s node-creation step 9
requires a `relationships[].target` to resolve against the branch being merged into,
not the author's own worktree. The `part-of` edge to `architecture-containers-postgres`
is the one relationship this node declares, because that node is confirmed merged on
`origin/launchpad` (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`).

**Expected but not verified when this node was written:**

- **Whether `.env.example`'s omission of `BUZZ_DB_READ_POOL_SIZE` and
  `BUZZ_REPLICA_READ_MAX_AGE_MS` is deliberate or an oversight was not established.**
  Both are read by `crates/buzz-relay/src/config.rs` and neither appears in
  `.env.example`; named as a real gap in *Configuration surface* above, not resolved
  either way.
- **What `sqlx::postgres::PgPoolOptions`'s own crate-level default `max_connections`
  is was not checked against the vendored `sqlx` source**, so the search pool's row
  in *The pools that exist* states only that this repository's own construction call
  sets no explicit override, not what value results.
- **Whether `squareup/block-coder-tf-stacks` or `squareup/sprout-oss` sets
  `BUZZ_DB_POOL_SIZE`/`BUZZ_DB_READ_POOL_SIZE`/`BUZZ_REPLICA_READ_MAX_AGE_MS`
  differently from these defaults in staging or production was not established.**
  Both are private repositories this task did not open; `architecture-containers-postgres.md`
  records the identical disclosure about provisioning generally.
- **Cross-model review was not run.** Per this overnight batch's own established
  practice (recorded in `backup-boundary.md`, PR #1875, citing issue #1467), the
  cross-model (Codex) review provider's availability was not re-checked for this
  task; a same-model self-review is this node's own verification pass.
- **The `type: layers` versus `templates/datastore.md`'s suggested `type: architecture`
  tension is disclosed, not resolved**, per this batch's established precedent; a
  future corpus-wide pass may revisit which is correct for every instance node
  written from that template.
