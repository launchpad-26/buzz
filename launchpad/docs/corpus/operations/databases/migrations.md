---
id: operations-databases-migrations
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-db embeds every file under the repository-root migrations/ directory into the relay binary at compile time via sqlx::migrate!(\"../../migrations\"), assigned to a static MIGRATOR; this is the sole mechanism that applies incremental schema changes to a running deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:15"
  - statement: "The public entry point run_migrations acquires the exclusive Postgres advisory session lock SCHEMA_DESTRUCTION_LOCK_KEY on a detached connection, runs the migration batch on that same connection, then explicitly releases the lock and closes the connection on both the success and error paths -- serializing schema changes against buzz-db's destructive deletion transactions, which take the shared counterpart of the same lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:17-33"
      - "crates/buzz-db/src/runtime/migration.rs:77-103"
  - statement: "A source lint, migration_execution_cannot_bypass_schema_destruction_lock, scans every .rs file under crates/ and asserts sqlx::migrate!, MIGRATOR.run(, and MIGRATOR.run_to( each appear exactly once in migration.rs and nowhere else workspace-wide (with one named exception: buzz-push-gateway's own dedicated, non-tenant-scoped authority database), and that the one production run site sits inside run_migrations_locked, reached only through the exclusive-lock wrapper -- so no other code path in the workspace can run a migration outside that lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:1476"
  - statement: "Before running any pending SQL, run_migrations_locked calls reject_legacy_nip_rs_cardinality_ambiguity, which queries whether migration 0007 (checksum-frozen, and described in its own doc comment as a step that would 'irreversibly purge duplicate-tag history') has already been applied; if not, and the database holds a specific class of ambiguous pre-existing kind:30078 rows, the function returns an error before sqlx starts its migration transaction, specifically so an operator can inspect and repair the data first."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:106-109"
  - statement: "A test, pre_0007_ambiguous_nip_rs_data_blocks_without_mutation_and_allows_retry, demonstrates that this pre-check fails run_migrations without changing which migration versions are recorded as applied and without mutating the offending row, and that repairing the row and re-calling run_migrations then succeeds and reaches the migrator's latest embedded version -- i.e. a blocked migration run is retried by fixing the underlying condition and re-invoking the same migration entry point, not by any separate resume or rollback command."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:2240"
  - statement: "After the migration batch itself completes, run_migrations_locked re-verifies two additional catalog invariants on every run -- the replica-fence commit-time created_at floor trigger (from migration 0021) on the events parent table and every partition, and the channel-roster snapshot fence -- and fails the whole call if either is missing from any partition, even one attached outside the normal migration path."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:50-59"
  - statement: "Migration files are named with a four-digit, zero-padded, monotonically increasing sequence number followed by an underscore and a snake_case description (for example 0001_initial_schema.sql and 0040_push_message_kinds.sql), and sqlx's embedded migrator discovers, orders and records applied migrations by that numeric version; at the recorded revision the directory holds exactly one file per integer from 1 through 40 with no gaps, established by a full directory listing of migrations/ rather than by opening every individual file."
    entry_class: INFERENCE
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0021_created_at_fence_floor.sql"
      - "migrations/0040_push_message_kinds.sql"
      - "crates/buzz-db/src/runtime/migration.rs:15"
    confidence: 0.9
  - statement: "Once a migration file has shipped and may already be recorded by a running relay, its SQL is treated as immutable: sqlx tracks a checksum per applied version, and this repository's own test suite repeatedly documents in comments that folding a later change into an earlier migration (for example 0001) 'would change [its] checksum and break brownfield startup (sqlx VersionMismatch)' -- so every schema change after the initial migration ships as a new, additive file rather than an edit to an existing one."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:718-721"
      - "crates/buzz-db/src/runtime/migration.rs:746-748"
  - statement: "No migration in this repository has a corresponding down/revert file, and no 'down' or reverse-migration command exists in the buzz-admin CLI or the Justfile; the mechanism is forward-only and additive by construction, consistent with the checksum-immutability convention above -- a schema change that must be undone is shipped as a further additive migration, not as a rollback of an earlier one."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-admin/src/main.rs:80"
      - "crates/buzz-admin/src/main.rs:151-154"
    confidence: 0.85
  - statement: "buzz-relay's own process startup only calls db.migrate() (which runs run_migrations) when the BUZZ_AUTO_MIGRATE environment variable parses as truthy (true/1/yes/on, case-insensitive, trimmed, via buzz_auto_migrate_enabled); any other value, or the variable being unset, is treated as disabled, and startup logs 'Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled' and proceeds without applying schema changes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:29-36"
      - "crates/buzz-relay/src/main.rs:201-210"
  - statement: "A unit test, buzz_auto_migrate_is_opt_in, directly asserts buzz_auto_migrate_enabled's parsing table: None, empty string, 'false', '0' and 'no' are all falsy, while 'true', 'TRUE', ' 1 ' (trimmed), 'yes' and 'on' are all truthy."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:2091-2102"
  - statement: "When BUZZ_AUTO_MIGRATE is enabled and the migration step returns an error, main() maps it into an anyhow::Error, logs 'Failed to run database migrations: {e}', and returns that Err from async fn main() -> anyhow::Result<()> -- Rust's runtime prints the error and exits the process with a non-zero status before the primary listener binds, identical in shape to every other fail-fast startup check named in this repository's own startup-sequence node; no partial-listening state and no in-process cleanup of already-open resources occurs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:97"
      - "crates/buzz-relay/src/main.rs:201-210"
  - statement: "The root .env.example (local development) does not set BUZZ_AUTO_MIGRATE at all, so a plain `just relay` or `just dev` never runs migrations through the relay process itself; local development instead applies migrations through the explicit `just _ensure-migrations` recipe, which runs `cargo run -p buzz-admin -- migrate` before seeding the local community, and which `just relay`, `just relay-web`, `just admin`, `just admin-seed`, `just relay-release` and `just dev` all depend on; `just migrate` is a bare alias for the same recipe."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "Justfile:211-212"
      - "Justfile:787-788"
  - statement: "buzz-admin's CLI exposes a Migrate subcommand whose handler calls db.migrate().await? directly -- the same run_migrations path buzz-relay's own startup gate uses -- so `buzz-admin migrate` (invoked directly or through `just migrate`) is the manual, always-available way to apply pending migrations independent of BUZZ_AUTO_MIGRATE."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:80"
      - "crates/buzz-admin/src/main.rs:151-154"
  - statement: "deploy/compose/.env.example sets BUZZ_AUTO_MIGRATE=true for the production Compose bundle, while deploy/compose/compose.yml's relay service reads that variable as ${BUZZ_AUTO_MIGRATE:-false} -- defaulting closed if the operator's own .env omits it -- so the production Compose path only auto-migrates if the operator's .env explicitly carries the true value the example file ships."
    entry_class: FACT
    evidence:
      - "deploy/compose/.env.example:20"
      - "deploy/compose/compose.yml:21"
  - statement: "schema/schema.sql is a hand-maintained, from-scratch desired-state rendering of the same multi-tenant schema the incremental migrations build up to; its own header states it is 'the source of truth for fresh database setup' and names docs/multi-tenant-conformance.md as its governing contract, and it is applied not by sqlx but by the third-party pgschema tool (bin/pgschema, Hermit-pinned) via `./bin/pgschema apply --file schema/schema.sql --auto-approve`."
    entry_class: FACT
    evidence:
      - "schema/schema.sql:1-13"
      - "docs/multi-tenant-conformance.md:1"
  - statement: "The schema.sql + pgschema path is used only by CI's desktop-E2E jobs and by three local test-relay launcher scripts (scripts/start-relay-for-tests.sh, scripts/start-isolated-test-relay.sh, scripts/run-desktop-release-smoke.sh) to bootstrap a downloaded or freshly built relay binary's database before the relay process itself starts -- CI's own comment explains this is necessary because the relay migrates at boot via BUZZ_AUTO_MIGRATE, which runs too late for a pre-boot database seed (the deployment community row) that other boot-time services require to already exist; it is not used by `just relay`, `just dev`, or any production deployment path this repository defines."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:502-504"
      - "scripts/start-relay-for-tests.sh:106"
  - statement: "pgschema reconciles DDL only: it does not execute the seed DML or preserve every table storage parameter schema.sql declares, and it currently emits partition children as standalone CREATE TABLE statements rather than attached partitions. scripts/reconcile-schema-after-pgschema.sql is the idempotent script that closes those specific gaps -- attaching each standalone events/delivery_log partition child (dropping any trigger or identity column pgschema copied onto it first, since PostgreSQL rejects an ATTACH that collides with those), restoring replica_heartbeat's vacuum_truncate=false storage parameter, and re-seeding replica_heartbeat's singleton row -- and every block ends with a live catalog or data assertion (RAISE EXCEPTION) that fails the bootstrap rather than silently leaving the gap unconverged."
    entry_class: FACT
    evidence:
      - "scripts/reconcile-schema-after-pgschema.sql:1-7"
      - "scripts/reconcile-schema-after-pgschema.sql:200-227"
  - statement: "A repository test, every_pgschema_apply_runs_post_apply_reconciliation, scans every file under scripts/ and .github/workflows/ for the literal string './bin/pgschema apply' and asserts that one of the next six lines after each occurrence invokes scripts/reconcile-schema-after-pgschema.sql, and further asserts at least one such occurrence exists -- so a new pgschema-apply call site that omits the reconciliation step fails this test rather than merely being a documentation gap."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:1238"
  - statement: "Two further repository tests independently check that schema.sql has not drifted from the incremental migrations for specific surfaces: admin_schema_parity_between_desired_state_and_migrations bootstraps one database through the real pgschema binary and another through migrations 1-39, then asserts identical column definitions and structurally identical index shapes (including per-key NULLS FIRST/LAST catalog options pgschema is documented as discarding when it re-emits an index) for the relay_admin_actions, relay_admin_outbox and relay_operator_audit tables; deletion_surface_parity_between_migration_0029_and_schema_sql performs the analogous structural comparison for every table, function, trigger, index and operator-global registry row migration 0029 introduces for community deletion."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:2083"
      - "crates/buzz-db/src/runtime/migration.rs:1605"
  - statement: "Both parity tests are scoped to specific surfaces (the three admin tables; the deletion-control-plane surface) rather than to the whole schema, and both are marked #[ignore = \"requires Postgres\"] or otherwise require a live database, so neither runs in a plain `cargo test`; whether every other table and index in schema.sql currently matches its migration-built equivalent is not established by any test this task found, only by the two named surfaces."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:2083"
      - "crates/buzz-db/src/runtime/migration.rs:1605"
    confidence: 0.8
  - statement: "This repository's own 2026-08-18 ecosystem audit independently recorded schema.sql/migration parity as a coverage gap ('only migrations 20/25/27/28 have an equivalence assertion; 1-24 have none... no confirmed drift found, only a coverage gap in the check that would catch one'), naming it as needing scoping by the buzz-db owner; this node's own reading of migration.rs at the later recorded revision above found two parity tests (admin tables and the 0029 deletion surface) rather than the four specific migration numbers the audit names, so the exact scope of coverage has moved since the audit and the audit's specific migration-number claim should not be read as still current."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md:221"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference-description paragraph, a structured-entries table (one row per fact, ordered per the subject's own order rather than alphabetically), an optional Commands table, an explicit boundary paragraph, a Relationships section, and Scope and omissions naming both what is out of scope and what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: layers-lifecycle-startup
---

# Database migrations: reference

This node catalogues the schema migration mechanism as an operator or
developer touching it needs to look it up: what `migrations/` is and how it
is applied, the naming and checksum-immutability conventions that govern
adding to it, the `BUZZ_AUTO_MIGRATE` startup gate and the manual
`buzz-admin migrate` alternative, the separate desired-state
`schema/schema.sql` + `pgschema` bootstrap path used by CI and test-relay
launchers, `scripts/reconcile-schema-after-pgschema.sql` and the gaps it
exists to close, and what currently happens — and does not happen — when a
migration fails. It is linked from `architecture-containers-postgres` (the
Postgres container this mechanism operates inside) and
`layers-lifecycle-startup` (the relay boot sequence this mechanism is one
step of); this node goes one level deeper than either on the migration
mechanism specifically, without restating their broader material.

## Migration mechanism reference

| Field | Description | Example |
|---|---|---|
| Source directory | `migrations/` at the repository root; every `.sql` file in it is embedded into the relay binary at compile time. | `migrations/0021_created_at_fence_floor.sql` |
| Runner | `sqlx::migrate!` (embedded `MIGRATOR`), invoked once in production through `run_migrations`. | `crates/buzz-db/src/runtime/migration.rs` |
| Concurrency safety | Exclusive Postgres advisory session lock (`SCHEMA_DESTRUCTION_LOCK_KEY`), serialized against destructive-deletion transactions; enforced as the only call site by a source lint. | `pg_advisory_lock($1)` / `pg_advisory_unlock($1)` |
| Startup trigger gate | `BUZZ_AUTO_MIGRATE` env var, parsed by `buzz_auto_migrate_enabled` (`true`/`1`/`yes`/`on`, case-insensitive, trimmed; anything else, including unset, is off). | unset locally; `true` in `deploy/compose/.env.example` |
| Manual invocation | `buzz-admin migrate` (direct `db.migrate()` call, independent of the startup gate). | `just migrate`, `cargo run -p buzz-admin -- migrate` |
| Pre-flight guard | `reject_legacy_nip_rs_cardinality_ambiguity` blocks the whole batch, before any DDL runs, if a populated pre-0007 database holds ambiguous NIP-RS rows. | fails closed; no version recorded, no row mutated |
| Post-migration verification | Replica-fence floor-guard trigger catalog and channel-roster snapshot fence are re-checked on every successful run, on every partition. | fails the call if either is missing anywhere |
| Naming / ordering convention | Four-digit zero-padded sequence number + `_snake_case_description.sql`; sqlx orders and records applied state by that integer. | `0001_initial_schema.sql` … `0040_push_message_kinds.sql` |
| Checksum-immutability convention | Once shipped, a migration's SQL is never edited — a later change is a new additive file, because editing an applied file's content changes its checksum and breaks brownfield startup (`sqlx` `VersionMismatch`). | 0001's schema is repeatedly extended by later migrations, never itself edited |
| Rollback / down migrations | None exist. The mechanism is forward-only; undoing a change ships as a further additive migration. | no `*.down.sql` files anywhere in `migrations/` |
| Failure recovery | Retry the same entry point (`run_migrations` / `buzz-admin migrate`) after fixing the condition that blocked it — not a separate resume or rollback command. | demonstrated by `pre_0007_ambiguous_nip_rs_data_blocks_without_mutation_and_allows_retry` |
| Desired-state alternative | `schema/schema.sql`, applied by the third-party `pgschema` binary, not `sqlx` — a from-scratch bootstrap, not an in-place migration. | `./bin/pgschema apply --file schema/schema.sql --auto-approve` |
| Desired-state gap-filling | `scripts/reconcile-schema-after-pgschema.sql` — mandatory after every `pgschema apply`, enforced by a repository test that scans for the pairing. | partition re-attachment, `replica_heartbeat` storage parameter + seed row |
| Desired-state/migration parity checks | Two targeted structural-parity tests exist (admin tables; the 0029 deletion surface) — not a whole-schema check. | `admin_schema_parity_between_desired_state_and_migrations` |

## Commands

| Command | Description | Argument | Example |
|---|---|---|---|
| `buzz-admin migrate` | Runs `db.migrate()` directly; the manual path independent of `BUZZ_AUTO_MIGRATE`. | none | `cargo run -p buzz-admin -- migrate` |
| `just migrate` | Alias for the `_ensure-migrations` recipe (which itself calls `buzz-admin migrate` then seeds the local dev community). | none | `just migrate` |
| `just _ensure-migrations` | Dependency of `just relay`, `just relay-web`, `just admin`, `just admin-seed`, `just relay-release`, `just dev`. | none | `just relay` (implicitly runs this first) |
| `./bin/pgschema apply` | Applies the desired-state `schema/schema.sql` against a target database — the CI/test-relay bootstrap path, not the production migration path. | `--file schema/schema.sql --auto-approve` plus connection flags | `.github/workflows/ci.yml` (desktop E2E jobs) |
| `psql ... < scripts/reconcile-schema-after-pgschema.sql` | Mandatory immediately after every `pgschema apply` call. | `-v ON_ERROR_STOP=1` | `scripts/start-relay-for-tests.sh` |

## Boundary

This node does not describe:
- **Why the multi-tenant schema is shaped the way it is**, or the row-zero
  community-binding invariant `schema/schema.sql` and every migration since
  0001 implement — that conceptual/explanation material belongs to
  `docs/multi-tenant-conformance.md` and any future concept-shaped corpus
  node built from it, not re-narrated here.
- **How to diagnose or recover from a migration failure at startup as an
  operational procedure** — what to check first, how to identify a stuck
  advisory lock, when to intervene manually versus wait. That is a
  step-ordered how-to/runbook, explicitly out of scope for this reference
  node and claimed by sibling task **#1222**; this node states only the
  mechanism-level facts (fail-fast, no partial listening state, retry by
  fixing the blocking condition and re-invoking the same entry point) that a
  runbook would build on.
- **A full API-reference-depth catalogue of every migration's own SQL
  contents** — the table above catalogues the mechanism, not each of the 40
  files' individual schema changes; a reader wanting that detail should open
  `migrations/` directly.
- **The Postgres container's connection pooling, sizing, or its role among
  buzz-relay's other Postgres pools (audit, search)** — covered by
  `architecture-containers-postgres` (see *Relationships*).
- **The rest of buzz-relay's startup sequence** (config load, Redis, NIP-43
  membership bootstrap, background task spawn order) — covered by
  `layers-lifecycle-startup` (see *Relationships*); this node only expands
  the one step in that sequence gated by `BUZZ_AUTO_MIGRATE`.

## Relationships

- `references`: `architecture-containers-postgres` — the Postgres container
  this migration mechanism operates inside; supporting context, no ownership
  or currency dependency implied.
- `references`: `layers-lifecycle-startup` — the relay boot sequence whose
  migration step this node expands in more operational detail.

No other node on `origin/launchpad` at the checked revision was found to be a
valid `relationships` target: no `operations/**` sibling exists there yet
(checked against `<SCRATCH>/existing-node-ids.txt`, 204 ids, none prefixed
`operations-`), so this is the first node on that surface and there is no
`part-of` parent to declare.

## Scope and omissions

**This node covers** the embedded-`sqlx` migration mechanism in
`migrations/`, its naming and checksum-immutability conventions, the
`BUZZ_AUTO_MIGRATE` startup gate and its environment-specific defaults, the
manual `buzz-admin migrate` / `just migrate` path, what is currently known
about failure behavior at startup (fail-fast, no partial listening state,
retry-after-repair for the one documented pre-flight guard), the absence of
a rollback/down-migration mechanism, and the separate desired-state
`schema/schema.sql` + `pgschema` bootstrap path together with
`scripts/reconcile-schema-after-pgschema.sql`'s documented gap-filling role
and the tests that check it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The multi-tenant schema design rationale and conformance rules | `docs/multi-tenant-conformance.md`; no corpus concept node yet |
| The failure-recovery runbook (diagnosing and acting on a failed migration) | `#1222` |
| The Postgres container's pooling/sizing and its other consumers | `architecture-containers-postgres` |
| The rest of buzz-relay's startup sequence | `layers-lifecycle-startup` |
| Per-migration SQL content (all 40 files individually) | `migrations/` directly |
| Staging/production `BUZZ_AUTO_MIGRATE` configuration in the private deploy pipelines | `squareup/block-coder-tf-stacks`, `squareup/sprout-oss` (separate private repositories, not opened by this task) |

**Expected but not verified when this node was written:**

- **Whether a genuine mid-batch SQL failure inside one of the 40 migration
  files — as distinct from the explicit `reject_legacy_nip_rs_cardinality_ambiguity`
  pre-check, which is demonstrated by test to fail closed without mutating
  anything — leaves the target database with partial DDL applied.** This
  depends on `sqlx::migrate!`'s own per-migration transaction handling, and
  this task did not open the `sqlx` crate's own source to verify it one way
  or the other; the mechanism-level facts stated above (advisory lock,
  post-migration catalog re-verification, fail-fast process exit) are
  independently true regardless of the answer, but this node does not assert
  whether such a failure is atomic per-migration.
- **Whether every table and index in `schema/schema.sql` currently matches
  its migration-built equivalent beyond the two tested surfaces** (the three
  admin tables, and the 0029 deletion-control-plane surface) was not
  established here; no whole-schema parity test was found.
- **Whether the staging/production deploy pipelines this repository's own
  contributor guide names** (`squareup/block-coder-tf-stacks`,
  `squareup/sprout-oss`) **set `BUZZ_AUTO_MIGRATE`** could not be checked —
  those are separate private repositories this task did not open, the same
  gap `architecture-containers-postgres` already discloses.
