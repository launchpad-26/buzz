# Plan — issue #634: corpus completeness and source-coverage accounting

Issue #634 (launchpad-26/buzz), parent Feature #621. Alias: TASK-CORPUS-COVERAGE.
Stated size: the issue carries no Size line; the #621 batch dispatch caps this task at 5  ->  cap: 5 steps

Objective: compare the source inventory (inventory.py), a #626 manifest, and the
canonical corpus nodes (validate.py's discovery/front-matter contract) so every
in-scope inventory item gets exactly one positive disposition — `documented`,
`represented-elsewhere`, `generated-only`, `explicitly-excluded` — and anything
else is a visible `GAP` that can never satisfy completeness.

ALREADY TRUE
- inventory.py exists and defines the in-scope item universe: `InventoryItem`
  (category, source_key, path, symbol) plus `unrecognized_areas`, deterministic
  JSON, `--root` override (launchpad/project-intelligence/corpus/inventory.py).
- manifest.py exists: `build_manifest(plan)` -> validated `ManifestRow`s with
  `path` (the task alias per issue_plan.py's `alias=row.path`), `issue_title`
  and `source_start_points`. Library only, no CLI, no committed manifest file.
- validate.py exists and owns node discovery + front-matter parsing:
  `load_nodes(corpus_root)` -> `LoadedNode(path, id, data, error)`, plus the
  citation-form regexes (`_FILE_POSITION_RE`, `_MARKDOWN_LINK_RE`, URL/commit/
  edge/tool forms) and `DEFAULT_ROOT = "launchpad/docs/corpus"`.
- Tests load sibling modules by `importlib.util.spec_from_file_location`
  (project-intelligence is not a legal package name); suite runs via
  `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` — 170 tests today.
- There is no coverage.py and no dispositions/exclusions registry anywhere in
  the tree yet.

STEP 1 [independent]  <- RUNS HERE
Build launchpad/project-intelligence/corpus/coverage.py: Python API first.
- Load siblings (inventory, manifest, validate) by path with a shared
  sys.modules cache (same names tests already use, e.g. `corpus_inventory`).
- `build_coverage(root, corpus_root, manifest_rows=(), registry=None)` ->
  `CoverageReport` of frozen `CoverageRow`s: category, source_key, path,
  disposition, nodes (tuple of node ids), aliases (tuple of task aliases),
  detail.
- Positive assignment only, precedence documented-first:
  (a) `documented` when a loaded node's file/position evidence citation covers
      the item (same file with line containment, or citation file under the
      item's directory path), or a manifest row's source_start_points name the
      item (exact source_key, or path containment either direction); rows link
      every covering node id and task alias, sorted.
  (b) else the auditable registry's entry decides: one of
      `represented-elsewhere` (requires non-empty accounted_by naming node ids
      or aliases), `generated-only`, `explicitly-excluded` (both require a
      reason). coverage.py never invents these.
  (c) else `GAP`. inventory's `unrecognized_areas` are always GAP rows — the
      fix for those is teaching inventory.py, not papering over in coverage.
- Registry validation is fail-closed: unknown disposition value (including any
  "not-examined"/"unknown" spelling), `documented` in the registry, duplicate
  or inventory-unmatched source_key, missing reason/accounted_by all raise
  `CoverageInputError`. Nodes whose `LoadedNode.error` is set contribute no
  citations and surface as findings (their absence shows up as visible gaps,
  never silent passes).
- `CoverageReport.complete` is True exactly when the report has zero GAP rows;
  findings are advisory context and never substitute for a disposition.
done when: `python3 -c` smoke-import of coverage.py succeeds and
`build_coverage` returns rows for a two-item fixture in an interactive check.

STEP 2 [needs 1]
CLI on top of the API, matching validate.py/inventory.py conventions.
- `--root PATH` (repo root, default via git), `--corpus-root PATH` (default
  `<root>/launchpad/docs/corpus`), `--manifest PATH` (JSON: `{"rows": [...]}`
  or a bare list; validated through manifest.build_manifest), `--dispositions
  PATH` (registry JSON), `--format tsv|markdown` (default tsv), `--strict`.
- stdout: only the sorted table (header + rows, stable sort by category then
  source_key, no timestamps) — byte-identical across runs. stderr: one summary
  line (`COMPLETE ...` / `INCOMPLETE: N gap(s)`) plus findings.
- Exit codes, documented in the module docstring for the later CI job:
  0 = report produced (gaps are advisory by default), 1 = `--strict` and gaps
  or findings exist, 2 = input error (missing corpus root, malformed manifest
  or registry). CI can therefore distinguish hard failures (2) from advisory
  findings (0) and enforce completeness only where it opts in (`--strict`).
done when: `python3 launchpad/project-intelligence/corpus/coverage.py
--format tsv` exits 0 against the real repo and prints a deterministic table.

STEP 3 [needs 1]
Tests in launchpad/project-intelligence/corpus/tests/test_coverage.py, fixture
trees built under tempfile like test_inventory.py (never asserting on real
repo content except one smoke test):
- every disposition class exercised (documented via node citation, documented
  via manifest start point, represented-elsewhere, generated-only,
  explicitly-excluded);
- gap visibility: an unaccounted item and an unrecognized area both appear as
  GAP and flip completeness false;
- the no-not-examined rule: a registry entry with disposition "not-examined"
  (and "unknown") raises CoverageInputError; a GAP row never counts toward
  completeness;
- linkage: a documented row carries the covering node id(s) and task alias(es);
- determinism: two full CLI runs over the same fixture produce byte-identical
  stdout;
- exit codes: 0 with gaps, 1 with --strict and gaps, 2 on malformed registry.
done when: the full suite `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` passes (170
baseline + new tests, zero failures).

STEP 4 [needs 3]
Validate + commit. Run `python3 launchpad/project-intelligence/corpus/
validate.py` (must exit 0 — this task adds no corpus documents), run the full
unittest suite as the sole command of its own tool call to earn the verify-gate
stamp, then `git add` + `git commit -s` with
`feat(corpus): completeness and source-coverage accounting (#634)`.
done when: one signed local commit exists on task/634-corpus-coverage and the
suite output shows OK.

PARALLEL
None — steps 2 and 3 both need step 1's API, and this is one builder.

GATES
- verify-gate pre-commit stamp: the unittest discover command above, run alone
  in its own tool call, in this worktree, immediately before the commit.
- validate.py exit 0 against the real corpus root.
- check-plan.sh exit 0 on this plan before building.

BUDGET
One module (~350-450 lines with docstrings), one test file (~350 lines), one
plan. No new dependencies beyond what validate.py already imports (yaml,
jsonschema arrive only via loading validate.py; coverage.py itself imports
stdlib + siblings). No corpus documents, no registry file committed — the
registry is an input, exercised through test fixtures and `--dispositions`.

OPEN
- Where the auditable dispositions registry will live in the tree (a committed
  JSON under project-intelligence/corpus/, or per-decision records) is a
  curation choice for whoever first records an exclusion — #634 only fixes its
  schema and the rule that coverage.py reads, never writes, it.
- Whether CI runs `--strict` from day one belongs to the CI-wiring task, not
  here; both modes are provided and documented.

LEFT OUT
- Authoring canonical corpus documents (issue's out-of-scope list).
- generated/coverage.md rendering — that is #892, which consumes this API.
- Changing inventory.py's notion of in-scope (reused as-is, per the brief).
- Staleness/line-length checking of citations — validate.py deliberately
  defers that to the staleness work; coverage inherits the same boundary.
