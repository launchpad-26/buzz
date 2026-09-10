Issue #1306: generate specifications/superseded-documents.md (parent PRD #621)

Stated size: DoD checklist, one generated document + minimal generator/test change  ->  cap: 5 steps

ALREADY TRUE
- Base branch `feature/621-generated-traceability` carries the #633 generator
  framework (`launchpad/project-intelligence/corpus/indexes.py`) and 25 merged
  builders, including #1302's `specifications_index.py` (path-prefix scoping
  precedent for the `specifications/` subtree) and #896's `dependency_graph.py`
  (already computes and renders `ctx.inverse_edges` for all four
  generated-inverse relationship types, including `superseded-by`, in
  `build_context`).
- `relationships.schema.json` marks `supersedes`'s inverse as `superseded-by`,
  `inverse: generated` -- computed once by the framework, never by a builder.
- `launchpad/docs/corpus/specifications/` exists on this base and currently
  contains only `specifications/INDEX.md` (#1302's own generated output,
  excluded from canonical inputs before any builder runs). No other node lives
  under the `specifications/` prefix yet.
- Corpus-wide at this revision: zero `supersedes` edges exist (confirmed via
  #896's dependency-graph docstring and a direct grep for
  `type: "supersedes"` under `launchpad/docs/corpus/`), and zero nodes carry
  `status: deprecated` or `status: retired` (confirmed via grep against the
  real front matter, not the template's placeholder text). The inclusion rule
  below is therefore expected to match zero nodes today -- an honest empty
  listing, not a bug to fix by widening scope.

STEP 1 -- Read family precedent and confirm current corpus state [independent]
Read `index_defs/specifications_index.py` (#1302, path-prefix scoping
rationale) and `index_defs/dependency_graph.py` (#896, `ctx.inverse_edges`
rendering) in full. Re-run the greps above inside the worktree to confirm the
zero-match state still holds at HEAD.
done when: both files read; grep output for `supersedes` edges and
`deprecated`/`retired` statuses reconfirmed as empty in this worktree.

STEP 2 -- Write the builder module <- RUNS HERE [needs 1]
Add `index_defs/superseded_documents.py` exposing `SPEC`
(`name: superseded-documents`, `output_path: specifications/superseded-documents.md`,
`node_id: specifications-superseded-documents`, `node_type: governance`,
`audiences: (agent, developer, reviewer)`). `generate(ctx)` scopes candidates to
valid nodes whose `ctx.rel_path(node)` starts with `specifications/`, then
selects those with a non-empty entry for their id in
`ctx.inverse_edges['superseded-by']` (reused directly, never recomputed). A
second, always-rendered subsection surfaces divergence between that signal and
`status: deprecated`/`retired` in both directions (status-flagged-no-edge, and
edge-exists-status-not-flagged), per #890/#900's transparency precedent for a
signal mismatch. `relationships`: `references -> corpus-agents`,
`implements -> corpus-template-generated-index`,
`references -> corpus-template-specification` (mirrors #1302; all three
targets are merged on this base).
done when: module file exists; `python3 launchpad/project-intelligence/corpus/indexes.py --list`
shows `superseded-documents	specifications/superseded-documents.md`.

STEP 3 -- Generate and verify stability [needs 2]
Run `... indexes.py --only superseded-documents` to write the target file.
Re-run it a second time and confirm `git status --porcelain` shows no diff on
the target. Run `... indexes.py --check --only superseded-documents` and
confirm exit 0.
done when: target file written; second run produces no diff; `--check` exits 0.

STEP 4 -- Add the focused test [needs 2]
Add `tests/test_index_superseded_documents.py` following
`test_indexes.py`/sibling `test_index_*.py` conventions: builder discovered by
name and output path; output byte-stable across two in-memory `render_document`
calls; inclusion rule proven with a small fixture corpus (a `specifications/`
node with an incoming `supersedes` edge is included, one without is excluded,
a `status: deprecated` node with no `supersedes` edge lands only in the
divergence subsection); front matter carries `node_id` and `type`.
done when: test file exists and the full corpus test suite passes (Step 5's
run covers this).

STEP 5 -- Full verification, commit gate [needs 3, 4]
Run `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0).
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own Bash call. Self-review the diff against the
issue's DoD line by line, then commit.
done when: validate.py exits 0; full unittest discover run is OK with more
than the 225-test baseline; one signed commit exists on
`task/1306-specifications-superseded-documents` containing exactly the builder
module, the generated target, the test, and this plan.

PARALLEL
- Steps 1 is independent of everything else in this family; this task has no
  ordering dependency on sibling tasks #1303-#1305 (each is its own isolated
  worktree/builder module per the batch's add-a-file-only contract).
- Steps 3 and 4 both depend only on Step 2 and could run in either order, but
  are sequenced 3-then-4 here for a single builder to keep the loop small.

GATES
- `python3 launchpad/project-intelligence/corpus/indexes.py --check --only superseded-documents`
  exits 0 (no-change rerun proof).
- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  is OK, count above the 225-test baseline.

BUDGET
One builder module (~120-180 lines), one generated markdown file, one test
module (~80-150 lines), this plan. No edits to `indexes.py` or any other
shared file.

OPEN
- Whether a future `specifications/` node will actually declare a `supersedes`
  edge is out of this task's control -- the rule is written to activate
  automatically the moment one does, and that is left for a future revision to
  populate, not for this builder to simulate.

LEFT OUT
- Recomputing or altering the framework's `superseded-by` derivation --
  #896 already owns that in `indexes.py`'s `build_context`; this builder only
  reads `ctx.inverse_edges['superseded-by']`.
- Reconciling the `status: deprecated`/`retired` signal with the
  `superseded-by` signal into one merged rule -- the issue's own EXTRA note
  says these are different signals that must not be conflated; divergence is
  surfaced, never resolved, by this document.
- Any change to sibling tasks #1303 (draft-documents.md), #1304
  (implemented-documents.md), or #1305 (normative-documents.md) -- each is a
  separate isolated builder with no shared file to coordinate through besides
  `indexes.py` itself, which none of these tasks may edit.
