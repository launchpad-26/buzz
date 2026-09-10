Issue #1302: generate corpus document specifications/INDEX.md

Stated size: issue carries no explicit Size line; the shared batch dispatch brief caps every task in this family at 5 steps -> cap: 5 steps

ALREADY TRUE

- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is merged onto this branch's base (`feature/621-generated-traceability`), with
  20 registered builders and a working `--only NAME` / `--check` CLI.
- `launchpad/docs/corpus/templates/generated-index.md` (body skeleton) and
  `launchpad/docs/corpus/templates/specification.md` (the `specification` node
  template, id `corpus-template-specification`) both already exist on this base.
- `launchpad/docs/corpus/specifications/` does not exist as a directory on this
  base; zero canonical nodes currently have a corpus-root-relative path starting
  `specifications/` (verified: `find launchpad/docs/corpus -iname
  "specifications*"` returns nothing).
- Precedent for an honestly-empty listing exists twice already on this base:
  `index_defs/api_index.py` (#886, zero `interfaces-events` nodes) and
  `index_defs/concept_index.py` (#889) both render an explicit empty-state
  message instead of widening their rule.
- Precedent for a per-subtree "nodes under path prefix X" listing exists:
  `index_defs/decisions_index.py` (#845)'s second section lists canonical nodes
  whose `ctx.rel_path(node)` starts with `decisions/`, sorted by path, rendering
  an explicit "None" sentence when empty -- the same shape this task needs for
  `specifications/`.
- `corpus-agents` (`launchpad/docs/corpus/AGENTS.md`) and
  `corpus-template-generated-index` (`launchpad/docs/corpus/templates/generated-index.md`)
  both exist on this base, so `references -> corpus-agents` and
  `implements -> corpus-template-generated-index` are resolvable relationships.
- `GenerationContext.rel_path(node)` gives the corpus-root-relative posix path
  needed for a deterministic `str.startswith("specifications/")` prefix check;
  no directory listing or filesystem walk of `specifications/` is needed or
  possible (the framework's inputs come from `validate.py`'s node walk, not
  `Path.iterdir()`), so the builder cannot assume the directory exists on disk.

STEP 1 -- Write the builder module [independent]

Create `launchpad/project-intelligence/corpus/index_defs/specifications_index.py`
exposing `SPEC` as a plain dict:
- `name`: `"specifications-index"`, `output_path`: `"specifications/INDEX.md"`,
  `node_id`: `"specifications-index"`, `title` naming it the specifications
  index, `node_type`: `"governance"` (justified in the module docstring the same
  way `decisions_index.py` justifies its own `governance` pick: node.schema.json
  has no `specification`/`index` type member, and this is a corpus-about-corpus
  meta-document, not an instance of the subject it lists), `audiences`:
  `("agent", "developer", "reviewer")` (matches `decisions_index.py`).
- `generate(ctx)`: select `n for n in ctx.valid_nodes if ctx.rel_path(n).startswith("specifications/")`,
  sorted by `ctx.rel_path(n)`. Render a table (id, path, status, audiences) when
  non-empty; when empty, render an explicit sentence stating the rule matched
  zero nodes at this input digest and that the listing populates automatically
  as specification documents are authored (mirrors `api_index.py`'s empty-state
  wording) -- and additionally point the reader at
  `launchpad/docs/corpus/templates/specification.md` (`corpus-template-specification`)
  as what a `specifications/` node is expected to look like, so the empty
  listing is informative rather than blank, per the dispatch EXTRA note.
- `includes`/`excludes`/`ordering`/`not_covered` bullets naming the prefix rule
  precisely (path-prefix on `ctx.rel_path`, not front-matter `type`, since a
  specification node's own `type` varies by subject per the template's own
  type-choice guidance).
- `relationships`: `references -> corpus-agents`, `implements ->
  corpus-template-generated-index`, `references -> corpus-template-specification`
  (all three resolvable on this base; no worktree-only id used).
done when: the module imports cleanly under `python3 -c "import ast;
ast.parse(open('launchpad/project-intelligence/corpus/index_defs/specifications_index.py').read())"`
and `python3 launchpad/project-intelligence/corpus/indexes.py --list` lists
`specifications-index	specifications/INDEX.md` alongside the existing 20
builders with no duplicate-name/duplicate-output-path error.

STEP 2 -- Generate and verify determinism <- RUNS HERE [needs 1]

Run `python3 launchpad/project-intelligence/corpus/indexes.py --only
specifications-index` to write `launchpad/docs/corpus/specifications/INDEX.md`.
Re-run the same command a second time and confirm `git status --porcelain`
shows no change to that file. Run `python3
launchpad/project-intelligence/corpus/indexes.py --check --only
specifications-index` and confirm exit 0.
done when: two consecutive generations are byte-identical (`git status
--porcelain launchpad/docs/corpus/specifications/INDEX.md` empty after the
second run) and `--check --only specifications-index` exits 0.

STEP 3 -- Add the focused test module [needs 1]

Write `launchpad/project-intelligence/corpus/tests/test_index_specifications_index.py`
following `test_index_api_index.py`'s conventions (load `indexes.py` by path as
`corpus_indexes`, generate into a `tempfile.TemporaryDirectory()` corpus root,
never touch the real corpus). Cover: builder discovered with the declared
`output_path`/`node_id`/`node_type`; two runs byte-identical; a fixture node
written under a `specifications/` subdirectory (e.g.
`root / "specifications" / "fixture-spec-node.md"`) appears in the listing
while a fixture node at the corpus root or another subtree does not; the
zero-match case renders the honest-empty sentence and the
`corpus-template-specification` pointer, not the table; front matter carries
`id: "specifications-index"` and `type: "governance"`.
done when: `python3 -m unittest
launchpad.project-intelligence.corpus.tests.test_index_specifications_index -v`
(run via `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p
"test_index_specifications_index.py"`) passes with all new test methods green.

STEP 4 -- Full corpus test suite and validate.py [needs 2, 3]

Run the full suite: `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` and confirm OK with
more than the 225-test base baseline. Run `python3
launchpad/project-intelligence/corpus/validate.py` and confirm exit 0 (pre-existing
UNVERIFIED notices are not fatal; any new hard error is this task's to fix).
done when: both commands exit 0 and the suite's reported test count exceeds 225.

STEP 5 -- Self-review and commit [needs 4]

Re-read the full diff against issue #1302's DoD checklist line by line: exactly
one corpus document created (`specifications/INDEX.md`); the file is
generator-emitted (proven by the Step 2 rerun-no-diff and `--check`); schema-valid
front matter with stable id/type/status/origin/audiences/evidence/relationships;
generator/inputs/inclusion-exclusion/ordering named in the rendered body;
explicit do-not-edit marker (framework-rendered); regenerable from canonical
nodes only; no-change rerun produces no diff (already proven). Stage the builder
module, generated file, test module and this plan; commit with `git commit -s`.
done when: `git status --porcelain` inside the worktree shows a clean tree after
the commit, and `git log -1 --format='%s%n%b'` shows the DCO
`Signed-off-by` trailer and names the inclusion rule in the body.

PARALLEL

Step 1 has no upstream dependency inside this task. Steps 3 depends only on
Step 1 (the module existing) so it can be drafted while Step 2 runs, but both
must complete before Step 4's full-suite run. This task does not depend on, and
must not wait for, the sibling tasks #1303-#1306 (draft/implemented/normative/
superseded documents under the same `specifications/` prefix) -- the batch's own
rule is no ordering dependency among siblings; this index is honestly empty
until they (or any other specification node) land.

GATES

- `python3 launchpad/project-intelligence/corpus/indexes.py --check --only
  specifications-index` must exit 0 before commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must be OK (baseline 225 tests on this base; this task adds more)
  as THE SOLE COMMAND in its own Bash call before `git add`/`git commit`, per
  the batch dispatch brief's commit-gate recipe.
- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.

BUDGET

5 steps, matching the declared cap. Steps 1 and 3 are small (one new module,
one new test module, each following an existing precedent file almost
line-for-line). Steps 2, 4 and 5 are command-running/verification steps with
no design work of their own. No step is expected to need splitting.

OPEN

- Whether a future specification node's own front-matter `type` will vary
  (interfaces-events / architecture / implementation, per
  `templates/specification.md`'s own guidance) is left to those authoring tasks;
  this index's inclusion rule is deliberately type-agnostic (path prefix only)
  so it does not need to special-case that variation.
- Whether `specifications/INDEX.md` should eventually gain per-status or
  per-type grouping once real nodes exist is left to a future task if the flat
  listing stops being useful -- not decided here, since zero real nodes exist
  to design groupings against yet.

LEFT OUT

- No edit to `indexes.py` or any other shared framework file -- the builder
  contract is add-a-file-only, and this task's EXTRA note repeats that the
  builder must not assume `specifications/` exists as a directory on disk.
- No hand-authored content in `specifications/INDEX.md` itself -- the file is
  entirely generator output; if its content were ever wrong the fix is the
  builder, never the file.
- No work on sibling issues #1303-#1306 -- each is its own isolated task per
  the batch dispatch brief, and this task must not wait for or reference their
  unmerged worktrees.
- No new relationship types beyond `references`/`implements` -- inverse edge
  names (e.g. `implemented-by`) are generated by the framework, never authored
  in a builder's `relationships` field.
