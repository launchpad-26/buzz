# Issue #830: document capabilities/workflows/reaction-action.md

Parent: Feature #613 (corpus batch, PRD #602). Repo revision at plan time:
cad6c375fdcc590158c1456c9fc7875f0f84a844 (origin/launchpad tip).

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/reaction-action.md` does not exist.
- No `capabilities/` directory exists yet in the corpus at all — this is one of the
  first instance nodes for that surface.
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`)
  and `launchpad/docs/corpus/architecture/flows/workflow-execution.md` (id
  `architecture-flows-workflow-execution`) are both merged and readable — both are
  valid `relationships` targets.
- The `AddReaction` workflow action (`action: add_reaction`) is defined in
  `crates/buzz-workflow/src/schema.rs:121-125` and dispatched in
  `crates/buzz-workflow/src/executor.rs:655-680`, calling
  `add_reaction_impl` (`executor.rs:967-1014`), which POSTs to
  `{BUZZ_RELAY_BASE_URL}/api/messages/{message_id}/reactions`.
- That route does not exist anywhere in `crates/buzz-relay/src/router.rs`'s route
  table (`router.rs:62-143`), and `buzz-relay/Cargo.toml:65` unconditionally enables
  the `reqwest` feature that makes this code path live in the real relay build — so
  this action is broken today, not merely undocumented. This is the central finding
  of the node.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/reaction-action.md` per
`node.schema.json` and the capability template, adapted with the flow-shaped body
sections issue #830's own DoD requires (trigger/preconditions/termination, ordered
interactions, trust-boundary crossings, failure/rollback — the same category used by
`architecture-flows-workflow-execution`). `type: capabilities` (matches the file's
directory and PRD #602's enumerated surface). Every claim opened and cited directly
from `crates/buzz-workflow` and `crates/buzz-relay` source, `crates/buzz-cli`'s
contrasting reaction path, and `error.rs`'s error-code mapping. Declare
`relationships: [references: architecture-flows-workflow-execution, implements:
corpus-template-capability]`.

Done-when: file exists, front matter validates conceptually against
`node.schema.json`'s field rules (checked mechanically in STEP 2).

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
root. Confirm the new node reports zero new FAIL entries beyond the 21 pre-existing
ones tracked in #1951.

Done-when: validator output shows the new node clean (or only pre-existing FAIL
entries, unrelated to this file).

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`.

Done-when: `OK` printed, no `--no-verify`, no touching the stamp file.

## STEP 4 — Commit

`git add` the new node file and this plan file; `git commit -s` with a message
naming issue #830. No push, no PR — a later integration phase handles that.

Done-when: commit created on `task/830-reaction-action`, working tree clean.

## GATES

- `validate.py` exit 0 with zero new FAIL entries.
- `unittest discover` on `launchpad/project-intelligence/corpus/tests` reports `OK`.
- `git commit -s` succeeds (DCO trailer present).

## BUDGET

Single node, ~1 file. No code changes. Expected total: under 30 tool calls.

## OPEN

- Whether `/api/messages/{id}/reactions` was ever implemented and removed, or never
  built, is not traced through git history — only its current absence is confirmed.
  Left as an explicit gap in the node's own Scope and omissions section.

## LEFT OUT

- The `reaction_added` *trigger* side (issue #831, sibling task) — this node covers
  only the `add_reaction` *action*, the opposite direction.
- Every other workflow action type (`send_message`, `send_dm`, `set_channel_topic`,
  `call_webhook`, `request_approval`, `delay`) — each is its own sibling issue in
  Feature #613.
- Fixing the broken HTTP target — that is a product-code fix, not a documentation
  task, and is out of scope per #830's own "Out of scope" section (no runtime
  behavior changes).
