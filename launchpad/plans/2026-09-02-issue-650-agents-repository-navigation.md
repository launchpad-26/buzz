# Issue #650 — agents/repository-navigation.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`
(id `corpus-agents`), `launchpad/docs/corpus/agents/invariants.md` (id `agents-invariants`),
and `launchpad/docs/corpus/templates/procedure.md` (id `corpus-template-procedure`, `status:
active`) are merged on `origin/launchpad` — confirmed via `git show origin/launchpad:<path>`.
`launchpad/docs/corpus/agents/repository-navigation.md` does not exist yet (confirmed by
`test -f`). A fresh `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` (run
in this task, not copied from the brief) shows the corpus tree is larger than the task brief's
"real right now" list: `capabilities/**`, `layers/**`, and `development/**` are merged too
(build.md, debugging.md, hermit.md, prerequisites.md), alongside `AGENTS.md`, `README.md`,
`agents/invariants.md`, `architecture/**`, `standards/*.md`, `templates/*.md`. None of these
overlaps this node's subject on inspection (`development/*.md` covers running builds/tooling,
not navigating the repo to gather authoring evidence) and none is another sibling `agents/*.md`
or `ingestion/*.md` task under Feature #620 — so the brief's "no sibling relationship target"
conclusion still holds, verified independently rather than trusted. Sibling `#644`
(`agents/corpus-usage.md`, local commit only, unmerged) already drew this node's boundary from
its own side: it covers finding/traversing *within* `launchpad/docs/corpus/` itself; this node
covers navigating the *wider* repository (`crates/`, `desktop/`, `web/`, `mobile/`,
`migrations/`, `launchpad/`) to find the source an agent cites as evidence. `check-plan.sh` does
not exist anywhere in this worktree (confirmed by `find`), consistent with the brief.

STEP 1  Gather evidence: exercise real navigation across the wider repository, not describe it
abstractly. Already run in this session: `git grep -n descendant_count -- crates/` (traces one
concept — thread counters — across three files/two crates: `buzz-core/src/kind.rs`'s doc
comment, `buzz-db/src/store/thread.rs`'s increment/decrement logic, `buzz-db/src/store/event.rs`'s
deletion-path decrement); `git log --oneline -- crates/buzz-db/src/store/thread.rs` (one commit,
looks like the whole history); `git log --follow --oneline` on the same path (reveals five more
commits hidden by a file rename, back to the original `crates/sprout-db/src/thread.rs`); `git log
--oneline --diff-filter=R --follow` (isolates the two rename commits themselves: PR #958 "rename
sprout backend to buzz" and PR #6987 "extract domain stores from database runtime"); `git blame
-L` on the same range (attributes current lines but names the pre-rename path in its own output);
`grep -rn descendant_count migrations/*.sql` (finds the column's origin in
`migrations/0001_initial_schema.sql`); `grep -n '#\[tokio::test\]' crates/buzz-db/src/store/thread.rs`
(finds inline `mod tests` — this crate's tests live beside the code, not in a sibling
`tests/` directory, unlike `crates/buzz-test-client/tests/`); `git grep -n "function
resetCommunityState"` (locates a TS symbol CLAUDE.md names, in `desktop/src/features/communities/
useCommunityInit.ts`). Also attempted `mcp__repoql__explore`/`query` scoped to `crates/**` — both
failed with "DuckDB ... database was invalidated by an earlier fatal failure", confirmed
persistent by `command(command="host status")` (large dirty/discovered counts, an active sweep)
and a second failed `query` call — an honestly-timestamped observation for the node, not
resolved here (`host restart` is a shared side-effect out of this task's scope). ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `agents-repository-navigation`, type
`agent` — same reasoning as `agents-invariants` and `agents-corpus-usage`: this node's subject is
the same corpus surface `AGENTS.md` documents, not the `standards/`/`templates/` governance
family; status `draft`; origin `launchpad`; audiences `[agent, developer, reviewer]`;
relationships `depends-on: corpus-agents` (this node's authority for *why* an agent must inspect
real sources before citing them in step 3's ledger is `AGENTS.md`'s own "Creating a node" step 3,
not original to this node) and `implements: corpus-template-procedure` (this node is a how-to
instance of that template, its own "should declare implements" guidance) — both resolve on
`origin/launchpad`) and the body as a `templates/procedure.md`-shaped how-to: Overview — using
`git grep`/`git log`/`git blame`/RepoQL to find the source paths, symbols, tests, migrations, and
configuration an agent cites as evidence when authoring or reviewing a corpus claim, grounded in
CLAUDE.md's "Repo Structure" crate/directory map. Task 1: locating a symbol/concept across the
repository and its tests (the `descendant_count` walk from STEP 1, generalized into steps).
Task 2: reading a symbol's real history through a rename (the `--follow`/`--diff-filter=R`
technique). Task 3: RepoQL as a faster alternative when reachable, with this session's own
failure honestly cited as a live-instance condition, not a permanent property. Boundary section
naming: not corpus-internal search/traversal (`#644`, discussed only to state the boundary since
it is unmerged), not authoring/updating/retiring a node (`AGENTS.md`), not the MUST/SHOULD
invariants list (`agents-invariants`), not a reference-shaped catalog of every RepoQL verb (no
such node exists in this Feature; keep proportionate, per `procedure.md`'s own warning against
reference-style completeness in a how-to).

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command to earn the verification stamp, confirm `OK`, then commit in
a separate call. Attempt `Skill(review-code)`/`serina:review-code`; if unreachable, self-review
the diff against issue #650's DoD line by line. No push, no PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The unittest
discovery command must print `OK` before the commit. `review-adjudicate` and the cross-model
final review pass are deferred to the batch owner's later integration, per sibling precedent
(`#644`, `#698`) — not run here.

BUDGET: small — one document, no product code changes. Evidence gathering scoped to `AGENTS.md`,
`templates/procedure.md`, `agents/invariants.md`, `node.schema.json`, CLAUDE.md's Repo Structure
table, a handful of real `git grep`/`git log`/`git blame`/`grep` commands against `crates/`,
`desktop/`, and `migrations/`, and the RepoQL tool calls already run in STEP 1.

OPEN: `check-plan.sh` does not exist anywhere in this worktree — proceeding without it, reported
here as the brief instructed. RepoQL's `explore` and `query` both returned a fatal "database was
invalidated by an earlier fatal failure" error in this session, confirmed non-transient by a
`host status` check and a repeat failure — reported in the node as a timestamped observation, not
silently retried past or smoothed over, and no `host restart` issued (a shared side-effect outside
this task's scope). Whether `#644`'s eventual merged text draws the corpus-usage/repository-
navigation boundary identically to how this node draws it from its own side is unverified —
`#644` is a local, unmerged commit as of this writing.

LEFT OUT: No relationships to any unmerged sibling `agents/*.md` or `ingestion/*.md` node
(confirmed absent from `origin/launchpad`'s corpus tree by this task's own `git ls-tree`) —
including no edge to `#644`, whose content was read for boundary-drawing only, not cited as a
merged dependency. No attempt to catalog every RepoQL tool/verb/modifier or every crate in
`crates/` — the worked examples in Tasks 1-2 demonstrate the technique on real symbols rather than
enumerating the whole tree, per `procedure.md`'s own warning against reference-style
completeness. No fix to the RepoQL host's fatal DB state — reported, not resolved, here.
