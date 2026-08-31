# Plan: issue #837 — document capabilities/workflows/webhook-trigger.md

## ALREADY TRUE

- `launchpad/docs/corpus/architecture/flows/workflow-execution.md` is merged on
  `origin/launchpad` (`type: architecture`, `status: draft`) and already documents all
  three workflow trigger paths (channel-event, schedule, webhook) plus the shared
  executor at flow level, including the webhook path's host-bind/secret/authority
  sequence. This node must not duplicate that content — it narrows to the webhook
  trigger specifically and `references` that node instead.
- The `capabilities/` directory does not exist yet on `origin/launchpad` (only
  `architecture/`, `standards/`, `schema/`, `templates/` do), so there is no merged
  sibling under `capabilities/workflows/` to set a `type` precedent for this batch.
- `launchpad/docs/corpus/templates/capability.md`'s own Boundary section explicitly
  excludes step-by-step narration ("a capability node states that the product can do
  the thing; it does not narrate the sequence of steps") — but issue #837's DoD
  requires exactly that narration (trigger/preconditions/termination, ordered
  interactions, auth crossings, failure/rollback), the same four bullets
  `architecture/flows/workflow-execution.md` was built against. So the content this
  issue demands is flow-shaped, not capability-shaped, despite the file's
  `capabilities/workflows/` path.
- `launchpad/docs/corpus/templates/flow.md` (merged) states its own instance nodes
  carry `type: architecture` (no `flow` enum value exists), the precedent
  `architecture-flows-workflow-execution` already sets.
- Sibling tasks #822-#844 (same Feature #613 batch) are all still OPEN — no merged
  sibling in this batch settles the `capabilities` vs `architecture` type question.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/webhook-trigger.md`:
`id: capabilities-workflows-webhook-trigger`, `type: architecture` (chosen over
`capabilities` — documented as an explicit `INFERENCE` in the evidence ledger, per the
ALREADY TRUE reasoning above), `status: draft`, `origin: launchpad`, evidence citing
`crates/buzz-relay/src/api/bridge.rs`'s `workflow_webhook` handler,
`crates/buzz-relay/src/webhook_secret.rs`, `crates/buzz-relay/src/handlers/
command_executor.rs`'s secret-generation-on-save logic, `crates/buzz-workflow/src/
schema.rs`'s `TriggerDef::Webhook` variant and its `reply_in_thread` precondition,
`crates/buzz-workflow/src/lib.rs`'s `trigger_matches_event`/`check_owner_authority`,
and `crates/buzz-relay/src/router.rs`'s route registration — all opened directly, not
paraphrased from the existing flow node. One `references` relationship to
`architecture-flows-workflow-execution` (merged, resolves). Body follows the flow
template's required sections (Flow statement, Sequence, Diagram, Outcome, Boundary,
Relationships, Scope and omissions), scoped narrowly to the inbound `POST /hooks/{id}`
door — explicitly excluding the outbound `call_webhook` action (sibling #836) and the
other two trigger paths / shared executor (owned by `architecture-flows-
workflow-execution`).

**Done when:** file exists, front matter is schema-valid, every substantive claim has
an evidence entry classed and cited per `AGENTS.md`.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.

**Done when:** exit 0, and the new node adds zero new FAIL entries beyond the known
21 pre-existing ones tracked in issue #1951.

## STEP 3 — Earn the commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`, then commit the new file plus this plan file with `git commit -s`.

**Done when:** commit exists on `task/837-webhook-trigger`; no push, no PR.

## PARALLEL

None — single file, single commit, no concurrent work in this worktree.

## GATES

- `validate.py` exit 0 with zero new FAIL entries.
- The commit-gate unittest suite prints `OK` before any `git add`/`git commit`.

## BUDGET

Single document, one commit. No code changes, no runtime behavior change.

## OPEN

- Whether a future reviewer agrees `type: architecture` (not `capabilities`) is the
  right call for a node filed under `capabilities/workflows/` — flagged explicitly as
  an `INFERENCE` in the node's own evidence ledger for that reason.
- Whether `webhook_secret::strip_secret` (defined and unit-tested, but no call site
  found in `crates/buzz-relay/src` outside its own module/tests) is actually wired
  anywhere a stored workflow definition is returned to a caller — noted as an
  unresolved gap in the node's own Scope and omissions, not resolved by this task.

## LEFT OUT

- Any change to `crates/buzz-relay`, `crates/buzz-workflow`, or their tests — this is
  a documentation-only task.
- Re-documenting the channel-event and schedule trigger paths, the shared step
  executor, or the outbound `call_webhook` action — all owned by
  `architecture-flows-workflow-execution` or sibling issue #836 respectively.
- `review-code`/`review-adjudicate` — deferred per batch mode; self-review substitutes.
