Issue #896 — generate launchpad/docs/corpus/generated/dependency-graph.md
Stated size: one generated document + minimal builder/test (batch task)  ->  cap: 5 steps

Base: local branch feature/621-generated-traceability (10 builders merged: glossary,
index, decisions-index, api-index, capability-index, code-to-doc-map, concept-index,
configuration-index, corpus-index, coverage). Worktree
__worktrees/task-896-generated-dependency-graph, branch
task/896-generated-dependency-graph.

ALREADY TRUE
- The #633 framework (launchpad/project-intelligence/corpus/indexes.py) already
  computes everything this document needs: `ctx.forward_edges` (Edge(source, type,
  target), sorted), `ctx.inverse_edges` (the four generated-inverse views --
  depended-on-by, superseded-by, implemented-by, has-part -- {target: sorted
  sources}, computed by build_context from the forward edges), `ctx.broken_edges`
  (BrokenEdge(source, type, target) for a declared target resolving to no known
  id, sorted, reported never raised), and `ctx.orphans` (sorted ids of valid nodes
  with no in- or out-edge). No new graph-derivation code is needed; the builder
  only renders what ctx already carries.
- templates/generated-index.md's own boundary table names dependency-graph.md
  (#896) explicitly as a GRAPH ("edges between nodes, not a flat listing"), so the
  framework's index-shaped body skeleton is reused (front matter, do-not-edit
  marker, Generator/Inclusion-exclusion/Relationships/Scope sections) but the
  listing content (`sections`) is graph-shaped, not table-of-contents-shaped --
  the dispatch EXTRA's own instruction, and the code-to-doc-map (#888) and
  coverage (#892) builders are the precedent for a non-index-shaped sibling
  reusing the same framework honestly (see their module docstrings).
- relationships.schema.json's `relationshipMeta` marks exactly four of the five
  forward types generated-inverse (depends-on->depended-on-by,
  supersedes->superseded-by, implements->implemented-by, part-of->has-part);
  `references`'s inverse (referenced-by) is `authored`, so the framework never
  computes it and ctx.inverse_edges has no key for it.
- Measured against the real corpus at this revision (build_context run directly):
  205 valid nodes, 192 forward edges (references 167, implements 17, depends-on 6,
  part-of 2, supersedes 0), 0 broken edges, 81 orphans. depended-on-by/
  implemented-by/has-part each have a handful of distinct targets; superseded-by
  is empty. The dispatch EXTRA says use ctx.forward_edges (unfiltered) as the
  source, so all five forward types are graphed, not a "depends-on only" subset
  -- a depends-on-only reading would yield a 6-row document, which the EXTRA's own
  "as your source" phrasing does not support.
- tests/fixtures/indexes/broken/ already has a worked node-broken-a.md
  (depends-on -> nonexistent target) and node-orphan.md (no edges) precedent for
  what a broken/orphan fixture node looks like, though this task writes its own
  self-contained temp-corpus fixtures (code-to-doc-map's pattern) rather than
  reusing that shared directory, since no builder test currently does.

STEP 1  [independent]  Builder module   <- RUNS HERE
Write launchpad/project-intelligence/corpus/index_defs/dependency_graph.py exposing
SPEC (name "dependency-graph", output generated/dependency-graph.md, node_id
generated-dependency-graph, node_type governance -- corpus-about-corpus
traceability machinery, no subject-specific enum value fits a graph over the
corpus's own relationships any better than it fits code-to-doc-map/coverage;
justified in the module docstring alongside the all-forward-types reading of
"dependency graph" and why it is not filtered to depends-on only).
generate(ctx) renders four labeled subsections from ctx alone, no new derivation:
  - "Forward edges (authored)": one row per ctx.forward_edges entry (source, type,
    target), honest empty message if none.
  - "Derived inverse edges (generated, not authored)": one sub-table per
    ctx.inverse_edges key in sorted order (depended-on-by, has-part,
    implemented-by, superseded-by), each row target -> sorted source list,
    explicitly labeled as computed by the framework, never hand-authored; notes
    that references' inverse (referenced-by) is authored per schema and is
    therefore not computed or rendered here.
  - "Broken edges": always rendered, one row per ctx.broken_edges entry
    (source, type, declared target), or an explicit "none at this revision, N
    forward edges checked" line -- never omitted even when empty, per Feature
    #621's acceptance criterion that unresolved relationships stay visible.
  - "Orphaned nodes": one row per ctx.orphans id (with ctx.rel_path for
    findability), or an explicit empty line -- same #621 criterion, which names
    orphaned nodes directly.
extra_evidence states the forward/inverse/broken/orphan counts at the input
digest. Relationships: references -> corpus-agents only -- implements ->
corpus-template-generated-index deliberately omitted, since the template's own
boundary table classifies dependency-graph.md as a graph outside its scope (same
reasoning code-to-doc-map and coverage already used for their own omission).
done when: python3 launchpad/project-intelligence/corpus/indexes.py --list shows
dependency-graph alongside the ten existing builders.

STEP 2  [needs 1]  Generate + stability
Run --only dependency-graph to write the target; rerun and confirm git status
shows no second change; run --check --only dependency-graph.
done when: target file exists, second run leaves it byte-identical, --check exits 0.

STEP 3  [needs 1]  Focused test
launchpad/project-intelligence/corpus/tests/test_index_dependency_graph.py in
code-to-doc-map's shape (self-contained temp corpus, no shared fixture dir):
discovery/identity assertions; two-run byte-identity; a small fixture corpus with
(a) a depends-on edge and a references edge between two real nodes (forward rows
for both, inverse row only for depends-on's depended-on-by), (b) a relationship
target that resolves to nothing (broken-edges row, not a crash), (c) a node with
no relationships in or out (orphaned-nodes row); front matter carries
generated-dependency-graph + governance; broken/orphan sections render their
explicit empty message when a fixture corpus has none of either.
done when: python3 -m unittest discover over corpus/tests passes the new test file.

STEP 4  [needs 2, 3]  Validate + full suite
python3 launchpad/project-intelligence/corpus/validate.py exits 0 (pre-existing
UNVERIFIED notices tolerated); full unittest discover over corpus/tests passes
(baseline 225 + prior batch siblings' additions + this task's new tests).
done when: both commands exit 0 in the worktree.

STEP 5  [needs 4]  Commit
git add builder, generated file, test, this plan; git commit -s with the issue
number and the inclusion rule named in the body.
done when: one signed commit on task/896-generated-dependency-graph contains
exactly those files.

PARALLEL
- None within this task; steps 2 and 3 both need step 1 but can run in either
  order. Batch-level parallelism is between sibling worktrees, not here.

GATES
- Commit gate: full unittest discover as the sole command in its own Bash call
  (brief §7) before git add/commit.
- Self-review (batch mode): diff re-read against the issue DoD line by line; no
  separate review-code pass.

BUDGET
- One builder module (~150 lines, no new graph-derivation logic -- ctx already
  carries everything), one generated markdown (size scales with the real corpus's
  192 forward edges + inverse views + 81 orphans, a few hundred lines), one test
  file (~130 lines), this plan. No shared file touched.

OPEN
- Whether a reader can distinguish "genuine authoring mistake" from "sibling node
  not yet merged" for a broken edge or orphan -- left to the reader per the
  not_covered bullet; this document surfaces the finding, not the diagnosis.

LEFT OUT
- implements -> corpus-template-generated-index edge: same reasoning code-to-doc-
  map and coverage already used -- the template's own boundary table names this
  document as a graph, not index-shaped, so claiming to implement it would
  contradict the template's own text.
- Transitive/indirect dependency paths (A depends-on B depends-on C implying
  something about A and C): only direct declared edges are graphed; stated as a
  not_covered bullet, not computed here.
- A depends-on-only narrower reading of "dependency graph": considered and
  rejected -- the dispatch EXTRA says use ctx.forward_edges (unfiltered) as the
  source, and a depends-on-only document would be 6 rows against the real corpus,
  too thin against the EXTRA's own phrasing.
- Filtering by node type/audience/path prefix: relationships are graphed
  regardless of the endpoints' own type or audience, since the graph's subject is
  the corpus's declared relationship structure itself, not a subset of nodes.
