# Plan: issue #822 — document capabilities/workflows/approval-action.md

## ALREADY TRUE

- Worktree `__worktrees/task-822-approval-action` on branch `task/822-approval-action`,
  based on `origin/launchpad` at `cad6c375fdcc590158c1456c9fc7875f0f84a844`.
- Target file `launchpad/docs/corpus/capabilities/workflows/approval-action.md` does
  not exist yet (confirmed with `test -f`).
- `node.schema.json`'s `type` enum has 13 members including `capabilities`; no `flow`
  member exists. Issue #822 (and its closed duplicate #827) both title the Objective
  "the single canonical flow node for approval action," but the file path
  (`capabilities/workflows/...`), parent Feature #613's own title ("workflow and
  supporting **capability** corpus exists"), and VISION_PROJECTS.md's own capability
  catalog (which names "Approval gates" as one of its rows) all point at
  `type: capabilities` instead — the "flow" wording in the Objective is the same
  copy-paste boilerplate drift `AGENTS.md`, `templates/flow.md` and
  `templates/capability.md` each document elsewhere in this batch.
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md` is already merged
  on `origin/launchpad` and documents the shared step-dispatch loop `RequestApproval`
  runs inside, including one summary bullet on its current failure mode — a valid
  `references` target, and the node this task must not duplicate wholesale.
- Verified directly in code (not assumed from the flow node's own claim):
  - `crates/buzz-workflow/src/executor.rs:713-731` — `RequestApproval` dispatch
    generates a token (`generate_approval_token`) and returns
    `StepResult::Suspended { approval_token }`; the `// TODO (WF-08)` comment says
    plainly no DB record is created and no event is emitted.
  - `crates/buzz-workflow/src/lib.rs:229-256` — `finalize_run` maps any
    `Suspended`-derived result straight to `RunStatus::Failed` with error code
    `approval_not_supported`, never to `WaitingApproval`.
  - `grep -rn "RunStatus::WaitingApproval" crates/` outside tests/Display/FromStr
    returns only two *read*-side guards
    (`crates/buzz-relay/src/handlers/command_executor.rs:1231,1290`) — no production
    code path ever *writes* `WaitingApproval`.
  - `grep -rn "create_approval(" crates/` shows the DB insert function
    (`crates/buzz-db/src/store/workflow.rs:992`) is called only by its own unit
    tests (lines 2702, 2717) — never from `executor.rs`, `lib.rs`, or
    `command_executor.rs`.
  - The resolve-side is fully built and merely unreachable: table
    `workflow_approvals` (`schema/schema.sql:413-433`, present since
    `migrations/0001_initial_schema.sql`), `ApprovalStatus`/`ApprovalRecord`/
    `create_approval`/`get_approval_by_stored_hash`/`update_approval_by_stored_hash`
    (`crates/buzz-db/src/store/workflow.rs`), relay command handlers
    `handle_approval_grant`/`handle_approval_deny` keyed to
    `KIND_APPROVAL_GRANT`=46030/`KIND_APPROVAL_DENY`=46031
    (`crates/buzz-relay/src/handlers/command_executor.rs:1020-1270`,
    `crates/buzz-core/src/kind.rs:559-562`), `resume_workflow_after_approval`
    (`command_executor.rs:1273-1366`), and a CLI surface
    (`crates/buzz-cli/src/commands/workflows.rs:205-225`,
    `crates/buzz-cli/src/lib.rs:965-971`) that builds and signs those events via
    `buzz_sdk::build_workflow_approval`.
  - `VISION_PROJECTS.md:253` — `"Approval gates | 🚧 Infrastructure exists; executor
    wiring in progress"` — a citable, canonical maturity statement that matches the
    code-level finding exactly.
  - `crates/buzz-workflow/src/schema.rs:165-169` —
    `requires_elevated_authority` only checks for `CallWebhook` steps; a
    `RequestApproval` step needs no elevated authority to define or run.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/workflows/approval-action.md`.

- Front matter: `id: capabilities-workflows-approval-action`, `type: capabilities`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
  one `evidence` entry per substantive claim (FACT citing real `path:line` spans for
  everything opened above; one `TEAM_KNOWLEDGE` entry, `provided_by` naming the
  issue, for the Objective-vs-path type discrepancy), `relationships: [{type:
  references, target: architecture-flows-workflow-execution}]`.
- Body: Capability statement; Maturity (cited to VISION_PROJECTS.md + code);
  Trigger/preconditions/termination; Ordered interactions and data/state movement
  (request side as it behaves today, and the built-but-unreachable resolve side,
  kept visibly separate); Trust-boundary crossings (`check_approver_spec`, token
  hashing, the no-elevated-authority note); Failure/abort/rollback
  (`approval_not_supported`, the orphaned token, the resume guard); Boundary
  statement; Relationships; Scope and omissions.

Done-when: file exists with schema-shaped front matter (hand-checked against
`node.schema.json`'s required fields and enums before running the validator).

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.
Fix anything it names for this node. Confirm the run adds **zero** new FAIL entries
beyond the 21 pre-existing, unrelated ones tracked in issue #1951.

Done-when: validator output shows no new FAIL attributable to
`capabilities-workflows-approval-action`.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`

Done-when: output ends `OK`.

## STEP 4 — Self-review and commit

Re-read the diff against #822's DoD line by line; re-open every cited source; confirm
no second canonical document was created; confirm no new `validate.py` FAIL entries.
Then `git add` the new node + this plan file and
`git commit -s -m "docs(corpus): document capabilities/workflows/approval-action (#822)"`.

Done-when: commit exists; `git status` is clean except for the two added files.

## PARALLEL

None. Single-file authoring task with no independent sub-work to parallelize.

## GATES

- `validate.py` — zero new FAIL entries for this node.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` — must print `OK`, run as its own command, never piped or redirected.
- Any local commit hooks that fire on `git commit -s` (formatting/lint) — fix and
  re-commit if they auto-fix and re-stage; do not touch the stamp file or use
  `--no-verify` if blocked.
- No push, no PR — local commit only, per the batch's integration phase.

## BUDGET

One document, one plan file, four steps. This is a single corpus-node authoring task
scoped by issue #822 alone; no multi-day or multi-file work is in scope.

## OPEN

- Whether `type: capabilities` (this plan's choice) or `type: architecture` (the
  precedent `architecture-flows-workflow-execution.md` set for flow-shaped content)
  is the "correct" long-term answer is not settled anywhere in the schema or its
  standards track yet — recorded as a judgment call in the evidence ledger, the same
  way `templates/flow.md` and `templates/capability.md` each recorded their own.
- Whether narrating the resolve-side (grant/deny/resume) infrastructure inside this
  node oversteps "one independently maintainable idea": treated as in-scope here
  because it is the direct, mechanical counterpart of the `RequestApproval` action
  this node documents (the token this action mints is meaningless without it), not a
  separate concept — flagged explicitly in the Boundary/Scope sections so a reviewer
  who disagrees has a named seam to split on.

## LEFT OUT

- Full wire contracts for `kind:46010`/`46011`/`46012` — an event-kind node's job;
  only referenced here.
- The CLI `buzz workflows approve`/`deny` subcommand's own interface contract — only
  cited as evidence that the resolve-side infrastructure exists.
- Any runtime behavior change. This task is documentation only.
