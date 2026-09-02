# Issue #964 — ingestion/migrations.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md`, `standards/code-references.md`,
`templates/policy.md`, and `architecture/containers/postgres.md` are merged on
`origin/launchpad`; `launchpad/docs/corpus/ingestion/migrations.md` does not exist yet.
`architecture/containers/postgres.md` already documents the migration *runner*
mechanics in depth (embedded `sqlx::migrate!`, single guarded call site,
`BUZZ_AUTO_MIGRATE` opt-in gate, migration 0001/0021 specifics) — this task must not
restate that.

STEP 1  Gather evidence, real files only: `schema/schema.sql`'s own header comment
("Source of truth for fresh database setup... NOT additive... migrate via the
documented backfill migration (0002)"), `migrations/0002_git_repo_names.sql`'s header
("Additive migration (not folded into 0001): brownfield databases... must not see its
checksum change, or sqlx aborts startup with a VersionMismatch"),
`crates/buzz-db/src/runtime/migration.rs`'s `reject_legacy_nip_rs_cardinality_ambiguity`
(migration 0007 checksum-frozen) and its test
`deletion_surface_parity_between_migration_0029_and_schema_sql` (a real, narrow test
cross-checking one migration's DDL surface against `schema/schema.sql`'s cumulative
state), and `every_pgschema_apply_runs_post_apply_reconciliation` plus
`scripts/reconcile-schema-after-pgschema.sql`'s header (pgschema omits seed DML/storage
params; every `./bin/pgschema apply` call site must run the reconcile script,
mechanically enforced). Confirm no `migrations/README.md` exists. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `ingestion-migrations`, type
`ingestion` per the issue's own directive, status `draft`, origin `launchpad`,
audiences `[agent, developer, reviewer]`, `relationships: [{depends-on:
corpus-agents}, {references: corpus-standard-code-references}, {references:
architecture-containers-postgres}]` — all three resolve on `origin/launchpad`) and the
body, using `templates/policy.md`'s six required sections (Scope and authority, MUST,
SHOULD, Enforcement, Exceptions and escalation, Scope and omissions). Scope: a
migration file's own content is evidence of a **point-in-time schema change**, never
of the schema's current cumulative state, because migrations are checksum-frozen
(immutable once applied — editing one breaks brownfield `VersionMismatch`) and
additive-only; `schema/schema.sql` (or, for a live database bootstrapped via
`pgschema`, that plus `scripts/reconcile-schema-after-pgschema.sql`) is the correct
citation for a present-tense "the schema currently has X" claim. MUST rules center on:
citing a migration file only for "this changed at revision Y," never alone for "this
is the current state"; a present-tense schema claim needing `schema/schema.sql` (and
the reconcile script when the citing claim is about a pgschema-bootstrapped database)
alongside or instead of the migration; not restating the runner mechanics
`architecture-containers-postgres` already owns. Explicitly note in Scope and omissions
that no `migrations/README.md` exists (checked, per the task background) and that the
runner mechanics are `architecture-containers-postgres`'s content, linked not
duplicated.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix
and re-run until exit 0.

STEP 4  [needs 3] Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole prior command
to earn the verification stamp, confirm `OK`, then commit in a separate call. Dispatch
an independent `serina:review-code` pass on the diff; fix genuine findings.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`review-adjudicate` and the cross-model final review pass are deferred to the batch
owner's later review — not run here; an independent `review-code` pass substitutes as
this task's own verification step per the build-loop instructions.

BUDGET: small — one document, no code changes; evidence gathering scoped to
`schema/schema.sql`'s header, `migrations/0002` and `0007`'s headers, one migration
runner module (`crates/buzz-db/src/runtime/migration.rs`) and its two named tests, and
`scripts/reconcile-schema-after-pgschema.sql`'s header.

OPEN: whether `type: ingestion` is the corpus-wide-settled convention for a node whose
subject is "how to treat a class of repository evidence when authoring/citing it," or
merely this task's own directive from the batch dispatch — the issue background states
it explicitly ("type enum includes ingestion... your doc is under ingestion/ → type:
ingestion"), so this plan follows that rather than re-litigating the enum choice.

LEFT OUT: no restatement of the embedded-migrator mechanics, the `BUZZ_AUTO_MIGRATE`
gate, or partition/replica-fence details — all owned by
`architecture-containers-postgres`. No claim about staging/production migration
practice (that node already flags it as unverifiable from this repo). No edit to
`architecture-containers-postgres` itself to add a `references` edge back — that is a
follow-up for whoever touches that node next, not this task's to make on its behalf.
