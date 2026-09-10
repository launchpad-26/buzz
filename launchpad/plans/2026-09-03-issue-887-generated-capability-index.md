# Plan — issue #887: generate generated/capability-index.md

Issue #887 (launchpad-26/buzz), parent PRD #621. Alias: DOC:generated/capability-index.md.
Stated size: the issue carries no Size line; the #621 batch dispatch caps this task at 5 -> cap: 5 steps

Objective: one generated corpus document at
`launchpad/docs/corpus/generated/capability-index.md` — a deterministic,
schema-grounded index of every canonical corpus node whose front-matter
`type` is `capabilities` — produced by a new builder module under the #633
generator framework, never hand-edited, byte-identical on a no-change rerun.

ALREADY TRUE
- The #633 framework exists at launchpad/project-intelligence/corpus/indexes.py:
  discovers builder modules in index_defs/ (sorted, one module = one builder),
  validates SPEC fields against node.schema.json enums, derives the graph,
  renders ALL front matter (status: draft, origin: launchpad, framework
  evidence entries) and the templates/generated-index.md body skeleton
  (do-not-edit marker, Generator, Inclusion/exclusion, Relationships, Scope
  and omissions) around the builder's `sections`/`includes`/`excludes`.
  CLI: --list / --all / --only NAME / --check, --root/--defs-dir for tests.
- index_defs/ ships only __init__.py; discover_builders() currently returns []
  and test_indexes.py's `test_shipped_index_defs_package_registers_no_builders`
  asserts exactly that — adding any real builder makes that one test stale.
- The real corpus at this revision has 70 .md files under capabilities/**;
  69 carry `type: capabilities`, and exactly one
  (capabilities/communities/community-provisioning.md) carries
  `type: architecture` — so front-matter type, not path prefix, is the honest
  deterministic inclusion signal, and the two signals measurably diverge.
- No node outside capabilities/** carries `type: capabilities`.
- `capabilities` is a node.schema.json type-enum value; audiences enum is
  agent/developer/operator/reviewer.
- Relationship targets `corpus-agents` (AGENTS.md) and
  `corpus-template-generated-index` (templates/generated-index.md) are both
  merged on origin/launchpad.
- Test suite baseline on this base: 225 tests OK via
  `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
- launchpad/docs/corpus/generated/ does not exist yet; the framework mkdirs it.

STEP 1 [independent]  <- RUNS HERE
Write launchpad/project-intelligence/corpus/index_defs/capability_index.py —
one new module, no shared-file edits for the builder itself. Module-level SPEC:
name "capability-index", output_path "generated/capability-index.md",
node_id "generated-capability-index", node_type "capabilities" (justified in
the module docstring: a subject-specific index fits its subject's own type,
per the batch precedent note), audiences (agent, developer, reviewer),
relationships references->corpus-agents and
implements->corpus-template-generated-index. generate(ctx):
- inclusion rule: ctx.valid_nodes where node.data.get("type") == "capabilities"
  (front-matter field only, never path or prose judgement);
- listing: one markdown table sorted by corpus-root-relative path (groups by
  capability area naturally), columns Area / Id / Path / Status, where Area is
  the path segment under capabilities/ (or the parent directory for a
  hypothetical capabilities-typed node elsewhere);
- a deterministic divergence subsection: nodes whose path is under
  capabilities/ but whose type is NOT capabilities (today: exactly
  community-provisioning.md, type architecture) — computed from ctx each run,
  never hand-listed;
- includes/excludes bullets state the type-based rule, the invalid-node
  exclusion (node.error is not None), and that path prefix is deliberately not
  the rule; ordering states the path sort.
done when: `python3 launchpad/project-intelligence/corpus/indexes.py --list`
shows capability-index and `--only capability-index` writes
launchpad/docs/corpus/generated/capability-index.md.

STEP 2 [needs 1]
Determinism + validation against the real corpus, and the minimal shared-test
adjustment the DoD's "minimal generator/test change" clause covers:
- rerun `--only capability-index`; `git status --porcelain` shows the generated
  file unchanged; `--check --only capability-index` exits 0;
- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
  (UNVERIFIED notices are pre-existing and non-fatal);
- replace test_indexes.py's now-false zero-shipped-builders assertion with the
  invariant that stays true as the #886-#906 siblings land: every shipped
  builder discovered from the real index_defs/ has an output_path under
  generated/ (discovery itself already hard-fails invalid SPECs). This is the
  only shared-file edit, it is one test method, and it is required for the
  suite to pass at all with any real builder present.
done when: both generator invariants hold and validate.py exits 0.

STEP 3 [needs 1]
Focused test launchpad/project-intelligence/corpus/tests/test_index_capability_index.py
following test_indexes.py conventions (load indexes.py by path as
corpus_indexes; fixtures via tempfile copies, plus read-only use of the real
corpus root for smoke assertions):
- builder discovered from the real index_defs/ with the expected name,
  output_path, node_id "generated-capability-index" and node_type
  "capabilities";
- inclusion rule behaves on a small fixture corpus: a capabilities-typed node
  is listed; a node under a capabilities/ path with a different type is NOT
  listed and appears in the divergence subsection; an invalid node is not
  listed;
- output stable: two renders over the same fixture are byte-identical;
- against the real corpus root (read-only): generated front matter carries
  id generated-capability-index and type capabilities, and the do-not-edit
  marker is present.
done when: full suite `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` shows OK
(225 baseline + new tests).

STEP 4 [needs 2, 3]
Commit gate + signed commit. Run the unittest discover command as the sole
command of its own tool call inside this worktree (verify-gate stamp), then in
a separate call `git add` the builder module, the generated TARGET, the focused
test, the one-method test_indexes.py adjustment and this plan, and
`git commit -s -m "docs(corpus): generate generated/capability-index.md (#887)"`
with a body naming the inclusion rule.
done when: one signed local commit exists on task/887-generated-capability-index
and the suite output shows OK.

PARALLEL
None — steps 2 and 3 both need step 1's builder; this is one builder task.

GATES
- check-plan.sh exit 0 on this plan before building.
- No-change rerun: second `--only capability-index` run leaves git clean;
  `--check --only capability-index` exits 0.
- validate.py exit 0 against the real corpus root.
- verify-gate stamp: the unittest discover command run alone in its own tool
  call immediately before the commit; suite OK.

BUDGET
One builder module (~120-160 lines with docstring), one focused test file
(~150-200 lines), one generated document (framework-emitted), a one-method
replacement in test_indexes.py, one plan. No new dependencies, no edits to
indexes.py or validate.py, no other corpus documents.

OPEN
- Sibling tasks #886-#906 will each touch the same zero-builders test method;
  whichever merges second resolves a trivial conflict in favour of the
  builder-count-agnostic invariant. The batch coordinator owns merge order.
- Whether a capability index should also list per-area rollup nodes
  differently (channel.md vs channel-types.md) is curation for a future
  revision; this index lists every capabilities-typed node uniformly.

LEFT OUT
- Any second corpus document, and any hand-edit to the generated file
  (regeneration is the only write path).
- Changing the framework's rendering, evidence, or discovery (owned by #633).
- The other fifteen generated/* documents (#886, #888-#906 own those).
- Runtime product behavior (issue's out-of-scope list).
