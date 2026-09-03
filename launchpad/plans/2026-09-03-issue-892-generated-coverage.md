# Plan: issue #892 — generate launchpad/docs/corpus/generated/coverage.md

Issue #892 (parent PRD #621): create `launchpad/docs/corpus/generated/coverage.md`
as the single generated corpus node for coverage — a METRIC REPORT rendered from
`coverage.py`'s `build_coverage()` API (issue #634, already merged on the base
branch), emitted through the #633 generator framework (`indexes.py`).

Stated size: none on the issue; the batch brief caps document tasks  ->  cap: 5 steps

ALREADY TRUE
- The #633 framework (`launchpad/project-intelligence/corpus/indexes.py`) is merged
  on `feature/621-generated-traceability` with five shipped builders
  (glossary, index, decisions-index, api-index, capability-index) proving the
  add-a-module-only contract works.
- `launchpad/project-intelligence/corpus/coverage.py` (#634) is merged and exposes
  `build_coverage(root, corpus_root, manifest_rows=(), registry=None) -> CoverageReport`
  with `.rows`, `.gaps`, `.complete`, `.to_markdown()`; its rows are stable-sorted by
  `(category, source_key)` and carry no timestamps.
- A real run on this tree reports 407 in-scope items: 297 `documented`, 110 `GAP`
  (verified by running the CLI directly). No dispositions registry and no manifest
  JSON exist anywhere in the tree, so the report's only `documented` earner is a
  canonical node's file/position citation.
- `test_coverage.py` already establishes the fixture shape (mini repo with corpus
  under `<tmp>/launchpad/docs/corpus/`, `launchpad` being in inventory.py's ignored
  top-level set), and `test_index_capability_index.py` establishes the
  focused-builder-test conventions.

STEP 1 [independent] Builder module <- RUNS HERE
Write `launchpad/project-intelligence/corpus/index_defs/coverage.py` exposing SPEC:
name `coverage`, output_path `generated/coverage.md`, node_id `generated-coverage`,
node_type `governance` (precedent: glossary/index/decisions-index; the subject is
the corpus's own completeness accounting, a corpus-governance concern, and no
subject-specific enum value fits a meta-report), audiences agent/developer/reviewer.
`generate(ctx)` loads `coverage.py` by path as `corpus_coverage` (the sibling-load
pattern coverage.py itself uses), derives the repo root from `ctx.corpus_root`
(strip a trailing `launchpad/docs/corpus`; otherwise treat the corpus root itself
as the inventory root, so fixture corpora stay hermetic), calls
`build_coverage(root, corpus_root)` with no manifest/registry (none exist in-tree),
and renders: a disposition-count summary that states completeness ONLY per
`report.complete`, states plainly that GAP rows are visible rather than hidden, the
full accounting table in `to_markdown()`'s column shape, and the advisory findings.
Nothing rendered may depend on the generated file's own presence on disk (no
node-count of `build_coverage`'s own load), so the first and second runs are
byte-identical. `extra_evidence` cites `coverage.py`. Relationships: only
`references -> corpus-agents` — deliberately NOT `implements ->
corpus-template-generated-index`, because that template's own boundary table names
`coverage.md` as a metric report that is not index-shaped.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list` shows
builder `coverage` and discovery raises no SpecError.

STEP 2 [needs 1] Generate and prove stability
Run `... indexes.py --only coverage` to write the target; rerun and confirm
`git status --porcelain` shows the file unchanged; `... indexes.py --check --only
coverage` exits 0. Never hand-edit the output.
done when: target exists, second run makes no diff, `--check` exits 0.

STEP 3 [needs 1] Focused test
`launchpad/project-intelligence/corpus/tests/test_index_coverage.py` following
test_index_capability_index.py's conventions plus test_coverage.py's fixture repo
shape: discovery/identity test; fixture test that a node citation flips an item to
`documented` while an unrecognized top-level dir renders a visible `GAP` row and the
summary says incomplete; determinism test (two renders byte-equal); real-corpus
smoke test (committed file carries `id: "generated-coverage"`, the do-not-edit
marker, and a `GAP` visibility statement).
done when: `python3 -m unittest` on the new file passes.

STEP 4 [needs 2, 3] Full gates and commit
Full suite via `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` (baseline 225 + new),
then `python3 launchpad/project-intelligence/corpus/validate.py` exit 0, then one
signed commit of builder + generated doc + test + this plan.
done when: suite OK, validate.py exit 0, one signed commit exists.

PARALLEL
Steps 2 and 3 are independent of each other once step 1 lands.

GATES
- `indexes.py --check --only coverage` exit 0 (no-change rerun).
- Full unittest discovery OK.
- `validate.py` exit 0 (UNVERIFIED notices are pre-existing and non-fatal).
- Commit gate per batch brief: suite run as the sole command, then signed commit.

BUDGET
One builder module (~150 lines), one generated document (~470 lines, 407 table
rows), one test file (~150 lines), one plan. No shared file is touched.

OPEN
- Whether `coverage.py --strict` becomes a hard CI/validate gate is #621's CI
  wiring decision, explicitly out of this task's scope; this document only reports.
- Whether a dispositions registry file should be created and fed to the generator
  is a future authoring decision (#634 requires it be human-recorded); until one
  exists the builder passes none.

LEFT OUT
- Any change to indexes.py, coverage.py, inventory.py, validate.py or other shared
  files — the builder contract forbids it and nothing here needs it.
- A second corpus document, registry seeding, or CI workflow changes.
- Enabling `--strict` anywhere (per dispatch EXTRA: that belongs to CI wiring).
