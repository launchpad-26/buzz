# Plan: issue #890 — generate corpus document generated/configuration-index.md

Issue #890 (launchpad-26/buzz), parent PRD #621.
Stated size: none in the issue body; the #621 batch brief caps this family  ->  cap: 5 steps

Base: local branch `feature/621-generated-traceability` at a7b215bb254e2cf5a175bfc6ec0df2e6e1aed60d.
Worktree: `__worktrees/task-890-generated-configuration-index`, branch `task/890-generated-configuration-index`.

ALREADY TRUE
- The #633 generator framework (`launchpad/project-intelligence/corpus/indexes.py`)
  is on the base with five shipped builders in `index_defs/` (glossary, index,
  decisions-index, api-index, capability-index) and per-builder tests; the
  builder contract (module-level SPEC, generate(ctx) -> sections/includes/
  excludes/ordering) is proven by `index_defs/capability_index.py` and
  `tests/test_index_capability_index.py`.
- The framework renders all front matter (status: draft, origin: launchpad),
  the do-not-edit marker, the input digest, and the generated-index body
  skeleton; a builder supplies only listing content and inclusion/exclusion
  bullets. `--check --only NAME` verifies no-change reruns.
- The subject set exists: 9 canonical nodes under
  `launchpad/docs/corpus/layers/configuration/` (agent-configuration,
  defaults, desktop-configuration, environment-configuration, feature-flags,
  mobile-configuration, relay-configuration, secrets, validation), all with
  `type: layers`, all `status: draft`.
- Signal investigation (per dispatch EXTRA), verified on this base:
  - `type: layers` is NOT configuration-specific — `layers/compute/`,
    `layers/lifecycle/` and `layers/observability/` nodes carry it too, and
    node.schema.json's type enum has no `configuration` value.
  - `implements -> corpus-template-configuration` matches only 8 of 9:
    `defaults.md` declares no relationships at all (its body records the
    template was unmerged when it was authored), so a relationship rule
    silently drops a real configuration node.
  - The path prefix `layers/configuration/` matches exactly the 9 real
    configuration nodes at this revision. It is the accurate signal.
- `templates/configuration.md` (id `corpus-template-configuration`,
  type governance, status active) and `templates/generated-index.md`
  (id `corpus-template-generated-index`) both exist on the base, so
  relationships targeting them resolve.
- Test baseline on the base is 225 tests OK.

STEP 1 [independent]  <- RUNS HERE
Write the builder module
`launchpad/project-intelligence/corpus/index_defs/configuration_index.py`
exposing SPEC: name `configuration-index`, output
`generated/configuration-index.md`, node_id `generated-configuration-index`,
node_type `layers` (the subject nodes' own enum value — capability-index
precedent: a subject-specific index takes its subject's type; docstring must
justify this and the path-prefix rule over type/relationship signals).
Inclusion rule: every valid canonical node whose corpus-root-relative path
starts with `layers/configuration/`. Listing table sorted by path with
columns Id | Path | Status | Implements configuration template (yes/no from
the node's own forward `implements -> corpus-template-configuration` edge).
Two divergence subsections, each rendering "None at this revision." when
empty: (a) listed nodes whose `type` is not `layers`; (b) valid nodes outside
the prefix that declare `implements -> corpus-template-configuration`.
Relationships: `references -> corpus-agents`,
`implements -> corpus-template-generated-index`,
`references -> corpus-template-configuration`.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list`
shows `configuration-index` and no discovery error.

STEP 2 [needs 1]
Generate the document: `... indexes.py --only configuration-index` writes
`launchpad/docs/corpus/generated/configuration-index.md`; never hand-edit it.
Rerun the generator and confirm `git status --porcelain` shows the file
unchanged after the second run; `... indexes.py --check --only
configuration-index` exits 0.
done when: TARGET exists with front-matter id
`generated-configuration-index`, the 9 configuration nodes are listed with
`defaults.md` marked as not implementing the template, and `--check --only
configuration-index` exits 0.

STEP 3 [needs 1]
Write `launchpad/project-intelligence/corpus/tests/test_index_configuration_index.py`
following test_index_capability_index.py conventions: discovery/identity
test; fixture-corpus tests (path-prefix inclusion; a `layers`-typed node
under another `layers/` subtree excluded; a non-`layers` node under the
prefix listed AND surfaced in divergence (a); an outside implementer
surfaced in divergence (b) but not listed; an invalid node under the prefix
appearing nowhere; a template-implementing node marked yes and a
relationship-less node marked no); two-render stability; honest empty
listing on a corpus with no `layers/configuration/`; read-only real-corpus
smoke test of the committed document's id, type and do-not-edit marker.
done when: from the worktree root, `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p
"test_index_configuration_index.py"` reports OK with every listed behavior
asserted.

STEP 4 [needs 2, 3]
Full validation and gate: `python3
launchpad/project-intelligence/corpus/validate.py` exits 0 (pre-existing
UNVERIFIED notices tolerated, no new hard errors), then the commit-gate
suite `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` — 225 baseline
tests plus this task's — all OK.
done when: validate.py exit 0 and the full discover run prints OK with
more than 225 tests.

STEP 5 [needs 4]
Self-review the diff against #890's DoD line by line, then commit builder
module + generated TARGET + test + this plan in one signed commit:
`docs(corpus): generate generated/configuration-index.md (#890)` with a
body naming the inclusion rule.
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
- validate.py + full 225+-test suite after Step 4 (the commit gate).
- Self-review against the DoD checklist before the commit in Step 5.

BUDGET
One builder module (~120 lines), one generated markdown file, one test file
(~150 lines), this plan. Zero edits to indexes.py, validate.py, any shared
file, or any hand-authored corpus node.

OPEN
- Whether a future revision should re-point the rule at
  `implements -> corpus-template-configuration` once `defaults.md` gains the
  edge — the generated divergence subsections make that drift visible each
  run, but the switch itself is a maintainer decision, not this task's.

LEFT OUT
- Documenting what each configuration node says (the nodes own their
  content; the index only locates them) — required by the atomicity DoD line.
- Adding the missing `implements` edge to `defaults.md` — that edits a
  hand-authored canonical node, explicitly out of scope for this issue.
- Any second generated document or "while here" cleanup — out of scope per
  the issue.
