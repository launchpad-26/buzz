---
id: layers-data-postgres-role
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum has 13 members including layers; this node uses type: layers rather than type: architecture, which templates/datastore.md's own worked guidance recommends for a real datastore instance node (the same enum member its sibling architecture-container and architecture-component templates independently direct their own instances to use, since no finer-grained member distinguishes a container-, component-, or datastore-level view)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
  - statement: "type: layers is used here instead because Feature #610's batch precedent -- set by the earlier-authored sibling layers/data/object-storage/role.md (#1073) and continued by layers/data/redis/role.md (#1097) -- directs every layers/data/... document in this Feature to type: layers rather than whatever type the chosen template's own worked example suggests; this is a disclosed override, per corpus-standard-taxonomy.md's rule that an imperfect or overridden type fit must be named in the node's own scope-and-omissions or evidence, not silently picked."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author dispatch brief for Feature #610 (this task's own overnight-batch instructions), naming #1073 and #1097 as the type: layers precedent for layers/data/... documents"
  - statement: "buzz-db's crate-level doc comment states four design invariants: AUTH events (kind 22242) are never stored because they carry bearer tokens; ephemeral events (kind range 20000-29999) are never stored, Redis pub/sub only; the events table is partitioned by month on created_at; and no foreign key references a partitioned table."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "buzz-db declares 22 typed data-access modules (admin_moderation, api_token, archived_identities, channel, deletion, dm, error, event, feed, git_repo, migration, moderation, partition, product_feedback, push, reaction, relay_invite, relay_members, replica_fence, thread, usage, user, workflow), each a pub mod in crates/buzz-db/src/lib.rs, covering the full set of Postgres-owned data this document treats as owned rather than re-describing table by table."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "DbConfig::default sizes the writer pool to 20 max / 2 min connections, a 3-second acquire timeout, a 1800-second max connection lifetime and a 600-second idle timeout, and its own doc comment records that staging measured 51 idle + 1 active out of a 50-connection budget -- most pooled connections sat unused. read_database_url defaults to None, which disables replica routing; Db::read then falls back to the writer pool."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: ".env.example sets DATABASE_URL to a postgres:// connection string, documents an optional (commented-out) READ_DATABASE_URL for exercising replica routing locally, and documents BUZZ_DB_POOL_SIZE as sizing the writer and, when READ_DATABASE_URL is set, the reader pool (default 50)."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "crates/buzz-db/src/runtime/migration.rs embeds every file under migrations/ via a static sqlx::migrate! MIGRATOR and runs it through a single run_migrations call site; that call site's own doc comment states the entire run holds the exclusive SCHEMA_DESTRUCTION_LOCK_KEY session lock, serializing schema changes against destructive community-deletion transactions, and that a source lint (migration_execution_cannot_bypass_schema_destruction_lock) enforces MIGRATOR.run has no other caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "crates/buzz-relay/src/main.rs gates migration execution on buzz_auto_migrate_enabled(std::env::var(\"BUZZ_AUTO_MIGRATE\")); when the variable is absent or not truthy, main.rs logs \"Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled\" and starts the relay without applying pending migrations, rather than running them automatically."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "After the migration decision, crates/buzz-relay/src/main.rs calls db.validate_deletion_serving_catalog() (community-deletion serving-fence validation, fatal on failure -- the process errors out) and then db.spawn_fence_probe() for the replica-freshness fence; the fence probe's own surrounding comment states verification failure is loud but non-fatal: \"the fence stays closed and every cursor page routes to the writer,\" and is deliberately sequenced after the migration decision so a relay running with BUZZ_AUTO_MIGRATE off and migration 0021 unapplied can never open the fence over an unenforced floor guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "crates/buzz-db/src/runtime/replica_fence.rs's module doc comment describes a two-part bounded-staleness proof for routing keyset-cursor reads to a Postgres read replica: a commit-time floor guard trigger (migration 0021) that aborts any transaction inserting a channel-bearing events row with created_at more than floor seconds before commit time, and an ordered heartbeat-token handshake (migration 0026) that lets a reader session prove, from its own observed token, that every commit before that token has already replayed on the session it is about to read from. The same comment states every failure mode -- probe errors, masked pg_stat_activity visibility, an unreadable heartbeat row, an epoch mismatch, or a token below every retained entry -- routes the request back to the writer: \"Everything fails closed... degraded capacity, never holes.\""
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/replica_fence.rs"
  - statement: "replica_fence.rs's own mod tests (crates/buzz-db/src/runtime/replica_fence.rs) contains multiple #[test] and #[tokio::test] functions exercising the fence proof; migration.rs's own mod tests (crates/buzz-db/src/runtime/migration.rs) contains dedicated tenant-isolation lint tests -- all_non_operator_global_tables_have_not_null_community_id, scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id, migration_lint_detects_tables_missing_community_id_by_default -- run against the concatenated SQL of every embedded migration."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/replica_fence.rs"
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "migrations/0001_initial_schema.sql's own header comment states its governing contract is docs/multi-tenant-conformance.md and names \"row zero\" as the invariant that a request's community is resolved from the connection host by the server, never supplied by the client, and that every scoped row carries that immutable community_id; the communities table itself is marked operator-global (the tenant registry, not itself tenant-scoped) and its own comment states resolve_host(host) reads exactly one row here to mint the request's TenantContext."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "migrations/0029_community_deletion.sql adds a whole-community deletion lifecycle: community_deletion_requests, community_deletion_approvals (FK to a request's id/community_id/inventory_digest triple), community_deletion_checkpoints and community_deletion_manifest_keys, guarded by BEFORE UPDATE/DELETE triggers (prevent_community_deletion_request_retargeting, prevent_community_deletion_approval_removal) that block a request from being redirected or an approval from being silently removed once recorded."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "crates/buzz-audit/src/lib.rs describes itself as a \"tamper-evident, per-community hash-chain audit log,\" and crates/buzz-audit/src/service.rs's own doc comment on its service type calls it an \"append-only, per-community hash-chain audit log backed by Postgres\" with a verify method that checks the hash chain for one community over a sequence range; crates/buzz-relay/src/main.rs constructs this service's own 5-max/1-min-connection Postgres pool only when config.audit_enabled is true, logging \"Audit logging disabled by BUZZ_AUDIT_ENABLED\" otherwise."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/lib.rs"
      - "crates/buzz-audit/src/service.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "crates/buzz-relay/src/main.rs opens a third independent Postgres pool for buzz-search: search_db_url prefers config.read_database_url over config.database_url, and the surrounding comment states search is lag-tolerant because the searchable row IS the persisted event row (its tsvector column, populated by insert_event), so there is no separate index to provision or keep in sync."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "crates/buzz-db/src/lib.rs imports buzz_datastore_tracing::datastore_span and applies it as #[datastore_span(name = \"...\", system = \"postgresql\")] on dozens of its own data-access methods (for example read_session_query_events and migrate), tagging each as a traced logical Postgres operation under this repository's own datastore-tracing policy crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "docker-compose.yml pins the postgres:17-alpine image for local development, with a pg_isready healthcheck and a named buzz-postgres-data persistent volume."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "Whether the staging/production deployment pipelines this repository's own contributor guide names (squareup/block-coder-tf-stacks, squareup/sprout-oss) set BUZZ_AUTO_MIGRATE, and what Postgres topology (single instance, a managed read replica, or otherwise) those pipelines actually provision, cannot be established from this repository -- those are separate private repositories this task did not open, and DbConfig::read_database_url's own doc comment mentions only an illustrative \"Aurora cluster-ro- endpoint\" shape, not a confirmed production topology."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-db/src/lib.rs"
    confidence: 0.6
  - statement: "Issue #1087's definition of done requires this node to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copy DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1087 definition of done"
  - statement: "architecture-principles-relay-is-source-of-truth.md states that a multi-pod buzz-relay-mesh deployment does not create a second source of truth -- \"Postgres and the Redis fenced generation remain the arbiters regardless of how many pods the relay runs as\" -- naming Postgres as one of the two authorities the relay's own source-of-truth principle rests on."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md"
relationships:
  - type: part-of
    target: architecture-containers-postgres
  - type: references
    target: architecture-principles-relay-is-source-of-truth
---

# Datastore role: Postgres

## Purpose & scope statement

This node zooms into `architecture-containers-postgres` (the container-level
inventory row: that Postgres exists, its technology, and a one-line
responsibility and communication edge) and states the datastore-level view
that document deliberately keeps to one line: what Postgres actually owns,
how its schema evolves, who reads and writes it and how, what consistency and
tenancy guarantees it provides, and how it behaves when something goes wrong.
It is not a second container inventory and not a domain model -- it does not
describe what a Nostr event or a channel *means* (a future `layers/data/...`
data-entity node's job), only where that data lives, how it changes shape
over time, and how it is reached.

## Authoritative role

**Postgres is the authoritative, durable system of record for the data it
owns -- not a cache, a derived projection, or a transport layer.**
`architecture-principles-relay-is-source-of-truth.md` names Postgres,
alongside the Redis fenced generation, as one of the two arbiters that remain
authoritative regardless of how many relay pods are running. Two explicit
exclusions from that authority are load-bearing rather than incidental:
AUTH events (kind 22242) are never persisted because they carry bearer
tokens, and ephemeral events (kind range 20000-29999) are never persisted --
Redis pub/sub is their only channel, by the same crate-level invariant. Redis
itself, by contrast, is transport/derived state for pub/sub, presence and
typing (out of this node's scope; see `layers/data/redis/role.md`, #1097,
not yet merged at this revision).

## Technology & attachment profile

Postgres 17 (`postgres:17-alpine` pinned in `docker-compose.yml` for local
development, with a `pg_isready` healthcheck and a named
`buzz-postgres-data` persistent volume). The application attaches through a
URL-style connection string (`DATABASE_URL` in `.env.example`) plus an
optional read-replica URL (`READ_DATABASE_URL`, commented out by default
locally) -- an externalized, config-driven attachment point rather than a
hardcoded address. `buzz-db::DbConfig::default` sizes the writer pool to 20
max / 2 min connections, a 3-second acquire timeout, an 1800-second maximum
connection lifetime and a 600-second idle timeout; `BUZZ_DB_POOL_SIZE`
(writer, and reader when `READ_DATABASE_URL` is set; default 50) and
`BUZZ_DB_READ_POOL_SIZE` (defaults to the writer size) make pool sizing
deploy-time configurable. A read-replica pool, when configured, connects
lazily (`min_connections: 0`) so a replica that is down at boot cannot crash
the relay.

Two further, independent Postgres pools exist alongside `buzz-db`'s, both
opened directly by `buzz-relay`'s own startup code rather than through
`buzz_db::Db`: a 5-max/1-min-connection audit pool, created only when
`config.audit_enabled` (`BUZZ_AUDIT_ENABLED`) is true, and a search pool that
prefers `READ_DATABASE_URL` over `DATABASE_URL` when a replica is
configured. Whatever value each environment actually gives these connection
strings, and whether a given environment runs a managed replica at all, is
deployment's fact (`layers/platforms/...` or a future
`architecture/deployment/*` node), not this one's -- this section states the
shape of the attachment, not its per-environment value.

## Schema / namespace inventory

`crates/buzz-db/src/lib.rs` declares 22 `pub mod` data-access modules, one
per owned data area: `admin_moderation`, `api_token`, `archived_identities`,
`channel`, `deletion`, `dm`, `error`, `event`, `feed`, `git_repo`,
`migration`, `moderation`, `partition`, `product_feedback`, `push`,
`reaction`, `relay_invite`, `relay_members`, `replica_fence`, `thread`,
`usage`, `user`, `workflow`. The `events` table -- the durable store behind
every persisted Nostr event -- is partitioned by month on `created_at`
(crate-level invariant), with `buzz-relay` calling
`db.ensure_future_partitions(3)` on every startup to keep three months of
partitions ahead of the current one. `migrations/0001_initial_schema.sql` is
the from-scratch, multi-tenant schema; `migrations/0029_community_deletion.sql`
adds the whole-community deletion control-plane tables (below). This node
does not restate table-by-table column contents -- read `migrations/` for
that, and a future `layers/data/...` data-entity node for what any one row
*means*.

## Migration / schema-versioning mechanism

Every file under `migrations/` is embedded via a static `sqlx::migrate!`
`MIGRATOR` in `crates/buzz-db/src/runtime/migration.rs` and applied through exactly
one call site, `run_migrations`, whose own doc comment states the entire run
holds the exclusive `SCHEMA_DESTRUCTION_LOCK_KEY` Postgres advisory session
lock, serializing schema changes against destructive community-deletion
transactions; a source lint
(`migration_execution_cannot_bypass_schema_destruction_lock`) enforces that
`MIGRATOR.run` has no other caller. Execution is opt-in, not automatic at
startup: `crates/buzz-relay/src/main.rs` only calls that path when
`BUZZ_AUTO_MIGRATE` parses as truthy; unset or any other value skips
migrations and logs a message rather than applying them. After a successful
run, the same startup path re-verifies (`spawn_fence_probe`, sequenced after
the migration decision on purpose) that the commit-time floor-guard trigger
migration 0021 adds is present on the `events` parent table and every
partition, so a relay that never enables `BUZZ_AUTO_MIGRATE` cannot open the
replica-freshness fence over an unenforced floor. `migration.rs`'s own
`mod tests` additionally runs tenant-isolation lint checks
(`all_non_operator_global_tables_have_not_null_community_id`,
`scoped_primary_key_unique_and_foreign_key_constraints_lead_with_community_id`,
`migration_lint_detects_tables_missing_community_id_by_default`) against the
concatenated SQL of every embedded migration, catching a missing or
misordered `community_id` constraint before it ships.

## Access-pattern summary

| Caller | Pool | Mechanism | Tracing |
|---|---|---|---|
| `buzz-relay` main process | `buzz-db::Db` writer pool + optional lazy reader | Every event/channel/user/moderation/workflow read and write | `#[datastore_span(system = "postgresql")]` on the underlying `buzz-db` methods |
| `buzz-admin`, `buzz-deletion` | `buzz-db::Db` | Operator CLI administration; whole-community deletion lifecycle | Same, via `buzz-db` |
| `buzz-relay` main process | Direct 5-max/1-min `sqlx::PgPool`, `BUZZ_AUDIT_ENABLED`-gated | Backs `buzz-audit`'s append-only, per-community hash-chain log | Not observed going through `#[datastore_span]` in this task's read of `main.rs` |
| `buzz-relay` main process | Direct `sqlx::PgPool`, prefers `READ_DATABASE_URL` | Backs `buzz-search`'s Postgres full-text search over the same `events` rows (the `tsvector` column `insert_event` populates -- no separate index) | Same as above |

`crates/buzz-db/src/lib.rs` applies `#[datastore_span(name = "...", system =
"postgresql")]` to dozens of its own methods (for example
`read_session_query_events`, `migrate`), instrumenting each as a traced
logical Postgres operation under `buzz-datastore-tracing`'s policy. This
node observed that attribute on `buzz-db` call sites only; whether the two
pools `buzz-relay` opens directly (audit, search) carry the same
instrumentation was not established while drafting this node -- named as a
gap rather than assumed either way.

## Operational characteristics

**Consistency semantics -- bounded-staleness read-replica routing, fails
closed.** `crates/buzz-db/src/runtime/replica_fence.rs` implements a two-part proof
before any keyset-cursor read is allowed to route to a configured read
replica: a commit-time floor-guard trigger (migration 0021) that aborts, at
commit, any transaction inserting a channel-bearing `events` row more than a
configured `floor` seconds stale, and an ordered heartbeat-token handshake
(migration 0026) that lets a reader session prove, from its own observed
token, that every commit preceding that token has already replayed on the
exact session about to serve the page. The module's own doc comment states
every failure mode -- probe errors, masked catalog visibility, an unreadable
heartbeat row, an epoch mismatch, or a token below every retained entry --
routes the request back to the writer: degraded capacity, never a
consistency hole. `replica_read_max_age_ms` (`0` by default, the rollout
default) is the bounded-staleness budget; `0` disables the bounded arm
entirely.

**Lifecycle & retention -- whole-community deletion, not per-row TTL.**
There is no row-level TTL or automatic expiry visible in the schema this
node inspected. Instead, `migrations/0029_community_deletion.sql` implements
a whole-community deletion control plane:
`community_deletion_requests`, `community_deletion_approvals` (foreign-keyed
to a request's `id`/`community_id`/`inventory_digest` triple),
`community_deletion_checkpoints`, and `community_deletion_manifest_keys`,
guarded by `BEFORE UPDATE`/`DELETE` triggers that block a request from being
silently retargeted or an approval from being removed once recorded.
`crates/buzz-relay/src/main.rs` calls `db.validate_deletion_serving_catalog()`
at every startup and treats its failure as fatal -- the process refuses to
start serving traffic against an unsafe deletion-serving fence, a stricter
failure mode than the replica fence's fail-closed-but-non-fatal behavior
below.

**Tenancy & security boundary.** `migrations/0001_initial_schema.sql`'s own
header names its governing contract as `docs/multi-tenant-conformance.md`
and states the schema's "row zero" invariant: a request's community is
resolved from the connection host by the server, never supplied by the
client, and every tenant-scoped row carries that immutable `community_id`.
The `communities` table itself is the one deliberate exception -- marked
operator-global (the tenant registry, not itself tenant-scoped) -- and its
own comment states `resolve_host(host)` reads exactly one row there to mint
a request's `TenantContext`. `migration.rs`'s own lint tests enforce this
boundary mechanically against every embedded migration's SQL, not only
against `0001`.

**Failure behavior, summarized.** Three distinct postures observed in
`crates/buzz-relay/src/main.rs`'s startup sequence: (1) migrations are
opt-in and silently skipped, not failed, when `BUZZ_AUTO_MIGRATE` is unset;
(2) the community-deletion serving-fence check is fatal -- the relay process
errors out rather than serve traffic it cannot prove is deletion-safe; (3)
the replica-freshness fence probe is loud-but-non-fatal -- on any
verification failure it logs an error and leaves the fence closed, routing
every cursor page to the writer rather than risk serving stale or
unreplicated rows. A read-replica pool that is unreachable at boot is a
fourth, warn-only case: `buzz-db` pings it once for visibility but does not
block or crash relay startup, because the lazy pool (`min_connections: 0`)
dials nothing until first use.

## Scope and omissions

**This node covers** Postgres's authoritative role, its owned schema
namespaces at a structural level, its migration mechanism, which components
access it and how, and its consistency, lifecycle, tenancy and failure
characteristics as observed in this repository's own code and configuration.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres's container-level existence, technology name, and one-line responsibility/communication edge | `architecture-containers-postgres` |
| Table-by-table schema contents and the full multi-tenant conformance contract | `migrations/0001_initial_schema.sql`, `docs/multi-tenant-conformance.md` |
| The domain meaning of the data Postgres holds (what a Nostr event, channel or thread *is*) | A future `layers/data/...` data-entity node, not yet drafted at this revision |
| Where this Postgres instance actually runs per environment, replica counts, managed-vs-local, secret provisioning | A future deployment-scoped `layers/platforms/...` or `architecture/deployment/*` node |
| The replica-freshness fence's full correctness proof | `crates/buzz-db/src/runtime/replica_fence.rs`'s own module doc comment and `mod tests` |
| Redis (pub/sub, presence, typing) as a separate datastore | `layers/data/redis/role.md` (#1097), not yet merged at this revision |
| The object-storage (media, Git-CAS) datastore | `layers/data/object-storage/role.md` (#1073), not yet merged at this revision |
| Whether the audit and search pools `buzz-relay` opens directly carry `#[datastore_span]` instrumentation | Not established by this task; named as a gap above |
| Production/staging Postgres provisioning and topology | `squareup/block-coder-tf-stacks` (private, not opened by this task) |

**No relationship to `layers/data/object-storage/role.md` (#1073) or
`layers/data/redis/role.md` (#1097).** Both are unmerged sibling-batch work
at this revision -- neither appears in
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` --
and `AGENTS.md`'s node-creation step 9 makes declaring an edge to an
unmerged id a hard validation error once this branch lands on `launchpad`,
even though it would validate locally in this worktree today.

**Expected but not verified when this node was written:**

- Whether `buzz-relay`'s directly-opened audit and search Postgres pools are
  covered by `#[datastore_span]` tracing was not established -- only
  `buzz-db`'s own call sites were confirmed to carry the attribute.
- Whether staging/production deployment pipelines
  (`squareup/block-coder-tf-stacks`, `squareup/sprout-oss`) set
  `BUZZ_AUTO_MIGRATE`, and what Postgres topology they actually provision,
  could not be established from this repository -- those are separate
  private repositories this task did not open.
- Whether any row-level TTL or retention policy exists outside the
  whole-community deletion path was not exhaustively checked against every
  migration file; the deletion control plane in `migrations/0029_community_deletion.sql`
  is the only retention/lifecycle mechanism this task located.
