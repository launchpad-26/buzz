# Plan: issue #829 — document capabilities/workflows/message-trigger.md

## ALREADY TRUE

- `crates/buzz-workflow` implements `TriggerDef::MessagePosted { filter }`
  (`crates/buzz-workflow/src/schema.rs:38-44`), matched against stored events by
  `trigger_matches_event` (kind:9 only, `crates/buzz-workflow/src/lib.rs:1038-1042`) and
  narrowed by `should_fire_workflow`'s optional evalexpr filter
  (`crates/buzz-workflow/src/lib.rs:883-931`).
- The sibling flow node `launchpad/docs/corpus/architecture/flows/workflow-execution.md`
  (id `architecture-flows-workflow-execution`, merged on `origin/launchpad`) already
  documents the shared executor/authority/tenant-fence plumbing all three channel-event
  triggers (message/reaction/diff) run through. This task must not restate that content.
- The repository's own directory convention (21/21 sampled nodes under `architecture/`
  and `standards/`) ties a node's top-level corpus directory to its front-matter `type`.
  The issue's own impacted-component path is `capabilities/workflows/message-trigger.md`,
  so `type: capabilities` is used, matching that convention.
- Target file does not exist yet (confirmed via `test -f`).

## STEP 1 — Gather evidence

Read `crates/buzz-workflow/src/schema.rs` (TriggerDef::MessagePosted, WorkflowDef::validate's
reply_in_thread precondition), `crates/buzz-workflow/src/lib.rs` (on_event's channel_id/kind
preconditions, trigger_matches_event, should_fire_workflow, build_trigger_context,
event_is_reply), and `crates/buzz-workflow/src/executor.rs` (TriggerContext, build_eval_context's
`trigger_*` variable exposure, evaluate_condition's length/timeout bounds). Record exact
`path:start-end` citations for every claim. Done when every claim in STEP 2 has a citation
opened and verified, not paraphrased from memory.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/message-trigger.md` with schema-valid
front matter (`id: capabilities-workflows-message-trigger`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer]`, one `evidence` entry
per claim, one `references` relationship to `architecture-flows-workflow-execution`). Body
sections satisfy #829's DoD literally: trigger/preconditions/termination, ordered
interactions and data/state movement, trust-boundary crossings, failure/abort/rollback with
representative verification, plus a boundary/scope-and-omissions section pointing at
`architecture-flows-workflow-execution` for the shared executor. Done when every DoD bullet
maps to a named section.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree. Done when
it reports zero new FAIL entries beyond the known 21 pre-existing ones tracked in #1951.

## STEP 4 — Earn the commit gate

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call. Done when it prints `OK`.

## STEP 5 — Commit

`git add` the new document plus this plan file; `git commit -s` with the standard batch
message. Done when the commit exists locally. No push, no PR — a later integration phase
folds this commit into the Feature #613 PR.

## PARALLEL

None — single-file task, no fan-out.

## GATES

- `validate.py`: zero new FAIL entries.
- `unittest discover` on `launchpad/project-intelligence/corpus/tests`: `OK`.

## BUDGET

Single document, ~5 evidence-backed sections. No code changes, no test changes beyond the
existing suite already gating the commit.

## OPEN

- Whether `KIND_STREAM_MESSAGE_V2` (kind:40002) messages are intentionally excluded from
  `message_posted` triggers, or an unaddressed gap — no design doc or issue found deciding
  this; stated as an explicit gap in the node's Scope and omissions, not resolved here.

## LEFT OUT

- Restating the shared executor step-loop, SEC-006 authority recheck, or tenant/community
  fencing — owned by `architecture-flows-workflow-execution`, referenced not duplicated.
- Documenting `reaction_added`, `schedule`, or `webhook` triggers — siblings #831/#832/#837,
  each its own task.
- `review-code`/`review-adjudicate` — deferred per batch mode; step 6 self-review substitutes.
