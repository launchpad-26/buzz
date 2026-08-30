Issue #1077 — task: document layers/data/postgres/channel-members-table.md
Stated size: no `Size` line  →  cap: 5 steps (batch dispatch brief for Feature #610: "this is one small document")

ALREADY TRUE  (verified against git and the schema, not notes)
  Worktree `__worktrees/task-1077-channel-members-table` is on branch
    `task/1077-channel-members-table`, based on `origin/launchpad`, HEAD
    `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`, working tree clean.
  `launchpad/docs/corpus/layers/data/postgres/channel-members-table.md` does not
    exist on this base — confirmed with a direct `test -f`.
  `node.schema.json`'s `type` enum contains `layers` (and no `table`/`entity` value);
    front matter requires `id, type, status, origin, audiences, evidence` and permits
    `relationships`, rejecting anything else.
  `origin/launchpad`'s `launchpad/docs/corpus` tree carries no `layers/` subtree at
    all yet — every prior `layers/data/...` sibling this batch has produced so far
    lives in an unmerged sibling worktree, so none is a legal `relationships` target
    (a target that does not resolve on the branch being merged into is a hard
    validation error per `AGENTS.md` step 9).
  `launchpad/docs/corpus/templates/datastore.md` documents one whole running
    datastore instance (Postgres/Redis/S3 itself) — its own "Schema / namespace
    inventory" section is a one-line-per-table structural list, explicitly not a
    deep dive on a single table's identity, fields, invariants and relationships.
  `launchpad/docs/corpus/templates/data-entity.md` documents one domain concept and
    requires exactly the sections this issue's own DoD asks for — Identity,
    Attributes and shape, Invariants, Relationships, Provenance, Storage pointer —
    and its own worked illustration (`thread_metadata`) is the same shape as this
    task: one Postgres table treated as one entity. Its "Storage pointer, not
    storage description" section is the explicit boundary against datastore.md:
    name the table and link the datastore node (none merged yet), do not restate
    column types/indexes there.
  The `channel_members` table is defined in `migrations/0001_initial_schema.sql`
    (columns, PK `(community_id, channel_id, pubkey)`, FK to `channels`, the
    `idx_channel_members_pubkey` partial index) and altered by
    `migrations/0029_community_deletion.sql` (`attach_community_write_fence`
    trigger; listed in both `EXPECTED_SCOPED_TABLES` and the FK-ordered
    `PURGE_SCOPED_TABLES` in `crates/buzz-db/src/deletion.rs`).
  `crates/buzz-db/src/channel.rs` (`add_member`, `remove_member`,
    `acquire_channel_membership_lock`, `is_member`, `get_members`,
    `get_member_role`) and `crates/buzz-core/src/channel.rs` (`MemberRole` enum,
    `is_elevated`, `permission_level`) are the read/write code paths and the role
    vocabulary already read this session.
  `crates/buzz-db/src/dm.rs` (`hide_dm`/`unhide_dm`) is the only code touching
    `hidden_at`, and it is scoped to DM-type channels only.

STEP 1  [independent]  ← RUNS HERE  Read `crates/buzz-db/src/channel.rs` in full
        around `add_member`/`remove_member`/`get_member_role`/`get_members_bulk`,
        `crates/buzz-core/src/channel.rs`'s `MemberRole`, and
        `crates/buzz-db/src/dm.rs`'s `hide_dm`/`unhide_dm`, to confirm the lifecycle
        (soft-delete via `removed_at`/`removed_by`, role-change authorization,
        last-owner protection, DM-specific `hidden_at`) and capture the exact line
        citations the node's evidence ledger will use.
        done when: every claim planned for the node's Identity, Attributes,
        Invariants, Relationships and Provenance sections has a specific file (and,
        where useful, symbol) it will cite, recorded in this session's notes.

STEP 2  [needs 1]  Write the front matter: `id:
        layers-data-postgres-channel-members-table`, `type: layers` (overriding
        data-entity.md's own "type: implementation" suggestion for a real instance,
        per this batch's established precedent for every `layers/data/...` sibling
        so far — the tension is disclosed in the evidence ledger, not silently
        resolved), `status: draft`, `origin: launchpad`, `audiences: [agent,
        developer, reviewer]`, no `relationships` (no sibling `layers/` node is
        merged on `origin/launchpad` yet, confirmed above).
        done when: the file exists with schema-valid front matter only (body still
        empty or stubbed) and a YAML parse reports `id`, `type: layers`, `status:
        draft` and no `relationships` key.

STEP 3  [needs 2]  Write the body against `data-entity.md`'s six required sections
        (Identity, Attributes and shape, Invariants, Relationships, Provenance,
        Storage pointer) using STEP 1's citations, plus a Scope-and-omissions
        section naming the datastore-mechanics boundary (column-level storage
        detail belongs to a future `layers/data/postgres` datastore node, not
        repeated here) and anything expected but not verified (e.g. no merged
        sibling node to link `part-of`/`references` against yet).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0 and every one of the six required sections is present as a `##`
        heading in the file.

STEP 4  [needs 3]  Self-review the finished node against the issue's own DoD
        checklist line by line and against `validate.py`'s output; confirm every
        evidence entry cites a source actually opened in STEP 1, no second
        hand-authored corpus document was created, and the `type: layers` deviation
        from the template's own suggestion is stated plainly in the ledger.
        done when: `validate.py` exits 0 and a written line-by-line note maps each
        DoD bullet to the section/evidence entry that satisfies it.

STEP 5  [needs 4]  Run the corpus test suite as the sole, unpiped command
        (verify-gate stamp), confirm `OK`, then in a separate call stage and commit
        the plan and the node with `git commit -s`.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK as
        its own standalone invocation, and `git log --format=%B -1` shows a
        `Signed-off-by:` trailer and references `(#1077)`.

PARALLEL  None. Steps 2, 3 and 4 all edit the same single file; STEP 1 gathers the
          evidence STEP 2/3's ledger cites and must finish first. No step is
          dispatched as an independent subagent.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
          before commit. `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report
          OK, run bare and unpiped, before commit. This task's own brief explicitly
          defers `review-adjudicate` and a cross-model final pass to the batch
          owner's later review — not run in this session; a same-model self-review
          (STEP 4) substitutes.

BUDGET    STEP 3. The hard part is the Identity/Provenance split for a table with a
          non-trivial soft-delete and per-DM-hide lifecycle layered on one composite
          primary key, not the section count.

OPEN      Whether a future merged `layers/data/postgres` *datastore*-level sibling
          node should carry the `part-of`/`references` edges data-entity.md's own
          "Relationships an instance node should consider" section describes, or
          whether this entity-level node should instead. Left for whoever authors
          that sibling, since it does not exist yet and no edge from this node can
          resolve today regardless.

LEFT OUT  Any `relationships` edge — no sibling `layers/` node is merged on
          `origin/launchpad` at this revision, confirmed directly
          (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
          during planning), so none would resolve. Column-level storage mechanics
          (data types, index internals, migration ordering beyond naming the two
          migration files) — `data-entity.md`'s own boundary reserves that for a
          future datastore-level node, not this entity-level one. Any change to
          runtime product behavior or to a second hand-authored corpus document, per
          the issue's own Out of scope section.
