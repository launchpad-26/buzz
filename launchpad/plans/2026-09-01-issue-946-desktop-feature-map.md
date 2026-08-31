# Issue #946 — implementation/desktop/feature-map.md

Stated size: issue #946 carries no Size label; the corpus-batch-author dispatch brief caps this task at 5 steps.  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/schema/node.schema.json`
are merged on `origin/launchpad`. `launchpad/docs/corpus/architecture/containers/desktop.md`
(id `architecture-containers-desktop`) is merged and its own *Scope and omissions*
names "the React frontend's internal feature/component architecture" as an explicit
gap this task fills the breadth half of. No `launchpad/docs/corpus/implementation/`
subtree exists yet on `origin/launchpad` — confirmed via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, so this is the
corpus's first `implementation`-typed node and no sibling `implements`/`part-of`
target other than `architecture-containers-desktop` exists.
`launchpad/docs/corpus/implementation/desktop/feature-map.md` does not exist yet
(confirmed by `ls`).

STEP 1  [independent] Gather evidence: `ls desktop/src/features/` (30 top-level
feature directories) and one level inside each; `ls desktop/src/app/` and
`desktop/src/app/routes/`; read `desktop/src/app/routes.ts` for the actual
TanStack Router route table; grep `desktop/src/app/**` for `features/<name>`
imports to find which features are wired directly from routes/shell versus
composed from inside another feature's UI (e.g. `chat`, `forum`, `gifs`,
`search`, `moderation`, `agent-memory`, `identity-archive`, `mesh-compute`,
`community-members` have no top-level route and are imported from sibling
features instead); confirm the `shared/features/` (feature-flagging: `FeatureGate`,
`manifest.ts`, `resolveEnabled.ts`) vs top-level `features/` (feature-module
convention) naming collision by listing `desktop/src/shared/features/`.
Record `git rev-parse HEAD`. ← RUNS HERE
done when: the feature-to-directory table and the routing/import cross-reference are
recorded (working notes, not necessarily committed) and `git rev-parse HEAD` has been
run and its output captured for the provenance citation.

STEP 2  [needs 1] Write the plan file (this file) and run
`~/.claude/skills/plan-issue/check-plan.sh launchpad/plans/2026-09-01-issue-946-desktop-feature-map.md`;
fix and re-run until it exits 0.
done when: `check-plan.sh` prints "Mechanical checks: clean" and exit code 0.

STEP 3  [needs 2] Write `launchpad/docs/corpus/implementation/desktop/feature-map.md`
following `implementation-reference.md`'s required sections (Realization statement,
Target, Implementation surface, Divergences, Verification, Relationships, Scope and
omissions), front matter `id: implementation-desktop-feature-map`, `type:
implementation`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`, one evidence entry per substantive claim (FACT for every directory listing
and import grep actually run, classed honestly), and `relationships: [{type: part-of,
target: architecture-containers-desktop}]`. Body scoped as a feature-to-directory
index (breadth), explicitly naming #947 (frontend internals) and #948 (Tauri backend
internals) as the depth owners in *Scope and omissions*.
done when: the file exists at that path with schema-required front-matter keys present
and all seven template sections present as `##`/`###` headings.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`;
if nonzero exit, diff the failing node list against a `git stash`d baseline run on
`origin/launchpad` to confirm any pre-existing failures are not newly introduced by
this node; fix and re-run until this node's own entry reports no FAIL.
done when: `validate.py` reports zero FAIL lines whose node path is
`launchpad/docs/corpus/implementation/desktop/feature-map.md`.

STEP 5  [needs 4] As the sole command in its own tool call, run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
and confirm `OK`; then, in a separate tool call, `git add` the two new files and
`git commit -s` with message `docs(corpus): add desktop feature-map implementation
reference (#946)`.
done when: the unittest run prints `OK` and `git log -1 --stat` shows both files in a
new local commit signed with `-s`.

PARALLEL: none — single file, single task, no independent sub-work to fan out.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report zero
FAIL entries for this node (a pre-existing ~21-failure baseline unrelated to this task
already exists on `origin/launchpad`, per the task brief — confirmed rather than
assumed via the `git stash` diff in STEP 4). `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` before the
commit gate is earned. `review-adjudicate` and the cross-model final review pass are
deferred to the batch integration phase, not run here — this task stops after the
local commit, per its own dispatch instructions (no push, no PR).

BUDGET: small — one Markdown document, no code changes, evidence gathering scoped to
directory listings and import greps across `desktop/src/features/` (28 directories,
one level deep) and `desktop/src/app/`.

OPEN: Whether `implements` (rather than only `part-of`) should eventually target a
future corpus node for CLAUDE.md's own "Features are organized under
desktop/src/features/" convention statement is left to a human — no such convention
node exists in the corpus yet, so this task names that convention by file path
(`CLAUDE.md`) in the *Target* section rather than inventing an `implements` edge to a
nonexistent id, per `AGENTS.md`'s explicit rule against that.

LEFT OUT: No deep-dive into any single feature's internal design, hooks, or state
management (sibling issues #947 frontend internals and #948 Tauri backend internals
own that depth). No claim about `mobile/` or `web/`'s own feature organization — this
node is desktop-scoped only. No attempt to reconcile the `shared/features/`
(feature-flagging) vs `features/` (feature-module) naming collision in code — it is
reported as a fact in *Divergences*, not fixed. No new `relationships` beyond
`part-of: architecture-containers-desktop` — no other merged node is a legitimate
target at this task's merge base.
