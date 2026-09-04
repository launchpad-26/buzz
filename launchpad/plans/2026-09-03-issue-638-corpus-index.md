Issue #638 — generate launchpad/docs/corpus/INDEX.md (corpus root index)
Stated size: none in issue  →  batch brief caps this family  →  cap: 5 steps

One builder module + one generated document + tests, per the #633 framework's
add-a-file-only contract. Base is the local integration branch
`feature/621-generated-traceability` (worktree task-638-corpus-index), which carries
the #633 framework and #634 coverage — both verified present on HEAD f7bba2836.

ALREADY TRUE  (verified against the worktree, not notes)
  - launchpad/project-intelligence/corpus/indexes.py exists on this base and ships
    zero builders (index_defs/ holds only __init__.py). Its SPEC contract, CLI
    (--list/--all/--only/--check/--root/--defs-dir), GenerationContext fields and
    duplicate-name/output loud-fail were all read directly from the file.
  - The framework renders front matter (status: draft, origin: launchpad), the
    do-not-edit marker, Generator/Inclusion/Relationships/Scope skeleton and the
    input digest itself; a builder supplies only sections/includes/excludes/ordering.
  - validate.py's node.schema.json type enum has no "index" value; governance is the
    documented precedent (README.md, standards/*, templates/generated-index.md all
    carry type: governance and say why).
  - Node ids corpus-agents and corpus-template-generated-index both exist on this
    base (grep '^id:' confirmed) — safe relationship targets per the brief.
  - tests/test_indexes.py::DiscoveryTest.test_shipped_index_defs_package_registers_no_builders
    asserts discover_builders() == [] against the SHIPPED index_defs/. Adding any
    real builder makes it fail; the DoD's "minimal generator/test change" covers
    updating it. Baseline suite on this base: 225 tests OK (re-run before building).
  - The corpus tree holds ~200 canonical nodes across root files plus agents/,
    architecture/, capabilities/, development/, layers/, standards/, templates/;
    schema/ is excluded by validate.py's discovery contract.

STEP 1  [independent]  <- RUNS HERE
        Builder module launchpad/project-intelligence/corpus/index_defs/index.py
        exposing SPEC: name "index", output_path "INDEX.md", node_id "corpus-index",
        node_type "governance" (justified in the module docstring), audiences
        agent/developer/reviewer, relationships references→corpus-agents and
        implements→corpus-template-generated-index. generate(ctx) lists EVERY
        canonical node ctx provides (valid ones as id/type/path table rows; any
        parse-failed ones in a separate honest subsection by path), grouped by
        top-level directory — corpus root group first, then directories in sorted
        name order; rows sorted by corpus-root-relative path within each group.
        Plus one small static section listing ctx.output_paths (registered
        generated outputs, which the canonical listing excludes by construction).
        done when: python3 launchpad/project-intelligence/corpus/indexes.py --list
        prints exactly "index<TAB>INDEX.md".

STEP 2  [needs 1]
        Generate: ... indexes.py --only index writes launchpad/docs/corpus/INDEX.md.
        Rerun the same command; then ... --check --only index.
        done when: second run leaves `git status --porcelain` for INDEX.md unchanged
        and --check exits 0.

STEP 3  [needs 1]
        Tests. (a) Minimal update to test_indexes.py: the shipped-package test
        becomes "shipped index_defs/ discovers cleanly" (loud-fail contract intact,
        no zero-builders assertion — that premise ends with this issue and every
        sibling). (b) New tests/test_index_index.py following test_indexes.py
        conventions: builder discovered from the real index_defs/ with the right
        name/output/node_id/type; two in-memory renders byte-identical; rendered
        front matter carries id corpus-index + type governance; every valid
        canonical node's id appears in the rendered listing and no registered
        output path is listed as a canonical row (uses the real corpus root
        read-only via build_context — no writes).
        done when: python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py" is OK, count > 225.

STEP 4  [needs 2, 3]
        Full gate: validate.py exit 0 (INDEX.md is now a validated node; hard
        errors are mine to fix, UNVERIFIED notices pre-existing), the exact
        unittest-discover commit-gate command as the sole command in one call,
        then git add builder/INDEX.md/tests/plan and git commit -s
        "docs(corpus): generate INDEX.md (#638)" with the inclusion rule in the body.
        done when: one local signed commit exists; nothing pushed.

PARALLEL
  Steps 2 and 3 are independent of each other once step 1 exists. Everything else
  is sequential. No file here is touched by another task except test_indexes.py
  (every sibling in this batch must make the same one-test change; identical edits
  merge cleanly, and the integrator resolves any residue).

GATES
  - indexes.py --check --only index exit 0 (no-change rerun proof)
  - validate.py exit 0
  - unittest discover OK (baseline 225 + new)
  - commit gate per brief §7; STOP on "no stamp found", never --no-verify

BUDGET
  One builder module (~90 lines), one generated file, one new test file, one
  minimal edit to an existing test, this plan. No edits to indexes.py, validate.py
  or any corpus node.

OPEN
  - Whether the integrator wants the shipped-package discovery test to assert a
    specific builder count as siblings land — this plan deliberately makes it
    count-agnostic so parallel tasks cannot fight over it.

LEFT OUT
  - extra_evidence on the SPEC: the framework's two FACT entries (generator +
    builder module citations, input digest) already satisfy the DoD's provenance
    bullet for a document nobody hand-wrote; a hand-authored extra claim would add
    surface without adding verifiability.
  - Listing node titles (H1s) in the index rows: title is body content, not front
    matter; parsing bodies would invent a second content contract beyond
    validate.py's. Id + type + path is enough to find any node.
  - generated/corpus-index.md — reserved for the separate generated-corpus-index
    task per the dispatch EXTRA note; this node's id corpus-index does not collide
    with it.
