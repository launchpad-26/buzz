# Plan: issue #842 — document capabilities/workflows/workflow-step.md

## ALREADY TRUE

- `crates/buzz-workflow/src/schema.rs` defines `Step` (id, name, if_expr aka
  `if:`, timeout_secs, action: ActionDef) and the seven-variant `ActionDef`
  enum (SendMessage, SendDm, SetChannelTopic, AddReaction, CallWebhook,
  RequestApproval, Delay).
- `crates/buzz-workflow/src/executor.rs`'s `execute_steps` is the single
  dispatch loop every trigger path converges on: per step, evaluate optional
  `if:` -> skip on false/abort on error, resolve `{{...}}` templates, dispatch
  under a per-step timeout, record `StepResult::{Completed,Suspended,Skipped}`
  into a trace and `step_outputs` map.
- `crates/buzz-workflow/src/error.rs`'s `WorkflowError` has no retry variant
  and no retry loop exists anywhere in `buzz-workflow` (verified: zero grep
  hits for "retry"). A step-level error aborts the remaining steps; no
  compensating/rollback action exists for any `ActionDef` variant.
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md`
  (`architecture-flows-workflow-execution`, merged, `type: architecture`)
  already documents `execute_steps`'s mechanics in FACT-level detail: trigger
  paths, ordered interactions, trust boundaries, failure/abort/rollback. This
  is the biggest duplication risk for #842 and must be linked, not restated.
- `launchpad/docs/corpus/templates/capability.md` (merged) is the applicable
  template: `type: capabilities` names "what the product can do" as a noun
  phrase, distinct from architecture (how it's built). Sibling issues
  #822/#823/#830/#833/#834/#835/#836 confirm the naming convention
  `capabilities/workflows/<action>-action.md` for individual step *types*;
  none are merged yet, so no relationship targets them.
- No `capabilities/` node is merged to `origin/launchpad` yet at HEAD
  (`131b02f989684117d9ab1dd426f1673fa638e523`), so `type: capabilities` has no
  merged precedent to check consistency against beyond the template itself.
- Target file `launchpad/docs/corpus/capabilities/workflows/workflow-step.md`
  does not exist.

## STEP 1 — Write the node

Create `launchpad/docs/corpus/capabilities/workflows/workflow-step.md`,
`type: capabilities`, documenting the **umbrella step abstraction**: what a
step is (schema shape), the closed set of action kinds a step may perform
(naming, not detailing, each — those are the sibling docs' job), sequencing
(`if:` gating, ordering, template resolution), per-step timeout, and
failure/retry semantics common to every step type (fail-fast, no retry, no
rollback). `references` the merged `architecture-flows-workflow-execution`
node for the detailed mechanics instead of restating them.

Done when: front matter validates against `node.schema.json`; every
substantive claim has a real `path:line`/`path:start-end` or `path` citation
(no `#symbol=`); body stays at the umbrella level (no per-action-type
operational detail); `Scope and omissions` names the individual step-type
docs and the flow node as owning what this node doesn't cover.

## STEP 2 — Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py`, confirm the
new node adds zero new FAIL entries (21 pre-existing FAIL baseline tracked in
#1951 is expected and unrelated). Run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call, confirm `OK`.

## STEP 3 — Commit

`git add` the new node + this plan file, `git commit -s`. Stop — no push, no
PR (integration phase handles that).

## GATES

- `validate.py` exits 0, zero new FAIL entries vs. the origin/launchpad
  baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.

## BUDGET

1 file created (+ this plan). Single commit. No code changes.

## OPEN

- Whether `type: capabilities` or a different enum value best fits an
  "abstraction within a capability" rather than a top-level capability itself
  — resolved by following `templates/capability.md`'s own precedent (the
  sibling per-action docs use the same `capabilities/workflows/` path) and
  disclosing the reasoning in the node's own body per `standards/taxonomy.md`
  step 4.

## LEFT OUT

- No relationship to any sibling step-type doc (#822/#823/#830/#833/#834/#835/#836)
  — none are merged on `origin/launchpad`, so none are valid targets per
  `AGENTS.md` step 9.
- No changes to `crates/buzz-workflow` or any other implementation code.
