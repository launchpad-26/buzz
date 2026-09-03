Issue #898 — generate launchpad/docs/corpus/generated/documentation-graph.md
Stated size: one generated document + minimal builder/test (batch task)  ->  cap: 5 steps

Base: local branch feature/621-generated-traceability (15 builders merged: glossary,
index, decisions-index, api-index, capability-index, code-to-doc-map, concept-index,
configuration-index, corpus-index, coverage, crate-index, database-index,
decision-index, dependency-graph, doc-to-code-map). Worktree
__worktrees/task-898-generated-documentation-graph, branch
task/898-generated-documentation-graph.

ALREADY TRUE
- generated/dependency-graph.md (#896, merged, index_defs/dependency_graph.py) already
  renders every forward relationship edge (all 5 schema types: references,
  implements, depends-on, part-of, supersedes), the 4 derived generated-inverse
  views, broken edges, and orphaned nodes -- one row per edge/inverse-pair. A
  documentation-graph.md that repeats that same edge listing would be a
  near-duplicate; this plan must state a genuinely distinct angle.
- templates/generated-index.md's own boundary table (line 184) already classifies
  documentation-graph.md (#898) as "A graph -- Same reason as dependency-graph.md",
  so this document stays graph-shaped (uses ctx.forward_edges as its underlying
  data) but must render that data at a different granularity/shape than
  dependency-graph.md's per-edge table -- the same "same source data, different
  shape" relationship decision-index.md (#895, stats/bucket view) already holds
  against decisions-index.md (#845, per-record citing-node listing), and
  corpus-index.md (#891, stats view) holds against the corpus INDEX (#638, full
  listing). Neither of those pairs restates the other's content; each states the
  distinction in its own body section.
- Measured directly against the real corpus (build_context run in-worktree,
  launchpad/docs/corpus root): 205 valid nodes, 192 resolved forward edges
  (references 167, implements 17, depends-on 6, part-of 2, supersedes 0), 0 broken
  edges, 81 orphans (zero in+out degree). part-of has only 2 edges corpuswide, too
  thin to carry a whole document as a part-of-only tree rendering (candidate angle
  b, considered and rejected below). Of the 205 nodes, 124 have nonzero total
  degree and 81 have zero.
- Chosen angle (candidate c from the dispatch EXTRA): a per-node degree/
  connectivity summary -- which nodes are structural hubs (highest in+out degree)
  and how connectivity is distributed -- computed from the identical
  ctx.forward_edges dependency-graph.md already renders per-edge, but summarized
  per-node instead of per-edge. This is "true" (the data supports a real hub/leaf
  spread: architecture-containers-relay has in-degree 29, corpus-agents has
  in-degree 15, vs. 81 nodes at degree 0) and "useful" (a reader asking "which
  corpus documents are most load-bearing" gets an answer dependency-graph.md's flat
  edge table does not surface directly). Degree is computed independently in this
  builder from ctx.forward_edges (resolved edges only, matching dependency-graph.md's
  own scope) -- no new graph-derivation logic is added to indexes.py.
- Leaf/zero-degree nodes are NOT re-listed here in full: at the current revision
  the zero-total-degree set computed by this builder is set-identical to
  ctx.orphans (81 == 81, verified directly), and dependency-graph.md's own
  "Orphaned nodes" section already lists them one row per node with path. This
  document states the count and cross-references that section by name instead of
  duplicating the listing -- the same "don't duplicate canonical content" instinct
  code-to-doc-map/coverage/decision-index already apply to their own overlaps. A
  documented caveat (not_covered/unverified) notes the one case where the two sets
  could theoretically diverge: ctx.orphans excludes a node with a broken outgoing
  edge (has_out counts broken sources too), while this builder's resolved-only
  degree would still show 0 for that node -- 0 broken edges exist at this revision
  so the sets coincide today, but a future broken edge could open a gap.

STEP 1  [independent]  Builder module   <- RUNS HERE
Write launchpad/project-intelligence/corpus/index_defs/documentation_graph.py
exposing SPEC (name "documentation-graph", output
generated/documentation-graph.md, node_id generated-documentation-graph, node_type
governance -- same corpus-about-corpus-traceability reasoning dependency-graph.md
already gives, justified in the module docstring). generate(ctx) computes, from
ctx.forward_edges alone (no new ctx field, no filesystem read beyond what ctx
already loaded):
  - per-node in_degree/out_degree/total_degree dict over every ctx.node_ids entry.
  - "## Distinction from `generated/dependency-graph.md`" section (required,
    rendered first): states in prose that dependency-graph.md is the per-edge raw
    listing and this document is the per-node degree/connectivity summary over the
    identical forward-edge data, naming both documents and the decision-index.md /
    decisions-index.md precedent for the pattern.
  - "## Connectivity summary": total valid nodes, total resolved forward edges,
    a small by-type count table (reusing ctx.forward_edges type counts, not the
    full per-edge listing), nodes with degree > 0 vs. degree == 0.
  - "## Hub nodes (highest total degree)": every node with total_degree > 0, one
    row (id, path, in-degree, out-degree, total degree), sorted
    (-total_degree, node_id) -- deterministic, no arbitrary top-N cutoff.
  - "## Leaf nodes (zero degree)": states the zero-total-degree count and
    cross-references dependency-graph.md's "Orphaned nodes" section by name
    instead of re-listing; notes the resolved-degree-vs-orphans caveat above.
extra_evidence states the degree computation and the 0-broken-edges caveat at the
input digest. Relationships: references -> corpus-agents only (implements ->
corpus-template-generated-index omitted, identical reasoning to dependency-graph.md
-- the template's own boundary table names this document a graph, outside
index-shaped scope).
done when: python3 launchpad/project-intelligence/corpus/indexes.py --list shows
documentation-graph alongside the 15 existing builders.

STEP 2  [needs 1]  Generate + stability
Run --only documentation-graph to write the target; rerun and confirm git status
shows no second change; run --check --only documentation-graph.
done when: target file exists, second run leaves it byte-identical, --check exits 0.

STEP 3  [needs 1]  Focused test
launchpad/project-intelligence/corpus/tests/test_index_documentation_graph.py,
following test_index_dependency_graph.py's self-contained-temp-corpus shape:
discovery/identity assertions (output path, node_id, node_type, relationships);
two-run byte-identity; a small fixture corpus with (a) a hub node targeted by two
distinct sources (renders with total_degree 2 in the hub table, ranked above a
degree-1 node), (b) a node with zero in/out edges (counted in the leaf section,
not itemized), (c) mixed edge types from one source (both counted toward degree
regardless of type); front matter carries generated-documentation-graph +
governance; the Distinction section names both this document and
dependency-graph.md.
done when: python3 -m unittest discover over corpus/tests passes the new test file.

STEP 4  [needs 2, 3]  Validate + full suite
python3 launchpad/project-intelligence/corpus/validate.py exits 0 (pre-existing
UNVERIFIED notices tolerated); full unittest discover over corpus/tests passes
(baseline 225 + prior batch siblings' additions + this task's new tests).
done when: both commands exit 0 in the worktree.

STEP 5  [needs 4]  Commit
git add builder, generated file, test, this plan; git commit -s with the issue
number and the inclusion rule named in the body.
done when: one signed commit on task/898-generated-documentation-graph contains
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
- One builder module (~180 lines, degree computation only -- no new ctx field),
  one generated markdown (size scales with 205 nodes: a ~124-row hub table plus
  summary text, smaller than dependency-graph.md's 192-edge-plus-inverse-views
  document), one test file (~120 lines), this plan. No shared file touched.

OPEN
- Whether the full hub table (every node with degree > 0, ~124 rows at this
  revision) reads better as a complete deterministic listing or a curated top-N --
  chose the complete listing to avoid an arbitrary cutoff, consistent with the
  framework's own "never hide data behind a threshold" instinct for broken
  edges/orphans.

LEFT OUT
- Re-listing every zero-degree node with its path: dependency-graph.md's Orphaned
  nodes section already owns that full listing; this document states the count
  and cross-references it instead of duplicating.
- A references+part-of-only narrower graph (candidate angle a from the dispatch
  EXTRA): considered and rejected -- it would still be an edge-shaped listing,
  just filtered, which risks the same near-duplicate shape the EXTRA specifically
  warned against; the degree-summary angle changes shape, not just scope.
- A part-of-nesting tree rendering (candidate angle b): considered and rejected --
  only 2 part-of edges exist corpuswide at this revision, too thin to carry a
  whole document; noted as a fact in ALREADY TRUE rather than forced into the
  design.
- Transitive/indirect connectivity (e.g. two-hop reachability): only direct
  ctx.forward_edges degree is computed; stated as a not_covered bullet.
