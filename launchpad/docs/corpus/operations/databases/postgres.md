---
id: operations-databases-postgres
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The required Postgres version is 17, shipped as the postgres:17-alpine image, in every topology this repository defines: the root local-development docker-compose.yml, the self-hosted deploy/compose/compose.yml, and (for the eval-only in-cluster subchart) deploy/charts/buzz's postgresql dependency."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "deploy/compose/compose.yml"
  - statement: "migrations/0001_initial_schema.sql runs CREATE EXTENSION IF NOT EXISTS pgcrypto as the first statement of the schema, and no other migration file under migrations/ contains a CREATE EXTENSION statement, so pgcrypto is the one Postgres extension this repository requires."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "DbConfig (crates/buzz-db/src/runtime/mod.rs) is the struct buzz-relay, buzz-admin, and buzz-deletion all pass to Db::new; its Default impl sets max_connections 20, min_connections 2, acquire_timeout_secs 3, max_lifetime_secs 1800, and idle_timeout_secs 600, with a doc comment recording that staging measured 51 idle plus 1 active out of a 50-connection budget."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "buzz-relay's own startup code (crates/buzz-relay/src/main.rs) never uses DbConfig::default()'s literal max_connections value: it builds DbConfig with max_connections explicitly set to config.db_pool_size and read_max_connections to config.db_read_pool_size, spreading only the remaining fields (min_connections, the three timeouts, replica_read_max_age_ms) from ..DbConfig::default(). config.db_pool_size (crates/buzz-relay/src/config.rs) parses BUZZ_DB_POOL_SIZE and defaults to 50, not 20, when the variable is unset or non-positive."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The effective, operator-facing default writer-pool ceiling for a deployed relay is therefore 50 connections (BUZZ_DB_POOL_SIZE's own default), not the 20 that DbConfig::default()'s doc comment describes -- the doc comment documents the struct's own fallback value, which every real relay-driven construction path overrides before Db::new ever runs."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
    confidence: 0.85
  - statement: ".env.example comments '# BUZZ_DB_POOL_SIZE=50 ... READ_DATABASE_URL is set, reader (default 50)', matching config.rs's parsed default rather than DbConfig::default()'s literal 20."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "BUZZ_DB_READ_POOL_SIZE (crates/buzz-relay/src/config.rs) parses to an Option<u32> with no fallback value of its own; when unset it is None, and Db::new (crates/buzz-db/src/runtime/mod.rs) then sizes the read-replica pool from config.max_connections instead, i.e. it inherits the writer's effective size rather than taking a hardcoded default of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "READ_DATABASE_URL (crates/buzz-relay/src/config.rs) is trimmed and treated as unset when blank; a unit test in the same file asserts directly that both an unset and a blank READ_DATABASE_URL 'must disable routing', and Db::new only opens a second pool when config.read_database_url is Some."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "The read-replica pool is connected lazily (Db's connect_read_pool path) with min_connections pinned to 0 and a 150-millisecond acquire timeout (Db::READER_ACQUIRE_TIMEOUT), so a reader that is unreachable at boot cannot block or crash relay startup, and a saturated or absent reader fails closed to the writer quickly rather than adding writer-scale latency to a routed read."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "buzz-relay's main.rs parses BUZZ_AUTO_MIGRATE case-insensitively and trimmed via buzz_auto_migrate_enabled, which returns true only for the literal values true, 1, yes, or on; every other value, including an unset variable, is treated as disabled and logs 'Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled' rather than running migration.rs's embedded sqlx::migrate! runner."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-admin's Migrate subcommand (crates/buzz-admin/src/main.rs) connects a Db and calls db.migrate(), which runs the identical embedded migration path (crates/buzz-db/src/runtime/migration.rs) that buzz-relay's BUZZ_AUTO_MIGRATE gate would otherwise invoke, guarded by the same exclusive Postgres advisory lock -- it is a separate, explicit trigger for the same migration runner, not a different code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "The local-development Justfile's migrate recipe, and every recipe that depends on _ensure-migrations (relay, relay-web, admin, admin-seed, dev, relay-release, and the desktop-e2e recipes), runs 'cargo run -p buzz-admin -- migrate' followed by ./scripts/seed-local-community.sh, after first waiting for the Postgres and Redis Docker healthchecks in _ensure-services to report healthy; local development therefore migrates through buzz-admin migrate and never sets BUZZ_AUTO_MIGRATE, which .env.example does not mention at all."
    entry_class: FACT
    evidence:
      - "Justfile"
      - ".env.example"
  - statement: "The repository-root docker-compose.yml provisions only infrastructure services (postgres, redis, adminer, keycloak, minio, minio-init, prometheus) for local development; it defines no relay service and sets no BUZZ_AUTO_MIGRATE value, consistent with migrations being driven by the Justfile's buzz-admin migrate step rather than by the relay's own startup gate in this topology."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "deploy/compose/compose.yml (the self-hosted single-host production bundle, distinct from the repository-root development compose file) passes BUZZ_AUTO_MIGRATE: ${BUZZ_AUTO_MIGRATE:-false} to the relay container -- the same off-by-default the relay binary itself applies -- while deploy/compose/.env.example ships the variable pre-set to BUZZ_AUTO_MIGRATE=true, so an operator who copies that template file to .env, rather than leaving the variable unset, gets migrations applied automatically on every relay start."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
      - "deploy/compose/.env.example"
  - statement: "deploy/charts/buzz/values.yaml's migrate.autoMigrate defaults to true, and deploy/charts/buzz/templates/deployment.yaml renders it directly into the relay container's BUZZ_AUTO_MIGRATE environment variable, so the Helm chart's shipped default runs migrations automatically on every pod start unless an operator explicitly sets migrate.autoMigrate=false -- the opposite default from the relay binary's own unset-is-disabled behavior."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "deploy/charts/buzz/README.md states that with migrate.autoMigrate=false 'the chart does not run migrations for you' and that an operator then owns running buzz-admin migrate as a separate Pod or one-shot Job before every helm install/helm upgrade, and separately states that readiness probes only verify DB connectivity, not schema freshness, so a pod can appear healthy against an unmigrated schema and fail under load."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "deploy/charts/buzz/README.md states that migration 0032 is 'a hard compatibility boundary for relay versions that publish repaired channel rosters' and that the relay verifies the roster-fence trigger catalog and behavior before opening listeners, refusing to start if migration 0032 is missing or inert; the same document recommends a controlled buzz-admin migrate job with PostgreSQL lock monitoring ahead of the code rollout for large installations."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "Three deployment topologies for provisioning Postgres exist in this repository at the recorded revision: the root docker-compose.yml (local development, infrastructure only, no relay service), deploy/compose/ (a self-hosted single-host production bundle of relay+postgres+redis+minio+optional Caddy TLS, run through deploy/compose/run.sh), and deploy/charts/buzz (a Helm chart with a production profile expecting external managed Postgres via externalPostgresql.url or secrets.existingSecret's DATABASE_URL key, and an eval-only quickstart profile that bundles an in-cluster Postgres via the postgresql.enabled CloudPirates subchart)."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "deploy/compose/compose.yml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "deploy/charts/buzz/templates/secret-chart.yaml composes DATABASE_URL itself only when postgresql.enabled is true (from the in-cluster subchart's host, database and username plus a generated or looked-up postgres-password) or when externalPostgresql.url is set; when neither applies -- the production default with secrets.existingSecret supplied -- DATABASE_URL must come from that existing Secret instead, and the chart-managed Secret template renders no DATABASE_URL key in that case."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/secret-chart.yaml"
  - statement: "The relay exposes three distinct HTTP endpoints touching health: /health (a bare 200 OK with no dependency checks), /_liveness (also a bare 200 OK, used by the Helm chart's livenessProbe and startupProbe), and /_readiness, whose handler checks a shutdown flag first, then concurrently (tokio::join!, 2-second overall timeout) pings Postgres via Db::ping (SELECT 1), checks the Redis pool, and calls db.validate_deletion_serving_catalog; it returns 503 with a per-check JSON breakdown if the shutdown flag is set, the timeout elapses, or any of the three checks fails, and 200 with {\"status\":\"ready\"} only when all three succeed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "deploy/charts/buzz/values.yaml wires livenessProbe and startupProbe to GET /_liveness and readinessProbe to GET /_readiness on the health port, and deploy/compose/compose.yml's relay healthcheck independently probes /_readiness over a raw /dev/tcp connection (the runtime image ships bash but no curl, wget, or socat) rather than /health or /_liveness, so both non-development topologies gate container health on the readiness check that includes the Postgres ping, not on the liveness check that does not."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/compose/compose.yml"
  - statement: "Both docker-compose.yml (local development) and deploy/compose/compose.yml (self-hosted production) run pg_isready against the postgres container itself as its own Docker healthcheck, independent of and upstream from the relay's own /_readiness check; docker-compose.yml's local Postgres container additionally carries a 512m memory limit."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "deploy/compose/compose.yml"
  - statement: "Db::ensure_future_partitions (crates/buzz-db/src/store/partition.rs) is called with an argument of 3 exactly once in this repository, from buzz-relay's own startup sequence in main.rs; no other caller, cron configuration, Kubernetes CronJob template, or scheduled Justfile recipe invokes it anywhere in this repository, even though the function's own module doc comment says to 'call ensure_future_partitions on startup and monthly via cron.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/partition.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "Because ensure_future_partitions only runs at relay-process startup and nothing in this repository schedules it independently, keeping the events and delivery_log tables' monthly partitions ahead of the current month depends entirely on the relay restarting at least once every three months (the months_ahead argument main.rs passes); this repository defines no operator-facing alert or check for a relay that runs longer than that without a restart."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/partition.rs"
      - "crates/buzz-relay/src/main.rs"
    confidence: 0.8
  - statement: "buzz-search's SearchService (crates/buzz-search/src/lib.rs) is a thin wrapper around a PgPool constructed independently in buzz-relay's main.rs, preferring READ_DATABASE_URL when set and falling back to the writer's database_url otherwise; that pool is created with sqlx::postgres::PgPoolOptions::new() and no explicit .max_connections(...) or .min_connections(...) call, unlike the writer, reader, and 5-connection audit pools, which all set max_connections explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-search/src/lib.rs"
  - statement: "buzz-search's own crate-level doc comment states that its full-text search index is not a separate structure: the events table carries 'search_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED' with 'GIN (search_tsv)' as the access path, so indexing is the ordinary row insert owned by buzz-db and there is no separate indexer, queue, reindex job, or consistency window for an operator to manage."
    entry_class: FACT
    evidence:
      - "crates/buzz-search/src/lib.rs"
  - statement: "migrations/0001_initial_schema.sql defines the search_tsv column exactly as buzz-search's doc comment describes (a GENERATED ALWAYS STORED tsvector over content using the 'simple' text search configuration) and creates idx_events_search_tsv as a single-column GIN index over it, with an adjacent code comment noting the index is deliberately minimal because community-scoping filters are handled by leading btree predicates BitmapAnd-ed with the GIN probe rather than folded into the GIN index itself."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
  - statement: "An operator therefore has no separate search index to provision, rebuild, or monitor for staleness against the events table: because the tsvector column is database-computed and always in step with the row that carries it, any operational procedure this node would otherwise describe for keeping full-text search current does not apply here."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-search/src/lib.rs"
      - "migrations/0001_initial_schema.sql"
    confidence: 0.85
  - statement: "This repository contains no pg_dump, pg_restore, pg_basebackup, or other backup-execution script or automation for Postgres; the only two mentions of pg_dump anywhere in the repository are prose recommendations -- deploy/compose/run.sh's backup_hint function ('Postgres data (prefer pg_dump or a quiesced volume snapshot)') and scripts/cutover/README.md's 'Take a pg_dump / PVC snapshot first' -- neither of which is itself an executable backup procedure."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "deploy/charts/buzz/README.md's Backups section names 'PostgreSQL database -- the canonical event store' as one of five items an operator must save, stating that losing any of them is data loss, but the chart itself implements no backup automation for any of the five -- it only documents the requirement."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "Issue #618's dispatch brief names backup (#1197), migrations (#1198), restore (#1202), and database-failure (#1215) as sibling operations-corpus tasks to this one, and instructs this node to name those boundaries in prose; none of the four exists as a resolvable corpus node id on origin/launchpad at the recorded revision (checked against the id list supplied to this batch), so no relationships[] edge to any of them is declared."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#618 dispatch brief for this batch, and the existing-node-ids listing supplied alongside it"
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md (id architecture-containers-postgres) is a merged-shaped sibling node that already covers Postgres's container-level responsibility, the buzz-db/buzz-relay ownership split, the replica-freshness fence mechanism, and partitioning, and states in its own scope-and-omissions table that production/staging Postgres provisioning is owned by a private repository (squareup/block-coder-tf-stacks) it did not open."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "This node's own attempt to verify what BUZZ_AUTO_MIGRATE value, connection-pool sizing, or Postgres topology squareup/block-coder-tf-stacks and squareup/sprout-oss actually configure for staging or production could not be completed for the same reason architecture-containers-postgres.md records: those are separate private repositories this task did not open."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad/docs/corpus/architecture/containers/postgres.md's own scope-and-omissions table, and this task's own attempt to check the same repositories"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference-description paragraph, structured entries ordered to match the source's own declaration order, an optional Commands section, an explicit boundary statement, relationships guidance, and a scope-and-omissions section separating what the node excludes from what it expected to verify and could not."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-deployment-docker-compose
  - type: references
    target: architecture-deployment-kubernetes
---

# Postgres: operations reference

What an operator actually configures, provisions, and checks for Postgres as
Buzz's system of record -- required version and extensions, the connection-pool
and migration knobs exposed as environment variables, how Postgres is stood up
across this repository's three deployment topologies, and the health checks
that gate traffic on it. `architecture-containers-postgres.md` is the
container-level companion to this node: it explains *why* the schema, the pool
architecture, and the replica-freshness fence are shaped the way they are. This
node catalogues the operational surface an operator turns knobs on, and does
not restate that reasoning.

## Configuration keys and operational knobs

Ordered to match where each variable is consumed in the source, not
alphabetically. "Effective default" is what an operator gets when the
variable is unset, which is not always the same as a struct's own literal
default value -- see the pool-sizing entries below.

| Key | Consumed by | Effective default | Description |
|---|---|---|---|
| `DATABASE_URL` | `crates/buzz-relay/src/config.rs` | `postgres://buzz:buzz_dev@localhost:5432/buzz` (local dev only; production topologies require an explicit value) | Writer connection string for the primary Postgres pool. |
| `READ_DATABASE_URL` | `crates/buzz-relay/src/config.rs` | unset -- disables replica routing | Optional read-replica connection string. Trimmed; a blank value is treated as unset. When set, `buzz-db` opens a second, lazily-connected pool and search/reads may route to it. |
| `BUZZ_DB_POOL_SIZE` | `crates/buzz-relay/src/config.rs` | `50` | Writer pool `max_connections`. This is the value that actually reaches `Db::new` -- `DbConfig::default()`'s own literal `20` is never used by a relay-driven construction path. |
| `BUZZ_DB_READ_POOL_SIZE` | `crates/buzz-relay/src/config.rs` | inherits `BUZZ_DB_POOL_SIZE`'s effective value | Read-replica pool `max_connections`, only meaningful when `READ_DATABASE_URL` is set. |
| `BUZZ_AUTO_MIGRATE` | `crates/buzz-relay/src/main.rs` (`buzz_auto_migrate_enabled`) | disabled (any value other than `true`/`1`/`yes`/`on`, case-insensitive and trimmed, including unset) | Gates whether the relay process runs pending `sqlx::migrate!` migrations at its own startup, under an exclusive Postgres advisory lock. Off by default in the relay binary itself; see *Boundary* for where the shipped defaults differ by topology. |
| `BUZZ_AUDIT_ENABLED` | `crates/buzz-relay/src/main.rs` | disabled | Gates a separate, directly-constructed 5-connection (1 minimum) Postgres pool backing `buzz-audit`'s hash-chain log. Not part of `buzz-db::Db`. |
| — (search pool) | `crates/buzz-relay/src/main.rs` | prefers `READ_DATABASE_URL`, else `DATABASE_URL` | A third, independently-constructed Postgres pool backing `buzz-search`. Built with `PgPoolOptions::new()` and no explicit `.max_connections(...)`, unlike the writer, reader, and audit pools. |

## Commands

| Command | Where | Description |
|---|---|---|
| `just migrate` | `Justfile` | Local development: waits for the Postgres/Redis Docker healthchecks, then runs `cargo run -p buzz-admin -- migrate` followed by `./scripts/seed-local-community.sh`. `just relay`, `just relay-web`, `just admin`, `just admin-seed`, `just dev`, `just relay-release`, and the `desktop-e2e-*` recipes all depend on the same `_ensure-migrations` step. |
| `buzz-admin migrate` | `crates/buzz-admin/src/main.rs` | Connects a `Db` and calls `db.migrate()` directly -- the same embedded, advisory-lock-guarded migration runner `BUZZ_AUTO_MIGRATE` would otherwise trigger from relay startup. This is the command `deploy/charts/buzz/README.md` recommends running as a separate Pod/Job ahead of a rolling upgrade when `migrate.autoMigrate=false`. |
| `deploy/compose/run.sh {start\|stop\|...}` | `deploy/compose/run.sh` | Wraps `docker compose --env-file .env` for the self-hosted single-host bundle (relay, Postgres, Redis, MinIO, optional Caddy TLS). Refuses to start if `.env` is missing or still contains `CHANGE_ME` placeholders. Its `backup_hint` output names Postgres data as one of the things to snapshot before an upgrade -- see *Boundary*. |
| `helm install / helm upgrade` | `deploy/charts/buzz` | `helm upgrade` is the chart's entire documented upgrade procedure. With the chart's default `migrate.autoMigrate=true`, each relay pod start races safely for the migration advisory lock; with `migrate.autoMigrate=false`, migrations must be applied separately (see *Boundary*) before rolling the relay, because readiness probes check connectivity, not schema freshness. |

## Boundary

This node does not describe:

- **Why the pool, schema, and replica-fence are shaped this way** -- the
  design rationale for partitioning, the floor-guard trigger, and the
  writer/reader split belongs to `architecture-containers-postgres.md`, the
  container-level node this one links rather than restates.
- **How to actually author a migration, or the migration numbering/locking
  contract in depth** -- that is the migrations operations node's subject
  (issue #1198 at the time this node was written; not yet a corpus node on
  `origin/launchpad`).
- **How to take or verify a backup, or how to restore one** -- both are
  named above only to record that this repository has no executable
  automation for either today (see the evidence ledger); the procedures
  themselves are the backup (#1197) and restore (#1202) operations nodes'
  subject.
- **What an operator does when Postgres itself is unreachable, corrupted, or
  has failed over** -- that is the database-failure node's subject (#1215).
- **A full API-reference-depth catalogue of every `buzz-db` data-access
  module or every migration file** -- this node stops at the operator-facing
  surface (connection strings, pool sizes, migration triggers, health
  checks, provisioning topology), not the internal schema or query layer.
- **Production/staging topology, credentials, or actual `BUZZ_AUTO_MIGRATE`
  values used by this project's real deployments** -- `squareup/block-coder-tf-stacks`
  and `squareup/sprout-oss` own that, and are private repositories this task
  did not open; see *Scope and omissions*.

The Helm chart's `migrate.autoMigrate` defaulting to `true` and the
self-hosted `deploy/compose`'s shipped `.env.example` defaulting
`BUZZ_AUTO_MIGRATE=true`, against the relay binary's own unset-is-disabled
behavior and the self-hosted compose file's own `${BUZZ_AUTO_MIGRATE:-false}`
fallback, is a genuine cross-source discrepancy in shipped defaults recorded
in the evidence ledger above rather than resolved here -- three different
"what happens if an operator sets nothing" answers exist across three
topologies, and an operator moving between them should not assume the
behavior they saw in one carries to another.

## Relationships

- `references architecture-containers-postgres` -- the container-level node
  this one is the operations-side companion to; declared because a reader
  arriving here for a specific env var or command should be one link away
  from why the system behind it is shaped the way it is.
- `references architecture-deployment-docker-compose` -- covers the
  self-hosted `deploy/compose` bundle's full multi-service topology (relay,
  Postgres, Redis, MinIO, optional Caddy), of which this node only describes
  the Postgres-specific slice.
- `references architecture-deployment-kubernetes` -- covers `deploy/charts/buzz`'s
  full chart (profiles, HA requirements, autoscaling, secrets composition),
  of which this node only describes the Postgres-specific slice.
- No `relationships[]` edge is declared to any sibling `operations/**` node
  (migrations, backup, restore, database-failure): none of their ids resolve
  on `origin/launchpad` at the recorded revision, and a `relationships[].target`
  naming an id no loaded node carries is a hard validation error. They are
  named in prose in *Boundary* instead.

## Scope and omissions

**This node covers** the Postgres version and extension this repository
requires; the environment variables that control connection pooling,
replica routing, and migration triggering, and their effective (not merely
literal-default) values; how the full-text search dependency is wired so an
operator understands there is no separate index to maintain; how Postgres is
provisioned across this repository's three deployment topologies (local
development, self-hosted compose, Kubernetes/Helm); the relay's health-check
surface and which checks gate on Postgres; and the operator-facing commands
that trigger migrations.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Container-level responsibility, pool architecture rationale, replica-freshness fence design | `architecture-containers-postgres.md` |
| Full self-hosted compose deployment topology beyond Postgres | `architecture-deployment-docker-compose.md` |
| Full Kubernetes/Helm deployment topology beyond Postgres | `architecture-deployment-kubernetes.md` |
| Authoring or numbering a migration; the migration-locking contract in depth | #1198, not yet a corpus node at the recorded revision |
| Backup procedure and verification | #1197, not yet a corpus node at the recorded revision |
| Restore procedure | #1202, not yet a corpus node at the recorded revision |
| Failure/incident response for Postgres | #1215, not yet a corpus node at the recorded revision |
| Table-by-table schema contents and the multi-tenant conformance contract | `migrations/0001_initial_schema.sql`, `docs/multi-tenant-conformance.md` |

**Expected but not verified when this node was written:**

- **Real staging/production `BUZZ_AUTO_MIGRATE` values, pool sizes, and
  Postgres topology** -- whether either deployment pipeline
  (`squareup/block-coder-tf-stacks`, `squareup/sprout-oss`) overrides the
  Helm chart's or self-hosted compose's shipped defaults could not be
  checked; both are private repositories outside this repository's tree.
- **Whether any relay deployment in practice runs longer than three months
  without a restart**, which would leave `ensure_future_partitions`'s
  startup-only invocation short of the partitions the events/delivery_log
  tables need. No operator-facing alert for this condition exists in this
  repository to check against.
- **Whether the search pool's unset `max_connections` (defaulting to sqlx's
  own internal default) has ever caused connection pressure in practice** --
  only the source construction was read; no runtime metric for this specific
  pool was examined.
- **Whether `deploy/charts/buzz`'s `migrate.preUpgradeJob.enabled` knob (the
  README calls it "reserved," not yet implemented) has since landed** --
  checked only at the recorded revision.
