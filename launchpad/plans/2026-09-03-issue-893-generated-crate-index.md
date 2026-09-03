Issue #893 — generate corpus document generated/crate-index.md
Stated size: no Size line on the issue; family task under parent PRD #621 -> cap: 5 steps

ALREADY TRUE
- The #633 generator framework (launchpad/project-intelligence/corpus/indexes.py) is
  merged on this base: builder discovery from index_defs/*.py, IndexSpec/GeneratedBody
  contracts, GenerationContext (valid_nodes, inverse_edges, input_digest, rel_path),
  and full front-matter/body-skeleton rendering per templates/generated-index.md.
- Ten builders are already registered (glossary, index, decisions-index, api-index,
  capability-index, code-to-doc-map, concept-index, configuration-index,
  corpus-index, coverage); crate-index is not among them.
- No canonical corpus node currently carries front-matter `type: implementation`
  (verified: zero matches on this base) -- node.schema.json's natural per-crate type
  value is unpopulated, so a type-enum filter alone would render an empty index.
- The corpus already holds real `crates/<name>/...` path citations in several nodes'
  `evidence[].evidence` arrays (e.g. capabilities/presence/user-status.md cites
  `crates/buzz-core/src/kind.rs:67-70`), so a citation-based cross-reference is not
  merely a fallback -- it populates non-trivially today.
- index_defs/code_to_doc_map.py already ships a mechanical, schema-grounded citation
  classifier (path-shaped, resolves to a real working-tree file, excludes prose/URLs)
  that this task's classifier mirrors rather than reinvents.
- `crates/*/Cargo.toml` exists for every crate (30 on this base) and 28 of 30 declare
  `package.description`; Python's stdlib `tomllib` (3.11+, matches CI's pinned
  python-version) parses it without a new dependency.

STEP 1 [independent] Builder module index_defs/crate_index.py  <- RUNS HERE
  Determinism source for "known crates": a sorted glob of `crates/*/Cargo.toml` in the
  repository working tree (via validate.repo_root(), same resolution code_to_doc_map.py
  uses), read with tomllib for `package.name` and optional `package.description` --
  never AGENTS.md's hand-written crates/ table, which is prose, not a corpus node, and
  is already stale against the tree (~20 named vs. 30 present). Cross-reference rule:
  a crate is "documented by" every valid canonical node whose evidence citation is
  path-shaped, resolves to a real file, and that file's path starts with
  `crates/<name>/` (mirrors code_to_doc_map.py's classifier; line-suffix stripped).
  SPEC: name crate-index, output_path generated/crate-index.md, node_id
  generated-crate-index, node_type governance (rows are repository crates, not
  canonical nodes of one front-matter type -- same reasoning code_to_doc_map.py gives),
  audiences [agent, developer], relationships references->corpus-agents and
  implements->corpus-template-generated-index (the template's own text names
  crate-index as one of the nine literally index-shaped documents in its family).
  Empty-crate-list and empty-citation-set branches both render an honest empty/partial
  state, never a widened rule.
  done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list` shows
  crate-index, and `--only crate-index` writes generated/crate-index.md without error.

STEP 2 [needs 1] Generate and confirm stability
  Run the generator to write TARGET, then rerun and diff (git status --porcelain must
  be empty) and run `--check --only crate-index` (must exit 0).
  done when: two consecutive generations are byte-identical and --check exits 0.

STEP 3 [needs 1] Test file
  tests/test_index_crate_index.py, following test_index_code_to_doc_map.py's
  conventions (indexes.py loaded by path as corpus_indexes; generation into a
  tempdir corpus; the builder still resolves crates/ against the real repo root).
  Cover: builder discovered with declared identity; two runs byte-identical; the
  real crates/buzz-core directory appears in the listing even with zero fixture
  nodes (crate enumeration is independent of the corpus); a fixture node citing a
  real crates/buzz-core file attributes documentation to that crate; line-suffixed
  citations collapse; non-path-shaped/URL/prose citations and citations resolving
  outside any crates/<name>/ directory are excluded; front matter carries the
  declared node_id and type.
  done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` is OK with more tests than the 225-test baseline.

STEP 4 [needs 2] Validate
  Run validate.py against the real corpus; UNVERIFIED notices are pre-existing and
  non-fatal, any hard error is this task's to fix.
  done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 5 [needs 4] Commit gate
  Run the full unittest suite as the sole Bash command in the worktree to earn the
  verify-gate stamp, then stage builder module + generated file + test + this plan
  and create one signed commit.
  done when: `git log` on task/893-generated-crate-index shows exactly one commit
  ahead of feature/621-generated-traceability, containing exactly those four files.

PARALLEL
- None within this plan; steps are a short chain (module -> generate -> test/validate
  -> commit). This task itself runs in parallel with the other #621 family builders,
  each isolated to its own worktree and its own new index_defs/ module.

GATES
- python3 launchpad/project-intelligence/corpus/indexes.py --check --only crate-index (exit 0)
- python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py" (OK, >225 tests)
- python3 launchpad/project-intelligence/corpus/validate.py (exit 0)
- pre-commit verify-gate stamp earned by the real suite run as a sole command

BUDGET
- 1 new builder module (index_defs/crate_index.py), 1 generated file
  (generated/crate-index.md), 1 test file, this plan. No edits to indexes.py,
  validate.py, or any other builder module.

OPEN
- Whether a future `[workspace] members` field in the root Cargo.toml would be a
  more authoritative crate enumeration than `crates/*/Cargo.toml` -- not present on
  this base as an explicit members list to read; the directory glob is the
  inspectable source available today.

LEFT OUT
- Per-crate dependency graph, feature flags, or version metadata -- out of scope for
  an index-shaped cross-reference; the "not covered" section names this explicitly.
- Any hand-authored second document -- Definition of done bars folding a second
  concept into this task.
