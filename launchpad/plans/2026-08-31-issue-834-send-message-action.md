# Plan: issue #834 -- document capabilities/workflows/send-message-action.md

## ALREADY TRUE

- `crates/buzz-workflow` implements the `send_message` workflow action end to
  end: `ActionDef::SendMessage` (schema.rs), `dispatch_action`'s matching arm
  and `resolve_send_message_channel` (executor.rs), and the relay's
  `RelayActionSink::send_message` (buzz-relay/src/workflow_sink.rs) that
  actually builds, signs and persists the `kind:9` event.
- `architecture-flows-workflow-execution` is already merged on
  `origin/launchpad` and documents the encompassing multi-trigger flow
  (including a brief summary of `SendMessage`'s channel-confinement rule) --
  this task's node zooms into that one action step, not the whole flow.
- `launchpad/docs/corpus/templates/flow.md` (`corpus-template-flow`) and
  `templates/capability.md` (`corpus-template-capability`) are both merged.
  The flow template's own precedent assigns `type: architecture` to instance
  nodes; the capability template explicitly excludes step-by-step narration
  from its own scope. Issue #834's DoD (trigger/preconditions/termination,
  ordered interactions, trust boundaries, failure/rollback) matches the flow
  template's shape, not the capability template's.
- No node exists yet under `launchpad/docs/corpus/capabilities/` on
  `origin/launchpad` -- this is the first node at that path, so there is no
  merged in-Feature precedent for `type: capabilities` vs `type: architecture`
  at this action-node granularity.
- Sibling tasks #833 (`send-dm-action`) and #830 (`reaction-action`) are open
  and undrafted at this revision -- no relationship target exists for either.

## STEP 1 -- Gather evidence and confirm no existing document

Read `crates/buzz-workflow/src/schema.rs`, `executor.rs`, `lib.rs`,
`action_sink.rs`, `error.rs`, and `crates/buzz-relay/src/workflow_sink.rs` +
`handlers/event.rs`'s anti-recursion check, recording exact line numbers.
Confirm `launchpad/docs/corpus/capabilities/workflows/send-message-action.md`
does not already exist. Done-when: line-numbered citations collected for
every claim the node will make; target path confirmed absent.

## STEP 2 -- Draft the node

Write the node against the merged `corpus-template-flow` template's required
sections (Flow statement, Sequence, Diagram, Outcome, Boundary,
Relationships, Scope and omissions), mapped onto issue #834's own DoD
headings (trigger/preconditions/termination, ordered interactions, trust
boundaries, failure/rollback). Classify every claim FACT/INFERENCE/
TEAM_KNOWLEDGE per `AGENTS.md`. Document the `type: architecture` choice as
an explicit INFERENCE since no merged sibling settles it. Add `part-of` ->
`architecture-flows-workflow-execution` and `implements` ->
`corpus-template-flow` relationships (both merged, valid targets). Done-when:
file written, every DoD bullet addressed.

## STEP 3 -- Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0,
zero *new* FAIL entries beyond the pre-existing 21 tracked in #1951) and
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` (must print OK) as the commit gate. Done-when: both pass.

## STEP 4 -- Commit

`git add` the new node + this plan file; commit with `-s` referencing #834.
No push, no PR (integration phase handles that separately).

## GATES

- `validate.py` exits 0 with no new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints OK.

## BUDGET

Capped at 4 steps; single node, no code changes.

## OPEN

- Whether `type: capabilities` or `type: architecture` is the eventual
  corpus-wide convention for action-level workflow nodes is not settled by
  this task -- flagged as an explicit INFERENCE in the node's own evidence
  ledger for a later reviewer/standard to confirm or override.

## LEFT OUT

- Drafting `send-dm-action.md` or `reaction-action.md` (#833, #830) --
  separate tasks, separate nodes.
- Any change to workflow engine runtime behavior.
- A dedicated `kind:9` event-kind corpus node -- named as a gap, not created.
