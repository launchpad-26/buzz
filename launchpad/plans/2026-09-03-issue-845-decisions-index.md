# Plan — issue #845: generate decisions/INDEX.md

Issue #845 (launchpad-26/buzz), parent Feature #621. Alias: DOC:decisions/INDEX.md.
Stated size: the issue carries no Size line; the #621 batch dispatch caps this task at 5  ->  cap: 5 steps

Objective: one generated corpus document at `launchpad/docs/corpus/decisions/INDEX.md`,
produced by a new builder module under the #633 framework, indexing where the
canonical corpus depends on decision records — with the raw ADR files under
`launchpad/decisions/` explicitly out of scope as non-corpus inputs.

ALREADY TRUE
- indexes.py (#633) is merged on the base branch `feature/621-generated-traceability`:
  builder discovery from `index_defs/*.py` modules exposing `SPEC`, canonical-input
  contract via validate.py's `discover_markdown_files`/`load_nodes`, input digest,
  front-matter + body-skeleton rendering, CLI `--list/--all/--only/--check` and
  `--root/--defs-dir` for tests. It ships zero builders.
- `index_defs/` contains only `__init__.py`; `--list` prints "no builders registered".
- The corpus has 205 valid canonical nodes; 23 of them carry front-matter evidence
  citations naming `launchpad/decisions/*.md` paths (measured by loading nodes via
  validate.py and matching citation strings). No canonical node lives under a
  `decisions/` path prefix inside the corpus root, and no node declares a
  relationship targeting `corpus-template-decision-reference`.
- Relationship targets `corpus-agents`, `corpus-standard-decision-references` and
  `corpus-template-generated-index` all exist on origin/launchpad (verified via
  `git ls-tree origin/launchpad`).
- test suite baseline: 225 tests OK. `test_indexes.py` contains
  `test_shipped_index_defs_package_registers_no_builders`, which asserts the shipped
  `index_defs/` package discovers zero builders — true today, false the moment any
  real builder lands.

STEP 1 [independent]  <- RUNS HERE
Write the builder `launchpad/project-intelligence/corpus/index_defs/decisions_index.py`
exposing `SPEC` (name `decisions-index`, output `decisions/INDEX.md`, node_id
`decisions-index`, node_type `governance` with docstring justification, audiences
agent/developer/reviewer, relationships: implements → corpus-template-generated-index,
references → corpus-agents, references → corpus-standard-decision-references).
Deterministic inclusion rule, front-matter-only, no prose judgement:
(a) a canonical node is listed iff any `evidence[].evidence` citation string's path
    part (before any `#` fragment) starts with `launchpad/decisions/` and ends with
    `.md` — grouped one table row per cited decision-record path, citing node ids
    sorted;
(b) a second section lists canonical nodes whose corpus-root-relative path starts
    with `decisions/` — honestly empty today.
Excludes state plainly that the ADR files in `launchpad/decisions/` are not corpus
nodes and cannot be generator inputs, and that body-prose mentions do not count.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --only decisions-index`
writes `launchpad/docs/corpus/decisions/INDEX.md` with the 23-node/record listing.

STEP 2 [needs 1]
Determinism + validation: rerun the generator (no diff via `git status --porcelain`),
`--check --only decisions-index` exits 0, and
`python3 launchpad/project-intelligence/corpus/validate.py` exits 0 (pre-existing
UNVERIFIED notices tolerated; hard errors are mine).
done when: all three commands give the required results in one shell session.

STEP 3 [needs 1]
Focused test `launchpad/project-intelligence/corpus/tests/test_index_decisions_index.py`
following test_indexes.py conventions (path-loaded module, fixture corpus copied to a
temp dir; plus a read-only pass over the real corpus root): builder discovered with
the right name/output/node_id/type; two runs byte-identical; inclusion rule behaves
(a fixture node citing `launchpad/decisions/X.md` is listed, a non-citing node is
not); generated front matter carries `id: decisions-index` and `type: governance`.
Also the minimal shared-test edit the issue's "minimal generator/test change" allows:
`test_shipped_index_defs_package_registers_no_builders` becomes an assertion that
shipped-package discovery succeeds and every SPEC validates (the zero-builders
premise is retired by this task family by design).
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
runs 225+new tests, OK.

STEP 4 [needs 2, 3]
Commit gate and signed commit: full suite as the sole command, then
`git add` builder + generated INDEX.md + test + plan and
`git commit -s -m "docs(corpus): generate decisions/INDEX.md (#845)"` with a body
naming the inclusion rule.
done when: `git log -1` shows the signed commit containing exactly those files.

PARALLEL
Steps 2 and 3 are independent of each other after step 1; everything else is serial.

GATES
- `python3 launchpad/project-intelligence/corpus/indexes.py --check --only decisions-index` == 0
- `python3 launchpad/project-intelligence/corpus/validate.py` == 0
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` OK
- No hand edits to the generated file (regenerate-and-diff proves it).

BUDGET
4 steps of a 5-step cap. One builder module, one generated document, one focused
test file, one minimal shared-test adjustment, one plan file. No changes to
indexes.py, validate.py, or any canonical corpus node.

OPEN
- The shared-test adjustment in STEP 3 will textually conflict with sibling builder
  tasks making their own version of the same change; the batch integrator resolves
  it once. Flagged for the report's NOTES.

LEFT OUT
- Any hand-authored second corpus document (out of scope per the issue).
- Indexing the content/status/outcomes of the ADRs themselves — deciding or
  summarizing decisions is explicitly out of scope; this index only maps which
  canonical nodes cite which decision-record paths.
- Body-prose decision mentions (non-deterministic to attribute; front-matter
  evidence citations are the schema-grounded signal).
