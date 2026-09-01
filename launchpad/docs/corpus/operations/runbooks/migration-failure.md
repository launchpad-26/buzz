---
id: operations-runbooks-migration-failure
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
  - statement: "buzz-db's migration module doc comment describes migrations as the checked-in additive SQL files under migrations/; buzz-admin's Command enum (AddMember, RemoveMember, ListMembers, GenerateKey, Migrate, ProductFeedback, Deletions, ReconcileChannels) defines no rollback, revert, or down-migration variant anywhere; and the Justfile contains zero occurrences of the words rollback or revert -- so this repository ships no down-migration mechanism and no CLI or task-runner command that reverts an applied schema migration."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:1-6"
      - "crates/buzz-admin/src/main.rs"
      - "Justfile"
  - statement: "buzz_auto_migrate_enabled parses the BUZZ_AUTO_MIGRATE environment variable by trimming it and lowercasing it, returning true only for true/1/yes/on; an absent variable or any other value, including an empty string, returns false."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:29-36"
  - statement: "buzz-relay's main() calls db.migrate() only when buzz_auto_migrate_enabled returns true; on Err it logs \"Failed to run database migrations: {e}\" and returns an Err wrapping \"Database migration failed: {e}\", which ends the process before any router or listener is built, before ensure_future_partitions, before the deletion-serving-fence validation, and before the replica-fence probe; on success it logs \"Database migrations complete\"; when disabled it logs \"Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled\" and proceeds without applying anything."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:201-211"
  - statement: "Db::migrate() is a one-line delegation to buzz_db::runtime::migration::run_migrations(&self.pool); it adds no behavior of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs:859-861"
  - statement: "run_migrations acquires a detached connection, takes the exclusive SCHEMA_DESTRUCTION_LOCK_KEY session advisory lock on it via SELECT pg_advisory_lock($1), runs the migration body on that same connection, and -- on both the success and the error path -- issues SELECT pg_advisory_unlock($1) and closes the connection before propagating the outcome."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:77-104"
  - statement: "with_exclusive_schema_destruction_lock's own doc comment states that PostgreSQL releases a session advisory lock only when its owning backend finishes, and that this -- not the explicit unlock call -- is the safety contract: cancelling this future (dropping the connection while a migration statement is still executing server-side) cannot expose the lock to a shared destructive holder before that statement's own backend terminates."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:65-76"
  - statement: "run_migrations calls pg_advisory_lock, PostgreSQL's blocking form, rather than pg_try_advisory_lock; a second concurrent caller requesting the same key is therefore expected to block until the first releases it rather than fail immediately, consistent with the Helm chart's own documentation that multiple replicas are race-safe behind this advisory lock during a rolling deploy."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:85-94"
      - "deploy/charts/buzz/README.md:221"
    confidence: 0.8
  - statement: "SCHEMA_DESTRUCTION_LOCK_KEY is a single fixed, deployment-global advisory-lock key (decimal value of the literal ASCII \"buzzdel1\"); its own doc comment states run_migrations holds the exclusive session form for its entire run while destructive whole-community-deletion catalog validation, purge, and final logical verification hold the shared transaction-scoped counterpart, so schema migration and destructive community deletion are mutually exclusive by construction."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs:31-41"
  - statement: "Inside the lock, run_migrations_locked runs, in order: reject_legacy_nip_rs_cardinality_ambiguity, then MIGRATOR.run, then replica_fence::verify_floor_guard_catalog, then channel::verify_channel_roster_fence_catalog; any of the four steps returning Err fails the whole call, and the two post-migration verification steps re-check the schema even when MIGRATOR.run applied nothing."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:50-63"
  - statement: "reject_legacy_nip_rs_cardinality_ambiguity is a no-op when the _sqlx_migrations table does not yet exist (a fresh database) or when the highest version recorded with success=true is already 7 or above; otherwise it queries the events table for kind:30078 rows whose tags do not conform to the exact single-d/single-t shape the check expects, and, if any exist, returns DbError::InvalidData(\"NIP-RS migration blocked: pre-0007 database contains kind-30078 rows with ambiguous d/t tag cardinality; repair or remove those nonconforming rows before retrying\") before sqlx's own migrator runs anything."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:106-174"
  - statement: "This guard's own doc comment states migration 0007 is checksum-frozen and predates exact NIP-RS tag-cardinality enforcement, and that a populated database still on migrations 0001-0006 must not be allowed to let 0007 irreversibly purge duplicate-tag history -- the check exists specifically to fail before sqlx starts its migration transaction, so an operator can inspect and repair the offending rows rather than have them silently deleted."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:106-109"
  - statement: "An ignored, Postgres-backed test (pre_0007_ambiguous_nip_rs_data_blocks_without_mutation_and_allows_retry) seeds one ambiguous kind:30078 row on a database migrated only through version 6, asserts that run_migrations against it returns Err, that the set of applied migration versions is unchanged by the attempt, and that the ambiguous row's tags and content columns are byte-for-byte identical before and after the blocked call; it then repairs the row's tags and asserts run_migrations succeeds on retry and reaches the migrator's latest embedded version."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:2238-2314"
  - statement: "MIGRATOR is the static sqlx::migrate!(\"../../migrations\") migrator, embedding every file under this repository's top-level migrations/ directory into the relay binary at compile time."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:15"
  - statement: "Migration 0027's own comment states plainly that sqlx runs each migration inside a transaction and that CREATE INDEX CONCURRENTLY cannot run inside one, and that 0027 is therefore built without CONCURRENTLY -- matching migration 0004's identical precedent for the same reason -- taking a SHARE lock on the target table (blocking writes, not reads) for the build's duration instead, with a hand-written CONCURRENTLY alternative offered in a comment for an operator who wants to pre-build the index by hand on a large brownfield table."
    entry_class: FACT
    evidence:
      - "migrations/0027_channels_id_lookup_index.sql:41-51"
      - "migrations/0004_events_tags_gin.sql:13-17"
  - statement: "Migration 0033's own comment states its DROP COLUMN plus regenerate-GENERATED-column rewrite of the events table's search_tsv column runs \"under an ACCESS EXCLUSIVE lock inside the migration transaction ... with no lock_timeout,\" rewrites the entire events heap, and rebuilds the GIN index on it, and explicitly warns that an operator with a large brownfield database should schedule a maintenance window because \"expect relay downtime proportional to the size of events.\""
    entry_class: FACT
    evidence:
      - "migrations/0033_private_managed_agent_fts.sql:9-22"
  - statement: "This repository's own migration test-suite comments state, in two separate places, that folding an additive migration's schema change into migration 0001 would change 0001's checksum and break brownfield startup with what the comments name a sqlx VersionMismatch, and that migrations 0007 and 0008's sqlx checksums are immutable once a running relay has recorded them as applied -- naming an edit to the content of an already-shipped, checked-in migration file as the specific authoring mistake that produces a checksum-mismatch failure on any database that already recorded that migration."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:718-721"
      - "crates/buzz-db/src/runtime/migration.rs:822-823"
  - statement: "A source-scanning test, migration_execution_cannot_bypass_schema_destruction_lock, walks every .rs file in the Cargo workspace (with one named, documented exception for buzz-push-gateway's own separate migrator, which never holds community-scoped data) and asserts that no file other than migration.rs itself contains sqlx::migrate!, MIGRATOR.run(, or MIGRATOR.run_to(, and further asserts that migration.rs's own single production run site sits textually inside run_migrations_locked and that the only public entry point wraps it in with_exclusive_schema_destruction_lock."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:1474-1585"
  - statement: "buzz-push-gateway is a separate crate with its own migrations/ directory (four files, 0001-0004) and, per the test cited above, its own migrator outside buzz-db's schema-destruction-lock contract, because it never holds relay tenant tables; this runbook does not cover it."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
      - "crates/buzz-db/src/runtime/migration.rs:1502-1519"
  - statement: "In Docker Compose, the relay service's restart policy is unless-stopped and its healthcheck polls /_readiness; the readiness handler checks the shutdown flag and then, in parallel with a 2-second timeout, Postgres connectivity (db.ping()), a Redis pool checkout, and validate_deletion_serving_catalog() -- three connectivity/catalog checks, none of which reads _sqlx_migrations or otherwise confirms which migration version is applied."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml:36-47"
      - "crates/buzz-relay/src/router.rs:409-447"
  - statement: "buzz-admin's Migrate command connects to the database with the same buzz_db::Db path buzz-relay uses and calls db.migrate(), the identical run_migrations entry point buzz-relay's startup calls; it is the operator's manual, out-of-band way to apply pending migrations without starting the relay."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:151-156"
  - statement: "The Docker Compose bundle's admin wrapper commands (add-member, remove-member, list-members) all invoke docker compose exec relay /usr/local/bin/buzz-admin <subcommand>, establishing that /usr/local/bin/buzz-admin is the binary's path inside the running relay container; run.sh defines no dedicated migrate wrapper, so an operator runs buzz-admin migrate the same way, substituting the subcommand."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh:90-96"
  - statement: "deploy/compose/run.sh's backup_hint function lists what to back up before an upgrade and on a regular schedule: deploy/compose/.env (BUZZ_RELAY_PRIVATE_KEY, DB/Redis/S3 secrets, BUZZ_GIT_HOOK_HMAC_SECRET), the owner private key if bootstrap generated one, Postgres data (pg_dump or a quiesced volume snapshot), MinIO/S3 bucket contents, the buzz-git-data volume, and Caddy data/config volumes if used, and states plainly to keep the Postgres and object/git snapshots from the same maintenance window."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh:38-50"
  - statement: "deploy/compose/README.md states that an image-only rollback (reverting BUZZ_IMAGE and re-running check/upgrade) is safe only when the intervening database migrations are backward-compatible, and that otherwise the operator must restore the matching pre-upgrade database and object/git snapshots as a coordinated recovery."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md:91-98"
  - statement: "The Helm chart's README lists five things an operator must back up -- BUZZ_RELAY_PRIVATE_KEY, the PostgreSQL database, the S3 media bucket, the git PVC, and the owner private key held outside the chart -- and states that Migration 0032 is a hard compatibility boundary: the relay verifies the channel-roster fence trigger catalog and behavior before opening listeners and refuses to start if migration 0032 is missing or inert, and recommends a controlled buzz-admin migrate job with PostgreSQL lock monitoring before the code rollout on large installations."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md:223-235"
  - statement: "The Helm chart's README states that when migrate.autoMigrate is set false, the chart does not run migrations at all, the operator owns running buzz-admin migrate as a separate Pod or one-shot Job before every install/upgrade, and readiness probes verify DB connectivity only, not schema freshness, so a pod can appear healthy against an unmigrated schema and fail under load; a pre-upgrade Helm Job for this is on the chart's roadmap but not yet implemented (the migrate.preUpgradeJob.enabled values knob is reserved)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md:225"
  - statement: "architecture-containers-postgres (merged on origin/launchpad) already documents that migrations are opt-in at startup rather than automatic, that BUZZ_AUTO_MIGRATE defaults off, and that this repository's own top-level contributor guide describes migrations/ as \"auto-applied on relay startup\" without mentioning that gate; this runbook does not restate that container-level context and links it instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "layers-lifecycle-startup (merged on origin/launchpad) already documents buzz-relay's full startup sequence and names \"Migration failure (only reachable when BUZZ_AUTO_MIGRATE=true) -- exits with the migration error\" as one of its enumerated fail-fast exit paths, stating that none of the fail-fast paths perform partial cleanup of already-opened resources and that the process simply exits; this runbook does not re-narrate the full startup sequence and links it instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/lifecycle/startup.md"
  - statement: "After a successful migration run, main() spawns the replica-fence probe and, if verification of the floor-guard trigger catalog and behavior fails, logs \"Replica fence disabled -- floor guard verification failed: {e}. All cursor reads stay on the writer\" as a non-fatal error rather than exiting; this is the same floor-guard catalog run_migrations_locked itself re-verifies under the advisory lock on every successful migration run."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:232-241"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook's body to carry a trigger, severity and impact, diagnosis, mitigation and resolution, escalation, and a scope-and-omissions section, each traceable to the Google SRE Workbook's playbook definition."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: layers-lifecycle-startup
---

# Runbook: database migration failure

## Trigger

The relay process (`buzz-relay`) fails to reach a serving state because
applying its embedded database migrations failed during startup. This path is
reachable only when `BUZZ_AUTO_MIGRATE` parses as truthy (`true`/`1`/`yes`/`on`,
case-insensitive and trimmed) — an absent variable, an empty string, or any
other value skips the migration step entirely and this runbook does not apply.

Recognize it from:

- **Process logs.** The line `Failed to run database migrations: {e}` followed
  by the process exiting, where `{e}` is the underlying error (a `DbError`,
  most often wrapping a `sqlx::migrate::MigrateError` or the pre-0007 guard's
  own `DbError::InvalidData`). This is distinct from `Database migrations
  complete` (success) and from `Skipping database migrations because
  BUZZ_AUTO_MIGRATE is not enabled` (auto-migrate disabled — not this runbook).
- **Container/pod restart behavior.** In Docker Compose (`restart:
  unless-stopped`) the relay container exits and restarts, repeating the same
  failure on each attempt. In Kubernetes, a Deployment whose container process
  exits non-zero on every start produces the same restart-loop symptom the
  platform reports on the pod.
- **The `/_readiness` health check never turns healthy**, because the process
  exits before the router — and therefore the readiness handler — is ever
  built. This differs from a relay that *starts* successfully against a stale
  schema (`BUZZ_AUTO_MIGRATE=false` or `migrate.autoMigrate=false`): in that
  case the process runs and readiness reports healthy, because the readiness
  handler checks only Postgres/Redis connectivity, never schema freshness —
  that is a schema-drift condition, not a migration failure, and this runbook
  does not cover it.
- **A rolling deploy where several replicas appear to hang at startup.**
  `run_migrations` takes Postgres's blocking `pg_advisory_lock`, not the
  non-blocking `pg_try_advisory_lock`, on a single fixed key
  (`SCHEMA_DESTRUCTION_LOCK_KEY`); a second replica calling `db.migrate()`
  concurrently is expected to block behind the first rather than fail or race
  it. Seeing multiple pods still starting during a migrating rollout is
  therefore not on its own evidence of a stuck migration — see *Diagnosis*
  below for how to tell the two apart.

## Severity and impact

**Every replica that reaches this migration call fails to start.** Migration
failure in `main()` returns an `Err` before the router, the health listener,
partition maintenance, the deletion-serving-fence validation, or the
replica-fence probe are built — there is no partial-listening state. A fresh
deployment or a rolling upgrade that hits this is a **total outage for every
replica currently starting**, not a degraded-but-serving condition. An
already-running previous-version replica that is not restarting is unaffected
until it, too, is rolled.

Because the exclusive advisory lock is shared with destructive
whole-community-deletion transactions (the shared, transaction-scoped
counterpart of the same `SCHEMA_DESTRUCTION_LOCK_KEY`), a migration attempt
that is genuinely stuck holding this lock also blocks any in-flight community
deletion from validating or acting on its catalog for as long as the lock is
held.

### Prerequisites

- Network access to the Postgres instance the relay is configured against
  (`DATABASE_URL`), with a role that can run DDL and query
  `pg_stat_activity`/`pg_locks`/`_sqlx_migrations`.
- For Docker Compose: shell access to the host and `docker compose` (or the
  wrapper, `./launchpad/deploy/run.sh`); `docker compose exec relay
  /usr/local/bin/buzz-admin migrate` is how `buzz-admin` is invoked inside the
  running container — `run.sh` defines no dedicated `migrate` subcommand of
  its own.
- For Kubernetes: `kubectl` access to the namespace, and — if
  `migrate.autoMigrate=false` — the ability to run a `buzz-admin migrate`
  Pod/Job against the same database.
- Knowing whether this deployment runs with `BUZZ_AUTO_MIGRATE=true` (Compose
  default `false`; Helm chart default `true`) — the failure mode this runbook
  describes is only reachable when it does.
- A recent backup per *Evidence to preserve*, below, taken **before** any
  mitigation step that writes to the database.

## Diagnosis

1. **Read the log line.** `Failed to run database migrations: {e}` names the
   underlying error. Three shapes recur; skip ahead to the matching
   subsection under *Mitigation and resolution*:
   - Contains `NIP-RS migration blocked: pre-0007 database contains kind-30078
     rows with ambiguous d/t tag cardinality` — the pre-0007 data guard fired.
     Nothing was mutated; see *Ambiguous pre-0007 data*, below.
   - Mentions a checksum, version, or `MigrateError` — likely a version
     mismatch between the deployed binary's embedded migrations and what
     `_sqlx_migrations` already recorded as applied. See *Checksum or version
     mismatch*, below.
   - A plain SQL error (permission denied, disk full, connection reset,
     statement timeout) during a specific migration's DDL. See *A migration
     statement itself failed*, below.
   - No log line reaches this point at all, and the process appears to hang
     — go to *Distinguishing a slow migration, a lock wait, and a dead
     holder*, below, before assuming failure.

2. **Inspect applied-migration state**, connected directly to Postgres:

   ```sql
   SELECT version, success FROM _sqlx_migrations ORDER BY version;
   ```

   `version` and `success` are the two columns this repository's own guard
   code reads; the table's remaining columns are created by the `sqlx` crate
   itself, not by anything in this repository's `migrations/` directory, and
   this runbook does not enumerate them. Compare the highest `version` here
   against the highest version number under `migrations/` in the deployed
   image to see how far behind (or ahead of) the codebase the database is.

3. **Distinguishing a slow migration, a lock wait, and a dead holder.** If the
   process has not logged success, failure, or the skip message, and appears
   to hang, it has not necessarily failed:

   - Some migrations in this repository are genuinely slow by design and hold
     locks the whole time. Migration 0033, for example, rewrites the entire
     `events` heap under an `ACCESS EXCLUSIVE` lock with **no
     `lock_timeout`**, and its own comment warns that downtime is proportional
     to table size. Migrations 0004 and 0027 build an index without
     `CONCURRENTLY` (sqlx runs each migration in a transaction, and
     `CREATE INDEX CONCURRENTLY` cannot run inside one), taking a blocking
     `SHARE` lock on the target table for the build's duration. Check
     `pg_stat_activity` for the migrating backend's `query` and `state` —
     an `active` state with a real DDL statement means it is making progress,
     not stuck.
   - To find who holds the migration advisory lock itself, join `pg_locks`
     (`locktype = 'advisory'`) against `pg_stat_activity` on `pid`. A holder
     backend that is `idle` with no query, rather than `active` on a DDL
     statement, may be an orphaned session from a killed migrator process
     rather than one still working.
   - `run_migrations` takes this lock with `pg_advisory_lock` on the *same
     backend connection* for the whole call, and its own code comment states
     that PostgreSQL releases a session advisory lock only when its owning
     backend finishes — so a lock that is genuinely stuck, with no
     corresponding live TCP session, should not persist once Postgres detects
     the dead connection. A holder that is visibly present in
     `pg_stat_activity` but idle for an implausible amount of time (well
     beyond any migration in `migrations/` running its slowest documented
     case) is the concrete signal of a truly orphaned session, not a live one
     still finishing.
   - During a rolling deploy, a second and third replica blocking behind the
     first on this same lock is expected, not a symptom — see *Trigger*,
     above.

## Mitigation and resolution

Try these in the order a responder would reasonably reach them; each names
whether it mutates anything.

1. **Ambiguous pre-0007 data (non-destructive, safe to inspect).** This guard
   runs *before* `sqlx`'s own migrator starts anything, so a block here has
   applied nothing and mutated nothing — confirmed by this repository's own
   test, which asserts the applied-migration set and the offending row's
   content are byte-for-byte unchanged after a blocked attempt. Query the
   `events` table for `kind = 30078` rows whose `tags` do not have exactly one
   `d` tag matching the row's own `d_tag` and exactly one `["t",
   "read-state"]` tag — that is the shape the guard checks. Repair or remove
   the nonconforming rows per your own data-correctness judgment (this
   runbook does not prescribe the repair SQL, since the correct fix depends on
   what produced the ambiguous tags), then restart the relay (or re-run
   `buzz-admin migrate`) to retry. A retry after repair is exactly what this
   repository's own test exercises and expects to succeed.

2. **Checksum or version mismatch (do not edit already-shipped migration
   files).** This repository's own migration comments treat every
   already-applied migration file's content as immutable once shipped —
   folding a schema change into an earlier file, or otherwise editing one
   after it has been recorded as applied anywhere, is the documented cause of
   this failure class. The fix is a deploy/version-skew correction, not a data
   repair: confirm the deployed binary's embedded `migrations/` directory
   matches — or is a strict superset of — what `_sqlx_migrations` already
   recorded, and deploy the correct image rather than altering migration file
   contents or database rows to force agreement.

3. **A migration statement itself failed (a plain SQL error).** Because
   `sqlx` runs each migration inside its own transaction in this repository (a
   fact this repository's own 0027 migration comment states directly, as the
   reason it avoids `CONCURRENTLY`), a migration that errors partway rolls
   back that migration's own transaction automatically — the schema is left
   at the last successfully-applied version, and `_sqlx_migrations` does not
   record the failed migration as applied. **No manual schema rollback is
   needed for this case.** Fix the underlying blocker named in the error
   (grant the missing permission, free disk space, restore connectivity,
   raise a timeout) and restart the relay, or re-run `buzz-admin migrate`
   directly — the unapplied migration is retried from where it left off, and
   every already-applied migration is skipped.

4. **Confirmed dead advisory-lock holder (targeted, service-impacting — use
   with caution).** Only after *Diagnosis* has established a specific backend
   `pid` holding the migration advisory lock while `idle` with no query for an
   implausible duration: `SELECT pg_terminate_backend(<pid>)`. This forcibly
   closes that connection and, because it is the lock-owning session, releases
   the advisory lock. This is **not** a data-destructive action, but it *is*
   disruptive to whatever else that backend was doing — confirm from
   `pg_stat_activity` that the backend is not mid-transaction on something
   else before terminating it. Terminating the wrong backend does not repair
   anything and creates a second incident.

5. **Manual out-of-band migration.** Independent of which of the above
   applies, `buzz-admin migrate` (Compose: `docker compose exec relay
   /usr/local/bin/buzz-admin migrate`; Kubernetes: a one-shot Pod/Job running
   the same binary) calls the identical `run_migrations` entry point the
   relay's own startup calls, under the same advisory lock. Running it
   separately from relay startup is the Helm chart's own recommended pattern
   for large installations, specifically so migration progress and Postgres
   lock state can be watched directly rather than inferred from relay
   restart-loop logs.

### Verify the recovery

Whichever step above applied, confirm all of the following before treating
the incident as closed — a relay that merely stopped crash-looping is not yet
confirmed to be on the schema version it should be:

1. **`SELECT version, success FROM _sqlx_migrations ORDER BY version;`**
   again. The highest `version` with `success = true` should now match the
   highest version number under `migrations/` in the deployed image, and no
   row should show `success = false`.
2. **Start (or restart) the relay** and confirm the log line
   `Database migrations complete` appears, not `Failed to run database
   migrations`. If `buzz-admin migrate` was run out-of-band with
   `BUZZ_AUTO_MIGRATE` left disabled, the relay's own startup will instead log
   the skip message — that is expected in that mode, not a sign the migration
   did not take effect.
3. **`/_readiness` reports `200` with `"status":"ready"`** — in Compose, watch
   `docker compose ps` for the container leaving its restart loop and the
   healthcheck reporting healthy; in Kubernetes, watch the pod leave
   `CrashLoopBackOff` and its readiness probe pass.
4. **No `Replica fence disabled` error is logged**, if a read replica is
   configured. `run_migrations_locked`'s own post-migration steps re-verify
   the replica-fence floor-guard and channel-roster fence catalogs on every
   successful run; a relay that migrated cleanly but still logs a fence
   refusal has a schema problem this runbook's steps did not fully resolve
   and warrants returning to *Diagnosis*.

## Escalation

### Evidence to preserve

Before touching anything that writes to the database (steps 2 and 4 under
*Mitigation and resolution*, and certainly before any restore), capture:

- The full text of the failing log line (`Failed to run database migrations:
  {e}`) and, if reachable, the container/pod's complete startup log for that
  attempt.
- The output of `SELECT version, success FROM _sqlx_migrations ORDER BY
  version;` (or `SELECT * FROM _sqlx_migrations ORDER BY version;` for
  whatever additional columns this deployment's `sqlx` version carries,
  uninspected by this runbook — see *Diagnosis*).
- If a lock investigation was needed: the `pg_locks`/`pg_stat_activity` join
  output identifying the holder, captured before any `pg_terminate_backend`
  call.
- For a suspected checksum/version mismatch: the deployed image's tag/digest
  and the exact set of files under its embedded `migrations/` directory.
- A fresh backup per the deployment's own checklist — Compose:
  `deploy/compose/run.sh`'s `backup_hint` (`.env` secrets, `pg_dump` or a
  quiesced Postgres volume snapshot, MinIO/S3 bucket contents, the
  `buzz-git-data` volume, Caddy volumes if used); Kubernetes: the Helm
  chart's own list (`BUZZ_RELAY_PRIVATE_KEY`, the PostgreSQL database, the S3
  media bucket, the git PVC, the owner private key held outside the chart).
  Both sources are explicit that the Postgres and object/git snapshots must
  come from the same maintenance window to be useful together.

**There is no down-migration path in this repository, at any level.** No
migration file under `migrations/` has a corresponding down/revert
counterpart, `buzz-admin`'s CLI defines no rollback or revert subcommand, and
the `Justfile` defines no down-migration recipe — confirmed by reading all
three surfaces directly, not assumed. If a migration has applied and its
effects are wrong, the only paths available are:

- **Roll forward.** Write and ship a new additive migration that corrects the
  problem, following this repository's own additive-only convention (already
  applied migrations are treated as checksum-immutable — see *Checksum or
  version mismatch*, above).
- **Restore from backup.** `deploy/compose/run.sh`'s documented backup
  checklist (`.env` secrets, Postgres data via `pg_dump` or a quiesced volume
  snapshot, MinIO/S3 bucket contents, the git data volume, Caddy volumes) and
  the Helm chart's equivalent (relay private key, the Postgres database, the
  S3 media bucket, the git PVC, the owner private key held outside the chart)
  are what a restore draws on. Both sources state explicitly that an
  image-only rollback is safe only when the intervening migrations were
  backward-compatible; otherwise the matching pre-upgrade database and
  object/git snapshots must be restored together, as one coordinated
  recovery, not the database alone.

**Escalate rather than improvise when:**

- The failing migration is at or above 0032 — the Helm chart's own README
  names migration 0032 as "a hard compatibility boundary for relay versions
  that publish repaired channel rosters," verified by the relay's own
  roster-fence trigger-catalog check before it opens listeners. A block here
  is a compatibility signal, not a transient error, and should not be forced
  past.
- Steps 1-4 under *Mitigation and resolution* do not resolve the failure
  within the time the on-call owner judges reasonable, or step 4's
  preconditions (confirmed dead holder) cannot be established with
  confidence.
- Any restore-from-backup path is being considered — coordinate the timing
  and scope of a Postgres + object/git snapshot restoration with whoever owns
  the deployment before acting, since it is destructive to data written since
  the snapshot.

## Scope and omissions

**This node covers** recognizing a database migration failure in
`buzz-relay`'s own startup path (the `buzz-db` migrator gated by
`BUZZ_AUTO_MIGRATE`); its severity and blast radius; prerequisites for an
operator responding to it; diagnosing which of the three known failure shapes
occurred, and distinguishing a slow-but-progressing migration or expected
multi-replica lock contention from a genuinely stuck or dead lock holder;
mitigation and resolution steps in the order a responder would reasonably try
them, each marked for whether it mutates data; and escalation, including the
confirmed absence of any down-migration mechanism and what a coordinated
restore actually requires.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full `buzz-relay` startup sequence beyond the migration decision | `layers-lifecycle-startup` |
| The Postgres container's ownership, connection pools, and general deployment/data implications | `architecture-containers-postgres` |
| A relay running successfully against a stale, un-migrated schema (`BUZZ_AUTO_MIGRATE=false` or `migrate.autoMigrate=false`) — a schema-drift condition, not a migration failure | Not a corpus node found at this revision; `architecture-deployment-kubernetes` and `architecture-deployment-multi-community` both name the readiness-probe gap this creates |
| `buzz-push-gateway`'s own, entirely separate migrator and `migrations/` directory — confirmed to exist and to be deliberately exempt from the schema-destruction lock because it never holds tenant-scoped data | No corpus node found at this revision |
| The exact repair SQL for an ambiguous pre-0007 row — deliberately not prescribed here, since the correct repair depends on how the ambiguous tags were produced, which this runbook cannot know in general | The operator's own data-correctness judgment, per *Mitigation and resolution* step 1 |
| A Kubernetes pre-upgrade migration Job running automatically | Not implemented — the Helm chart's own README names `migrate.preUpgradeJob.enabled` as a reserved-but-unimplemented values knob |
| Whether the staging/production deploy pipelines this repository's own contributor guide names (`squareup/block-coder-tf-stacks`, `squareup/sprout-oss`) set `BUZZ_AUTO_MIGRATE` or run a pre-migration step of their own | Separate private repositories `architecture-containers-postgres` already records as unopened by this corpus |

**Expected but not verified when this node was written:**

- **No real migration failure of any of the three diagnosed shapes was
  reproduced against a live Postgres instance while writing this node.** The
  pre-0007 guard's non-mutating, retry-safe behavior is established by reading
  this repository's own ignored integration test, not by running it (it
  requires Postgres and is marked `#[ignore]`); the transactional-rollback
  claim for an ordinary failed migration statement is established from this
  repository's own migration-comment evidence about `sqlx`'s per-migration
  transaction behavior, not by forcing a migration to fail and inspecting the
  result directly.
- **The exact `pg_locks`/`pg_stat_activity` query text for identifying the
  advisory-lock holder was not run against a live database with a real
  contended lock** — the join described in *Diagnosis* is standard PostgreSQL
  practice for this class of problem, not a query this repository ships or
  this session executed.
- **Whether `pg_terminate_backend` on a confirmed-dead migration holder has
  ever actually been exercised against this repository's schema in practice**
  is unknown; step 4 of *Mitigation and resolution* is reasoned from the
  code's own session-lock semantics, not from an observed incident.
- **The Compose healthcheck's specific retry/timeout values
  (`interval`/`timeout`/`retries`/`start_period`) were read from
  `deploy/compose/compose.yml` but their consequence for how long an operator
  waits before Compose reports the relay unhealthy was not independently
  timed.**
