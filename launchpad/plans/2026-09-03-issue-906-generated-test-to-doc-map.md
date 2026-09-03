Issue #906: generate corpus document generated/test-to-doc-map.md

Stated size: not stated on the issue itself; batch dispatch brief caps this family at 5 steps  ->  cap: 5 steps

ALREADY TRUE

- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is merged to `feature/621-generated-traceability` and exposes `IndexSpec`,
  `GenerationContext`, `discover_builders`, `--list/--all/--only/--check`.
- #888's `generated/code-to-doc-map.md` builder
  (`launchpad/project-intelligence/corpus/index_defs/code_to_doc_map.py`) is
  merged on this base branch. It walks every valid canonical node's
  `evidence[].evidence` citations, classifies which are code-path-shaped via
  its private `_code_path`, and exposes a private `_pairs(ctx)` returning
  sorted `(code path, node id)` tuples covering ALL path-shaped citations, not
  filtered by whether the path is a test file.
- #897's `generated/doc-to-code-map.md` builder
  (`launchpad/project-intelligence/corpus/index_defs/doc_to_code_map.py`) sets
  the precedent this task follows: load a sibling builder module by its own
  fixed path (private `sys.modules` key, independent of discovery order) and
  call its private `_pairs(ctx)` directly, instead of re-implementing the
  citation classifier.
- `index_defs/test_index.py` does not exist on this base (checked: `ls
  launchpad/project-intelligence/corpus/index_defs/` has no `test_index.py`),
  so #905 has not merged here. This task therefore defines its own explicit
  test-path pattern rather than depending on #905's.
- `templates/generated-index.md`'s boundary table classifies `*-map`
  documents as mappings, not indexes; `code_to_doc_map.py` and
  `doc_to_code_map.py` both omit the `implements ->
  corpus-template-generated-index` edge for that reason.
- 20 builders are already registered in `index_defs/`; discovery is
  add-a-file-only and fails loudly on duplicate `name`/`output_path`.

STEP 1 [independent]

Write `index_defs/test_to_doc_map.py` exposing `SPEC` for builder name
`test-to-doc-map`, output `generated/test-to-doc-map.md`, node id
`generated-test-to-doc-map`, type `governance` (identical justification to
`code_to_doc_map.py`'s: rows are repo paths / node ids, not one subject
type). Load `code_to_doc_map.py` by its own fixed path (same private
`sys.modules` key pattern as `doc_to_code_map.py`) and call its `_pairs(ctx)`
directly; filter to pairs whose code path is test-shaped per a new, explicitly
documented mechanical classifier `_is_test_path(rel)`:
  - a path segment (case-insensitive) equal to `test` or `tests`, OR ending in
    `Test`/`Tests` with a capital T (camelCase/PascalCase convention:
    `androidTest`, `RunnerTests`, `BuzzPushKitTests`) -- catches whole test
    directories, never a substring match (excludes false positives like
    `latest`);
  - OR a filename matching `test_*.py` / `*_test.py` (Python), `*.test.<ext>`
    / `*.spec.<ext>` for ext in {js,jsx,ts,tsx,mjs} (JS/TS unit + Playwright
    convention), or `*_test.dart` (Dart convention).
Sorted (code path, node id), same order as `code_to_doc_map.py`'s own pairs.
Relationships: only `references -> corpus-agents` (no `implements` edge,
matching both precedent builders). Inclusion/exclusion text states plainly
that this document is the test-filtered SUBSET of
`generated/code-to-doc-map.md` (#888), not an independent extraction, and
states the exact test-path pattern above.
<- RUNS HERE
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --only test-to-doc-map` exits 0 and writes `launchpad/docs/corpus/generated/test-to-doc-map.md`.

STEP 2 [needs 1]

Confirm regeneration determinism: run the generator a second time and diff
(`sha256sum` before/after, and `git status --porcelain` on the output path).
Also run `--check --only test-to-doc-map`.
done when: two runs are byte-identical and `--check` exits 0.

STEP 3 [needs 1]

Add `tests/test_index_test_to_doc_map.py` following
`tests/test_index_doc_to_code_map.py`'s conventions (load `indexes.py` by
path as `corpus_indexes`, build fixture nodes in a temp corpus root, generate
via `indexes.main`). Cover: builder discovered with declared identity; two
runs byte-identical; a real test-shaped-path citation (e.g.
`launchpad/project-intelligence/corpus/tests/test_validate.py`) becomes one
row while a real non-test-shaped citation
(`launchpad/project-intelligence/corpus/indexes.py`) is excluded from this
document's rows; each test-path shape (tests/ dir segment, PascalCase `Test`
suffix dir, `test_*.py`, `*_test.py`, `*.test.mjs`, `*.spec.ts`, `*_test.dart`)
is individually exercised; a decoy path containing "latest" as a directory
segment is excluded; line-suffixed citations collapse; empty-map renders the
honest empty message; front matter carries the node id and type.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_index_test_to_doc_map.py"` passes.

STEP 4 [needs 1, 3]

Run `python3 launchpad/project-intelligence/corpus/validate.py` against the
real corpus root (now including the newly generated file) and confirm it
exits 0.
done when: `validate.py` exits 0 (pre-existing UNVERIFIED notices unrelated to
this change are non-fatal).

STEP 5 [needs 1, 2, 3, 4]

Full test suite gate and commit, per the batch brief's exact recipe: run the
whole `tests/` suite (not just the new file) as the commit gate, then stage
the builder module, generated doc, test file and this plan, and commit with
`-s`.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK, and one signed commit exists containing exactly those four files.

PARALLEL

Steps 2, 3 and 4 each only need step 1's builder module to exist; they touch
disjoint files (no file conflicts) but are executed sequentially in practice
since this is a single-agent build, not a multi-agent dispatch.

GATES

- No edits to `indexes.py` or `index_defs/code_to_doc_map.py` — new files only.
- No-change rerun must be byte-identical (step 2).
- `validate.py` must exit 0 (step 4).
- Full test suite must pass, not just the new file (step 5).
- Document body states plainly it is the test-filtered subset of
  `generated/code-to-doc-map.md`, not an independent extraction.

BUDGET

One file added under `index_defs/`, one generated `.md` file, one test file,
one plan file. No edits to shared framework files or to `code_to_doc_map.py`.

OPEN

- Whether `code_to_doc_map.py` is ever renamed or moved — this builder's
  direct-load-by-path reuse would need updating if so; left as a known, named
  coupling, the same one `doc_to_code_map.py` already carries.
- Whether #905's `test-index.md` (if/when it merges) settles on a different
  test-path pattern than the one defined here. If so, a follow-up task can
  reconcile the two patterns; not solved here since #905 is unmerged on this
  base and this task cannot depend on it.

LEFT OUT

- No `implements -> corpus-template-generated-index` relationship — deferred
  to (and settled by) the template's own boundary table classifying `*-map`
  documents as non-index-shaped; not this task's decision to make.
- No dependency on `index_defs/test_index.py` (#905) — verified absent on this
  base; the test-path pattern is defined locally and explicitly instead.
- No change to `code_to_doc_map.py` itself — direct reuse of its existing
  `_pairs(ctx)` avoids duplicating the citation classifier without touching
  it, per the brief's stated preference (#897's precedent).
