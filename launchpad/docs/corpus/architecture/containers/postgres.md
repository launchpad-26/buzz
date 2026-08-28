---
id: architecture-containers-postgres
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-db is described as \"Postgres event store and data access layer for Buzz\" and is the crate that owns Postgres connection pooling, migrations, and every typed data-access module (events, channels, users, moderation, workflow, and more)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/Cargo.toml"
      - "crates/buzz-db/src/lib.rs"
  - statement: "buzz-db declares design invariants in its crate-level doc comment: AUTH events (kind 22242) are never stored because they carry bearer tokens, ephemeral events (20000-29999) are never stored (Redis pub/sub only), the events table is partitioned by month on created_at, there are no foreign-key references to partitioned tables, and query construction uses runtime sqlx::query() rather than compile-time sqlx::query!()."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "buzz-relay is the sole crate in the workspace that constructs buzz_db::DbConfig and calls Db::new at startup; buzz-admin and buzz-deletion are the only other crates that depend on the buzz-db crate directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-deletion/Cargo.toml"
  - statement: "buzz-relay's default DbConfig points at postgres://buzz:buzz_dev@localhost:5432/buzz, sizes the writer pool to 20 max / 2 min connections with a 3s acquire timeout, a 1800s max connection lifetime, and a 600s idle timeout, and the default's own doc comment records that staging measured 51 idle + 1 active out of a 50-connection budget, i.e. most pooled connections sat unused."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "The writer pool's after_connect hook sets the buzz.created_at_floor GUC on every connection and asserts the session's transaction_isolation is exactly \"read committed\", failing the connection attempt otherwise; this is what makes the replica-freshness fence in replica_fence.rs sound for every insert that goes through the pool."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "An optional read-replica pool is connected lazily (connect_lazy, min_connections pinned to 0) from READ_DATABASE_URL, using a much shorter 150ms acquire timeout than the writer so a saturated or absent replica fails closed to the writer quickly rather than adding writer-level latency to a routed read; a reader that is down at boot cannot crash the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "Pool sizing is configurable at deploy time via BUZZ_DB_POOL_SIZE (writer and, when READ_DATABASE_URL is set, reader; default 50) and BUZZ_DB_READ_POOL_SIZE (defaults to the writer size), both parsed in buzz-relay's Config::from_env."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
  - statement: "Migrations are embedded via sqlx::migrate!(\"../../migrations\") in buzz-db's migration module and applied with MIGRATOR.run inside a single call site guarded by an exclusive Postgres advisory session lock (SCHEMA_DESTRUCTION_LOCK_KEY), which a source lint enforces has no other caller; after running pending migrations the same code path re-verifies the replica-fence floor-guard trigger exists on the events parent table and every partition."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/migration.rs"
  - statement: "At relay startup, migrations only run when the BUZZ_AUTO_MIGRATE environment variable is truthy (\"true\"/\"1\"/\"yes\"/\"on\", case-insensitive and trimmed); the flag's own parser treats an absent or any other value as disabled, so a plain deploy with the variable unset starts the relay without running pending migrations and only logs \"Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "This is a real discrepancy against this repository's own top-level contributor guide, which lists migrations/ in its repo-structure map as \"SQL migrations (auto-applied on relay startup)\" without mentioning the BUZZ_AUTO_MIGRATE gate; the code is the FACT this node records, and the doc comment is flagged here rather than silently corrected."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "crates/buzz-relay/src/main.rs"
  - statement: "Postgres 17 (image postgres:17-alpine) is the version pinned for local development in docker-compose.yml, with a named buzz-postgres-data volume, a pg_isready healthcheck, and a 512m memory limit; the same image and default credentials (buzz/buzz_dev, database buzz) are recorded in .env.example."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - ".env.example"
  - statement: "Besides buzz-db's pool, buzz-relay opens two further independent Postgres connections in its own startup sequence: a 5-connection audit pool (used only when BUZZ_AUDIT_ENABLED is set, backing the buzz-audit hash-chain log) and a search pool that prefers READ_DATABASE_URL when configured (backing buzz-search's Postgres full-text search); both connect directly with sqlx::postgres::PgPoolOptions rather than going through buzz_db::Db."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-search/Cargo.toml"
  - statement: "buzz-search's Postgres full-text search reads the same events table buzz-db writes to -- the tsvector column populated by insert_event -- so search has no separate index to provision or keep in sync; it is described in code as lag-tolerant and prefers the read replica when one is configured."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "migrations/0001_initial_schema.sql is the from-scratch multi-tenant schema and states its own governing contract is docs/multi-tenant-conformance.md; every tenant-scoped table carries a NOT NULL community_id, and the schema's row-zero invariant is that a request's community is resolved from the connection host by the server, never supplied by the client."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0021_created_at_fence_floor.sql is the migration that adds the commit-time created_at floor trigger buzz-db's writer-pool after_connect hook and migration.rs's post-migration verification both depend on."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
      - "crates/buzz-db/src/migration.rs"
  - statement: "Because BUZZ_AUTO_MIGRATE defaults off and the code path that would apply migrations 0001-0021+ is opt-in, an operator who deploys with the variable unset is running against whatever schema Postgres already has; this node cannot verify from the repository alone whether the staging/production deploy pipelines referenced by this repo's own contributor guide (squareup/block-coder-tf-stacks, squareup/sprout-oss) set BUZZ_AUTO_MIGRATE, because those are separate private repositories this task did not open."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "AGENTS.md"
    confidence: 0.6
---

# Container: Postgres

## Responsibility, technology, and ownership boundary

**Postgres is Buzz's single system of record.** It is the durable event store
behind every Nostr event the relay accepts, plus the relational tables for
communities, channels, membership, moderation, workflows, push state, and
audit — there is no separate database per subsystem. The concrete technology
is Postgres 17 (`postgres:17-alpine` in local development).

**Ownership is split between two crates, on two separate connection pools
that both point at the same physical database:**

- **`crates/buzz-db`** owns the schema-facing contract: connection pooling
  and lifecycle (`Db::new`, `DbConfig`), the embedded migration runner, and
  every typed data-access module (events, channels, users, moderation,
  workflow, and more — see `crates/buzz-db/src/lib.rs`'s module list). Its
  crate doc comment states four invariants a caller must not violate: AUTH
  events (kind 22242) are never stored because they carry bearer tokens;
  ephemeral events (kind range 20000-29999) are never stored, Redis pub/sub
  only; the `events` table is partitioned by month on `created_at`; and no
  foreign key targets a partitioned table.
- **`crates/buzz-relay`** owns *when and how many* connections exist. It is
  the only crate that builds a `DbConfig` and calls `Db::new` at process
  startup, and it separately opens two more independent Postgres pools of
  its own for the audit and search subsystems (see *Directly connected
  containers/systems* below). `crates/buzz-admin` (operator CLI) and
  `crates/buzz-deletion` (whole-community deletion) are the only other
  crates that depend on `buzz-db` directly.

Postgres itself has no Buzz-specific logic beyond what ships in
`migrations/` — ownership of *behavior* stops at the SQL and Rust in this
repository; the database is a stock Postgres 17 instance.

## Inbound/outbound interfaces and directly connected containers

**Inbound (who connects to Postgres, and how):**

| Caller | Pool | Purpose |
|---|---|---|
| `buzz-relay` main process, via `buzz-db::Db` | Writer pool (`DbConfig::database_url`, default 20 max connections) plus an optional lazy read-replica pool (`READ_DATABASE_URL`) | All event/channel/user/moderation/workflow reads and writes |
| `buzz-relay` main process, direct `sqlx::PgPool` | 5-connection audit pool on `database_url`, only when `BUZZ_AUDIT_ENABLED` is set | Backs `buzz-audit`'s hash-chain log |
| `buzz-relay` main process, direct `sqlx::PgPool` | Search pool, preferring `READ_DATABASE_URL` when set | Backs `buzz-search`'s Postgres full-text search over the same `events` rows |
| `buzz-admin` | via `buzz-db::Db` | Operator CLI administration |
| `buzz-deletion` | via `buzz-db::Db` | Whole-community deletion lifecycle |

Pool sizing is deploy-time configurable through `BUZZ_DB_POOL_SIZE` (writer
and, when a replica URL is set, reader; default 50) and
`BUZZ_DB_READ_POOL_SIZE` (defaults to the writer size).

**Outbound (what Postgres itself depends on):** none within this
repository — it is a leaf in the container graph. `pg_isready` is the only
external check against it (Docker Compose healthcheck).

**Directly connected containers, not through the relay's own pools:** none
observed in this repository. `crates/buzz-backend-kubernetes` (the Kubernetes
provider for remote agent workstations) and the mobile/desktop clients do not
open Postgres connections themselves — they reach the relay's WebSocket/HTTP
surface instead, per `AGENTS.md`'s "Nostr-first HTTP surface" pattern.

## Deployment and data implications

**Migrations are opt-in at startup, not automatic.** `buzz-db`'s migration
module embeds every file under `migrations/` via `sqlx::migrate!` and runs
them with `MIGRATOR.run` inside a single call site (a source lint enforces
there is no other caller) that holds an exclusive Postgres advisory session
lock (`SCHEMA_DESTRUCTION_LOCK_KEY`) so schema changes never race destructive
community-deletion transactions. But `buzz-relay`'s `main.rs` only invokes
that path when the `BUZZ_AUTO_MIGRATE` environment variable parses as truthy
(`true`/`1`/`yes`/`on`); unset or any other value skips migrations and logs a
message rather than applying them. **This repository's own top-level
contributor guide (`AGENTS.md`, repo-structure section) describes
`migrations/` as "auto-applied on relay startup" without mentioning that
gate** — this node records the code's actual behavior as the FACT and flags
the mismatch rather than silently resolving it; see the corresponding
evidence entry above.

After a successful migration run, the same code path re-verifies (via
`replica_fence::verify_floor_guard_catalog`) that the commit-time
`created_at` floor trigger added by `migrations/0021_created_at_fence_floor.sql`
is present on the `events` parent table and on every partition. That trigger,
combined with the writer pool's `after_connect` hook (which sets the
`buzz.created_at_floor` session GUC and asserts `transaction_isolation =
'read committed'` on every connection, failing the connection otherwise) is
what makes bounded-staleness read-replica routing sound. A relay that never
enables `BUZZ_AUTO_MIGRATE` and starts against a schema older than migration
0021 will have that fence verification fail closed — reads stay on the
writer rather than silently trusting an unenforced floor.

**Partitioning.** The `events` table is partitioned by month on
`created_at` (crate-level invariant in `buzz-db`), and `buzz-relay` calls
`db.ensure_future_partitions(3)` on every startup to keep three months of
partitions ahead of the current one.

**Schema authority.** `migrations/0001_initial_schema.sql` is the
from-scratch, multi-tenant schema and states its own governing contract is
`docs/multi-tenant-conformance.md`. Its stated row-zero invariant: every
tenant-scoped row carries a `NOT NULL community_id`, resolved server-side
from the connection host — never supplied by the client. This is the
security-relevant boundary the container exists to hold: cross-community
data isolation is enforced in the schema and in `buzz-db`'s query
construction, not merely in application logic above it.

**Local development topology.** `docker-compose.yml` pins `postgres:17-alpine`,
exposes it on `127.0.0.1:5432`, persists to a named `buzz-postgres-data`
volume, and caps it at 512MB with a `pg_isready` healthcheck.
`.env.example` documents the matching `DATABASE_URL` and discrete
`PGHOST`/`PGPORT`/`PGUSER`/`PGPASSWORD`/`PGDATABASE` variables plus a
commented-out `READ_DATABASE_URL` example for exercising replica routing
locally.

**What this node could not verify.** Whether the staging and production
deployment pipelines referenced elsewhere in this repository's contributor
guide (`squareup/block-coder-tf-stacks`, `squareup/sprout-oss`) set
`BUZZ_AUTO_MIGRATE`, and what Postgres topology (single instance, Aurora
read replica, or otherwise) those pipelines actually provision, are questions
this task could not answer — those pipelines live in separate private
repositories this task did not open. `DbConfig::read_database_url`'s own doc
comment mentions "an Aurora `cluster-ro-` endpoint" as an example shape,
which is the only signal in this repository about the intended production
replica technology.

## Implementation paths

- `crates/buzz-db/` — connection pooling, migrations, and all typed
  data-access modules (see `crates/buzz-db/src/lib.rs`'s module list for the
  full set: events, channels, users, moderation, workflow, and more).
- `crates/buzz-db/src/migration.rs` — embedded migration runner and its
  schema-destruction-lock wrapper.
- `crates/buzz-relay/src/main.rs` — startup wiring: `DbConfig` construction,
  the `BUZZ_AUTO_MIGRATE` gate, partition maintenance, the audit pool, and
  the search pool.
- `migrations/` — the checked-in SQL migration files themselves,
  `0001_initial_schema.sql` through the current tip.
- `docker-compose.yml`, `.env.example` — local Postgres topology and
  configuration defaults.

This node does not restate the schema's table-by-table contents or the
migration runner's full transaction/locking proof — read the files above for
that; this node exists to name the container's boundary and its neighbors,
not to duplicate their detail.

## Scope and omissions

**This node covers** what Postgres is responsible for in Buzz, which crates
own its connections and under what technology, its inbound interfaces and
directly connected containers, and the deployment/data/security implications
visible from this repository.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Table-by-table schema contents and the multi-tenant conformance contract | `migrations/0001_initial_schema.sql`, `docs/multi-tenant-conformance.md` |
| The replica-freshness fence's full correctness proof | `crates/buzz-db/src/replica_fence.rs` |
| Production/staging Postgres provisioning and topology | `squareup/block-coder-tf-stacks` (private, not opened by this task) |
| Relay container responsibility, technology, and boundary | a future `architecture-containers-*` node for the relay (not merged at this revision) |
| Redis (pub/sub, presence) as a separate container | a future `architecture-containers-*` node for Redis (not merged at this revision) |

**No `relationships` are declared.** At the recorded revision no sibling
`architecture/containers/*` node, and no other corpus node this document
would naturally point at, is merged on `origin/launchpad` — a
`relationships[].target` naming an id no loaded node carries is a hard
validation error, and `corpus-standard-confidence.md` set the precedent of
omitting `relationships` for the identical reason. The first sibling
container node to merge is the moment to add edges here, not this pass.
