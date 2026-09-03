Issue: launchpad-26/buzz#1303 -- generate corpus document specifications/draft-documents.md

Stated size: no explicit Size label on the issue; the task family brief (Feature #621 batch dispatch) caps each single-document builder task -> cap: 5 steps

ALREADY TRUE

- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is merged to `feature/621-generated-traceability` and renders front matter, the
  do-not-edit marker, Generator/Inclusion-exclusion/Relationships/Scope sections
  around one builder-supplied `GeneratedBody`.
- #1302's sibling builder `index_defs/specifications_index.py` (output
  `specifications/INDEX.md`, node id `specifications-index`) is the closest
  precedent: it lists canonical nodes by the literal path prefix
  `specifications/`, renders an honest empty listing today, and points readers
  at `corpus-template-specification` when empty. Its output is a registered
  builder output path, so it is excluded from every other builder's canonical
  inputs automatically (`canonical_input_paths`/`build_context` in indexes.py).
- Verified directly against the checked-out schema: `node.schema.json`'s
  `status` enum is exactly `["draft", "active", "deprecated", "retired",
  "flagged"]`.
- Verified directly against this worktree's corpus tree: `specifications/`
  contains only `INDEX.md` (a registered generated output, hence excluded from
  canonical inputs), and no node anywhere declares
  `{"type": "implements", "target": "corpus-template-specification"}` (grepped
  every relationship block under `launchpad/docs/corpus`). Both halves of this
  issue's candidate inclusion rule (path-prefix vs. implements-relationship)
  therefore match zero canonical nodes today, before any builder-specific
  status filter is applied.
- `templates/generated-index.md` and `standards/generated-content.md` describe
  the body shape and policy this builder must satisfy; both are read, not
  guessed at.

STEP 1 -- Write the builder module <- RUNS HERE [independent]

Create `launchpad/project-intelligence/corpus/index_defs/specifications_draft_documents.py`
exposing module-level `SPEC` (plain dict, matching `specifications_index.py`'s
shape):

- `name`: `"specifications-draft-documents"`
- `output_path`: `"specifications/draft-documents.md"`
- `node_id`: `"specifications-draft-documents"`
- `node_type`: `"governance"` (same justification as #1302: node.schema.json's
  type enum has no `specification`/`index` member; `governance` is the
  established fit for corpus-about-corpus meta-documents in this family)
- `audiences`: `("agent", "developer", "reviewer")`
- Inclusion rule (stated in the module docstring and in `generate(ctx)`'s
  `includes` bullet, and enforced identically in code): a canonical node
  qualifies if and only if BOTH (a) `ctx.rel_path(node)` starts with the
  literal prefix `"specifications/"` (mirrors #1302's own path-prefix
  scoping, chosen over the implements-relationship alternative because the
  family's established inclusion axis is path membership under
  `specifications/`, not a relationship edge -- and because both axes
  currently agree on zero matches, there is no observed case where the
  relationship-based reading would differ) AND (b) `node.data.get("status")
  == "draft"` (literal string match against node.schema.json's `status`
  enum).
- `generate(ctx)` returns a dict with `sections` (a listing table when
  non-empty; an honest empty-listing paragraph today, naming
  `corpus-template-specification` and the `specifications/` prefix, mirroring
  #1302's empty-state wording), `includes`, `excludes` (nodes outside the
  prefix; nodes inside the prefix whose status is not literally `draft`; the
  template node itself; every registered generated output path -- the last
  one is already rendered by the framework, restate it in the builder's own
  `excludes` bullets for self-containedness only if #1302's builder does the
  same -- verify by reading it, do not assume), `ordering` (lexicographic by
  `ctx.rel_path(node)`), `not_covered`.
- `extra_evidence(ctx)` returns one FACT entry stating the exact count of
  matching nodes at the current input digest, citing `validate.py`, mirroring
  #1302.
- `relationships`: `references -> corpus-agents`,
  `implements -> corpus-template-generated-index`,
  `references -> corpus-template-specification` (all three merged/available
  on this base; the third is honest because the empty-listing prose points
  readers there, matching #1302's own reasoning for the identical edge).

done when: the module imports cleanly under `python3 -c "import importlib.util,
sys; ..."` (or via the generator's own `--list`) and appears in
`python3 launchpad/project-intelligence/corpus/indexes.py --list` output as
`specifications-draft-documents	specifications/draft-documents.md`.

STEP 2 -- Generate and verify determinism [needs 1]

Run `python3 launchpad/project-intelligence/corpus/indexes.py --only
specifications-draft-documents` to write the target file. Re-run the same
command and confirm `git status --porcelain` shows no change to the generated
file. Run `python3 launchpad/project-intelligence/corpus/indexes.py --check
--only specifications-draft-documents` and confirm exit 0.

done when: two consecutive generations are byte-identical (confirmed via
`git status --porcelain -- launchpad/docs/corpus/specifications/draft-documents.md`
showing nothing after the second run) and `--check --only
specifications-draft-documents` exits 0.

STEP 3 -- Add the focused test module [needs 1]

Create `launchpad/project-intelligence/corpus/tests/test_index_specifications_draft_documents.py`
following `test_index_specifications_index.py`'s conventions exactly (load
`indexes.py` by path as `corpus_indexes`, generate into a temp corpus root,
never touch the real corpus tree). Cover: builder discovered with declared
identity (name/output_path/node_id/node_type); two runs byte-identical; the
inclusion rule requires BOTH the `specifications/` path prefix AND
`status: draft` (a fixture node in-prefix but `status: active` must be
excluded; a fixture node with `status: draft` but outside the prefix must be
excluded; a fixture node satisfying both must appear); the empty-match case
renders the honest empty listing and still names
`corpus-template-specification`; front matter carries the declared
`node_id`/`node_type`.

done when: `python3 -m unittest
launchpad.project-intelligence.corpus.tests.test_index_specifications_draft_documents
-v` (or the discover form used in the commit gate) passes with zero failures,
and at least one test in the file would fail if the `status == "draft"` half
of the filter were removed (verified by temporarily commenting it out locally,
observing the expected test failure, then restoring it -- not committed).

STEP 4 -- Full test discovery, validate.py, and self-review [needs 2, 3]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` from the worktree root and confirm all tests pass (baseline on
this base is 225; this task adds its own new test file's cases). Run
`python3 launchpad/project-intelligence/corpus/validate.py` and confirm exit 0
(pre-existing UNVERIFIED notices are not a blocker; any new hard error is).
Re-read the full diff against issue #1303's Definition-of-Done checklist line
by line.

done when: both commands report success (unittest summary shows `OK`;
validate.py's own exit code is 0) and the self-review pass is noted in the
final report.

STEP 5 -- Commit [needs 4]

Stage exactly: the new builder module, the generated target file, the new test
module, and this plan file. Commit with `git commit -s -m "docs(corpus):
generate specifications/draft-documents.md (#1303)"` and a body naming the
inclusion rule (path prefix `specifications/` AND front-matter `status ==
"draft"`, currently zero matches).

done when: `git log -1 --format=%H` shows exactly one new commit on
`task/1303-specifications-draft-documents` containing only those four files,
and `git status --porcelain` is clean afterward.

PARALLEL

Steps 2 and 3 both depend only on Step 1 and touch disjoint files (the
generated target vs. the new test module), so they may run in either order or
concurrently; Step 4 needs both finished first.

GATES

- Step 2's generation must not be hand-edited if wrong -- fix the builder in
  Step 1 and regenerate, per the framework's own do-not-edit contract.
- Step 4's `python3 -m unittest discover` run and `validate.py` run must both
  be observed passing (not assumed) before Step 5 commits.
- The commit step runs alone in its own Bash call per the batch brief's exact
  recipe; the preceding full-test-discovery command also runs alone in its own
  Bash call, per the same brief.

BUDGET

One new builder module (~90-130 lines, following #1302's own module as the
size precedent), one generated Markdown file (framework-rendered, builder
supplies only the listing/rules text), one new test module (~120-150 lines,
mirroring `test_index_specifications_index.py`), and this plan file. No edits
to `indexes.py` or any other shared file.

OPEN

- Whether a future specification document could ever satisfy the
  implements-relationship reading without also living under `specifications/`
  path prefix -- not decided here; today both readings agree (zero matches),
  and the path-prefix choice is made for family consistency with #1302, not
  because the relationship reading was proven wrong. A future task that
  discovers a real divergence should revisit this choice explicitly rather
  than inherit it silently.

LEFT OUT

- Any change to `indexes.py`, `validate.py`, or any other shared framework
  file -- the builder contract is add-a-file-only.
- Any second generated or hand-authored corpus document -- this task delivers
  exactly one node, per the issue's own Definition of Done and Out of scope
  sections.
- Deciding the sibling tasks' (#1304-#1306) inclusion rules -- each is its own
  issue with no ordering dependency on this one.
