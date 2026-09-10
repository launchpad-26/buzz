Issue #897: generate corpus document generated/doc-to-code-map.md

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
  sorted `(code path, node id)` tuples.
- `templates/generated-index.md`'s own boundary table names
  `doc-to-code-map.md` (#897) explicitly as a mapping, not an index, and
  `code_to_doc_map.py`'s own docstring records that it therefore omits the
  `implements -> corpus-template-generated-index` edge for that reason.
- 10 builders are already registered in `index_defs/`; discovery is
  add-a-file-only and fails loudly on duplicate `name`/`output_path`.

STEP 1 [independent]

Write `index_defs/doc_to_code_map.py` exposing `SPEC` for builder name
`doc-to-code-map`, output `generated/doc-to-code-map.md`, node id
`generated-doc-to-code-map`, type `governance` (identical justification to
`code_to_doc_map.py`'s own: rows are repo paths / node ids, not one subject
type). Rather than re-implementing the citation classifier, load
`code_to_doc_map.py` by its own fixed path (private `sys.modules` key, not the
`corpus_index_def_*` name `discover_builders` uses, so this has no dependency
on discovery order) and call its `_pairs(ctx)` directly; regroup as
`(node id, code path)` sorted by node id then path. Relationships: only
`references -> corpus-agents` (no `implements` edge, matching
`code_to_doc_map.py`'s own precedent and the template's boundary table).
Inclusion/exclusion text names this as the explicit inverse of
`generated/code-to-doc-map.md` (#888).
<- RUNS HERE
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --only doc-to-code-map` exits 0 and writes `launchpad/docs/corpus/generated/doc-to-code-map.md`.

STEP 2 [needs 1]

Confirm regeneration determinism: run the generator a second time and diff
(`sha256sum` before/after, and `git status --porcelain` on the output path).
Also run `--check --only doc-to-code-map`.
done when: two runs are byte-identical and `--check` exits 0.

STEP 3 [needs 1]

Add `tests/test_index_doc_to_code_map.py` following
`tests/test_index_code_to_doc_map.py`'s conventions (load `indexes.py` by
path as `corpus_indexes`, build fixture nodes in a temp corpus root, generate
via `indexes.main`). Cover: builder discovered with declared identity; two
runs byte-identical; a real-path citation becomes one `(node id, path)` row;
line-suffixed citations collapse; every excluded citation shape (prose,
commit ref, URL, corpus-internal path, decision-record path, non-resolving
path) is excluded; empty-map renders the honest empty message; front matter
carries the node id and type.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_index_doc_to_code_map.py"` passes.

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

BUDGET

One file added under `index_defs/`, one generated `.md` file, one test file,
one plan file. No edits to shared framework files.

OPEN

- Whether `code_to_doc_map.py` is ever renamed or moved — this builder's
  direct-load-by-path reuse would need updating if so; left as a known,
  named coupling rather than solved here (duplication was the only
  alternative, and the brief prefers avoiding it when it doesn't require
  editing the other builder module).

LEFT OUT

- No `implements -> corpus-template-generated-index` relationship — deferred
  to (and settled by) the template's own boundary table classifying `*-map`
  documents as non-index-shaped; not this task's decision to make.
- No change to `code_to_doc_map.py` itself to formally share a third helper
  module — the brief permits this only if it does not require editing that
  file, and direct reuse of its existing `_pairs(ctx)` already avoids
  duplicating the citation classifier without touching it.
