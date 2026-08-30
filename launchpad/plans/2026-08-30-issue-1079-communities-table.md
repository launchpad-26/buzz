Issue #1079: document layers/data/postgres/communities-table.md

Stated size: one small hand-authored corpus document -> cap: 5 steps

ALREADY TRUE

- Repo is at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on
  origin/launchpad, checked out in worktree
  __worktrees/task-1079-communities-table on branch
  task/1079-communities-table.
- launchpad/docs/corpus/layers/data/postgres/communities-table.md does not
  exist yet (launchpad/docs/corpus/layers/data/postgres/ doesn't exist at
  all).
- node.schema.json's type enum has 13 members including layers; no
  datastore/data-entity/template member exists.
- Two candidate templates exist: templates/datastore.md (one running
  technology instance) and templates/data-entity.md (one domain concept --
  identity, attributes, invariants, relationships, provenance, storage
  pointer). The issue's own Objective calls this "the single canonical data
  entity node for communities table" and its DoD bullets (identity/key,
  fields by meaning without duplicating generated schema,
  relationships/lifecycle/invariants, links to migration/schema and
  read/write code) map onto data-entity.md's six required sections almost
  exactly. data-entity.md's own reasoning suggests type: implementation for a
  real instance; datastore.md suggests type: architecture. Per the dispatch
  brief, this batch's established precedent overrides either suggestion with
  type: layers for consistency, and that tension is disclosed in the
  evidence ledger rather than silently resolved.
- architecture-containers-postgres (status: draft) exists on origin/launchpad
  and is a reasonable part-of target -- it is buzz-db's Postgres container
  node.
- No sibling layers/data/postgres/* node exists on origin/launchpad yet
  (unmerged sibling worktrees), so no references/part-of edge to a sibling
  table node is possible today.
- Evidence already gathered by direct inspection this session: the
  communities table definition and every later ALTER TABLE communities
  across migrations/0001, 0003, 0016, 0029, 0030; the row-zero/
  operator-global schema comments; the _operator_global_tables registry row
  naming communities "the tenant registry itself; id IS the community key";
  every buzz-db/src/lib.rs method reading/writing communities
  (lookup_community_by_host, lookup_community_by_host_for_management,
  is_community_active, list_communities_owned_by, lookup_community_host,
  get_community_icon/set_community_icon, ensure_configured_community,
  create_community_with_owner, archive_community_owned_by,
  unarchive_community_owned_by); the deletion pipeline's final tombstone
  UPDATE in buzz-db/src/deletion.rs (nulls signing_key/icon); the Postgres
  write-fence functions in 0029_community_deletion.sql
  (community_write_allowed, assert_community_write_allowed,
  enforce_community_write_fence, enforce_community_tombstone) that key off
  communities.deletion_state/deletion_fence_generation; and that signing_key
  has no production write path today (only nulled on deletion, set only in
  one test fixture).

STEP 1 [independent] -- Write the corpus node <- RUNS HERE
Create launchpad/docs/corpus/layers/data/postgres/communities-table.md with:
- Front matter: id: layers-data-postgres-communities-table, type: layers,
  status: draft, origin: launchpad, audiences: [agent, developer, operator,
  reviewer], one part-of relationship to architecture-containers-postgres.
- Provenance entry citing commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5.
- Body sections adapted from data-entity.md's required shape to one table:
  Purpose & scope, Identity, Attributes and shape (by meaning, not restating
  column types), Relationships (code-level FKs/joins and corpus-level
  edges), Lifecycle & invariants (deletion state machine + write-fence),
  Migration history (all five migrations that touched the table), Access
  patterns (the buzz-db methods above, one row each), Scope and omissions
  (naming the type tension per taxonomy.md, the datastore-template boundary,
  and anything not verified).
- Every claim gets a provenance-ledger entry classified FACT/INFERENCE/
  TEAM_KNOWLEDGE per AGENTS.md / standards/evidence.md.
done when: the file exists, its YAML front matter parses, and every DoD
bullet in issue #1079 has a corresponding section in the body.

STEP 2 [needs 1] -- Validate
Run python3 launchpad/project-intelligence/corpus/validate.py from the
worktree root. Fix any schema violation, broken relationship target, or
unresolved evidence path; re-run until exit 0.
done when: the validator exits 0.

STEP 3 [needs 2] -- Earn the commit gate
Run, as a bare standalone command (no pipe):
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
done when: the suite reports OK with exit status 0.

STEP 4 [needs 3] -- Commit
git add the plan file and the new corpus doc; git commit -s with a
docs(corpus): message referencing #1079.
done when: exactly one new commit exists ahead of origin/launchpad (a second
small fix-up commit is acceptable if git-safety.sh blocks amend/reset).

STEP 5 [needs 4] -- Self-review
Re-diff against origin/launchpad, walk the issue's DoD checklist line by
line, re-check each evidence entry actually supports its claim, confirm
validate.py still exits 0, confirm no second hand-authored corpus document
was created. No push, no PR.
done when: every DoD bullet is confirmed satisfied against the actual diff,
and validate.py exit 0 is re-confirmed after any fix.

PARALLEL

None -- this is a single small document with no independent sub-tasks; steps
run strictly in sequence.

GATES

- python3 launchpad/project-intelligence/corpus/validate.py exits 0.
- python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" reports OK (bare command, unpiped).

BUDGET

Single small document, capped at 5 steps as instructed. No code changes, no
test-infrastructure changes.

OPEN

- Whether type: layers (batch precedent) or type: implementation
  (data-entity.md's own reasoning) is the eventually-correct enum value is
  unsettled corpus-wide; this node follows the established batch precedent
  and discloses the tension rather than resolving it unilaterally.
- Whether signing_key is dead/reserved code or an intentionally unused
  column awaiting a future feature is not established anywhere found this
  session; named as a gap in the node's Scope and omissions rather than
  guessed at.

LEFT OUT

- No relationships to sibling layers/data/postgres/* table nodes -- none are
  merged to origin/launchpad yet.
- No edit to any other corpus file, migration, or Rust source -- this is a
  documentation-only change per the issue's own Out of scope list.
