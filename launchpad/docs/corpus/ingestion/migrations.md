---
id: ingestion-migrations
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "schema/schema.sql's own header states it is the 'Source of truth for fresh database setup', that it is 'NOT additive over the single-community schema; the rewrite replaces it', and that 'Existing single-community deployments migrate via the documented backfill migration (0002), which assigns all pre-existing rows to one default community' -- i.e. the repository's own cumulative-schema file distinguishes itself from a migration's point-in-time record in its own opening comment."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "migrations/0002_git_repo_names.sql's header states it is an 'Additive migration (not folded into 0001)' and that 'brownfield databases that already applied the pre-PR 0001 must not see its checksum change, or sqlx aborts startup with a VersionMismatch' -- a migration file, once any database has applied it, is never edited again."
    entry_class: FACT
    evidence:
      - "migrations/0002_git_repo_names.sql"
  - statement: "crates/buzz-db/src/runtime/migration.rs's reject_legacy_nip_rs_cardinality_ambiguity carries a doc comment stating 'Migration 0007 is checksum-frozen and predates exact NIP-RS tag-cardinality enforcement', and the function itself reads the sqlx-managed _sqlx_migrations table's max(version) before deciding whether to guard a legacy data shape -- both are additional, independent instances of the same checksum-frozen, additive-only convention 0002's header states for itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "crates/buzz-db/src/runtime/migration.rs's own module doc comment states: 'Fresh deployments apply the checked-in additive SQL files under migrations/. The multi-tenant rewrite begins from a clean consolidated 0001; legacy single-tenant cutover/backfill is a separate operator script, not startup migration state.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "crates/buzz-db/src/runtime/migration.rs contains a test, deletion_surface_parity_between_migration_0029_and_schema_sql, whose own doc comment states a passing run means 'every deletion control-plane table, function, trigger, and index 0028 creates must exist in schema.sql with an identical normalized definition' and warns that without it a 'desired-state bootstrap... cannot silently omit part of the deletion surface the way the pre-parity schema.sql omitted community_deletion_manifest_keys... and storage_taxonomy_sweeps' -- this is a real, narrow mechanism reconciling one migration's DDL surface against schema.sql's cumulative state, scoped to migration 0029's deletion-control-plane objects only, not a general guarantee covering every migration or every table."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "scripts/reconcile-schema-after-pgschema.sql's header states: 'pgschema reconciles DDL, but it does not execute seed DML or preserve every table storage parameter from schema/schema.sql... Every pgschema apply caller must run this idempotent script so fresh bootstraps converge on the same live database contract as migration-managed databases.'"
    entry_class: FACT
    evidence:
      - "scripts/reconcile-schema-after-pgschema.sql"
  - statement: "crates/buzz-db/src/runtime/migration.rs contains a test, every_pgschema_apply_runs_post_apply_reconciliation, that scans every file under scripts/ and .github/workflows/ for a line containing './bin/pgschema apply' and asserts one of the following six lines invokes scripts/reconcile-schema-after-pgschema.sql, failing the test otherwise -- the pgschema-then-reconcile ordering is mechanically checked at every current call site, not merely documented."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
  - statement: "This repository's own top-level contributor guide states, as its seventh listed 'Common Gotcha': 'pgschema omits seed DML and some storage parameters -- Fresh desired-state bootstraps use ./bin/pgschema apply, which does not execute INSERT statements or preserve every table storage parameter from schema/schema.sql. Put each unsupported invariant in scripts/reconcile-schema-after-pgschema.sql as an idempotent convergence statement plus a live catalog or data assertion... A string assertion against schema.sql alone does not prove the pgschema-created database has the intended state.'"
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "architecture/containers/postgres.md, merged on origin/launchpad, already documents the embedded migration runner's mechanics in full: sqlx::migrate! embedding, the single MIGRATOR.run call site under an exclusive advisory lock, the BUZZ_AUTO_MIGRATE startup gate, and specific migrations 0001 and 0021 -- this node does not restate any of that and links to it instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "standards/code-references.md, merged on origin/launchpad, already governs the citation form for any file citation in a node's evidence ledger (bare-path preference, pinning, position syntax) -- this node adds only which claim-type a migrations/ file may honestly support, not a second citation-form contract."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "Issue #964's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#964 definition of done"
  - statement: "Parent Feature #620 lists ingestion/migrations.md among 32 child document tasks under an agents/ and ingestion/ path family; none of #964's ingestion/*.md or agents/*.md siblings were merged on origin/launchpad at this node's authoring time."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
  - statement: "This node treats the fact that a migration file, once applied by any database, is never edited again (only ever superseded by a later additive migration) as sufficient reason to forbid citing it alone for a present-tense schema claim -- a citation to a frozen point-in-time file cannot become stale in the way a citation to a live, evolving file can, but it also never updates to reflect what changed after it, so a present-tense reader needs the cumulative file instead."
    entry_class: INFERENCE
    evidence:
      - "migrations/0002_git_repo_names.sql"
      - "schema/schema.sql"
    confidence: 0.85
relationships:
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-standard-code-references
  - type: references
    target: architecture-containers-postgres
---

# Policy: migration files as point-in-time schema evidence

This node states the binding requirements on how a corpus node (or any author in this
repository) may cite a file under `migrations/` as evidence: what claim-type such a
citation honestly supports, and what it must be paired with when the claim being made
is about the database's current shape rather than its history.

## Scope and authority

**This node governs** how a citation naming a file under `migrations/` may be used to
support a claim in a corpus node's evidence ledger (or, by the same reasoning, any
other document in this repository): specifically, the distinction between "this
schema change happened, as of this migration" and "the schema currently looks like
this," and which source honestly supports each. **It does not govern** the citation's
*form* -- path syntax, pinning, line positions -- which `standards/code-references.md`
already governs for any file citation, code or migration alike; nor does it govern how
the migration runner itself is embedded, gated, or locked at startup, which
`architecture/containers/postgres.md` already documents. **Its authority comes from**
what the migration files and their own supporting code already state about
themselves, opened directly rather than assumed: `schema/schema.sql`'s header,
`migrations/0002`'s and the migration runner's checksum-frozen comments, and the two
tests named below. **Where this node and any of those sources disagree, they win** --
this node has drifted and should be fixed.

| For | Read |
|---|---|
| The citation form for any repository-file evidence, migration files included | `launchpad/docs/corpus/standards/code-references.md` |
| The migration runner's embedding, locking, and startup-gate mechanics | `launchpad/docs/corpus/architecture/containers/postgres.md` |
| Creating, updating and retiring a corpus node | `launchpad/docs/corpus/AGENTS.md` |
| The general policy-node shape this document instantiates | `launchpad/docs/corpus/templates/policy.md` |
| What pgschema does not reconcile, and why it matters for present-tense claims | `CLAUDE.md`'s Common Gotcha #7; `scripts/reconcile-schema-after-pgschema.sql` |

## MUST

| # | Requirement |
|---|---|
| **M1** | A citation to a file under `migrations/` MUST support only a point-in-time claim ("this changed, as of migration NNNN"), never a present-tense "the schema currently has X" claim standing alone. A migration is checksum-frozen the instant any database has applied it -- editing one after the fact aborts every already-migrated deployment's startup with a `VersionMismatch` (`migrations/0002_git_repo_names.sql`'s own header states this consequence; migration 0007's checksum-frozen status in `crates/buzz-db/src/runtime/migration.rs` is a second, independent instance of the same convention) -- so a migration file can never be edited to reflect what changed after it. Enforced by review only: `validate.py` discards a node's body before any check runs, so nothing mechanical can tell a historical claim from a present-tense one wearing the same citation. |
| **M2** | A present-tense claim about the schema's current shape MUST cite `schema/schema.sql` -- the fresh-install desired-state file which states of itself, "Source of truth for fresh database setup" and explicitly "NOT additive over the single-community schema" -- not a migration file alone. Enforced by review only. |
| **M3** | A present-tense claim about a database bootstrapped via `./bin/pgschema apply` MUST additionally account for `scripts/reconcile-schema-after-pgschema.sql`, because pgschema "does not execute seed DML or preserve every table storage parameter from `schema/schema.sql`" (the reconcile script's own header). Citing `schema.sql` alone does not establish that a pgschema-bootstrapped database actually has the seed rows or storage parameters `schema.sql` describes. Enforced partially: the test `every_pgschema_apply_runs_post_apply_reconciliation` (`crates/buzz-db/src/runtime/migration.rs`) mechanically checks that every `./bin/pgschema apply` call site in `scripts/` and `.github/workflows/` is followed by the reconcile script within six lines -- but nothing mechanical checks that a corpus node's own present-tense prose actually accounts for the gap. |
| **M4** | A migration citation's *form* MUST follow `standards/code-references.md` unchanged -- this node adds no second citation-form contract. A bare repository path is preferred over `path:line` for the same reason that standard already states: a migration's line numbers are not checked against the file's length either. |
| **M5** | A claim about how migrations are embedded (`sqlx::migrate!`), applied (the single `MIGRATOR.run` call site and its advisory lock), or gated at startup (`BUZZ_AUTO_MIGRATE`) MUST NOT be restated in this node or any node citing this one -- `architecture/containers/postgres.md` already carries that content in full; cite it instead of duplicating it. |

## SHOULD

| # | Guidance |
|---|---|
| **S1** | When a specific migration's DDL is mechanically checked against `schema.sql`'s cumulative definition -- as `deletion_surface_parity_between_migration_0029_and_schema_sql` does for migration 0029's deletion-control-plane tables, functions, triggers, indexes, and registry rows -- an author SHOULD name that test as the reconciling evidence, rather than assuming `schema.sql` was kept in sync by convention alone. This test is scoped to one migration and one object family; it is not evidence that any *other* migration's surface still matches `schema.sql`. |
| **S2** | An author citing a migration to explain *why* a current design decision exists (its rationale, not its current shape) SHOULD still separately confirm the design is still current in `schema.sql`, because a migration's rationale comment can outlive the thing it justified if a later migration replaced it. |
| **S3** | A claim needing both a point-in-time and a present-tense citation SHOULD cite both explicitly in the same evidence entry, naming which file supports which half of the claim, rather than one citation doing double duty. |

## Enforcement

**Nothing automated enforces M1, M2, M4, or M5.** `validate.py`'s `_load_frontmatter`
discards a node's Markdown body before any check runs (the same mechanism
`standards/code-references.md` and `templates/policy.md` each independently verify and
cite for their own Enforcement sections), so nothing compares a citation's claim-type
against the file it names. A `FACT` citing `migrations/0002_git_repo_names.sql` for a
present-tense "the schema currently has X" claim would pass `validate.py` cleanly --
the checker confirms the path resolves to a real file, never that the claim it
supports is the honest one.

**M3 is partially enforced.** `every_pgschema_apply_runs_post_apply_reconciliation`
mechanically checks that every `./bin/pgschema apply` call site in `scripts/` and
`.github/workflows/` is followed by the reconcile script -- a real, running gate, not
aspirational. It does not, and cannot, check that a corpus node's own prose correctly
accounts for the gap when making a present-tense claim; that half is review-only, same
as M1/M2/M4/M5.

**What a green `validate.py` run does not establish about a claim citing
`migrations/`**, per P6 of `templates/policy.md`:

| Not established | Consequence |
|---|---|
| That a migration citation supports only a point-in-time claim | A present-tense claim resting solely on a migration citation validates cleanly |
| That a present-tense claim is paired with `schema/schema.sql` | A missing pairing validates cleanly |
| That a pgschema-bootstrapped-database claim accounts for the reconcile script | Validated cleanly; only the `scripts/`/`.github/workflows/` call-site ordering itself is checked, by a Rust unit test outside this corpus |
| That a migration's own rationale comment still describes current behavior | A stale rationale comment, cited as if current, validates cleanly |

## Exceptions and escalation

**There is no exemption from M1-M5.** A node that needs to make a present-tense
schema claim and cannot find a corresponding `schema/schema.sql` statement to cite has
found a real gap between the migrations and the desired-state file -- that gap is
reported as a finding (or, if it blocks the node's own claim, the claim is dropped or
the node is marked `flagged` per `ADR-0029`), not silently bridged by citing the
migration alone.

**A disputed application of M1-M5 is a judgement, not an exception.** If an author and
reviewer disagree about whether a given statement is "point-in-time" or
"present-tense" phrased, the author records the tension in the pull request and the
reviewer decides. A repeated disagreement is filed as an issue against this node.

**A case none of M1-M5 covers is escalated, not invented.** Raise it as an issue
against parent Feature #620, describing the migration-citation situation that seemed
uncovered.

**`status: flagged` is not a substitute for M1-M3.** It names an unresolved
evidence-source conflict per `ADR-0029`, not a way to publish a present-tense claim
that only a migration file backs.

## Scope and omissions

**This node covers** the distinction between a migration file as point-in-time
evidence and `schema/schema.sql` (plus, for a pgschema-bootstrapped database,
`scripts/reconcile-schema-after-pgschema.sql`) as present-tense evidence; which claim
type a migration citation may honestly support; and what is and is not mechanically
checked about that distinction today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The citation form for any repository-file evidence (pinning, path syntax, line positions) | `launchpad/docs/corpus/standards/code-references.md` |
| How migrations are embedded, applied, locked, and gated at relay startup | `launchpad/docs/corpus/architecture/containers/postgres.md` |
| The multi-tenant schema's table-by-table contents and conformance contract | `migrations/0001_initial_schema.sql`, `docs/multi-tenant-conformance.md` |
| Whether staging/production deployment pipelines actually run `./bin/pgschema apply` or the embedded migrator, and in which order | `squareup/block-coder-tf-stacks`, `squareup/sprout-oss` (private, not opened by this task) |
| General corpus evidence classification (FACT/INFERENCE/TEAM_KNOWLEDGE) and precedence between conflicting sources | `launchpad/docs/corpus/AGENTS.md`, `ADR-0029` |
| Concrete agent procedures for evidence-gathering, ambiguity handling, and the rest of the `ingestion/`/`agents/` family | sibling tasks under parent Feature #620, none merged at this node's authoring time |

**No `migrations/README.md` exists in this repository at the recorded revision** --
checked directly (`ls migrations/`) rather than assumed; each migration's own header
comment is the only per-migration commentary that exists, there is no directory-level
document this node could instead point to or need to reconcile against.

**This node's own relationships.** Declared: `depends-on: corpus-agents` -- this
node's authority for how corpus evidence works at all (FACT/INFERENCE/TEAM_KNOWLEDGE,
citation checking) is derived from `AGENTS.md`, not original to itself, the same
relationship every sibling policy-shaped node in this corpus declares for the same
reason. Declared: `references: corpus-standard-code-references` -- supporting context
for the citation-form half this node explicitly defers to (M4); no ownership or
currency dependency implied, per that relationship type's own directionality. Declared:
`references: architecture-containers-postgres` -- supporting context for the runner
mechanics this node explicitly declines to restate (M5); same non-owning
directionality. No edge to any other sibling `ingestion/*.md` or `agents/*.md` task
under Feature #620: none are merged at this node's authoring time, so none is a valid
relationship target.

**Expected but not verified when this node was written:**

- **Whether every file under `migrations/` carries an explicit "additive, not folded
  into NNNN" or checksum-frozen style comment was not audited file-by-file.** This
  node spot-checked `0001`'s own header, `0002`, `0007` (via
  `reject_legacy_nip_rs_cardinality_ambiguity`'s doc comment), and `0029` (via the
  parity test) -- 4 of the 40 files present at the recorded revision -- and found the
  convention holds in each; it was not confirmed for the other 36.
- **`sqlx`'s own checksum-verification mechanism was not inspected upstream.** This
  node's claim about checksum-freezing rests on this repository's own comments
  describing the *consequence* (`VersionMismatch` on startup), not on reading `sqlx`'s
  source for how the check itself works.
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **Whether `deletion_surface_parity_between_migration_0029_and_schema_sql` or an
  equivalent exists for any migration other than 0029 was not checked beyond this
  node's own reading of `crates/buzz-db/src/runtime/migration.rs`'s test module; S1
  states what was found, not an exhaustive inventory of every parity test in that
  file.**
