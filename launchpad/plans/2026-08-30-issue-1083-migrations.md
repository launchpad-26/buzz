Issue #1083 — task: document layers/data/postgres/migrations.md
Stated size: no Size line on the issue; capped per this overnight corpus-batch-author run's own instruction  →  cap: 5 steps

ALREADY TRUE  (verified against git and the actual code this session, not notes)
  Repository revision for this plan: 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5
  (origin/launchpad, worktree __worktrees/task-1083-migrations, branch
  task/1083-migrations).
  launchpad/docs/corpus/layers/data/postgres/migrations.md does not exist yet
  ("git ls-tree origin/launchpad -- launchpad/docs/corpus" lists no layers/
  subtree at all).
  node.schema.json's type enum has 13 members including "layers"; no
  per-value definition exists beyond "the corpus surface this node documents"
  (standards/taxonomy.md).
  Precedent from earlier tasks in this overnight batch under Feature #610:
  every layers/data/... node uses type: layers, not type: architecture as
  templates/datastore.md's own note about real instances would otherwise
  suggest. This plan follows that precedent and discloses the override in the
  node's evidence ledger, per standards/taxonomy.md step 4 (say so in
  scope-and-omissions when the fit is imperfect or an override is made).
  launchpad/docs/corpus/architecture/containers/postgres.md (id
  architecture-containers-postgres, type: architecture, status: draft) is
  merged on origin/launchpad (commit 0020a2a03). It is the container-level
  Postgres node this migrations document zooms into procedurally — a
  reasonable part-of target.
  No other layers/data/postgres/* sibling exists on origin/launchpad yet
  (PR #1875 unmerged) — no relationship target there.
  Issue #1083's Definition of Done bullets (authoritative/derived/cache/
  transport; owned data, access patterns, lifecycle/retention, consistency
  semantics; tenancy/security boundaries and failure behavior; links
  schema/migrations/code/tests) are the generic templates/datastore.md
  checklist, copied wholesale onto this issue the same way earlier template
  tasks in this corpus effort found boilerplate DoD checklists mismatched to
  their real subject (templates/procedure.md and templates/reference.md each
  carry their own "Note on Definition of Done" section for the identical
  pattern). This issue's actual subject — the migration mechanism — is a
  process, not a table and not the whole Postgres instance, so those bullets
  do not map cleanly onto it. templates/reference.md (Diataxis Reference
  form: information-oriented description of "the machinery and how it
  operates") fits better than templates/datastore.md (whole-instance,
  seven-section template already substantially covered by
  architecture-containers-postgres and out of scope for a migrations-only
  node) or templates/procedure.md (goal-oriented task sequence — migrations
  are applied automatically at relay startup, not performed by a reader as a
  chosen task).
  crates/buzz-db/src/migration.rs embeds sqlx::migrate!("../../migrations")
  as MIGRATOR, and run_migrations holds the exclusive
  SCHEMA_DESTRUCTION_LOCK_KEY session lock for the whole run, serializing
  schema changes against destructive-deletion transactions. A source lint
  (migration_execution_cannot_bypass_schema_destruction_lock, a real test in
  the same file) enforces that MIGRATOR.run has exactly one call site.
  migrations/ holds 31 sequentially numbered SQL files
  (0001_initial_schema.sql .. 0031_workflow_run_error_codes.sql), applied in
  that order.
  crates/buzz-db/src/lib.rs's Db::migrate() (line ~1048) wraps
  migration::run_migrations, under a #[datastore_span(name = "migrate",
  system = "postgresql")] attribute.
  crates/buzz-relay/src/main.rs:191 calls db.migrate().await at relay
  startup — migrations are auto-applied on boot, matching root CLAUDE.md's
  "SQL migrations (auto-applied on relay startup)" note. crates/buzz-admin's
  Migrate subcommand (just migrate / cargo run -p buzz-admin -- migrate)
  calls the same db.migrate() path for operator-triggered runs.
  run_migrations_locked additionally runs
  reject_legacy_nip_rs_cardinality_ambiguity before MIGRATOR.run, and
  crate::replica_fence::verify_floor_guard_catalog after — the migration run
  fails closed on data that would make a later invariant unsafe, not merely
  "apply pending SQL files."
  schema/schema.sql is a separate, hand-maintained "desired-state bootstrap
  schema", structurally parity-checked against the deletion-surface
  migration (0029) by a dedicated test
  (deletion_surface_parity_between_migration_0029_and_schema_sql) — not
  itself applied by the migrator, but a load-bearing test fixture keeping the
  two in sync.
  crates/buzz-push-gateway/migrations is a separate migrator with its own
  tables (confirmed by
  migration_execution_cannot_bypass_schema_destruction_lock's explicit
  exemption plus its own community_id-absence check) — a real boundary to
  disclose, not silently folded into this node.
  Justfile's migrate / _ensure-migrations recipe runs
  "cargo run -p buzz-admin -- migrate"; CONTRIBUTING.md documents "just
  migrate" under its dependency table row for sqlx migrations.

STEP 1  Confirm the reference.md template shape covers every DoD bullet honestly  [independent]
        done when: a one-line mapping exists from each of issue #1083's four
        subject-specific DoD bullets to where it is satisfied in the drafted
        node or explicitly named as out of scope in its Boundary section
        (tenancy/security/failure -> the schema-destruction lock and the
        cardinality guard, cited to code; authoritative/derived/owned-data/
        access-patterns -> named out of scope, owned by
        architecture-containers-postgres; links-not-DDL -> structured-entry
        table cites file/symbol names only, never SQL bodies).

STEP 2  Draft launchpad/docs/corpus/layers/data/postgres/migrations.md      [needs 1]  ← RUNS HERE
        done when: the file exists with schema-valid front matter (id
        layers-data-postgres-migrations, type: layers, status: draft, origin:
        launchpad, audiences, evidence, one relationships entry: part-of ->
        architecture-containers-postgres) and a body following
        templates/reference.md's required sections (Reference description;
        structured entries; optional Commands; Boundary; Relationships;
        Scope and omissions), and
        "python3 launchpad/project-intelligence/corpus/validate.py" exits 0.

STEP 3  Self-check evidence honesty                                          [needs 2]
        done when: every evidence entry's citation was re-opened and confirmed
        to say what the statement claims; no FACT rests only on an
        UNVERIFIED-shaped citation except the mandatory provenance commit
        entry; the type: layers override and the DoD-mismatch disclosure both
        appear in the node's own body (Scope and omissions), not only in this
        plan.

STEP 4  Run the commit-gate test suite as a bare standalone command           [needs 2]
        done when: "python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p 'test_*.py'" run alone
        (never piped through tail/head) reports OK.

STEP 5  Commit the plan and the corpus document                              [needs 3, 4]
        done when: "git add launchpad/plans/2026-08-30-issue-1083-migrations.md
        launchpad/docs/corpus/layers/data/postgres/migrations.md && git commit
        -s -m 'docs(corpus): postgres migrations concept (#1083)'" succeeds
        and "git log -1" shows a signed-off commit on task/1083-migrations,
        with no push and no PR opened.

PARALLEL  None of these five steps can run as independent subagents against
          each other: step 1 must land before step 2's draft can honestly map
          its content to the DoD, steps 3 and 4 both read the step-2 output
          and gate step 5, and step 5 needs both. This is a single
          hand-authored document with one author and one file under edit at
          a time — there is no independent second file to parallelize
          against.
GATES     No review-* skill runs in this task (corpus-batch-author's isolated
          worktree scope stops at commit, per the outer task instructions —
          bundling and review happen in a later orchestration step). qa
          explore mode does not apply: this is a docs-only change with no
          runtime interface to exercise. The only gates are mechanical:
          validate.py (step 2) and the unittest suite (step 4), both must
          exit 0/OK before the commit in step 5.
BUDGET    Step 2 (the draft itself) is the step most likely to eat the
          budget — getting the reference.md shape right, keeping every
          structured-entry row cited to real code rather than restated SQL,
          and writing the Boundary/Scope-and-omissions disclosures honestly
          all happen there.
OPEN      Whether a future templates/procedure.md-shaped how-to node ("how to
          write and land a new Buzz migration") should exist separately —
          named as a gap in this node's Boundary/Scope-and-omissions, not
          resolved here. Whether schema/schema.sql's desired-state role
          deserves its own corpus node (currently only a test-parity fixture,
          cited here but not separately documented) — left as a gap, not
          folded into this node per AGENTS.md's one-node-one-idea rule.
LEFT OUT  No second canonical document. No edits to
          architecture-containers-postgres or any template file. No
          relay/database code changes — this is documentation-only, per the
          issue's own Out of scope section. No push, no PR — the outer task
          instructions reserve bundling for a later orchestration step.
