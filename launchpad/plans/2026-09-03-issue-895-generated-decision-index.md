Issue #895 -- generate corpus document generated/decision-index.md

Stated size: batch corpus-doc task, one generated document + minimal generator/test change -> cap: 5 steps

ALREADY TRUE

- Feature #621's generator framework (`launchpad/project-intelligence/corpus/indexes.py`,
  issue #633) is merged on the local integration branch `feature/621-generated-traceability`
  and this worktree is branched from its tip. It owns discovery of `index_defs/` builder
  modules, canonical-input digesting, and rendering of front matter + the
  `templates/generated-index.md` body skeleton. A builder is add-a-file-only.
- `launchpad/project-intelligence/corpus/index_defs/decisions_index.py` (issue #845,
  merged) already generates `launchpad/docs/corpus/decisions/INDEX.md` (node id
  `decisions-index`): a per-record table of which canonical nodes' front-matter evidence
  cites each `launchpad/decisions/*.md` path, plus a listing of canonical nodes living
  under the corpus's own `decisions/` path prefix. Read directly this session.
- `launchpad/decisions/` holds 56 ADR-numbered decision records (`ADR-####-*.md`) plus one
  `README.md` (not a record) at this revision -- counted directly via `ls`, not assumed
  from the issue brief's "16" estimate, which does not match the tree.
- Each ADR record's YAML front matter carries a free-text `status:` field. At this
  revision the observed values are `Accepted` (46), `Proposed` (3), and `Superseded by
  ADR-####` (7, three distinct target ADRs) -- counted directly via `awk` over every file.
- `index_defs/coverage.py` (issue #892, merged) is the precedent for a builder that reads
  repository files outside the corpus root (the source inventory) as an additional,
  digest-uncovered input: it discloses this explicitly in its `unverified` bullets and its
  `extra_evidence` FACT entry, and still passes `validate.py` and its own test suite. This
  session's builder follows that same disclosure pattern to read `launchpad/decisions/`
  directly (filenames + `status:` field only, never decision content), since the framework's
  `GenerationContext` never loads ADR records (`decisions_index.py`'s own module docstring
  confirms they are not canonical inputs).
- `SLUG`/`NODE_ID` are pre-reserved and distinct from `decisions-index`: this document's
  node id is `generated-decision-index`, its builder module is a new file (not an edit to
  `decisions_index.py`), and its output path is `generated/decision-index.md` (not
  `decisions/INDEX.md`).

STEP 1 -- Author the builder module [independent]

Write `launchpad/project-intelligence/corpus/index_defs/decision_index.py` (new module;
`decisions_index.py` already exists and is untouched) exposing `SPEC`:
- `name: "decision-index"`, `output_path: "generated/decision-index.md"`,
  `node_id: "generated-decision-index"`, `node_type: "governance"` (same justification as
  `decisions_index.py`: no `decision`/`index` enum member, and this document governs the
  corpus's own decision-citation bookkeeping, not a product surface).
- `generate(ctx)` renders a **stats/coverage view**, not a per-record listing (the explicit
  distinction from `decisions-index`, stated in this document's own body text): (a) a
  decision-record count and a status-bucket breakdown (`Accepted` / `Proposed` /
  `Superseded` / any other observed raw value, bucketed by a fixed prefix rule so an unknown
  future status renders honestly rather than miscategorized); (b) a citation-coverage count
  (records cited by >=1 canonical node's front-matter evidence vs. cited by zero, reusing
  `decisions_index.py`'s own path-prefix-and-`.md`-suffix matching rule against
  `ctx.valid_nodes`, recomputed here rather than imported, since builders are isolated
  modules); (c) a explicit "coverage gap" table listing every zero-citation record's path
  and status bucket, sorted by path. A leading section states in prose that this document is
  a stats/coverage view distinct from `decisions/INDEX.md`'s per-record citing-node listing,
  and says which of the two a reader wants for which question.
- `extra_evidence(ctx)` returns one FACT entry citing `launchpad/decisions/` (the directory
  itself) stating that record filenames and `status:` front matter were read directly.
- `generate(ctx)`'s `unverified` bullets disclose (mirroring `coverage.py`) that
  `ctx.input_digest` covers canonical corpus inputs only, not `launchpad/decisions/`, so an
  unchanged corpus digest with an added/removed/re-statused ADR record can change this
  report's content.
- `relationships`: `implements -> corpus-template-generated-index`,
  `references -> corpus-agents`.
done when: the module exists, `python3 launchpad/project-intelligence/corpus/indexes.py --list`
shows a `decision-index` builder with no discovery error, and `--only decision-index` writes
`launchpad/docs/corpus/generated/decision-index.md`.

STEP 2 -- Generate and confirm determinism [needs 1] <- RUNS HERE

Run `python3 launchpad/project-intelligence/corpus/indexes.py --only decision-index` to
produce the target file. Re-run it a second time and confirm `git status --porcelain`
shows no diff on the generated file. Run
`python3 launchpad/project-intelligence/corpus/indexes.py --check --only decision-index`
and confirm exit 0.
done when: two consecutive generations are byte-identical and `--check` exits 0.

STEP 3 -- Focused builder test [needs 1]

Write `launchpad/project-intelligence/corpus/tests/test_index_decision_index.py` following
`test_index_coverage.py` and `test_index_decisions_index.py`'s conventions: builder
discovered with the expected identity (output path, node id, node type); a fixture corpus
plus a fixture `launchpad/decisions/` tree (hermetic temp directory, mirroring
`coverage.py`'s repo-root derivation and its test fixture shape) exercising a cited record,
an uncited record (must appear in the coverage-gap table), and a non-`Accepted`/`Proposed`
status bucket; two renders byte-identical; front matter carries `id: "generated-decision-index"`
and `type: "governance"`.
done when: `python3 -m unittest` on this file alone passes.

STEP 4 -- Full verification [needs 2, 3]

Run the full corpus test suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
and `python3 launchpad/project-intelligence/corpus/validate.py`, both from this worktree.
Self-review the full diff against issue #895's Definition of Done line by line (exactly one
generated document; generator-produced, not hand-authored; schema-valid front matter;
do-not-edit marker; generator/inputs/inclusion-exclusion/ordering named; regenerable;
no-change rerun produces no diff) and against the EXTRA distinction requirement (the
document's own body text states, explicitly, how it differs from `decisions/INDEX.md`).
done when: the full suite passes (225 baseline + this task's new tests), `validate.py` exits
0, and the self-review notes are ready to fold into the commit body.

STEP 5 -- Commit [needs 4]

Run the commit-gate recipe exactly as specified (test suite as the sole command in one Bash
call, then `git add` the builder module, generated file, test file and this plan in a
separate call, then `git commit -s`).
done when: one signed local commit exists on `task/895-generated-decision-index` containing
exactly those four files, and `git status --porcelain` is clean afterward.

PARALLEL

Steps 1 and 3 both depend only on the (already-true) framework and precedent reading, so a
second agent could draft the test file (step 3) from `decisions_index.py`'s and
`coverage.py`'s test conventions while step 1 is being written, then wire it to the real
`SPEC` once step 1 lands -- not exercised in this single-agent run, but the dependency graph
allows it.

GATES

- `python3 launchpad/project-intelligence/corpus/indexes.py --check --only decision-index`
  must exit 0 before commit.
- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit
  (pre-existing UNVERIFIED notices are non-fatal; a new hard error is this task's to fix).
- The full test suite (step 4) must pass before commit; no `--no-verify`, no touching a
  stamp file, no widening the inclusion rule to force a non-empty result.

BUDGET

One builder module, one generated Markdown file, one focused test file, this plan file.
No edits to `indexes.py`, `decisions_index.py`, `validate.py`, or any other builder.

OPEN

- Whether a future `decisions/topic`-style taxonomy field ever gets added to ADR front
  matter is not this task's to decide; the status-bucket view uses only the field that
  exists today.
- Whether `coverage.py`'s digest-uncovered-input disclosure pattern should become a named,
  reusable framework convention (rather than each builder restating it) is a framework
  question for a future issue, not this one.

LEFT OUT

- Restating or summarizing any individual ADR's decision content -- `launchpad/decisions/`
  and `decisions/INDEX.md` own that; this document counts and buckets, it does not narrate.
- A decisions-by-topic breakdown: no schema-grounded topic field exists on ADR front matter
  today, so a topic rule would rest on prose judgement rather than deterministic extraction,
  which the builder contract (issue #633) rules out.
- Any change to `decisions_index.py` or its output -- that node is merged and out of this
  task's scope; this task's document is additive and distinct, not a replacement.
