# Issue #951 — implementation/web/feature-map.md

Stated size: none given on the issue — matches the batch dispatch brief's own instruction to cap this task at 5 steps  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/architecture/containers/web.md` (id `architecture-containers-web`) is merged on `origin/launchpad` and documents `web/`'s responsibility, interfaces and deployment at the container level. `launchpad/docs/corpus/templates/implementation-reference.md` exists and is this node's required template. `launchpad/docs/corpus/implementation/web/feature-map.md` does not exist yet, and no `implementation/` node exists in the corpus at all — this is the first. Sibling issue #952 (`task: document implementation/web/web-app.md`) is a separate, unmerged task in this same batch that owns the web app's internals in depth; confirmed by `gh issue view 952`.

STEP 1  [independent] Gather evidence: read `web/`'s directory tree (`web/src/app`, `web/src/features/{invite,repos}`, `web/src/shared/{lib,ui,theme}`, `web/tests`), open every file used as a table row or claim source, and record `git rev-parse HEAD`. ← RUNS HERE
done when: every planned table row and claim has a file actually opened this session backing it, and the commit SHA is recorded.

STEP 2  [needs 1] Write `launchpad/docs/corpus/implementation/web/feature-map.md`: schema-valid front matter (`id: implementation-web-feature-map`, `type: implementation`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, evidence ledger with the commit citation plus one entry per substantive claim, `relationships: [{type: part-of, target: architecture-containers-web}]`) and the template's required body sections (Realization statement, Target, Implementation surface as a feature-to-directory table, Divergences, Verification, Relationships, Scope and omissions), explicitly noting #952 owns the internals depth this node does not attempt.
done when: the file exists with all seven required template sections and schema-shaped front matter.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root; fix any FAIL entries naming this node and re-run.
done when: the run reports zero FAIL entries for `implementation-web-feature-map` (a pre-existing ~21-failure baseline unrelated to this node is expected and left alone).

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call to earn the commit-gate stamp.
done when: the run prints `OK`.

STEP 5  [needs 4] Stage exactly the new document and this plan, then `git commit -s`.
done when: `git log -1` on this branch shows the new commit containing both files.

PARALLEL: none — one document, one plan, no independent sub-tasks.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must show zero FAIL entries for this node before committing. The commit-gate stamp requires the unittest command in STEP 4 to run alone in its own tool call, immediately before the commit. Push and PR creation are explicitly out of scope for this run — the batch integrates all 37 documents into one Feature-level draft PR later.

BUDGET: small — one corpus document (breadth map, not a deep-dive), no code changes, evidence gathering scoped to `web/`'s existing ~35 source files (read at header/structure depth, not line-by-line) plus the one already-merged sibling node (`architecture-containers-web`) and one sibling issue (#952) consulted for scope boundary.

OPEN: Whether `relationships: part-of: architecture-containers-web` is the right typed relationship versus `implements` was a judgement call — `part-of` was chosen because this node is a narrower, implementation-level breakdown of the same container the architecture node already documents (not a code-realizes-spec/decision/contract claim, which is what `implements` is for per the template's own boundary section), and the task brief names `architecture-containers-web` as the likely `part-of` target. A future reviewer may decide `implements` fits better once #952 (the deeper internals node) exists and the two can be compared.

LEFT OUT: No line-by-line internals of `git-client.ts`, the React Query hook implementations, or component render logic — that depth is #952's job, named explicitly in this node's Scope and omissions. No new `implements` edge toward a spec/decision node, since none exists yet for the web app's routing/feature conventions. No relationships toward any other unmerged sibling in this batch, for the same reason `architecture-containers-web` itself declined them: an edge to an unmerged node is a hard CI failure on `origin/launchpad`. No push, no PR — this run stops at the local commit per the batch's integration-phase design.
