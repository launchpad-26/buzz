Issue: #902 (parent PRD #621)

Stated size: no explicit Size line on #902; every sibling generated/*.md task under #621 is single-document/single-builder-module -> cap: 5 steps.

# Generate launchpad/docs/corpus/generated/orphaned-docs.md

ALREADY TRUE

- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is merged on `feature/621-generated-traceability`: builder discovery,
  `GenerationContext` (including `ctx.orphans`, `ctx.rel_path`), front-matter
  rendering and the `templates/generated-index.md` body skeleton all exist and
  need no changes.
- `index_defs/dependency_graph.py` (#896, merged) already renders an "Orphaned
  nodes" section from `ctx.orphans` -- valid nodes with no forward or inverse
  edge in either direction. At the current worktree revision this is 81
  orphans out of 205 valid nodes. This document must reuse that exact
  definition (`ctx.orphans`), never recompute orphan detection independently,
  so the two documents cannot silently disagree.
- `coverage.py` (#634, merged) exposes `build_coverage(root, corpus_root)` ->
  `CoverageReport`, whose rows carry a `nodes` tuple of canonical node ids that
  earn a `documented` disposition for some in-scope source item.
  `index_defs/coverage.py` (#892, merged) already shows the repo-root
  derivation pattern (`corpus_root.parts[-3:] == ("launchpad","docs","corpus")`
  -> three levels up) this task reuses verbatim.
- `templates/generated-index.md` (merged) itself names `orphaned-docs.md`
  (#902) explicitly as "An audit report" / "A filtered exception list, not a
  full listing" -- confirming this document is NOT index-shaped and must not
  declare `implements -> corpus-template-generated-index`, mirroring
  `dependency-graph.py` and `coverage.py`'s identical reasoning for their own
  non-index-shaped siblings.
- Measured at this revision (read-only, via `indexes.build_context` +
  `coverage.build_coverage`): 81 orphans; grouped by top-level corpus
  directory (capabilities 25, templates 20, architecture 18, layers 10,
  standards 5, development 3); 70 of 81 orphans still earn a `documented`
  coverage row despite having no corpus-graph edge, 11 do not (all
  `standards/`+`templates/` governance docs); corpus-wide median evidence
  entry count across all 205 valid nodes is 19, and exactly one of the 11
  "doubly-disconnected" orphans falls below that median.

STEP 1 [independent]

Write `launchpad/project-intelligence/corpus/index_defs/orphaned_docs.py`
exposing `SPEC` (dict form, following `dependency_graph.py`/`coverage.py`
conventions): `name="orphaned-docs"`, `output_path="generated/orphaned-docs.md"`,
`node_id="generated-orphaned-docs"`, `node_type="governance"`,
`audiences=("agent","developer","reviewer")`, `relationships=({"type":
"references","target":"corpus-agents"},)` only (no `implements`, per
ALREADY-TRUE above). `generate(ctx)` renders four subsections directly from
`ctx.orphans` (never recomputed):
1. Orphaned nodes (verbatim reuse of `ctx.orphans` + `ctx.rel_path`, same rows
   `dependency-graph.md` shows, explicitly disclosed as reused not recomputed).
2. Grouped by top-level corpus directory and by `node.schema.json` type, so
   concentration is visible.
3. Coverage cross-reference: for each orphan, whether its id appears in any
   `coverage.build_coverage(...)` row's `nodes` field (repo-root derivation
   copied from `index_defs/coverage.py`) -- "earns coverage despite no corpus
   edge" vs "doubly disconnected" (higher audit priority), each in its own
   table, both rendered even when empty.
4. Evidence-thinness flag: orphans whose own `evidence` entry count falls
   below the corpus-wide median entry count across all `ctx.valid_nodes`
   (computed fresh each run, never a hardcoded number), rendered even when
   empty.
Plus a required "## Distinction from `generated/dependency-graph.md`" section
(precedent: `index_defs/decision_index.py`'s "Distinction from
`decisions/INDEX.md`") naming exactly what this document adds: directory/type
concentration, coverage cross-reference, evidence-thinness flag -- the graph
document only lists the orphan set. `extra_evidence(ctx)` names the digest,
the orphan count, and the coverage/evidence-threshold read as a
digest-uncovered input (the same disclosure pattern `coverage.py`/
`decision_index.py` already use for reads outside `ctx.input_digest`).
Module docstring records the `node_type`/relationship reasoning above.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --only orphaned-docs` exits 0 and writes `generated/orphaned-docs.md`.

STEP 2 [needs 1] <- RUNS HERE

Confirm determinism and validity: rerun `--only orphaned-docs`, diff against
the first write (must be empty); run `--check --only orphaned-docs` (must
exit 0); run `python3 launchpad/project-intelligence/corpus/validate.py`
(must exit 0, pre-existing UNVERIFIED notices allowed).
done when: no-change rerun is byte-identical, `--check` exits 0, and `validate.py` exits 0.

STEP 3 [needs 1]

Write `launchpad/project-intelligence/corpus/tests/test_index_orphaned_docs.py`
following `test_index_dependency_graph.py`'s fixture-node pattern and
`test_index_coverage.py`'s fixture-repo-root pattern (a temp root with
`launchpad/docs/corpus/` so the coverage repo-root derivation resolves the
fixture, not the real repository). Cover: builder discovered with the
declared identity; two-run byte-identical output; an orphaned fixture node is
listed and a connected one is not; directory/type grouping renders; a fixture
node cited by a fixture source item appears in the "earns coverage" table and
an uncited orphan appears in "doubly disconnected"; the evidence-thinness
table reacts to a fixture node with fewer evidence entries than the fixture
corpus's own median; the required "Distinction from
`generated/dependency-graph.md`" heading is present; front matter carries
`generated-orphaned-docs` / `governance`; a read-only smoke test against the
real committed document.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_index_orphaned_docs.py"` runs this file's tests standalone and every one passes.

STEP 4 [needs 1, 3]

Self-review the full diff against #902's DoD line by line (exactly one
generated document; generator-produced, proven by the Step 2 rerun-diff; every
evidence citation names a file actually inspected in this task; `validate.py`
exit 0 already confirmed in Step 2).
done when: self-review completed and noted in the commit body (batch mode: no separate review-code pass).

STEP 5 [needs 1, 3]

Run the full corpus test suite gate command
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
and confirm OK with more than the 225-test base branch baseline, then commit
(builder module, generated file, test file, this plan) as the sole other tool
call.
done when: gate command reports OK and the signed commit exists.

PARALLEL

Steps 1 and (2, 3) are sequential on the builder module existing; 2 and 3 can
run independently of each other once 1 lands, both gating 4 and 5. There is no
genuine multi-agent parallelism available in this single-file, single-builder
task -- everything after Step 1 depends on its output.

GATES

- No-change rerun byte-identical (Step 2).
- `indexes.py --check --only orphaned-docs` exit 0 (Step 2).
- `validate.py` exit 0 (Step 2).
- Full corpus test suite OK, above the 225-test baseline (Step 5).
- Signed commit only after the gate command passes (Step 5).

BUDGET

One new builder module (~150-200 lines with its docstring, following the
`dependency_graph.py`/`decision_index.py` precedent length), one generated
Markdown file (framework-rendered), one test file (~150-200 lines following
`test_index_dependency_graph.py`/`test_index_coverage.py`), this plan file.
No edits to `indexes.py`, `coverage.py`, or any other shared/framework file.

OPEN

- Whether the evidence-thinness median should be recomputed from
  `ctx.valid_nodes` (all 205 nodes, chosen here) or from `ctx.orphans` alone
  (81 nodes) -- this plan chooses the corpus-wide median as the more
  meaningful, less self-referential baseline; a reviewer could reasonably
  prefer the narrower one.

LEFT OUT

- Recomputing orphan detection independently of `ctx.orphans` -- explicitly
  disallowed by this task's own brief, to avoid the two documents silently
  disagreeing.
- Any second hand-authored canonical corpus document, or product-behavior
  change -- out of scope per #902's own "Out of scope" list.
- Deciding whether `coverage.py --strict` becomes a CI gate, or fixing any
  individual coverage gap -- not this document's job.
