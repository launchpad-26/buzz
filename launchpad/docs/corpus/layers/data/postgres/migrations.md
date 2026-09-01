---
id: layers-data-postgres-migrations
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
  - statement: "node.schema.json's type enum has 13 members, including layers, and describes the field only as 'the corpus surface this node documents,' with no per-value definition; standards/taxonomy.md confirms no document defines each of the 13 words beyond that one shared description."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/standards/taxonomy.md"
  - statement: "This node uses type: layers rather than type: architecture, overriding what templates/datastore.md's own note about real instances would otherwise suggest ('a real instance written from this template ... most plausibly takes type: architecture'). This follows the precedent already established by earlier tasks in this same overnight batch under Feature #610, that every layers/data/... corpus document uses type: layers, disclosed here per standards/taxonomy.md step 4 (say so in the node's own scope-and-omissions section when the fit is imperfect or an override is made) rather than left implicit."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "corpus-batch-author overnight run, Feature #610 batch precedent (task instructions for this session)"
  - statement: "launchpad/docs/corpus/architecture/containers/postgres.md carries id architecture-containers-postgres, type: architecture, status: draft, and is present on origin/launchpad at commit 0020a2a03 ('docs(corpus): add architecture container node for Postgres (#657)'), confirmed by git log against that path on origin/launchpad."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "git_log(origin/launchpad, path='launchpad/docs/corpus/architecture/containers/postgres.md') -> 0020a2a03"
  - statement: "No launchpad/docs/corpus/layers/data/postgres/* sibling document exists on origin/launchpad at the recorded revision: git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no layers/ subtree at all, so no relationship target exists there yet (a sibling batch, PR #1875, is unmerged at authoring time)."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, launchpad/docs/corpus) -> no layers/ path present"
  - statement: "Issue #1083's Definition of Done bullets (states whether the store is authoritative/derived/cache/transport; describes owned data, key access patterns, lifecycle/retention and consistency semantics; names tenancy/security boundaries and failure behavior; links schema/migrations/code/tests rather than copying DDL) are, verbatim in shape, the templates/datastore.md required-sections checklist, not a checklist written for a migrations-mechanism subject specifically."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
    confidence: 0.75
  - statement: "crates/buzz-db/src/runtime/migration.rs declares 'static MIGRATOR: sqlx::migrate::Migrator = sqlx::migrate!(\"../../migrations\");' and its module doc comment states 'Fresh deployments apply the checked-in SQL files under migrations/.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "run_migrations (crates/buzz-db/src/runtime/migration.rs) is documented as holding 'the exclusive SCHEMA_DESTRUCTION_LOCK_KEY session lock, serializing schema changes against destructive deletion transactions (which take the shared counterpart while they validate the live catalog and act on it)', implemented by with_exclusive_schema_destruction_lock acquiring 'SELECT pg_advisory_lock($1)' before running migrations and releasing it with 'SELECT pg_advisory_unlock($1)' afterward, on the same connection for the whole run."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "run_migrations's own doc comment states 'Migration execution must never bypass this wrapper — a source lint (migration_execution_cannot_bypass_schema_destruction_lock) enforces that MIGRATOR.run has no other call site', and that lint is a real #[test] in the same file (migration_execution_cannot_bypass_schema_destruction_lock) that scans every .rs file under crates/ and asserts sqlx::migrate! and MIGRATOR.run() each appear exactly once, only in migration.rs, with one documented exception for crates/buzz-push-gateway/src/postgres.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "run_migrations_locked (crates/buzz-db/src/runtime/migration.rs) calls reject_legacy_nip_rs_cardinality_ambiguity before MIGRATOR.run, and crate::replica_fence::verify_floor_guard_catalog after — the migration run fails closed on pre-existing data or a missing invariant guard, not merely applying pending SQL files unconditionally."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "reject_legacy_nip_rs_cardinality_ambiguity (crates/buzz-db/src/runtime/migration.rs) checks, before sqlx starts its migration transaction, whether a populated database still on migrations 0001-0006 contains kind-30078 rows with ambiguous d/t tag cardinality, and returns DbError::InvalidData with the message 'NIP-RS migration blocked: pre-0007 database contains kind-30078 rows with ambiguous d/t tag cardinality; repair or remove those nonconforming rows before retrying' rather than letting migration 0007 run against ambiguous data."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "The migrations/ directory contains 31 sequentially numbered SQL files, 0001_initial_schema.sql through 0031_workflow_run_error_codes.sql, applied by the embedded migrator in that numeric order; embedded_migrator_contains_consolidated_initial_schema (crates/buzz-db/src/runtime/migration.rs test module) asserts migrations.len() == 31 and each migration's version and description, one by one."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0031_workflow_run_error_codes.sql"
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Test comments in crates/buzz-db/src/runtime/migration.rs state a rule for every additive migration after 0001: 'folding it would change 0001's checksum and break brownfield startup (sqlx VersionMismatch)', so a new migration is always its own new numbered file, never folded backward into an earlier one, once that earlier migration may already be recorded as applied by a running relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Db::migrate (crates/buzz-db/src/lib.rs) is annotated #[datastore_span(name = \"migrate\", system = \"postgresql\")] and its body is 'migration::run_migrations(&self.pool).await' — the migration run is itself one instrumented datastore operation under this repository's own tracing policy."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "crates/buzz-relay/src/main.rs calls 'db.migrate().await' during relay startup (line 191), matching root CLAUDE.md's Repo Structure table description of migrations/ as 'SQL migrations (auto-applied on relay startup)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "CLAUDE.md"
  - statement: "crates/buzz-admin/src/main.rs's Command::Migrate arm calls 'db.migrate().await?' and prints 'Database migrations complete.' on success — an operator-triggered path through the same Db::migrate entry point relay startup uses, reachable via 'cargo run -p buzz-admin -- migrate'."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "The Justfile's migrate recipe depends on _ensure-migrations, whose comment reads 'Apply database migrations and seed the local dev community if the dev database is running', and whose body runs 'cargo run -p buzz-admin -- migrate'; CONTRIBUTING.md's dependency table lists 'sqlx migrations | workspace crate | just migrate applies embedded migrations from migrations/'."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "CONTRIBUTING.md"
  - statement: "schema/schema.sql's own header comment describes itself as 'Source of truth for fresh database setup. This is a clean, from-scratch schema ... It is NOT additive over the single-community schema; the rewrite replaces it.' It is a separate, hand-maintained file from the numbered migrations/ directory, not itself applied by the sqlx migrator."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "deletion_surface_parity_between_migration_0029_and_schema_sql (crates/buzz-db/src/runtime/migration.rs test module) structurally parses migration 0029's tables/functions/triggers/indexes/registry rows/fence attachments/added columns and asserts each exists with an identical normalized definition in schema/schema.sql, described in its own doc comment as guarding against schema.sql silently omitting part of the deletion surface migration 0029 defines."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "crates/buzz-push-gateway/migrations is a second, separate sqlx migrator with its own migration files, exempted by name (push_gateway_exception) from the migration_execution_cannot_bypass_schema_destruction_lock lint, which additionally asserts every SQL file under crates/buzz-push-gateway/migrations does not reference community_id — confirming its tables are outside the relay's tenant schema and outside the schema/destruction lock this document covers."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
relationships:
  - type: part-of
    target: architecture-containers-postgres
---

# Postgres schema migrations: reference

This node catalogues how the Buzz relay's Postgres schema is versioned and
applied — the embedded migrator, its ordering and locking guarantees, and the
guard checks that run around it — as distinct from the container-level fact
that Postgres exists and is one of Buzz's datastores, which
`architecture-containers-postgres` already covers. This is a zoomed-in view of
one mechanism belonging to that container: how its schema changes over time,
not what the container is or what domain data it holds.

## Migration mechanism

Prose first, because the mechanism's behavior needs describing before the
table below is legible per Diátaxis's reference-form nuance (reference
material "can and often needs to include a description of how something
works").

Every schema change to the relay's tenant database lives as a numbered SQL
file under `migrations/` (`0001_initial_schema.sql` through
`0031_workflow_run_error_codes.sql` at the recorded revision — 31 files,
sequential, no gaps). `crates/buzz-db/src/runtime/migration.rs` embeds them at compile
time as a static `sqlx::migrate::Migrator` (`sqlx::migrate!("../../migrations")`)
and applies them in numeric order. There is exactly one call site for that
migrator's `.run()` method in the whole workspace, enforced by a source lint
(`migration_execution_cannot_bypass_schema_destruction_lock`) that scans every
`.rs` file under `crates/` — a migration cannot be triggered from anywhere
else in the codebase without failing that test.

The entire migration run executes inside one exclusive Postgres advisory lock
(`SCHEMA_DESTRUCTION_LOCK_KEY`), acquired before the first migration statement
and released only after the run finishes (success or error). This serializes
schema changes against a shared counterpart lock that destructive
community-deletion transactions hold while validating and acting on the live
catalog — schema evolution and destructive deletion cannot interleave.
Immediately before running the embedded migrator, a guard
(`reject_legacy_nip_rs_cardinality_ambiguity`) checks whether a database still
on migrations 0001–0006 contains rows that migration 0007's destructive purge
would handle ambiguously, and refuses to proceed rather than silently
corrupting history. Immediately after, a second guard
(`replica_fence::verify_floor_guard_catalog`) confirms every `events` table
partition still carries the commit-time floor trigger migration 0021
introduced, because `CREATE TABLE .. PARTITION OF` clones a parent's triggers
but `ATTACH PARTITION` does not, and a missing guard on any one partition
would silently defeat a replica-fence correctness proof elsewhere in the
system.

Migrations are additive-only once a version has plausibly been recorded as
applied by a running relay: sqlx checksums each migration file, so editing an
already-shipped file changes its checksum and breaks startup
(`VersionMismatch`) for any deployment that already applied it. Every later
migration in the directory is its own new file for exactly this reason — the
test suite's own inline comments document this rule migration-by-migration
(e.g. "folding it would change 0001's checksum and break brownfield startup").

| Property | Description | Evidence |
|---|---|---|
| Embedding | Migrations are compiled into the `buzz-db` binary via `sqlx::migrate!("../../migrations")`, not read from disk at runtime. | `crates/buzz-db/src/runtime/migration.rs` |
| Ordering | Applied strictly in ascending numeric-prefix order; 31 files at the recorded revision. | `migrations/0001_initial_schema.sql`–`migrations/0031_workflow_run_error_codes.sql` |
| Single entry point | Exactly one call site for `MIGRATOR.run`, enforced by a compiled-in lint test scanning the whole workspace. | `crates/buzz-db/src/runtime/migration.rs` (`migration_execution_cannot_bypass_schema_destruction_lock`) |
| Concurrency / locking | The whole run holds the exclusive `SCHEMA_DESTRUCTION_LOCK_KEY` Postgres advisory lock, serialized against destructive-deletion transactions' shared counterpart. | `crates/buzz-db/src/runtime/migration.rs` (`with_exclusive_schema_destruction_lock`) |
| Pre-run guard | `reject_legacy_nip_rs_cardinality_ambiguity` blocks migration 0007 against pre-existing ambiguous kind-30078 rows rather than purging them silently. | `crates/buzz-db/src/runtime/migration.rs` |
| Post-run guard | `replica_fence::verify_floor_guard_catalog` confirms every `events` partition still carries the required floor trigger after migrating. | `crates/buzz-db/src/runtime/migration.rs` |
| Additivity rule | Once a version may already be applied in the field, its file is never edited (checksum-frozen); new schema changes are always a new, higher-numbered file. | `crates/buzz-db/src/runtime/migration.rs` (test-module comments, e.g. migrations 0002–0005) |
| Instrumentation | The migration run is one `#[datastore_span(name = "migrate", system = "postgresql")]`-traced operation. | `crates/buzz-db/src/lib.rs` (`Db::migrate`) |
| Trigger points | Auto-applied at relay startup (`crates/buzz-relay/src/main.rs`) and operator-triggered via `buzz-admin`'s `migrate` subcommand. | `crates/buzz-relay/src/main.rs`, `crates/buzz-admin/src/main.rs`, `CLAUDE.md` |
| Desired-state cross-check | `schema/schema.sql` is a separate, hand-maintained "fresh install" schema, not applied by the migrator itself, but structurally parity-checked against migration 0029's deletion surface by a dedicated test so the two cannot silently diverge. | `schema/schema.sql`, `crates/buzz-db/src/runtime/migration.rs` (`deletion_surface_parity_between_migration_0029_and_schema_sql`) |
| Separate migrator boundary | `crates/buzz-push-gateway/migrations` is a second, independent sqlx migrator for the push gateway's own non-tenant tables, explicitly exempted from and checked against this schema/destruction lock's scope. | `crates/buzz-db/src/runtime/migration.rs` (`push_gateway_exception`, `push_gateway_migrations`) |

## Commands

| Command | Description | Argument | Example |
|---|---|---|---|
| `just migrate` | Runs the `_ensure-migrations` recipe, which starts required services then applies pending migrations via `buzz-admin`. | none | `just migrate` |
| `cargo run -p buzz-admin -- migrate` | Direct invocation of the same migration path `just migrate` wraps; connects, runs `Db::migrate()`, prints `Database migrations complete.` on success. | none | `cargo run -p buzz-admin -- migrate` |

## Boundary

This node does not describe:
- **Whether Postgres is authoritative, derived, cache or transport, or its
  owned data, access patterns, lifecycle/retention and consistency
  semantics.** Those are container-level identity questions about the
  Postgres datastore as a whole, owned by `architecture-containers-postgres`,
  not by a node scoped to one mechanism (schema versioning) inside it. Issue
  #1083's own Definition of Done carries those bullets verbatim from
  `templates/datastore.md`'s checklist — see the evidence-ledger entry above
  and *Scope and omissions* below for why this document does not force its
  narrower subject to answer them.
- **How to author and land one new migration, step by step, as a task a
  developer performs.** No corpus template task for that how-to shape was
  found to exist at authoring time (`templates/procedure.md` documents the
  how-to/procedure template itself, not an instance of it) — named as a gap,
  not invented here.
- **The push gateway's own migrator or schema**, beyond noting its existence
  and its exemption from this mechanism's schema/destruction lock. Its tables
  are not tenant-scoped and are outside this node's subject.
- **The domain meaning of any table a migration creates** (what a `channel`
  or an `events` row *is*) — that is a data-entity-shaped node's job, not this
  reference node's, per `templates/datastore.md`'s own boundary against
  data-entity.

## Relationships

- part-of: architecture-containers-postgres

## Scope and omissions

**This node covers** the Buzz relay's Postgres schema-migration mechanism:
how migrations are embedded, ordered, and applied; the exclusive
schema-destruction lock serializing schema changes against destructive
deletion; the pre- and post-run correctness guards; the additive-only,
checksum-frozen convention; the operator- and startup-triggered entry points;
and the boundary against the separate push-gateway migrator and against
`schema/schema.sql`'s desired-state role.

**`type: layers`, disclosed.** This node uses `type: layers` rather than
`type: architecture`, which is what `templates/datastore.md`'s own note about
real instances written from it would otherwise suggest ("most plausibly takes
`type: architecture`"). This follows the precedent already set by earlier
`layers/data/...` documents in this same overnight batch under Feature #610.
`standards/taxonomy.md` states that when precedent does not fully resolve a
`type` choice, the gap should be disclosed rather than silently picked; this
is that disclosure.

**Issue #1083's Definition of Done, and why this node does not force every
bullet.** Four of its bullets ("authoritative/derived/cache/transport";
"owned data, access patterns, lifecycle/retention, consistency semantics";
"tenancy/security boundaries and failure behavior"; "links schema/migrations/
code/tests rather than copying DDL") are, in shape, `templates/datastore.md`'s
own required-sections checklist — a template for documenting a *whole
datastore instance*, not a single mechanism inside one. This issue's actual
Objective names a narrower subject: "the single canonical datastore node for
migrations." The tenancy/security/failure bullet is answered directly above
(the schema-destruction lock, the two run guards); the
authoritative/derived/owned-data/access-pattern bullets are named out of scope
in *Boundary*, above, and owned by `architecture-containers-postgres` instead
of stretched to fit a subject that has no data of its own to own. This is the
same kind of Definition-of-Done mismatch `templates/procedure.md` and
`templates/reference.md` each record for their own issues in this corpus
effort, disclosed here rather than silently forced.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres container-level identity, ownership, lifecycle, tenancy | `architecture-containers-postgres` |
| A how-to for authoring and landing one new migration | No corpus template task found for this at authoring time |
| The push gateway's own migrator and schema | Not this node's subject; noted only as a boundary |
| The domain meaning of tables a migration creates | A data-entity-shaped node for that table, not yet written |
| `schema/schema.sql`'s desired-state role as its own concept | Not yet its own corpus node; cited here only as a parity-checked artifact |

**Expected but not verified when this node was written:**

- **Whether `schema/schema.sql` is used anywhere at runtime (e.g. a
  fresh-install bootstrap path) versus existing only as this test suite's
  parity fixture** was not established. Its header comment calls it "source
  of truth for fresh database setup," but no runtime call site reading it was
  found during this session's search; only the test-module `include_str!`
  usages were confirmed.
- **Whether a future `templates/procedure.md`-shaped how-to node for
  authoring a new migration should exist** was not resolved — named as a gap
  above only.
