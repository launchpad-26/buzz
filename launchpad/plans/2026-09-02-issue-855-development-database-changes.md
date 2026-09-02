# Plan — issue #855: `launchpad/docs/corpus/development/database-changes.md`

Repository revision planned against: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`
(`origin/launchpad` at fetch time). Branch:
`task/855-development-database-changes`. Worktree:
`/home/serina/Launchpad/buzz/__worktrees/task-855-development-database-changes`.

One hand-authored canonical corpus node, procedure-shaped, documenting how a
contributor changes the database schema in this repository.

## ALREADY TRUE

Verified in this worktree at the revision above.

- `launchpad/docs/corpus/development/database-changes.md` **does not exist**.
  `launchpad/docs/corpus/development/` holds exactly `build.md`, `debugging.md`,
  `hermit.md`, `prerequisites.md`.
- The corpus carries 231 `id:` values; the target id `development-database-changes`
  is not among them.
- `migrations/` holds 40 files, `0001_initial_schema.sql` …
  `0040_push_message_kinds.sql`, all forward-only — no `.down.sql` exists.
- `schema/schema.sql` exists (93 KB) and declares itself "Source of truth for
  fresh database setup", listing four Lane-0 migration-lint obligations.
- `scripts/reconcile-schema-after-pgschema.sql` exists (228 lines) and ends with
  an `ALTER TABLE replica_heartbeat SET (vacuum_truncate = false)`, a seed
  `INSERT … ON CONFLICT (id) DO NOTHING`, and a `DO $$` block that raises unless
  `pg_class.reloptions` and the singleton row are both present.
- `bin/pgschema` is a symlink to `.pgschema-1.7.4.pkg` (Hermit).
- `crates/buzz-db/src/runtime/migration.rs` (2612 lines) holds the embedded
  migrator plus the whole lint/parity test battery.
- `Justfile` has `_ensure-migrations` (`cargo run -p buzz-admin -- migrate` then
  `./scripts/seed-local-community.sh`) and a `migrate` recipe that depends on it.
- Neighbouring merged nodes already cover the runtime side:
  `architecture-containers-postgres` (migration runner, `BUZZ_AUTO_MIGRATE`
  gate, schema authority) and `layers-lifecycle-startup` (step 6 of boot). This
  node must link, not restate, those.
- `launchpad/project-intelligence/corpus/validate.py` and
  `launchpad/project-intelligence/corpus/tests/` both exist.

## STEP 1 — Finish evidence gathering (done before drafting)

Open and read, recording exact assertions:
`crates/buzz-db/src/runtime/migration.rs` (migrator, advisory-lock wrapper, the
40-migration count assertion, `every_pgschema_apply_runs_post_apply_reconciliation`,
the three tenant lints, the two parity tests and their `#[ignore]` attributes);
`scripts/reconcile-schema-after-pgschema.sql`; `schema/schema.sql` header;
`.github/workflows/ci.yml` (paths filter, the two `pgschema apply` steps, job
gating); `scripts/run-tests.sh`; `Justfile`; `AGENTS.md` gotcha 7.

**Done when:** every claim intended for the node has a file open behind it, and
each unverifiable expectation is written down for the omissions section.

## STEP 2 — Write the front matter

`id: development-database-changes`, `type: development`, `status: draft`,
`origin: launchpad`, `audiences: [developer, agent]`. First `evidence` entry is
the commit citation for `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`. One entry
per substantive body claim; FACT only where the file was opened; INFERENCE
carries `confidence`; TEAM_KNOWLEDGE carries `provided_by` and no `confidence`.

**Done when:** `python3 -c "import yaml,jsonschema…"` equivalent passes via
validate.py in STEP 4, with no schema error.

## STEP 3 — Write the body

Procedure shape per `launchpad/docs/corpus/templates/procedure.md`: exactly one
`#` heading; Before you start; a numbered task sequence split by branch
(additive migration vs. desired-state-only change); success verification;
rollback and cleanup; See also; Boundary; Relationships; Scope and omissions.
No `relationships` in front matter unless a target id is confirmed present on
`origin/launchpad` — default is none, with prose "See also" links.

**Done when:** every DoD bullet in #855 maps to a section, and the file is well
under the 1000-line repository ceiling.

## STEP 4 — Validate

`python3 launchpad/project-intelligence/corpus/validate.py` reports PASS.
Unverified notices are acceptable; errors are not.

**Done when:** exit status 0.

## STEP 5 — Earn the gate, then commit

`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own sole command, confirm OK, then `git add` + `git commit -s` in a
separate call. Stop at the commit — no push, no PR.

**Done when:** one commit exists on `task/855-development-database-changes`
containing the node and this plan.

## PARALLEL

Nothing. Steps 1→5 are strictly sequential; this is a single-file document task.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK.
- File under 1000 lines (repository-wide `just file-size-check`).
- Exactly one new canonical corpus document; no generated outputs touched.

## BUDGET

Five steps, one document, one plan, one commit. No code changes, no migration
added, no database started.

## OPEN

- **Id convention.** `standards/naming.md` MUST 3 prescribes a `corpus-` prefix;
  practice across 231 nodes does not use it for content nodes, and the
  `development/` directory itself is internally inconsistent (`development-hermit`,
  `development-prerequisites`, `debugging`, `corpus-development-build`). Settled
  for this task as `development-database-changes`; the tension is reported, not
  filed as an issue by this task.
- Whether `admin_schema_parity_between_desired_state_and_migrations` runs in any
  automated lane. Searched `ci.yml` and `scripts/run-tests.sh`; no selector
  found. Stated in the node as an INFERENCE with its search recorded.

## LEFT OUT

- Adding an actual migration, or running Postgres to execute any of the
  documented commands. No database was started; command behaviour is documented
  from the files that define it, and that limit is disclosed in the node.
- Any second canonical corpus document.
- Editing `standards/naming.md`, `AGENTS.md`, or any neighbouring node.
- Filing issues for the naming tension or the CI-filter gap.
