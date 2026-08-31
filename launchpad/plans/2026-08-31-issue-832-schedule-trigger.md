# Issue #832: document capabilities/workflows/schedule-trigger.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/schedule-trigger.md` does not exist on
  `origin/launchpad` (confirmed: no `capabilities/` directory exists in the corpus tree
  yet — this is the first node under it).
- `crates/buzz-workflow`'s `WorkflowEngine::run()` background loop, `TriggerDef::Schedule`,
  `WorkflowDef::validate()`'s schedule rules, and `crates/buzz-db/src/store/workflow.rs`'s
  `scheduled_workflow_fires` claim functions are fully implemented and covered by unit
  tests (`crates/buzz-workflow/src/lib.rs`, `crates/buzz-workflow/src/schema.rs`) and
  `#[ignore = "requires Postgres"]` integration tests (`crates/buzz-db/src/store/workflow.rs`).
- `architecture-flows-workflow-execution` (merged, `type: architecture`) already narrates
  all three trigger paths (channel-event, schedule, webhook) plus the shared executor at
  a comparison level; it is a valid `part-of` target for this narrower node.
- `node.schema.json`'s `type` enum has no `flow`/`schedule` member; `corpus-template-flow`
  and the merged `architecture-flows-workflow-execution` both establish `type: architecture`
  as the precedent for a flow-shaped instance node, independent of the node's directory.

## STEP 1 — Gather evidence (done)

Read `schema.rs` (Schedule trigger fields, validate() rules, reply_in_thread rejection,
cron normalization), `lib.rs` (60s loop, cron/interval fire-instant computation, interval
liveness/restart anchor, owner-authority-before-claim ordering, run-creation and its
failure handling), `store/workflow.rs` (claim/attach/latest-fire functions and their
tests), and `migrations/0001_initial_schema.sql` / `0029_community_deletion.sql` (claim
table schema and write fence). Recorded exact `path:line` ranges for every claim.

## STEP 2 — Draft the node

Front matter: `id: capabilities-workflows-schedule-trigger`, `type: architecture` (with an
INFERENCE evidence entry explaining the type choice against the capabilities-suggesting
directory), `status: draft`, `origin: launchpad`, `audiences: [agent, developer]`, one
`relationships` entry (`part-of` → `architecture-flows-workflow-execution`, which exists
on `origin/launchpad`). Body organized around the DoD's four required sections: Trigger/
preconditions/termination, Ordered interactions and data/state movement, Trust-boundary
crossings, Failure/abort/rollback — plus Relationships and Scope and omissions. Every
substantive claim cited to a `path:line`/`path:start-end` FACT, with one INFERENCE (type
choice) and one TEAM_KNOWLEDGE (issue DoD attribution).

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.
Confirm the new node adds zero new FAIL entries beyond the known 21 pre-existing ones
(issue #1951).

## STEP 4 — Earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as a lone command. On `OK`, `git add` the new doc + this plan file and
`git commit -s`.

## GATES

- `validate.py` exits 0 with no new FAIL entries attributable to this node.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` reports `OK`.

## BUDGET

One node, one plan file. No source code changes.

## OPEN

- Whether `type: architecture` vs `type: capabilities` is the "right" long-term choice
  for this document family is not settled by any corpus standard read during drafting —
  recorded as an INFERENCE in the node's own evidence ledger, not asserted as fact.

## LEFT OUT

- The three sibling trigger/action docs (#829 message-trigger, #830 reaction-action,
  #831 reaction-trigger, #837 webhook-trigger) — separate tasks, separate commits, no
  relationships declared toward them since none is merged yet.
- Any change to `crates/buzz-workflow` or `crates/buzz-db` runtime behavior.
