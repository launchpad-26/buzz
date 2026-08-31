# Issue #844: document capabilities/workflows/workflow.md

Parent: Feature #613. Target: `launchpad/docs/corpus/capabilities/workflows/workflow.md`
(does not exist yet -- confirmed via `find launchpad/docs/corpus -iname workflow.md`, no
match, and `capabilities/` does not exist at all under `origin/launchpad`'s corpus tree).

## ALREADY TRUE

- `launchpad/docs/corpus/templates/capability.md` exists and is the governing template
  for `type: capabilities` nodes (required sections: capability statement, maturity,
  boundary, relationships, scope and omissions).
- `architecture-flows-workflow-execution` (`launchpad/docs/corpus/architecture/flows/workflow-execution.md`)
  is already merged on `origin/launchpad` and documents the run-time engine in detail
  (trigger paths, executor loop, trust boundaries, failure modes) -- this capability
  node must not duplicate that content, only cite/reference it.
- `architecture-containers-relay` is already merged and names `buzz-workflow` as one of
  the six subsystem crates the relay orchestrates directly.
- ~15 sibling issues (#829-#843, #822-#823, #830-#837) document individual
  workflow-domain nodes (triggers, actions, run, step, definition, condition,
  concurrency) under this same `capabilities/workflows/` directory -- none are merged
  yet, so none are valid `relationships` targets today (checked
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
- VISION_PROJECTS.md:250 already marks "Workflow engine (triggers, traces, conditional
  logic)" as "Ships today" -- citable maturity evidence.
- Known from batch dispatch: several sibling action types are unimplemented or broken
  (approval unwired, reaction-action calls a route absent from `router.rs`, send-dm and
  set-channel-topic both hard `NotImplemented`) -- confirmed independently by reading
  `crates/buzz-workflow/src/executor.rs` directly (lines ~643-728) and grepping
  `crates/buzz-relay/src/router.rs` for the reactions route (no match).

## STEP 1 -- Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/workflow.md`:
- Front matter: `id: capabilities-workflows-workflow`, `type: capabilities`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`.
- `relationships`: `references` -> `architecture-flows-workflow-execution` and
  `references` -> `architecture-containers-relay` (both merged on `origin/launchpad`,
  both directly support this capability's implementation).
- Body per the capability template: capability statement (trigger -> conditions ->
  actions automation, product-level), maturity (shipped core engine, cited to
  `VISION_PROJECTS.md:250` and the schema/executor/db code; several action types
  unimplemented/broken, cited directly to `executor.rs`), boundary (not architecture,
  not interface, not flow -- points at the merged flow node and the buzz-cli interface
  file without re-describing them), relationships section, scope and omissions.
- Evidence: real `path:line`/`path:start-end` citations only, classified
  FACT/INFERENCE/TEAM_KNOWLEDGE per schema rules.

**Done when:** file exists, front matter matches `node.schema.json`'s enum values,
every DoD bullet in #844 is addressed by a named section.

## STEP 2 -- Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.

**Done when:** exit 0, and the only FAIL lines are the 21 pre-existing baseline
failures tracked in #1951 (zero new FAIL entries attributable to this new node).

## STEP 3 -- Earn the commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`, then in a separate call `git add` the node + this plan file and
`git commit -s`.

**Done when:** commit exists on `task/844-workflow`, nothing pushed, no PR opened.

## GATES

- `validate.py` exit 0, zero new FAIL entries vs. the #1951 baseline.
- `unittest discover` on corpus tests prints `OK` before any `git add`/`git commit`.

## BUDGET

Single document, ~3 steps, no code changes. No parallelism needed (one file).

## OPEN

- Whether `references` toward `architecture-containers-relay` is worth keeping versus
  just `architecture-flows-workflow-execution` alone -- decided in favor of keeping
  both, since the container node is the one place that independently names
  `buzz-workflow` as an orchestrated subsystem (supports the "how it's built" pointer
  without re-describing it).

## LEFT OUT

- Any relationship to the ~15 sibling workflow-domain nodes or to `#941`
  (`implementation/crates/buzz-workflow.md`) or `#1285`
  (`platforms/relay/workflow-api.md`) -- none are merged, so none are valid targets
  yet (AGENTS.md's own trap warning: check `origin/launchpad`, not the working tree).
- Re-litigating the specifics of any single broken/unimplemented action (approval,
  reaction, send-dm, set-channel-topic) beyond the one honest maturity sentence this
  issue's brief authorizes -- those are each owned by their own sibling node.
