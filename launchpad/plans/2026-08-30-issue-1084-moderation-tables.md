Issue #1084 — task: document layers/data/postgres/moderation-tables.md
Stated size: not stated in the issue body  →  cap: 5 steps (per this batch's dispatch brief)

ALREADY TRUE  (verified against git, not notes)
  migrations/0006_moderation.sql defines moderation_actions (community-scoped
  audit trail of moderator decisions), alongside sibling tables
  moderation_reports and community_bans in the same file.
  crates/buzz-db/src/moderation.rs owns all typed access to moderation_actions:
  NewAction, ActionRecord, MODERATION_ACTION_CHECK_VOCAB, insert_action,
  list_actions.
  crates/buzz-relay/src/handlers/moderation_commands.rs is the sole write path:
  every accepted mod-signed command (kinds 9040-9044, buzz-core/src/kind.rs)
  calls its insert_audit helper, which calls state.db.insert_moderation_action.
  crates/buzz-relay/src/api/bridge.rs's moderation_audit handler (GET
  /moderation/audit, NIP-98 + mod-authz) and crates/buzz-cli/src/commands/
  moderation.rs's cmd_audit are the read paths; the row is never represented
  as a Nostr event.
  crates/buzz-db/src/deletion.rs's EXPECTED_SCOPED_TABLES and
  PURGE_SCOPED_TABLES both include moderation_actions; the purge order lists
  moderation_reports (which FKs to moderation_actions.id via action_id) before
  moderation_actions itself — child-before-parent.
  migrations/0029_community_deletion.sql attaches enforce_community_write_fence()
  to moderation_actions, so writes are rejected once a community's deletion
  lifecycle leaves active.
  architecture-containers-postgres (merged on origin/launchpad) names
  "moderation" as one of the domains buzz-db owns and Postgres holds — a valid
  part-of relationship target.
  The unmerged audit-tables.md (#1075, PR #1875) explicitly scopes
  moderation_actions out of its own document and names moderation-tables.md
  (#1084) as the owner — confirms this node's exclusive subject is
  moderation_actions, not moderation_reports or community_bans.
  templates/data-entity.md (merged) is the template whose required sections
  map onto issue #1084's own DoD wording; templates/datastore.md's sections
  do not (that template covers storage technology, not a domain entity).
  launchpad/docs/corpus/layers/data/postgres/moderation-tables.md does not
  exist on this branch or on origin/launchpad.
  No layers/data/postgres/* sibling node is merged on origin/launchpad at the
  recorded revision (git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus), so no references edge toward a sibling entity node
  is available.

STEP 1  Draft front matter + evidence ledger against node.schema.json          [independent]
        id: layers-data-postgres-moderation-tables; type: layers (disclosed
        override of data-entity.md's own type: implementation suggestion, per
        standards/taxonomy.md, mirroring audit-tables.md's identical disclosed
        choice); status: draft; origin: launchpad; audiences: agent,
        developer, operator, reviewer. One relationships entry: part-of →
        architecture-containers-postgres. One evidence entry per claim planned
        for step 2, classified FACT/INFERENCE/TEAM_KNOWLEDGE honestly.
        done when: every claim planned for step 2's body sections has a
        matching ledger entry, and every FACT cites a source actually opened
        this session.
STEP 2  Write the body per templates/data-entity.md's required sections        [needs 1]  ← RUNS HERE
        Identity: (community_id, id) primary key, server-generated UUID — not
        a hash chain, distinct from audit_log. Attributes and shape: prose
        table citing 0006_moderation.sql's DDL and moderation.rs's
        NewAction/ActionRecord docs — not JSON Schema (no JSON column).
        Invariants: the 12-value action CHECK vocabulary; community
        write-fence; append-only in application code (no UPDATE/DELETE call
        site against moderation_actions found anywhere in the repository).
        Relationships: moderation_reports.action_id -> moderation_actions.id
        FK; community_id -> communities FK; corpus part-of edge. Provenance:
        triggered by kind 9040-9044 mod-signed commands, processed directly
        and never stored as regular events; the row itself is never
        re-serialized as an event; served only via GET /moderation/audit and
        buzz moderation audit, not the shared REQ/query path. Storage
        pointer: Postgres table moderation_actions, linked out via part-of.
        Scope and omissions: defer moderation_reports/community_bans to a
        future task; defer Postgres container facts to
        architecture-containers-postgres; name what was expected but not
        verified (no dedicated test suite found for insert_action/
        list_actions).
        done when: the document exists at
        launchpad/docs/corpus/layers/data/postgres/moderation-tables.md,
        covers every required data-entity.md section, and every issue #1084
        DoD bullet is satisfied by name.
STEP 3  Validate, earn the commit gate, and commit                             [needs 2]
        Run python3 launchpad/project-intelligence/corpus/validate.py from
        the repo root; fix and re-run until exit 0. Run, as the sole bare
        unpiped command in its own call, python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py" and
        confirm OK. Stage exactly the plan file and the corpus document, then
        git commit -s.
        done when: validate.py exits 0, the unittest suite reports OK, and
        the commit exists containing only those two files.

PARALLEL  None of the three steps can run as independent subagents in
          practice — step 1's ledger and step 2's body are written together
          against the same evidence, and step 3 depends on both being final.
          Step 1 is nominally independent (no file collision with step 2/3
          yet), but is sequenced first because the ledger must exist before
          the body that cites it is finalized.
GATES     No review-* skill applies within this isolated worktree per the
          batch dispatch brief (isolate/plan/build/verify/commit only; a
          later orchestration step bundles siblings into one PR for review).
          qa explore mode does not apply — this is a docs-only corpus change
          with no runtime interface to exercise. The only gates are
          validate.py and the unittest discovery command in STEP 3.
BUDGET    STEP 2 (the body) is the step most likely to overrun — it is the
          only step touching prose that must satisfy every DoD bullet and
          stay evidence-honest at the same time.
OPEN      Whether type: layers is the corpus's eventual settled convention
          for this path, or whether a future taxonomy pass moves every
          layers/data/postgres/* node to implementation — not decided here,
          consistent with audit-tables.md's own disclosed tension. Whether
          moderation_reports and community_bans get their own future
          data-entity nodes, and what their relationship types back to this
          node should be once they exist.
LEFT OUT  No relationship to any unmerged layers/data/postgres/* sibling (all
          such nodes are on unmerged branches at the recorded revision). No
          JSON Schema fragment — moderation_actions has no JSON-typed column.
          No description of moderation_reports or community_bans beyond what
          is needed to state the action_id FK relationship and the scope
          boundary. No production/staging deployment facts (separate private
          repos, out of this task's reach, same limitation audit-tables.md
          records).
