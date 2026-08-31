# Plan: issue #836 — document capabilities/workflows/webhook-action.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/webhook-action.md` does not exist
  (confirmed: `capabilities/` has no entries at all in `origin/launchpad`'s corpus
  tree, verified via `git ls-tree`).
- The `call_webhook` action (`ActionDef::CallWebhook`, `crates/buzz-workflow/src/schema.rs:127-139`)
  is fully implemented, SSRF-guarded, and dispatched from `dispatch_action`
  (`crates/buzz-workflow/src/executor.rs:682-711`, impl at `:862-950`).
- A merged sibling node, `architecture-flows-workflow-execution`
  (`launchpad/docs/corpus/architecture/flows/workflow-execution.md`), already
  documents the whole workflow-execution flow (all three trigger paths + shared
  executor) at a coarser grain, including a summary mention of `call_webhook`'s
  SSRF guard. This task's node is the atomic, action-level detail one level
  below it — not a duplicate.
- No merged sibling node under `capabilities/workflows/` exists yet to set a
  `type` precedent for this Feature's own directory convention. The only
  directory-to-`type` precedent in the merged corpus is `architecture/flows/*`
  → `type: architecture`.
- The already-merged `templates/flow.md` states a flow instance node's closest
  schema fit is `type: architecture` (its own INFERENCE, confidence 0.6) — but
  that precedent was set for the `architecture/flows/` directory, not
  `capabilities/`.

## STEP 1 — Decide `type` and record it as an explicit INFERENCE

Choose `type: capabilities`, reasoning from the observed directory-mirrors-type
convention (`architecture/flows/*` → `architecture`) extended to
`capabilities/workflows/*` → `capabilities`, since the corpus-plan process
itself chose this directory for this batch of action/trigger docs distinct from
`architecture/flows/`. Record this as an `INFERENCE` evidence entry with
confidence and the reasoning, per the task brief's explicit instruction to
document this choice rather than restate the flow template's own precedent
blindly (that precedent was for a different directory).

Done when: front matter `type` field is set and the evidence ledger contains a
dedicated `INFERENCE` entry explaining the choice.

## STEP 2 — Gather evidence from `crates/buzz-workflow` and `crates/buzz-core`

Read and cite with `path:line`/`path:start-end` (no `#symbol=`):
`schema.rs` (`ActionDef::CallWebhook`, `requires_elevated_authority`),
`executor.rs` (`dispatch_action`'s `CallWebhook` arm, `call_webhook_impl`,
`check_ssrf`, the write-fence acquire/verify/protect/finish wrapper, the
step-timeout wrapper in `execute_steps`), `lib.rs` (`check_owner_authority`,
`owner_authority_allows`, and their unit tests), `error.rs` (`WorkflowError::code`),
`buzz-core/src/network.rs` (`is_private_ip` + its unit tests), and
`buzz-deletion/src/lib.rs` (`ServingWriteGuard::finish`/`Drop` — confirms a
step-timeout-cancelled webhook call still releases its write-fence lease via
`Drop`, not left dangling).

Done when: every substantive claim in STEP 3's draft has a citation opened and
verified against this step's reading, classified honestly (FACT only where the
source was opened and says so).

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/webhook-action.md` with:
front matter (`id: capabilities-workflows-webhook-action`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
`evidence`, `relationships: [{type: part-of, target: architecture-flows-workflow-execution}]`);
body sections satisfying #836's DoD line by line — Trigger/preconditions/
termination, Ordered interactions and data/state movement, Trust-boundary
crossings, Failure/abort/rollback with representative verification links,
Boundary/Scope-and-omissions (what this node does not cover: the inbound
webhook *trigger* path, owned by sibling task #837; the whole workflow-execution
flow, owned by the merged `architecture-flows-workflow-execution`).

Done when: every DoD bullet in #836 has a corresponding section or explicit
statement in the body.

## STEP 4 — Validate and earn the commit gate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root;
confirm zero new FAIL entries beyond the known 21 pre-existing ones (#1951).
Then, as the sole command in its own tool call, run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
and confirm `OK`.

Done when: both commands pass with no new failures attributable to this node.

## STEP 5 — Commit only

`git add` the new document + this plan file; `git commit -s` with the
prescribed message. Do not push, do not open a PR — a later integration phase
folds this commit into one Feature-wide PR.

## PARALLEL

None — single-file task, no parallelizable sub-work.

## GATES

- `validate.py` exits 0 with no new FAIL entries.
- `unittest discover` on `launchpad/project-intelligence/corpus/tests` reports `OK`.
- Every evidence entry citing a `crates/` source was opened and re-read during
  STEP 2, not paraphrased from memory.

## BUDGET

Single document, ~1 commit. No code changes to `crates/buzz-workflow` — this is
documentation-only.

## OPEN

- Whether `type: capabilities` (this node's INFERENCE) or `type: architecture`
  (the flow template's own precedent, set for a different directory) is what a
  human reviewer or a later corpus-standards task (#1307-#1351 range) will
  settle on for the `capabilities/workflows/` directory as a whole. Left
  explicit in the node's own evidence ledger and body rather than resolved here.

## LEFT OUT

- The inbound webhook *trigger* path (`POST /hooks/{id}`) — sibling task #837's
  scope, not this node's.
- Any change to `crates/buzz-workflow` runtime behavior (e.g. the URL-comment/
  code mismatch on HTTPS-only enforcement noted in STEP 2) — if this reads as a
  real product gap distinct from a documentation gap, file it as a separate
  GitHub issue rather than fixing it here, per the corpus atomicity standard.
