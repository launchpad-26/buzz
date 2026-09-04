# Plan: issue #894 — generate corpus document generated/database-index.md

Issue #894 (launchpad-26/buzz), parent PRD #621.
Stated size: none in the issue body; the #621 batch brief caps this family  ->  cap: 5 steps

Base: local branch `feature/621-generated-traceability` at 0c7f39cf76a1ae6dcfedfaa6a5283855ae286ffd.
Worktree: `__worktrees/task-894-generated-database-index`, branch `task/894-generated-database-index`.

ALREADY TRUE
- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is on the base with ten shipped builders in `index_defs/` (glossary, index,
  decisions-index, api-index, capability-index, code-to-doc-map, concept-index,
  configuration-index, corpus-index, coverage) and per-builder tests; the
  builder contract (module-level SPEC, generate(ctx) -> sections/includes/
  excludes/ordering) is proven by `index_defs/configuration_index.py` and
  `tests/test_index_configuration_index.py`, the closest sibling precedent
  (issue #890) for "check multiple candidate signals, pick the accurate one."
- Signal investigation (per dispatch EXTRA), verified on this base:
  - `templates/datastore.md` (id `corpus-template-datastore`) and
    `templates/data-entity.md` (id `corpus-template-data-entity`) both exist
    on the base and on `origin/launchpad`, both `type: governance`,
    `status: active` — these are the two per-type templates for
    database/schema-shaped corpus nodes.
  - Zero canonical nodes anywhere in the corpus declare a forward
    `implements` edge to either template id (checked by grepping every
    `type: implements` relationship in the corpus) — no node has yet been
    authored *from* either template.
  - Front-matter `type` gives no clean signal: `node.schema.json`'s enum has
    no `database`/`datastore`/`storage` value; `type: architecture` (the type
    a real datastore instance would carry, per `templates/datastore.md`'s own
    evidence ledger) covers 50+ unrelated nodes across
    `architecture/containers/`, `context/`, `deployment/`, `flows/` and
    `principles/`; `type: implementation` (the type a real data-entity
    instance would carry) has zero nodes at all today.
  - Path prefix gives no clean signal either: no `layers/storage/` or
    `layers/database/` subtree exists (`layers/` has only `compute/`,
    `configuration/`, `lifecycle/`, `observability/`); the nearest candidate,
    `architecture/containers/`, holds 10 nodes (postgres, redis,
    object-storage, relay, cli, desktop, mobile, web, agent-runtime,
    push-gateway) — only 3 of which are datastores, so the prefix
    over-includes non-database containers with no field to filter on.
  - `implements -> corpus-template-datastore` OR
    `implements -> corpus-template-data-entity` is therefore the accurate
    signal: it is the only one that does not over-include, and it correctly
    returns zero nodes at this revision rather than guessing from node names.
    An honest empty listing follows, per the dispatch brief's explicit
    allowance ("if the rule matches zero nodes, render an honest empty
    listing... do not widen the rule to look fuller").
  - A deterministic, non-inclusion "watch list" subsection is still useful
    and defensible without loosening the rule: every valid node under
    `architecture/containers/` (the 10 nodes above), shown with whether it
    declares either template's `implements` edge (today: all "no") — this is
    derived purely from front matter, states no subject-matter judgement,
    and makes future drift (a datastore node added without the edge)
    visible the same way configuration-index's divergence subsections do.
- The framework renders all front matter (status: draft, origin: launchpad),
  the do-not-edit marker, the input digest, and the generated-index body
  skeleton; a builder supplies only listing content and inclusion/exclusion
  bullets. `--check --only NAME` verifies no-change reruns.
- Test baseline on the base is 289 tests OK
  (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`).

STEP 1 [independent]  <- RUNS HERE
Write the builder module
`launchpad/project-intelligence/corpus/index_defs/database_index.py`
exposing SPEC: name `database-index`, output `generated/database-index.md`,
node_id `generated-database-index`, node_type `governance` (no subject-type
enum value fits: a real datastore instance would carry `architecture`, a
real data-entity instance would carry `implementation` — two different
types, so this index follows the concept-index/glossary/coverage precedent
of `governance` for a mixed-type subject rather than capability-index's
single-type precedent; docstring must justify this and the rejected
type/path signals above). Inclusion rule: every valid canonical node
declaring a forward `implements` edge whose target is
`corpus-template-datastore` or `corpus-template-data-entity`. Listing table
sorted by path with columns Id | Path | Status | Template implemented — at
this revision zero rows, with explanatory prose stating the rule found no
matches yet (honest empty, not widened). Second subsection: "Architecture
containers watch list" — every valid node under `architecture/containers/`
(path-prefix derived, no name-matching), sorted by path, columns Id | Path |
Implements a database template, all "no" at this revision, framed explicitly
as informational (not part of the index). Relationships:
`references -> corpus-agents`, `implements -> corpus-template-generated-index`,
`references -> corpus-template-datastore`,
`references -> corpus-template-data-entity`.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list`
shows `database-index` and no discovery error.

STEP 2 [needs 1]
Generate the document: `... indexes.py --only database-index` writes
`launchpad/docs/corpus/generated/database-index.md`; never hand-edit it.
Rerun the generator and confirm `git status --porcelain` shows the file
unchanged after the second run; `... indexes.py --check --only
database-index` exits 0.
done when: TARGET exists with front-matter id `generated-database-index`,
type `governance`, an empty primary listing with the stated inclusion rule,
the 10-row architecture/containers watch list, and `--check --only
database-index` exits 0.

STEP 3 [needs 1]
Write `launchpad/project-intelligence/corpus/tests/test_index_database_index.py`
following test_index_configuration_index.py conventions: discovery/identity
test; fixture-corpus tests (a node declaring `implements ->
corpus-template-datastore` is listed; a node declaring `implements ->
corpus-template-data-entity` is listed; a node under
`architecture/containers/` with neither edge appears only in the watch list,
not the primary listing; a node with the edge but outside
`architecture/containers/` is listed in the primary table and not in the
watch list; an invalid node under either path appears nowhere; a corpus with
no matches of any kind renders an honest empty primary listing and an empty
watch list, each saying so rather than omitting the section); two-render
stability; read-only real-corpus smoke test of the committed document's id,
type, do-not-edit marker, and that today's primary listing is genuinely
empty (proving the empty-listing claim rather than assuming it).
done when: from the worktree root, `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p
"test_index_database_index.py"` reports OK with every listed behavior
asserted.

STEP 4 [needs 2, 3]
Full validation and gate: `python3
launchpad/project-intelligence/corpus/validate.py` exits 0 (pre-existing
UNVERIFIED notices tolerated, no new hard errors), then the commit-gate
suite `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` — 289 baseline
tests plus this task's — all OK.
done when: validate.py exit 0 and the full discover run prints OK with
more than 289 tests.

STEP 5 [needs 4]
Self-review the diff against #894's DoD line by line, then commit builder
module + generated TARGET + test + this plan in one signed commit:
`docs(corpus): generate generated/database-index.md (#894)` with a body
naming the inclusion rule and the rejected signals.
done when: `git log -1` shows the signed commit containing exactly those
four files and `git status --porcelain` is clean.

PARALLEL
Steps 2 and 3 are independent of each other once Step 1 lands; everything
else is a chain. This whole task is one worktree in a wider batch — no
cross-worktree coordination is needed because the framework discovers
builders in sorted module order and duplicate names/paths fail loudly.

GATES
- Framework discovery (`--list`) after Step 1.
- Determinism gate after Step 2: second run diff-free plus `--check` exit 0.
- Focused test run after Step 3.
- validate.py + full 289+-test suite after Step 4 (the commit gate).
- Self-review against the DoD checklist before the commit in Step 5.

BUDGET
One builder module (~150 lines), one generated markdown file, one test file
(~150 lines), this plan. Zero edits to indexes.py, validate.py, any shared
file, or any hand-authored corpus node.

OPEN
- Whether a future revision should extend the watch list to
  `layers/observability/datastore-tracing.md` or other datastore-adjacent
  nodes — left to the maintainer once a real pattern of "close but not
  template-implementing" nodes emerges; widening it now on a guess would be
  exactly the "widen the rule to look fuller" the dispatch brief warns against.
- Whether `architecture/containers/postgres.md`, `redis.md` and
  `object-storage.md` should eventually be rewritten from
  `templates/datastore.md` and gain the `implements` edge — a hand-authored
  canonical-node change, out of scope for this generator task.

LEFT OUT
- Adding the missing `implements` edge to any existing container node — that
  edits a hand-authored canonical node, explicitly out of scope for this
  issue.
- A `layers/storage/` or `layers/database/` reorganization of the corpus tree
  — out of scope; this task indexes what exists, it does not restructure it.
- Any second generated document or "while here" cleanup — out of scope per
  the issue.
