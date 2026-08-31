# Plan: issue #839 — document capabilities/workflows/workflow-condition.md

## ALREADY TRUE

- `crates/buzz-workflow` implements a single evalexpr-based condition-evaluation
  mechanism (`executor::evaluate_condition` / `build_eval_context` in
  `crates/buzz-workflow/src/executor.rs`) reused at two independent gate points:
  a step's optional `if:` expression (`schema.rs::Step.if_expr`, evaluated in
  `executor.rs::execute_steps`) and a trigger's optional `filter` expression
  (`schema.rs::TriggerDef::{MessagePosted,ReactionAdded,DiffPosted}.filter`,
  evaluated in `lib.rs::should_fire_workflow`).
- No node exists yet at `launchpad/docs/corpus/capabilities/workflows/` on
  `origin/launchpad` — sibling tasks #829 (message-trigger) and #831
  (reaction-trigger) are still OPEN, unmerged, so there is no in-Feature
  precedent for `type` on this path.
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md`
  (id: `architecture-flows-workflow-execution`) is merged on `origin/launchpad`
  and already documents the shared executor's step loop, including a one-line
  mention of condition evaluation, at the level of the whole run's lifecycle —
  not the condition mechanism's own contract (variables, functions, limits,
  divergent failure handling between the two call sites).
- `launchpad/docs/corpus/templates/capability.md` establishes the `capabilities`
  template's shape (capability statement / maturity / boundary / relationships /
  scope-and-omissions) and states a capability node `may reference` an
  architecture node that realizes it.

## STEP 1 — Confirm target absence and gather evidence

Confirm `launchpad/docs/corpus/capabilities/workflows/workflow-condition.md`
does not exist. Re-read `crates/buzz-workflow/src/executor.rs` (`evaluate_condition`,
`build_eval_context`, `EVAL_TIMEOUT`, `MAX_EXPR_LEN`), `schema.rs` (`Step.if_expr`,
`TriggerDef` filter fields), `lib.rs` (`should_fire_workflow`), and
`VISION_PROJECTS.md`'s capability status table. Done when: exact `path:line`
evidence recorded for every claim the body will make.

## STEP 2 — Draft the node

Write front matter (`id: capabilities-workflows-workflow-condition`,
`type: capabilities` — no merged sibling precedent exists, so recorded as an
explicit INFERENCE — `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, reviewer]`, one `references` relationship to
`architecture-flows-workflow-execution`). Write the body: capability statement,
maturity (cite `VISION_PROJECTS.md:250`), the two call sites and how they share
one mechanism, available variables/functions, the two safety limits (100ms
timeout via `spawn_blocking`, 4096-byte length cap), the failure-handling
divergence (step error aborts the run; trigger error only skips that workflow),
boundary (not the flow, not the trigger types themselves), scope and omissions.
Done when: every DoD bullet in #839 has body content.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Done when: exit 0, and the new node introduces zero new FAIL entries (21
pre-existing FAILs on `origin/launchpad`, tracked in #1951, are not this node's
to fix).

## STEP 4 — Earn the commit gate and commit

Run, as a lone command: `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`. Confirm `OK`. Then
`git add` the new node + this plan file and `git commit -s`.

## STEP 5 — Self-review

Re-read the diff against #839's DoD line by line. Re-open every cited source.
Confirm no second canonical document was created and no new validate.py FAIL
entries appeared.

## GATES

- `validate.py` exits 0, zero new FAIL entries vs. the 21-entry baseline (#1951).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` prints `OK`, run as a standalone command, before commit.

## BUDGET

One node, one plan file, one commit. No code changes.

## OPEN

- Whether `type: capabilities` matches what #829/#831 eventually land with —
  unresolvable now since both are unmerged; documented as an INFERENCE with
  reasoning any later reviewer can re-check against whatever they land as.

## LEFT OUT

- Documenting the trigger definitions themselves (`message_posted`,
  `reaction_added`, `diff_posted`) — that is #829/#831's own scope.
- Re-documenting the full workflow run lifecycle — owned by
  `architecture-flows-workflow-execution`, linked via `references`.
- Template-variable resolution (`{{trigger.X}}` / `{{steps.ID.output.X}}`) — a
  distinct mechanism from condition evaluation, not this node's subject.
