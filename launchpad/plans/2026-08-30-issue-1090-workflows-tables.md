Issue #1090 — task: document layers/data/postgres/workflows-tables.md
Stated size: no `Size` line -> cap: 5 steps (single hand-authored document, category: data-entity)

ALREADY TRUE  (verified against git, not notes)
  On `origin/launchpad` tip 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 (task/1090-workflows-tables
    branched from it); `launchpad/docs/corpus/layers/data/postgres/workflows-tables.md` does
    not exist; `node.schema.json`, `AGENTS.md`, and all 26 corpus templates (including
    `templates/data-entity.md` and `templates/datastore.md`) are merged;
    `architecture-containers-postgres` and `architecture-flows-workflow-execution` are
    merged, validated content nodes; `migrations/0001_initial_schema.sql` (lines 358-466)
    defines the `workflows`, `workflow_runs`, `workflow_approvals` and
    `scheduled_workflow_fires` tables plus the `workflow_status`/`run_status`/
    `approval_status` enums; `migrations/0031_workflow_run_error_codes.sql` is the only
    later migration touching any of the four tables (adds `workflow_runs.error_code`);
    `crates/buzz-db/src/workflow.rs` is the single read/write code path for all four
    tables (confirmed by grep: no other crate issues SQL against them).

STEP 1  [independent]  Choose the template and gather evidence. Issue #1090's DoD bullets ("identity/key
        and semantic ownership", "summarizes fields by meaning without duplicating
        generated schema detail", "relationships, lifecycle and invariants", "links
        authoritative migration/schema and read/write code paths") match
        `templates/data-entity.md`'s six required sections (Identity, Attributes and
        shape, Invariants, Relationships, Provenance, Storage pointer), not
        `templates/datastore.md`'s seven (which target one storage technology instance
        as a whole, not one family of tables within it). Read `migrations/0001_initial_schema.sql`
        lines 358-466 and `migrations/0031_workflow_run_error_codes.sql` in full. Read
        `crates/buzz-db/src/workflow.rs` in full for: the four record structs and their
        identity/community-scoping doc comments, `create_workflow`/`upsert_workflow`
        (NIP-33 d-tag upsert idempotency), `update_workflow_status`/`set_workflow_enabled`
        (lifecycle: active -> disabled -> archived, independent `enabled` flag),
        `delete_workflow` (CASCADE to runs/approvals), `update_workflow_run` (run status
        transition timestamps, the Fix C3 comment), `create_approval`/`update_approval`
        (TOCTOU-safe pending-only transition), and `claim_scheduled_workflow_fire`
        (at-most-once cron claim semantics).
        done when: each source above has been opened and every claim the finished
        document will make has a citation to a file actually opened here.

STEP 2  [needs 1]  <- RUNS HERE  Write `launchpad/docs/corpus/layers/data/postgres/workflows-tables.md`:
        schema-valid front matter (`id: layers-data-postgres-workflows-tables`,
        `type: layers` — an explicit override of data-entity.md's own worked-example
        type, `implementation`, disclosed in the ledger per standards/taxonomy.md
        precedent from earlier batches in this run — `status: draft`, `origin: launchpad`,
        `audiences: [agent, developer, operator, reviewer]`, an `evidence` ledger whose
        first entry is the HEAD commit citation, `relationships: part-of ->
        architecture-containers-postgres` and `references -> architecture-flows-workflow-execution`
        — both merged, both topically substantive), plus a body following
        data-entity.md's six required sections: Identity (composite
        `(community_id, id)` / `(community_id, token)` keys, never globally unique),
        Attributes and shape (fields by meaning, not restating column types already in
        the migration), Invariants (CASCADE deletion, TOCTOU-safe approval transition,
        at-most-once scheduled-fire claim, cache-invalidation contract on mutation),
        Relationships (the FK graph between the four tables, and the NIP-33 d-tag
        upsert path), Provenance (server-derived — no Nostr event is these tables' own
        canonical form; command/event-sourced mutation triggers the writes), and
        Storage pointer (Postgres, this repository's single instance). A scope-and-
        omissions section states what is deliberately not covered (the workflow
        *definition* JSON/DSL semantics — buzz-workflow's own concern) and anything
        expected but not verified.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
        with the file present, and every field/invariant/relationship named in the body
        has a matching `evidence` entry.

STEP 3  [needs 2]  Self-audit the finished node against issue #1090's DoD checklist line
        by line, confirm every evidence entry's citation was actually opened in STEP 1,
        confirm no second canonical document was created, and confirm the `type: layers`
        override is disclosed.
        done when: the audit is written inline in this session's notes (not committed)
        and `validate.py` still exits 0.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        prior command, then commit the plan + document. Do NOT push and do NOT open a
        PR — a later batch-orchestration step bundles this branch with its #610 siblings.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK; `git commit -s` succeeds without a "no verification stamp" block.

PARALLEL  None. One target file, sequential steps.

GATES     Corpus validator (`validate.py`) and the corpus unittest suite, both run
          locally in this session. `review-adjudicate` and a cross-model final pass are
          explicitly deferred to the batch owner's review of the #610 overnight run —
          not run here.

BUDGET    STEP 1/2. Four tables, four enums, and roughly two dozen CRUD functions in
          `workflow.rs` each carry a load-bearing doc comment that needs reading in full
          before any claim can honestly be FACT rather than INFERENCE.

OPEN      Whether `layers/data/postgres/*` is the corpus's eventual settled location for
          this document, or whether a later per-type standards pass (#1307-#1351)
          relocates it, is not resolved here — the `id` this task assigns is permanent
          regardless of where the file later moves, per `AGENTS.md`'s "id is permanent"
          rule.

LEFT OUT  Any second hand-authored canonical corpus document. Documenting the workflow
          *definition* DSL/JSON schema itself (buzz-workflow's own concern). Editing
          `node.schema.json`, `AGENTS.md`, or either template. Adding relationships to
          the unmerged sibling `layers/data/postgres/*` documents from this same batch.
          Pushing the branch or opening a PR.
