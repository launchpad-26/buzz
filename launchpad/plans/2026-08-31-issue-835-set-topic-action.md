# Issue #835: document capabilities/workflows/set-topic-action.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/set-topic-action.md` does not exist
  anywhere in this worktree or on `origin/launchpad`; no `capabilities/` directory
  exists in the merged corpus tree at all yet.
- `crates/buzz-workflow/src/schema.rs` defines `ActionDef::SetChannelTopic { topic:
  String }`, tagged `action: set_channel_topic`, parses/round-trips cleanly (test
  `parse_all_action_types`, schema.rs:394,410), and its `topic` field goes through
  the shared template-resolution pass (executor.rs:432) like every other action.
- `crates/buzz-workflow/src/executor.rs`'s `dispatch_action` match arm for
  `SetChannelTopic` (line 649-653) only logs a warning and returns
  `Err(WorkflowError::NotImplemented("SetChannelTopic".into()))` — no DB write, no
  event emission, no HTTP call. `WorkflowError::code()` maps this to
  `"action_not_implemented"` (error.rs:81).
- `ActionSink` (action_sink.rs), the trait the relay implements to give the executor
  real DB/event access, has exactly one method — `send_message` — no
  topic/description update method exists on it at all.
- The real, working, product-level path for setting a channel's topic is
  `buzz-cli`'s `channels set-topic` → `buzz_sdk::build_set_topic` → signed kind:9002
  NIP-29 edit-metadata event → relay's `handle_edit_metadata`
  (side_effects.rs:496) → updates the addressable kind:39000 metadata. The workflow
  action is not wired to this path in any way.
- Sibling task #830 (`reaction-action.md`, local branch `task/830-reaction-action`,
  not yet merged) already established this batch's document shape for a
  `capabilities/workflows/*` node: `type: capabilities`, id pattern
  `capabilities-workflows-<action>`, sections *Maturity*, *Trigger/preconditions/
  termination*, *Ordered interactions and data/state movement*, *Trust-boundary
  crossings*, *Failure/abort/rollback*, *Scope and omissions*, relationships
  `references: architecture-flows-workflow-execution` +
  `implements: corpus-template-capability` — both targets exist, merged, on
  `origin/launchpad`.
- `origin/launchpad` HEAD at task start: `131b02f989684117d9ab1dd426f1673fa638e523`.

## STEP 1 — Draft the corpus node

Write `launchpad/docs/corpus/capabilities/workflows/set-topic-action.md` following
#830's established shape, `id: capabilities-workflows-set-topic-action`,
`type: capabilities` (documented as an explicit INFERENCE in the evidence ledger,
since no *merged* sibling exists to set precedent — #830 is real precedent but
unmerged). Cover, with real citations (`path:line`, not `#symbol=`):

- Maturity: schema-valid but functionally a no-op stub — more thoroughly
  unimplemented than #830's `add_reaction` (which at least attempts a doomed HTTP
  call); `set_channel_topic` makes no attempt at any side effect at all.
- Trigger/preconditions/termination, ordered interactions, trust-boundary
  crossings (the shared community write-fence still runs before the stub returns;
  no further boundary is crossed because nothing is dispatched), and
  failure/abort/rollback (`NotImplemented` → `action_not_implemented` → run marked
  `Failed`; no rollback, no retry).
- Relationships: `references: architecture-flows-workflow-execution`,
  `implements: corpus-template-capability`.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
root. Confirm the new node adds zero new FAIL entries beyond the known 21
pre-existing baseline failures (issue #1951).

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK` before committing.

## STEP 4 — Commit

`git add` the new corpus doc + this plan file only. Commit with
`git commit -s -m "docs(corpus): document capabilities/workflows/set-topic-action (#835)"`.
No push, no PR — a later integration phase handles that.

## GATES

- `validate.py`: zero new FAIL entries.
- `unittest discover` on corpus tests: `OK`.
- Every claim in the node is FACT (cited path:line/commit) or explicit
  INFERENCE (with confidence) or TEAM_KNOWLEDGE (with provided_by) — never
  conflated.

## BUDGET

Single document, capped at the same depth as #830's sibling node. No code changes.

## OPEN

- Whether `type: capabilities` or `type: architecture` is the eventual settled
  convention for this whole `capabilities/workflows/*` family remains genuinely
  open until a first node in the batch actually merges to `origin/launchpad` — this
  node documents its choice as an INFERENCE for that reason, matching #830.

## LEFT OUT

- No change to `crates/buzz-workflow` — this is a documentation task only, the
  `NotImplemented` stub is described, not fixed.
- No second corpus document. If a distinct second concept surfaces during
  research it gets filed as a separate GitHub issue instead of folded in here.
- `review-code` / `review-adjudicate` are not run in batch mode; step 6 of the
  parent task is a self-review substitute instead.
