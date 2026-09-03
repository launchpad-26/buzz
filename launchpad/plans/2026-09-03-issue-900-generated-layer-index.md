# Plan: issue #900 — generate corpus document generated/layer-index.md

Issue #900 (launchpad-26/buzz), parent PRD #621.
Stated size: none in the issue body; the #621 batch brief caps this family  ->  cap: 5 steps

Base: local branch `feature/621-generated-traceability` at 920bfb9f3101440c39488787ad6653dea335130c.
Worktree: `__worktrees/task-900-generated-layer-index`, branch `task/900-generated-layer-index`.

ALREADY TRUE
- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is on the base with 15 shipped builders in `index_defs/` and per-builder
  tests; the builder contract (module-level SPEC, generate(ctx) ->
  sections/includes/excludes/ordering) is proven by
  `index_defs/configuration_index.py` and
  `tests/test_index_configuration_index.py`, the closest precedent (#890,
  also a `layers/` subtree).
- The framework renders all front matter (status: draft, origin: launchpad),
  the do-not-edit marker, the input digest, and the generated-index body
  skeleton; a builder supplies only listing content and inclusion/exclusion
  bullets. `--check --only NAME` verifies no-change reruns.
- The subject set exists: 36 canonical nodes under
  `launchpad/docs/corpus/layers/` in four sub-layer directories — compute
  (10), configuration (9), lifecycle (6), observability (11) — every one
  `type: layers`, `status: draft`.
- Signal investigation (per dispatch EXTRA), verified on this base:
  - `type: layers` matches 37 nodes corpus-wide: the 36 real `layers/` nodes
    plus `generated/configuration-index.md` itself (the #890 builder's own
    generated output also declares `type: layers`, following the
    subject-type precedent) — a type rule over-includes a generated index
    that is not itself a layer node.
  - The path prefix `layers/` matches exactly the 36 real layer nodes and
    nothing else at this revision. It is the accurate signal, confirming
    #890's precedent (path prefix correct, `type: layers` over-includes)
    generalizes from the configuration subtree to the whole layers tree.
  - This divergence is moot at generation time regardless: `build_context`
    excludes every registered builder's `output_path` (including
    `generated/configuration-index.md`) from canonical inputs before any
    builder runs, so the over-inclusion is structurally prevented — but the
    module docstring and a generated divergence subsection still name it
    for transparency (#887 precedent), since the framework guard is not
    self-evident to a reader of the rendered document.
- `templates/generated-index.md` (id `corpus-template-generated-index`) and
  `AGENTS.md` (id `corpus-agents`) both exist on the base, so relationships
  targeting them resolve.
- Test baseline on the base is 333 tests OK (`python3 -m unittest discover
  -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`).

STEP 1 [independent]  <- RUNS HERE
Write the builder module
`launchpad/project-intelligence/corpus/index_defs/layer_index.py` exposing
SPEC: name `layer-index`, output `generated/layer-index.md`, node_id
`generated-layer-index`, node_type `layers` (the subject nodes' own enum
value — capability-index/configuration-index precedent; docstring must
justify this and the path-prefix rule over the type signal, citing the
37-vs-36 divergence above). Inclusion rule: every valid canonical node whose
corpus-root-relative path starts with `layers/`. Listing grouped into one
subsection per sub-layer (`compute`, `configuration`, `lifecycle`,
`observability`, derived from the path segment after `layers/`, sorted
alphabetically — which is already compute/configuration/lifecycle/
observability order — plus a `(root)` bucket for any direct `layers/*.md`
child and an `(other)` bucket for an unrecognized sub-layer name, so the
grouping never silently drops a node), each a table sorted by path with
columns Id | Path | Status. One divergence subsection: valid nodes anywhere
in the corpus with `type: layers` that are NOT under `layers/` (renders
"None at this revision." when empty — expected to be empty at generation
time per the framework's own output-path exclusion, named as such).
Relationships: `references -> corpus-agents`,
`implements -> corpus-template-generated-index`.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list`
shows `layer-index` and no discovery error.

STEP 2 [needs 1]
Generate the document: `... indexes.py --only layer-index` writes
`launchpad/docs/corpus/generated/layer-index.md`; never hand-edit it. Rerun
the generator and confirm `git status --porcelain` shows the file unchanged
after the second run; `... indexes.py --check --only layer-index` exits 0.
done when: TARGET exists with front-matter id `generated-layer-index`, all
36 layer nodes are listed across their four sub-layer subsections, and
`--check --only layer-index` exits 0.

STEP 3 [needs 1]
Write `launchpad/project-intelligence/corpus/tests/test_index_layer_index.py`
following test_index_configuration_index.py conventions: discovery/identity
test; fixture-corpus tests (path-prefix inclusion across two sub-layers;
sub-layer grouping puts each node in the right subsection in alphabetical
sub-layer order; a `(root)` node directly under `layers/` grouped correctly;
a `type: layers` node outside `layers/` surfaced in the divergence
subsection but not listed; an invalid node under the prefix appearing
nowhere); two-render stability; honest empty listing on a corpus with no
`layers/` tree; read-only real-corpus smoke test of the committed document's
id, type, do-not-edit marker and that all four known sub-layer headings
appear.
done when: from the worktree root, `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p
"test_index_layer_index.py"` reports OK with every listed behavior asserted.

STEP 4 [needs 2, 3]
Full validation and gate: `python3
launchpad/project-intelligence/corpus/validate.py` exits 0 (pre-existing
UNVERIFIED notices tolerated, no new hard errors), then the commit-gate
suite `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` — 333 baseline
tests plus this task's — all OK.
done when: validate.py exit 0 and the full discover run prints OK with more
than 333 tests.

STEP 5 [needs 4]
Self-review the diff against #900's DoD line by line, then commit builder
module + generated TARGET + test + this plan in one signed commit:
`docs(corpus): generate generated/layer-index.md (#900)` with a body naming
the inclusion rule.
done when: `git log -1` shows the signed commit containing exactly those
four files and `git status --porcelain` is clean.

PARALLEL
Steps 2 and 3 are independent of each other once Step 1 lands; everything
else is a chain. This whole task is one worktree in a wider batch — no
cross-worktree coordination is needed because the framework discovers
builders in sorted module order and duplicate names/paths fail loudly.

GATES
- Framework discovery (`--list`) after Step 1.
- Determinism gate after Step 2: second run diff-free plus `--check` exit 0.
- Focused test run after Step 3.
- validate.py + full 333+-test suite after Step 4 (the commit gate).
- Self-review against the DoD checklist before the commit in Step 5.

BUDGET
One builder module (~130 lines), one generated markdown file, one test file
(~150 lines), this plan. Zero edits to indexes.py, validate.py, any shared
file, or any hand-authored corpus node.

OPEN
- Whether a future revision should rename the `(root)`/`(other)` buckets if
  the layers tree grows a fifth sub-layer or a direct-child node — the
  grouping function handles both without a code change, but no such node
  exists at this revision to verify against.

LEFT OUT
- Documenting what each layer node says (the nodes own their content; the
  index only locates them) — required by the atomicity DoD line.
- A per-sub-layer index distinct from this whole-tree one (configuration
  already has its own at `generated/configuration-index.md` from #890; the
  other three sub-layers have no dedicated index, and creating one is out of
  scope for this issue).
- Any second generated document or "while here" cleanup — out of scope per
  the issue.
