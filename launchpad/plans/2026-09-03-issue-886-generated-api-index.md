Issue #886 — generate corpus document generated/api-index.md
Stated size: none given in the issue  →  batch brief for Feature #621 caps every generated-document task  →  cap: 5 steps

ALREADY TRUE  (verified against the worktree at f7bba2836, not notes)
  - Worktree __worktrees/task-886-generated-api-index exists on branch
    task/886-generated-api-index, based on feature/621-generated-traceability
    (carries #633's generator framework and #634's coverage work).
  - The framework (launchpad/project-intelligence/corpus/indexes.py) discovers
    builder modules from index_defs/, renders all front matter (status: draft,
    origin: launchpad) and the templates/generated-index.md body skeleton, and
    embeds a sha256 input digest instead of timestamps. index_defs/ currently
    holds only __init__.py — no name/output collision possible for api-index.
  - validate.py's load_nodes finds 205 canonical nodes on this base; ZERO carry
    front-matter type: interfaces-events (checked by loading every node and
    counting types). No interfaces/ path subtree exists; no canonical node
    declares any relationship toward corpus-template-interface or
    corpus-template-event-kind. So the only schema-grounded API-surface signal
    available is the type enum value itself, and it currently matches nothing.
    The brief explicitly blesses an honest empty listing over a widened rule.
  - Relationship targets corpus-agents (AGENTS.md) and
    corpus-template-generated-index (templates/generated-index.md) both resolve
    on this base — checked by grepping their id: lines.
  - tests/test_indexes.py::test_shipped_index_defs_package_registers_no_builders
    asserts discover_builders() == [] — it MUST fail the moment any real builder
    ships. The issue's DoD allows "the minimal generator/test change required",
    so that one test changes to assert clean discovery instead of emptiness.

STEP 1  [independent]  <- RUNS HERE
        Write the builder module
        launchpad/project-intelligence/corpus/index_defs/api_index.py exposing
        SPEC: name api-index, output_path generated/api-index.md, node_id
        generated-api-index, node_type interfaces-events (the subject's own
        type — justified in the module docstring), audiences agent+developer,
        relationships references→corpus-agents and
        implements→corpus-template-generated-index. generate(ctx) selects
        valid canonical nodes with front-matter type == "interfaces-events",
        sorts rows by node id, and renders an explicit "zero nodes matched"
        section when the selection is empty rather than widening the rule.
        extra_evidence records the match count at the input digest.
        done when: python3 launchpad/project-intelligence/corpus/indexes.py
        --list prints "api-index  generated/api-index.md".

STEP 2  [needs 1]
        Generate the document: indexes.py --only api-index writes
        launchpad/docs/corpus/generated/api-index.md. Never hand-edit it; wrong
        content means fixing the builder and regenerating.
        done when: a second --only api-index run leaves git status --porcelain
        unchanged for the file, and --check --only api-index exits 0.

STEP 3  [independent]
        Minimal shared-test change: in tests/test_indexes.py replace the
        emptiness assertion in
        test_shipped_index_defs_package_registers_no_builders with an assertion
        that the shipped index_defs/ package discovers cleanly (every SPEC
        validates; discovery raises nothing) — true at zero builders and at N,
        so parallel sibling tasks stay green against the same line.
        done when: that single test passes both with and without
        index_defs/api_index.py present (verified by running it once, since the
        builder exists by then; the zero-builder case is the framework's own
        fixture-tested path).

STEP 4  [needs 1]
        Focused test launchpad/project-intelligence/corpus/tests/
        test_index_api_index.py following test_indexes.py conventions (path-load
        indexes.py as corpus_indexes, fixtures into temp copies): builder
        discovered from the real index_defs/ with the right name/output/node_id;
        two generations byte-identical; inclusion rule includes an
        interfaces-events fixture node and excludes an architecture one; empty
        corpus renders the explicit empty-listing sentence; generated front
        matter carries id generated-api-index and type interfaces-events.
        done when: python3 -m unittest that file passes.

STEP 5  [needs 2, 3, 4]
        Full gate: python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py" all OK
        (baseline 225 + new), python3 launchpad/project-intelligence/corpus/
        validate.py exits 0, then git add builder+generated+test+plan and
        git commit -s with the inclusion rule named in the body.
        done when: the signed commit exists and the suite output says OK.

PARALLEL
  Steps 1 and 3 touch disjoint files and could run in parallel; everything else
  is a chain. Within this batch, sibling tasks (e.g. #887 capability-index) add
  their own index_defs/ modules — no shared file collides except the STEP 3
  test line, which is why STEP 3 writes it count-agnostically.

GATES
  - Commit gate: the full unittest discover run as the sole command in its own
    call, then a separate git add/commit -s call. If the gate refuses with no
    stamp found: stop and report, never touch the stamp, never --no-verify.
  - validate.py exit 0 (pre-existing UNVERIFIED notices are non-fatal).
  - No-change rerun produces no diff (issue DoD, checked in STEP 2).

BUDGET
  One builder module (~90 lines), one generated document, one focused test
  (~120 lines), a one-assertion edit to test_indexes.py, this plan. No edits to
  indexes.py, validate.py, or any corpus hand-authored node.

OPEN
  - Whether the coordinator wants sibling builders to converge on one shared
    wording for the STEP 3 test body to avoid textual merge conflicts at
    integration — each sibling editing the same assertion independently will
    conflict textually even when semantically identical. Integrator's call.

LEFT OUT
  - Widening the inclusion rule (path keywords, prose matching, architecture
    flow nodes that merely describe endpoints) — the brief forbids widening to
    look fuller; the honest state of this base is zero interfaces-events nodes.
  - Any canonical interface/event node authoring — task branches
    task/1000–1022 own those; this index will populate as they merge.
  - Relationships toward nodes that exist only in this run's worktrees.
