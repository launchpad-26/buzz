---
id: development-database-changes
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: architecture-containers-postgres
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The schema has two independent authored sources: the incremental forward migrations under migrations/, embedded into the relay binary by `static MIGRATOR: sqlx::migrate::Migrator = sqlx::migrate!(\"../../migrations\")`, and the desired-state file schema/schema.sql, which declares itself the \"Source of truth for fresh database setup\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "schema/schema.sql"
  - statement: "At the recorded revision migrations/ holds exactly 40 forward-only files, numbered 0001_initial_schema.sql through 0040_push_message_kinds.sql, and contains no down/reverse migration of any kind."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "migrations/0040_push_message_kinds.sql"
      - "ls(migrations/) -> 40 entries, 0001_initial_schema.sql .. 0040_push_message_kinds.sql, no *.down.sql and no file whose name contains 'down'"
  - statement: "The unit test `embedded_migrator_contains_consolidated_initial_schema` asserts `migrations.len()` equals 40 and then makes per-version content assertions on individual migrations, so adding a forty-first migration file fails that test until its count and assertions are updated in the same change."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "That same test states in its own comments that an additive change is \"never folded into 0001 -- folding would change 0001's checksum and break brownfield startup (sqlx VersionMismatch)\", and asserts both that the new object appears in its own version and that 0001 does not carry it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Three tenant-isolation lints run over the concatenated SQL of every embedded migration, not just 0001: every table absent from the `_operator_global_tables` allowlist must declare `community_id` NOT NULL; every primary key, unique constraint, foreign key and unique index on such a table must lead with community_id; and channels.community_id must be immutable, with the lint requiring both no re-tenanting UPDATE statement and the presence of a BEFORE UPDATE trigger guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "The operator-global set is an explicit allowlist read out of the migrations' own `INSERT INTO _operator_global_tables` statement; the lint helper recognises 22 names, from `communities` and `replica_heartbeat` through `relay_operators`, `relay_admin_actions`, `relay_admin_outbox` and `relay_operator_audit`, and treats every other created table as tenant-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "schema/schema.sql's own header states the four migration-lint obligations the Lane 0 lint harness enforces -- community_id NOT NULL on every tenant-scoped table, no cross-community-observable UNIQUE/PRIMARY KEY/FK on a scoped table, immutable channels.community_id, and an explicit rather than implied operator-global allowlist -- and names docs/multi-tenant-conformance.md as the governing contract."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
      - "docs/multi-tenant-conformance.md"
  - statement: "`run_migrations` is the sole public migration entry point and executes the whole run while holding the exclusive SCHEMA_DESTRUCTION_LOCK_KEY advisory session lock on one detached connection; the unit test `migration_execution_cannot_bypass_schema_destruction_lock` enforces by source scan that `sqlx::migrate!`, `MIGRATOR.run(` and `MIGRATOR.run_to(` have no other call site in the workspace."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "Before sqlx starts its migration transaction, `reject_legacy_nip_rs_cardinality_ambiguity` inspects a populated pre-0007 database for kind-30078 rows with ambiguous d/t tag cardinality and returns an error instructing the operator to repair or remove those rows, rather than letting migration 0007 purge them."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "After the migrator runs, the same locked code path re-verifies the migration-0021 commit-time created_at floor trigger on the events parent and every partition, and the channel-roster fence catalog, failing the migration closed if either is missing."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "`just migrate` depends on the private `_ensure-migrations` recipe, which runs `cargo run -p buzz-admin -- migrate` followed by ./scripts/seed-local-community.sh; buzz-admin's Migrate command calls `db.migrate()`, which is a thin wrapper over `migration::run_migrations`."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "The relay applies pending migrations at startup only when BUZZ_AUTO_MIGRATE parses as truthy; unset or any other value logs \"Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled\" and starts against whatever schema Postgres already has."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Fresh desired-state bootstraps do not run migrations at all: five call sites across four files run `./bin/pgschema apply --file schema/schema.sql --auto-approve` and then pipe scripts/reconcile-schema-after-pgschema.sql into psql -- two steps in .github/workflows/ci.yml, plus one each in scripts/start-isolated-test-relay.sh, scripts/start-relay-for-tests.sh and scripts/run-desktop-release-smoke.sh."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "scripts/start-isolated-test-relay.sh"
      - "scripts/start-relay-for-tests.sh"
      - "scripts/run-desktop-release-smoke.sh"
  - statement: "`every_pgschema_apply_runs_post_apply_reconciliation` walks every file under scripts/ and .github/workflows/, and for each line containing \"./bin/pgschema apply\" asserts that one of the next six lines names scripts/reconcile-schema-after-pgschema.sql, additionally asserting that at least one such caller exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "scripts/reconcile-schema-after-pgschema.sql states in its own header that pgschema \"reconciles DDL, but it does not execute seed DML or preserve every table storage parameter from schema/schema.sql\" and \"currently emits partition children as standalone CREATE TABLE statements\", and it converges all three: it attaches the eight events and six delivery_log partitions idempotently, sets `vacuum_truncate = false` on replica_heartbeat, inserts the singleton heartbeat row with ON CONFLICT DO NOTHING, and then raises an exception unless pg_class.reloptions contains vacuum_truncate=false and exactly one row with id = 1 exists."
    entry_class: FACT
    evidence:
      - "scripts/reconcile-schema-after-pgschema.sql"
  - statement: "The repository's own contributor guide states this constraint as a numbered gotcha -- pgschema omits seed DML and some storage parameters, unsupported invariants go in scripts/reconcile-schema-after-pgschema.sql as an idempotent convergence statement plus a live catalog or data assertion, every pgschema apply caller must run that script, and a string assertion against schema.sql alone does not prove the pgschema-created database has the intended state -- and each clause holds against the files at the recorded revision."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "scripts/reconcile-schema-after-pgschema.sql"
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "`admin_schema_parity_between_desired_state_and_migrations` bootstraps one probe database from schema/schema.sql through the real bin/pgschema binary and migrates a second through versions 1-38, then asserts three admin tables have identical column definitions keyed by name and identical index shapes including each key's pg_index.indoption; its doc comment states that when a migration mutates the admin tables schema.sql must be hand-updated to match, that \"nothing enforces that automatically\", and that the lease/claim-token migrations 0035/0036 once drifted for exactly this reason."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "That parity test carries `#[ignore = \"requires Postgres\"]`, and scripts/run-tests.sh states in its own comment that the Postgres-backed buzz-db tests are ignored and that \"nothing here (or in integration mode below, which runs `cargo test -p buzz-db` without --ignored) runs them -- they need a separate isolated-DB gate\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "scripts/run-tests.sh"
  - statement: "`deletion_surface_parity_between_migration_0029_and_schema_sql` is an infra-free test that compares parsed statements rather than substrings, requiring every deletion control-plane table, function, trigger and index migration 0029 creates to exist in schema.sql with an identical normalized definition, every operator-global registry row to be inserted by both, equal write-fence attachment target sets, and every column added to communities to be present in the desired-state table."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "The infra-free migrator and lint tests are what `just test-unit` and scripts/run-tests.sh's unit mode run, via `cargo nextest run -p buzz-db --lib` and `cargo test -p buzz-db --lib` respectively; the Justfile comment states this gate exists so that \"a stray file in migrations/ or a broken lint\" cannot ship green."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "scripts/run-tests.sh"
  - statement: "CI's Detect Changed Paths job defines a `rust` filter listing crates/**, migrations/**, schema/**, Cargo.toml, Cargo.lock, rust-toolchain.toml, deny.toml, .github/workflows/ci.yml, scripts/run-tests.sh, scripts/model-capabilities.json, scripts/normative-corpus.json and justfile; both the Unit Tests job and the Backend Integration (relay e2e) job are gated on `github.event_name == 'push' || needs.changes.outputs.rust == 'true'`, and the workflow's push trigger is restricted to branches main and release."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "scripts/reconcile-schema-after-pgschema.sql is not named by that rust filter and matches none of its patterns, so a pull request whose only changed file is the reconcile script runs neither Unit Tests nor Backend Integration, leaving the migrator and reconciliation guards unexecuted for that pull request."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - "scripts/reconcile-schema-after-pgschema.sql"
    confidence: 0.85
  - statement: "The desired-state/migration admin parity check therefore runs in no automated lane at the recorded revision: it is ignored by the two unit paths and the integration path per the comment above, and no nextest selector anywhere in .github/workflows/ci.yml names a buzz-db migration:: test."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "scripts/run-tests.sh"
      - "grep(pattern='migration', path='.github/workflows/ci.yml') -> five matches, all paths-filter or cache-key entries; no test selector naming a buzz-db migration:: test"
    confidence: 0.8
  - statement: "bin/pgschema is a Hermit-managed symlink resolving to the pinned pgschema 1.7.4 package marker, so the tooling this procedure invokes comes from the repository's pinned toolchain rather than from whatever is on the developer's PATH."
    entry_class: FACT
    evidence:
      - "bin/pgschema"
  - statement: "`just check` runs file-size-check among its other gates and `just ci` runs check followed by test-unit and the platform suites, so the repository-wide 1000-line file ceiling and the buzz-db lint gate are both reachable from one command before a pull request."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "Two already-merged corpus nodes own the runtime half of this subject -- architecture-containers-postgres records the migration runner, the BUZZ_AUTO_MIGRATE gate and schema authority, and layers-lifecycle-startup records the conditional migration decision as step 6 of relay boot -- so this node links to them rather than restating their content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
      - "launchpad/docs/corpus/layers/lifecycle/startup.md"
  - statement: "Issue #855 requires that this node state goal, prerequisites and allowed environment/scope, provide ordered executable project-specific steps, define success verification and rollback/cleanup where relevant, link authoritative commands and configuration instead of giving generic advice, and carry an explicit scope-and-omissions section."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#855 definition of done"
  - statement: "Issue #855 requires that a newly discovered second concept, contract or procedure be filed as its own task rather than folded into this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#855 definition of done"
---

# Change the Buzz database schema

How to add or alter a Postgres table, column, index, trigger or seed row in this
repository, so that the change lands in **both** authored schema sources, satisfies
the tenant-isolation lints, and survives the fresh-bootstrap path as well as the
migration path. Perform this whenever a change touches `migrations/`,
`schema/schema.sql` or `scripts/reconcile-schema-after-pgschema.sql`.

The single fact that shapes every step below: **this repository has two
independent authored descriptions of the same schema.** `migrations/` is the
incremental history the relay embeds and replays; `schema/schema.sql` is the
desired-state file `pgschema` applies to a fresh database without replaying
anything. Nothing regenerates one from the other. A change made to only one of
them produces a database whose shape depends on how it was created.

## Before you start

- **Activate the pinned toolchain** — `. ./bin/activate-hermit`. `bin/pgschema`
  is a Hermit symlink to the pinned pgschema 1.7.4 package; without activation a
  differently versioned binary on `PATH` wins.
- **Have Postgres and Redis running** if you intend to verify against a live
  database. `just migrate` starts services and applies migrations; see
  `launchpad/docs/corpus/development/prerequisites.md` for what must be installed
  first.
- **Know which surface you are changing.** Adding or altering a schema object is
  step 2a below. Fixing something `pgschema` cannot reproduce — seed data, a
  storage parameter, a partition attachment — is step 2b, and does *not* get a
  migration.
- **Out of scope for this procedure:** anything that changes runtime behaviour
  rather than schema shape, and any change to how migrations are *applied* at
  deploy time. Those are owned elsewhere — see *Boundary* below.

## Change the schema

1. **Decide whether the change is additive.** Never edit an already-numbered
   migration. `crates/buzz-db/src/runtime/migration.rs`'s own test comments state
   the rule and the reason: folding a change into `0001` "would change 0001's
   checksum and break brownfield startup (sqlx VersionMismatch)". The test asserts
   both halves — that each additive object appears in its own version, and that
   `0001` does not carry it.

2a. **Add a forward migration** (schema-object changes).

   1. Create `migrations/00NN_<snake_case_description>.sql`, taking the next
      unused number. At the recorded revision the tip is
      `migrations/0040_push_message_kinds.sql`, so the next file is `0041_…`.
      There are no down migrations in this repository and none is expected —
      see *Roll back and clean up*.
   2. Give every new tenant-scoped table a `community_id` column declared
      `NOT NULL`. A table is tenant-scoped unless it is named in the
      `INSERT INTO _operator_global_tables` allowlist; the lint reads that
      allowlist out of the migration SQL rather than inferring it.
   3. Lead every primary key, unique constraint, foreign key and unique index on
      a tenant-scoped table with `community_id`, so no key is observable across
      communities.
   4. If the table belongs to the operator-global set, register it by adding its
      name to `_operator_global_tables` in the same migration, and add the name
      to the lint's recognised list in
      `crates/buzz-db/src/runtime/migration.rs` — the helper matches a fixed set
      of names, so an unregistered global table is linted as tenant-scoped and
      fails.
   5. Update `embedded_migrator_contains_consolidated_initial_schema` in
      `crates/buzz-db/src/runtime/migration.rs`: raise the
      `assert_eq!(migrations.len(), 40)` count, and add the version and content
      assertions for the migration you just wrote, in the same style as the
      surrounding cases.

2b. **Change the reconciliation script** (things `pgschema` cannot reproduce).

   1. Add the convergence statement to
      `scripts/reconcile-schema-after-pgschema.sql`, written so that running it
      twice is a no-op — the existing file uses `IF NOT EXISTS` guards around
      partition attachment and `ON CONFLICT (id) DO NOTHING` for its seed row.
   2. Add a **live assertion** immediately after it, in a `DO $$` block that
      `RAISE EXCEPTION`s when the catalog or the data disagrees. The script's
      existing pattern queries `pg_class.reloptions` for the storage parameter
      and counts the seeded row; asserting against the text of `schema.sql`
      instead would not prove the created database has the intended state.
   3. If you add a new `./bin/pgschema apply` caller anywhere under `scripts/` or
      `.github/workflows/`, run this script within the next six lines of it.
      `every_pgschema_apply_runs_post_apply_reconciliation` scans both trees and
      fails otherwise.

3. **Mirror the change into `schema/schema.sql`.** This is a hand edit, and
   nothing generates it. Match the object's shape exactly — column names, types,
   nullability, defaults, index key order and per-key sort/null options all
   participate in the parity checks. Honour the four lint obligations the file's
   own header states; they are the same four the migration lints enforce.

4. **Run the infra-free gate.**

   ```bash
   just test-unit          # includes: cargo nextest run -p buzz-db --lib
   ```

   This is the lane that catches a stray file in `migrations/`, a missing
   `community_id`, a key that does not lead with `community_id`, a re-tenanting
   `UPDATE` on `channels.community_id`, a `pgschema apply` caller that skips
   reconciliation, and a deletion-surface object present in one source and absent
   from the other.

5. **Run the parity check that CI does not run for you.** The desired-state and
   migration paths are compared by an `#[ignore]`d, Postgres-backed test, and
   `scripts/run-tests.sh` says in its own comment that neither its unit mode nor
   its integration mode executes the ignored buzz-db tests. Run it explicitly
   against a live database:

   ```bash
   cargo test -p buzz-db --lib -- --ignored \
     admin_schema_parity_between_desired_state_and_migrations
   ```

   The filter is the bare test-function name, which `cargo test` matches as a
   substring of the full path — the module prefix is not needed and is easy to
   get wrong.

6. **Exercise both creation paths.** A migration-created and a
   `pgschema`-created database must end up the same shape.

   ```bash
   just migrate                              # migration path: buzz-admin migrate + seed
   ./bin/pgschema apply --file schema/schema.sql --auto-approve
   psql ... -v ON_ERROR_STOP=1 < scripts/reconcile-schema-after-pgschema.sql
   ```

   Do not invent the second pair of commands from scratch — copy the exact
   invocation and environment from an existing caller:
   `scripts/start-relay-for-tests.sh`, `scripts/start-isolated-test-relay.sh`,
   `scripts/run-desktop-release-smoke.sh`, or the two steps in
   `.github/workflows/ci.yml`.

7. **Run the full pre-pull-request gate.** `just check` (which includes
   `file-size-check`) and `just ci`. If the change touches relay, database or
   auth behaviour, also run `just test` for the integration suite.

## Verify it succeeded

The change is correct when all of the following hold, in this order:

- `just test-unit` passes — the count assertion, the three tenant lints, the
  reconciliation-caller scan and the deletion-surface parity all agree.
- The `#[ignore]`d admin parity test from step 5 passes against a live database.
- `./bin/pgschema apply` followed by `scripts/reconcile-schema-after-pgschema.sql`
  completes with `ON_ERROR_STOP=1` and raises no exception — the script's own
  `DO $$` assertions are the fresh-bootstrap acceptance test.
- The relay starts against the migrated database. Migration success additionally
  requires the post-migration catalog checks to pass: the created-at floor
  trigger must exist on the `events` parent and every partition, and the
  channel-roster fence catalog must validate; either missing fails the migration
  closed rather than starting a relay on an unguarded schema.

## Roll back and clean up

- **There is no down migration, and adding one is not the answer.** Every file
  under `migrations/` is forward-only at the recorded revision. Recovery from a
  bad schema change is a *new* forward migration that corrects it, because the
  previous one is already checksum-frozen in `_sqlx_migrations` on every database
  that ran it.
- **Before it is applied anywhere**, cleanup is ordinary: delete the migration
  file, revert the `schema.sql` and reconciliation-script edits, and restore the
  count and content assertions in `crates/buzz-db/src/runtime/migration.rs`. All
  four must be reverted together or the unit gate fails.
- **For a local development database**, discarding and recreating is cheaper than
  unwinding. Re-run `just migrate` on a fresh database, or re-bootstrap through
  `./bin/pgschema apply` plus the reconciliation script.
- **A destructive or ambiguous data situation fails closed rather than
  proceeding.** The migrator's pre-flight check refuses to run on a populated
  pre-0007 database holding kind-30078 rows with ambiguous tag cardinality,
  returning an error that tells the operator to repair or remove those rows
  first. Treat that as the shape to imitate: a migration that could destroy
  history should refuse and report, not clean up silently.

## See also

- `launchpad/docs/corpus/architecture/containers/postgres.md` — the Postgres
  container, the embedded migration runner, and the `BUZZ_AUTO_MIGRATE` gate that
  decides whether a deploy applies your migration at all.
- `launchpad/docs/corpus/layers/lifecycle/startup.md` — where the migration
  decision sits in the relay's boot sequence and what happens when it fails.
- `launchpad/docs/corpus/development/prerequisites.md` — the tools and versions
  this procedure assumes are installed.
- `launchpad/docs/corpus/development/hermit.md` — how `bin/pgschema` and the rest
  of the pinned toolchain resolve.
- `docs/multi-tenant-conformance.md` — the governing contract behind the
  `community_id` rules the lints enforce.
- `AGENTS.md` — gotcha 7 states the `pgschema` constraint this node's step 2b
  operationalises.

## Boundary

This node does not describe:

- **Facts to look up rather than actions to perform** — the table-by-table
  contents of the schema, the meaning of an individual event kind, or the full
  argument surface of `pgschema`. Those live in the SQL itself
  (`migrations/0001_initial_schema.sql`, `schema/schema.sql`) and in
  `docs/multi-tenant-conformance.md`.
- **How to acquire the underlying skill from scratch** — this procedure assumes a
  reader who can already write Postgres DDL and run the repository's `just`
  recipes.
- **Why the schema is designed the way it is** — why community is the security
  boundary, why the relay is the source of truth, why the migration runner holds
  an advisory lock. Those are concept-shaped and belong to the architecture
  nodes linked above.
- **Applying migrations in a deployed environment.** Whether a running relay
  migrates itself is decided by `BUZZ_AUTO_MIGRATE`, and that is
  `architecture-containers-postgres`'s and `layers-lifecycle-startup`'s subject,
  not this one's.

## Relationships

Declared in this node's front matter, and both targets confirmed present on
`origin/launchpad` at the recorded revision rather than only in the authoring
worktree:

- `implements: corpus-template-procedure` — this node is an instance of the
  procedure template, which names a template instance of a standard as
  `implements`' own worked example.
- `references: architecture-containers-postgres` — background this procedure
  assumes and deliberately does not restate: the migration runner, its locking
  contract, and the startup gate.

`layers-lifecycle-startup`, `development-prerequisites` and `development-hermit`
are linked in prose above rather than as typed edges; each is adjacent context a
reader may want next, not something this procedure depends on or is part of.

## Scope and omissions

**This node covers** the contributor-facing procedure for changing the database
schema in this repository: which of the two authored sources a change belongs in,
the tenant-isolation rules a new migration must satisfy, the test assertions that
must move with it, the reconciliation contract for anything `pgschema` cannot
reproduce, how to verify both creation paths agree, and what recovery looks like
in a forward-only migration set.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Whether and how a deployed relay applies migrations | `architecture-containers-postgres`, `layers-lifecycle-startup` |
| The multi-tenant conformance contract itself | `docs/multi-tenant-conformance.md` |
| Table-by-table schema contents | `migrations/0001_initial_schema.sql`, `schema/schema.sql` |
| Deploy pipelines that create or migrate hosted databases | `squareup/block-coder-tf-stacks`, `squareup/sprout-oss` (separate private repositories) |
| The corpus authoring rules this node was written against | `launchpad/docs/corpus/AGENTS.md` |

**Two verification gaps found while writing this node, recorded rather than
fixed here.** Both are stated as INFERENCE in the provenance ledger above, with
the searches that produced them:

- The desired-state/migration admin parity test is `#[ignore]`d and appears to
  run in no automated lane — which is why step 5 exists as an explicit manual
  step rather than a note.
- `scripts/reconcile-schema-after-pgschema.sql` is not named by CI's `rust`
  paths filter, so a pull request changing only that file appears to run neither
  Unit Tests nor Backend Integration.

Neither was filed as an issue by this task, and neither is a claim about intent —
only about what the checked-in configuration does at the recorded revision.

**Expected but not verified when this node was written:**

- **No command in this node was executed.** No Postgres was started, no migration
  was applied, no `pgschema apply` was run, and the `#[ignore]`d parity test was
  not executed. Every command above is transcribed from the file that defines it
  — `Justfile`, `scripts/run-tests.sh`, the four `pgschema apply` callers — not
  from an observed run. The procedure template's own evidence expectation is that
  a step should cite having exercised the workflow; this node does not meet that
  bar, and that is the largest single gap in it.
- **sqlx's own behaviour on a checksum mismatch was not observed.** The
  `VersionMismatch` consequence of editing an applied migration is recorded here
  because `crates/buzz-db/src/runtime/migration.rs` states it, not because it was
  reproduced.
- **The next migration number was inferred from the tip, not from a reservation
  mechanism.** No lock, registry or CI check for concurrently claimed migration
  numbers was found; whether two contributors can collide on `0041` was not
  established.
- **`docs/multi-tenant-conformance.md` was confirmed to exist and to be named by
  `schema/schema.sql` as the governing contract, but its contents were not read
  in full**, so this node cites it as an authority to follow rather than
  summarising it.
