Issue #905 — generate corpus document generated/test-index.md
Stated size: no Size line on the issue; family task under parent PRD #621 -> cap: 5 steps

ALREADY TRUE
- The #633 generator framework (launchpad/project-intelligence/corpus/indexes.py) is
  merged on this base: builder discovery from index_defs/*.py, IndexSpec/GeneratedBody
  contracts, GenerationContext (valid_nodes, inverse_edges, input_digest, rel_path),
  and full front-matter/body-skeleton rendering per templates/generated-index.md.
- Twenty builders are already registered (glossary, index, decisions-index, api-index,
  capability-index, code-to-doc-map, concept-index, configuration-index, corpus-index,
  coverage, crate-index, database-index, decision-index, dependency-graph,
  doc-to-code-map, documentation-graph, event-kind-index, layer-index, nip-index,
  orphaned-docs); test-index is not among them.
- Both candidate templates (templates/test-contract.md id corpus-template-test-contract,
  templates/test-strategy.md id corpus-template-test-strategy) are merged, but zero
  canonical nodes carry a relationships[].target of either id (verified: a repo-wide
  grep found no matches on this base) -- an `implements` filter over either template
  would render an empty index.
- Front-matter `type: verification` is carried only by those same two templates and by
  no node describing an actual verification artifact -- a type-enum filter is equally
  unpopulated and conceptually wrong (it would name verification-strategy documents,
  not raw test files).
- The corpus already holds real test-file path citations in several nodes' evidence
  arrays (e.g. capabilities/search/search.md cites
  `crates/buzz-search/tests/fts_integration.rs:1-1509`, capabilities/notifications/
  notification-preferences.md cites `desktop/.../shouldNotify.test.mjs`), so a
  citation-based cross-reference populates non-trivially today.
- index_defs/crate_index.py and index_defs/code_to_doc_map.py already ship a
  mechanical, schema-grounded citation classifier (path-shaped, resolves to a real
  working-tree file, excludes prose/URLs, strips one trailing :N/:N-M suffix) that
  this task's classifier mirrors rather than reinvents.

STEP 1 [independent] Builder module index_defs/test_index.py  <- RUNS HERE
  Citation-based cross-reference (mirrors crate_index.py/code_to_doc_map.py's
  classifier): for each valid canonical node's evidence citation that resolves to a
  real repository file, keep it if the resolved path is "test-shaped" under a stated
  path-pattern rule -- a `tests` directory component anywhere above the filename, OR a
  filename matching `test_*`, `*_test.*`, or `*.test.*` (case-sensitive). Never opens a
  file to look for test markers inside it. One row per distinct test path, listing the
  sorted citing node ids. SPEC: name test-index, output_path generated/test-index.md,
  node_id generated-test-index, node_type governance (rows are repository test files,
  not canonical nodes of one front-matter type -- same reasoning crate_index.py and
  code_to_doc_map.py give), audiences [agent, developer], relationships
  references->corpus-agents and implements->corpus-template-generated-index (the
  template's own boundary table names test-index as one of its literally index-shaped
  documents). Empty-citation-set branch renders an honest empty message, never a
  widened rule.
  done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list` shows
  test-index, and `--only test-index` writes generated/test-index.md without error.

STEP 2 [needs 1] Generate and confirm stability
  Run the generator to write TARGET, then rerun and diff (git status --porcelain must
  be empty) and run `--check --only test-index` (must exit 0).
  done when: two consecutive generations are byte-identical and --check exits 0.

STEP 3 [needs 1] Test file
  tests/test_index_test_index.py, following test_index_code_to_doc_map.py's
  conventions (indexes.py loaded by path as corpus_indexes; generation into a tempdir
  corpus; the builder still resolves cited paths against the real repo root). Cover:
  builder discovered with declared identity; two runs byte-identical; a fixture node
  citing a real tests/-directory file (this corpus tooling's own
  tests/test_indexes.py) is listed; a fixture node citing a real *.test.-style or
  *_test.-style path is listed (or, if no such real repo file is stable to depend on,
  a synthetic tmp-tree file exercising the same _is_test_path predicate directly);
  line-suffixed citations collapse; a real non-test source file citation is excluded;
  non-path-shaped/URL/prose citations are excluded; front matter carries the declared
  node_id and type.
  done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` is OK with more tests than the 225-test baseline.

STEP 4 [needs 2] Validate
  Run validate.py against the real corpus; UNVERIFIED notices are pre-existing and
  non-fatal, any hard error is this task's to fix.
  done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 5 [needs 4] Commit gate
  Run the full unittest suite as the sole Bash command in the worktree to earn the
  verify-gate stamp, then stage builder module + generated file + test + this plan and
  create one signed commit.
  done when: `git log` on task/905-generated-test-index shows exactly one commit ahead
  of feature/621-generated-traceability, containing exactly those four files.

PARALLEL
- None within this plan; steps are a short chain (module -> generate -> test/validate
  -> commit). This task itself runs in parallel with the other #621 family builders,
  each isolated to its own worktree and its own new index_defs/ module.

GATES
- python3 launchpad/project-intelligence/corpus/indexes.py --check --only test-index (exit 0)
- python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" (OK, >225 tests)
- python3 launchpad/project-intelligence/corpus/validate.py (exit 0)
- pre-commit verify-gate stamp earned by the real suite run as a sole command

BUDGET
- 1 new builder module (index_defs/test_index.py), 1 generated file
  (generated/test-index.md), 1 test file, this plan. No edits to indexes.py,
  validate.py, or any other builder module.

OPEN
- Whether a future authored test-contract/test-strategy node would make the
  implements-edge signal viable instead -- not present on this base; the citation rule
  is the inspectable source available today, and can coexist once such nodes exist.

LEFT OUT
- Per-test pass/fail status, coverage percentage, or file-content parsing (looking for
  `#[test]`/`def test_` markers inside non-test-named files) -- out of scope for a
  path-pattern cross-reference; the "not covered" section names this explicitly.
- Any hand-authored second document -- Definition of done bars folding a second
  concept into this task.
