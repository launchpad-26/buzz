# Plan: issue #833 — document capabilities/workflows/send-dm-action.md

## ALREADY TRUE

- `crates/buzz-workflow` defines `ActionDef::SendDm { to, text }`
  (`schema.rs:109-115`) but `dispatch_action`'s match arm for it always logs a
  warning and returns `Err(WorkflowError::NotImplemented("SendDm"))`
  (`executor.rs:643-647`) — the action is not implemented.
- `ActionSink` (the side-effect interface the relay implements) has only a
  `send_message` method; no `send_dm` method exists at all
  (`action_sink.rs:48-73`).
- `architecture/flows/workflow-execution.md` is the one merged corpus node
  documenting the engine's overall trigger/run-loop machinery, with
  `type: architecture`; `templates/capability.md` and `templates/flow.md` are
  both merged on `origin/launchpad`.
- No sibling node under `capabilities/workflows/` (issues #829-#844) is merged
  yet, so no in-Feature precedent settles `type: capabilities` vs
  `type: architecture` for this task.
- The target file does not exist yet.

## STEP 1 — Evidence gathering (done)

Read `schema.rs`, `executor.rs`, `action_sink.rs`, `error.rs`, and the
owner-authority gate in `lib.rs` to establish: preconditions (no SendDm-specific
validation; not elevated-authority; SEC-006 owner-authority gate still applies
generically), ordered interactions (community write-fence check, then
immediate `NotImplemented` failure, no `ActionSink` call), outcome (run marked
`Failed`, code `action_not_implemented`, no rollback of prior steps' side
effects), and the one trust-boundary crossing actually reached (the community
write fence).

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/send-dm-action.md` with
`type: architecture` (documented as an explicit INFERENCE, since the DoD's
required content — trigger/preconditions/ordered-interactions/outcome/failure
— is flow-shaped per the merged `templates/flow.md`, not capability-shaped),
one `references` relationship to the merged `architecture-flows-workflow-execution`
node, and evidence classified FACT/INFERENCE per source.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with
  zero new FAIL entries (baseline: 21 pre-existing, tracked in #1951).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  prints `OK`, run as the sole command in its own tool call.

## OPEN

- Whether `type: capabilities` will later become the settled convention once a
  sibling in this Feature merges — flagged as an explicit INFERENCE in the
  node's own evidence ledger so a future reviewer can revisit it.

## LEFT OUT

- Documenting the implemented `send_message` action's own dispatch/publish
  behavior (a separate node).
- Any claim about a future WF-07 implementation's wire contract — it does not
  exist in code.
