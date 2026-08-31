# Plan: issue #841 — document capabilities/workflows/workflow-run.md

## ALREADY TRUE

- Corpus AGENTS.md, node.schema.json, relationships.schema.json read. Front matter
  requires id/type/status/origin/audiences/evidence; relationships optional but must
  resolve against `origin/launchpad`.
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md`
  (`architecture-flows-workflow-execution`) is already merged on `origin/launchpad`
  and documents the trigger-to-terminal-state control flow across all three trigger
  paths (channel event, schedule, webhook) in full: preconditions, ordered
  interactions, trust-boundary crossings, failure/rollback. Its DoD (issue #688) is
  near-identical wording to #841's own DoD. Re-narrating that flow here would
  duplicate a canonical node — not permitted.
- Sibling #840 (`capabilities/workflows/workflow-definition.md`) is unmerged; its DoD
  ("states the capability... behavioral rules... links major flows") matches the
  *capability* template's shape, confirming #840 = the static definition/capability
  node, #841 = the run/record.
- `crates/buzz-db/src/store/workflow.rs` defines `RunStatus` (6 variants),
  `WorkflowRunRecord` (schema), `create_workflow_run`/`get_workflow_run`/
  `list_workflow_runs(_page)`/`update_workflow_run`. `migrations/0001_initial_schema.sql`
  defines the `workflow_runs` table (PK `(community_id, id)`, FK to `workflows`).
  `crates/buzz-cli/src/commands/workflows.rs`'s `cmd_get_workflow_runs` queries Nostr
  kinds 46001-46003 for run history, which the relay never emits (confirmed also by
  the merged flow node) — the CLI's run-history command is dead code today, always
  returning `[]`. `finalize_run` (`buzz-workflow/src/lib.rs`) is the single place
  writing a run's terminal status, and its own DB-write failure is only logged, never
  retried — a run can get stuck mid-status with no reconciliation path.
- No `type: capabilities` node is merged anywhere in the corpus yet — no directory
  precedent to follow, so `type` needs an explicit INFERENCE per the task brief.

## STEP 1 — Scope the node around the run record, not the flow

Frame the document as the **workflow run as a persisted, queryable entity** (identity,
schema, `RunStatus` state machine and which states are actually reachable, how it is
created/updated/read) rather than re-narrating trigger paths. Declare
`relationships: references -> architecture-flows-workflow-execution` for the
step-by-step narrative, explicitly deferring it there. Done when: body drafted with no
paragraph duplicating that node's Sequence/Trigger content wholesale.

## STEP 2 — Write front matter + evidence ledger

`id: capabilities-workflows-workflow-run`, `type: capabilities` (explicit INFERENCE,
confidence ~0.6, directory-precedent reasoning since no capabilities-typed node is
merged yet), `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. Evidence entries per substantive claim, citing `path:start-end` (no
`#symbol=`/`#line=` fragments). Done when: every body claim has a ledger entry with
correct entry_class field rules (FACT+evidence, INFERENCE+evidence+confidence,
TEAM_KNOWLEDGE+provided_by).

## STEP 3 — Write the body

Sections: Trigger/preconditions/termination (run creation preconditions + reachable
vs. unreachable `RunStatus` values), Ordered interactions and data/state movement
(create → update → read lifecycle, current_step/execution_trace mutation), Trust-
boundary crossings (community-scoped PK/FK, fence re-verification tie-in, brief —
full detail deferred to the flow node), Failure/abort/rollback (finalize_run's
fire-and-forget DB write, stuck-Running gap, CLI observability gap), Scope and
omissions. Done when: DoD bullets from #841 are each satisfied by a named section.

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Done when: exit 0,
zero new FAIL entries beyond the known 21 pre-existing (#1951).

## STEP 5 — Gate + commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own command; confirm OK. Then `git add` + `git commit -s`. No push, no PR.

## GATES

- Zero new validate.py FAIL entries.
- Unit test suite OK before commit.
- No second hand-authored canonical corpus document created.

## BUDGET

Single session, no subagents needed — all research already gathered in this pass.

## OPEN

- Whether `type: capabilities` is the corpus's eventual settled answer for this
  directory is genuinely open (no merged precedent) — recorded as INFERENCE, not FACT.

## LEFT OUT

- Re-narrating the full trigger-path/step-execution sequence (owned by
  `architecture-flows-workflow-execution`).
- The approval-gate resume flow (WF-08, not implemented — already noted as a gap by
  the existing flow node).
- Workflow *definition* authoring/validation (owned by sibling #840).
