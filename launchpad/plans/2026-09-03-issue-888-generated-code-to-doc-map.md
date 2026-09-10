Issue #888 — generate launchpad/docs/corpus/generated/code-to-doc-map.md
Stated size: one generated document + minimal builder/test (batch task)  ->  cap: 5 steps

Base: local branch feature/621-generated-traceability (5 builders merged: glossary,
index, decisions-index, api-index, capability-index). Worktree
__worktrees/task-888-generated-code-to-doc-map, branch task/888-generated-code-to-doc-map.

ALREADY TRUE
- The #633 framework (launchpad/project-intelligence/corpus/indexes.py) discovers
  builder modules in index_defs/, renders front matter + the generated-index body
  skeleton, computes the input digest, and exposes GenerationContext with all
  canonical nodes (validate.py's own discovery contract).
- Five builders and their tests exist as worked examples; api_index.py +
  test_index_api_index.py are the closest precedent (temp-corpus fixtures,
  discovery assertions, byte-identical double run).
- The corpus holds 200+ valid nodes whose front-matter evidence[].evidence
  citations were surveyed: 2176 distinct path-shaped citations (bare paths plus
  `path:N` / `path:N-M` line suffixes), 195 tool-result/prose strings, 100 URLs,
  10 bare `commit <sha>` refs. Prototyping the inclusion rule below yields 2010
  (code path, node id) pairs over 649 distinct paths and 202 nodes; every
  path-shaped citation in the current tree resolves to a real file.
- The file-size ratchet only covers desktop trees (desktop/scripts/
  check-file-sizes.mjs rules), so a ~2100-line generated markdown is safe.

STEP 1  [independent]  Builder module   <- RUNS HERE
Write launchpad/project-intelligence/corpus/index_defs/code_to_doc_map.py exposing
SPEC (name "code-to-doc-map", output generated/code-to-doc-map.md, node_id
generated-code-to-doc-map, node_type governance — rows are repository files, not
corpus nodes of one subject type, so this is corpus-about-corpus traceability,
the README/standards precedent; justified in the module docstring).
Deterministic inclusion rule, applied to every valid canonical node's
evidence[].evidence citation strings:
  - reject any citation containing whitespace, "(", ")" or "->" (tool-result /
    prose shapes, including "commit <sha>" refs, which carry a space);
  - reject any citation containing "://" (URLs);
  - strip one trailing ":N" or ":N-M" line suffix; reject if a colon remains;
  - reject absolute paths and paths with ".." components;
  - reject paths under launchpad/docs/corpus/ (doc-to-doc, not code) and under
    launchpad/decisions/ (decision records, covered by the decisions index);
  - keep only paths that resolve to a real regular file under the repo root
    (validate.repo_root(), via the corpus_validate module the framework loads).
Emit one table row per distinct (code path, node id) pair, sorted by code path
then node id; honest empty message if zero pairs. extra_evidence states the pair
/ path / node counts at the input digest. Relationships: references ->
corpus-agents only — implements -> corpus-template-generated-index is
deliberately omitted because that template's own boundary table names
doc-to-code-map-style mappings as outside its scope (see LEFT OUT).
done when: python3 launchpad/project-intelligence/corpus/indexes.py --list shows
code-to-doc-map alongside the five existing builders.

STEP 2  [needs 1]  Generate + stability
Run --only code-to-doc-map to write the target; rerun and confirm git status
shows no second change; run --check --only code-to-doc-map.
done when: target file exists, second run leaves it byte-identical, --check exits 0.

STEP 3  [needs 1]  Focused test
launchpad/project-intelligence/corpus/tests/test_index_code_to_doc_map.py in
test_index_api_index.py's shape: discovery/identity assertions; two-run
byte-identity on a temp corpus; inclusion behaviour on fixture nodes citing (a) a
real repo file (kept), (b) a corpus-internal path, (c) a launchpad/decisions/
path, (d) a URL, (e) a "commit <sha>" ref, (f) a tool-result string, (g) a
nonexistent path (all excluded); line-suffix stripping maps path:N to path;
empty-map honesty; front matter carries generated-code-to-doc-map + governance.
done when: python3 -m unittest launchpad.project-intelligence path-based discover
run passes the new test file.

STEP 4  [needs 2, 3]  Validate + full suite
python3 launchpad/project-intelligence/corpus/validate.py exits 0 (pre-existing
UNVERIFIED notices tolerated); full unittest discover over corpus/tests passes
(baseline 225 + new).
done when: both commands exit 0 in the worktree.

STEP 5  [needs 4]  Commit
git add builder, generated file, test, this plan; git commit -s with the issue
number and the inclusion rule named in the body.
done when: one signed commit on task/888-generated-code-to-doc-map contains
exactly those files.

PARALLEL
- None within this task; steps 2 and 3 both need step 1 but could run in either
  order. The batch-level parallelism is between sibling worktrees, not here.

GATES
- Commit gate: full unittest discover as the sole command in its own Bash call
  (brief §7) before git add/commit.
- Self-review (batch mode): diff re-read against the issue DoD line by line; no
  separate review-code pass.

BUDGET
- One builder module (~120 lines), one generated markdown (~2100 lines,
  tool-emitted), one test file (~150 lines), this plan. No shared file touched.

OPEN
- Whether a future task should compress the pairwise table (one row per path with
  grouped node ids) if the corpus grows the map past readability — the issue and
  the dispatch EXTRA prescribe pairwise rows, so that decision is not this task's.

LEFT OUT
- implements -> corpus-template-generated-index edge: the template's "Boundary
  against the rest of the generated/*.md family" table classifies *-map documents
  as mappings that "each need their own per-type template", so declaring this
  document implements the index template would contradict the template's own
  text, even though the framework renders the same body skeleton. A references ->
  corpus-agents edge is kept.
- Any relationship to the decisions-index or other generated nodes: not
  resolvable on origin/launchpad (brief rule), and the exclusion of
  launchpad/decisions/ paths is stated in the body instead.
- Content verification of citations: the map proves a cited file exists, not that
  it still supports the citing claim; disclosed as an unverified bullet, not
  solved here.
- Widening the rule to salvage paths embedded inside tool-result strings — the
  EXTRA forbids inventing coverage; those shapes are named in the excludes.
