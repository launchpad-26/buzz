# Plan: issue #1265 — platforms/relay/command-executor corpus node

## ALREADY TRUE

- Worktree `__worktrees/task-1265-relay-command-executor` exists, branched
  `task/1265-relay-command-executor` off `origin/launchpad` at commit
  `131b02f989684117d9ab1dd426f1673fa638e523`.
- `launchpad/docs/corpus/platforms/relay/command-executor.md` does not exist yet
  (confirmed via `test -f`), and no `platforms/**` node exists anywhere on
  `origin/launchpad` (`git ls-tree -r origin/launchpad -- launchpad/docs/corpus/platforms`
  returns nothing).
- The actual component is `crates/buzz-relay/src/handlers/command_executor.rs`
  (1630 lines): its own crate-doc-style `//!` comment names it "Command
  executor — transactional event processing for command kinds." It is the sole
  dispatcher `buzz-relay/src/handlers/ingest.rs`'s `ingest_event_inner` routes
  to (`ingest.rs:2277-2279`, guarded by `buzz_core::kind::is_command_kind`,
  `buzz-core/src/kind.rs:815-826`) for the seven Buzz "command" event kinds:
  DM open/add-member/hide (41010-41012), workflow definition upsert (30620),
  manual workflow trigger (46020), and approval grant/deny (46030-46031).
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md`
  (`architecture-flows-workflow-execution`, merged on `origin/launchpad`)
  already documents the shared step-execution engine
  (`buzz_workflow::executor::execute_from_step`/`execute_steps`) that this
  component's `handle_workflow_trigger`, `handle_approval_grant`, and
  `resume_workflow_after_approval` all invoke or resume — that node's own
  Scope statement explicitly excludes command-kind events, so this node covers
  the relay-side dispatch/auth/persistence half and references it rather than
  re-describing step execution.
- No `component`/`architecture-component` template is merged yet; per the
  batch's own finding #4, sibling in-flight nodes under `platforms/**` have
  settled on `type: platforms`, borrowing `templates/component.md`'s section
  shape (Responsibility / Public interface / Dependencies / Boundary /
  Relationships / Scope and omissions) since no platforms-specific template
  exists.

## STEP 1 — Confirm scope and read every handler body from disk

Read the full file directly (not via a possibly-stale index) to ground every
claim in real, currently-checked-out source: `handle_command` (dispatch),
`persist_command_event` + `parse_expected_workflow_revision` (idempotency/CAS
persistence), the five domain handlers (`handle_dm_open`,
`handle_dm_add_member`, `handle_dm_hide`, `handle_workflow_def`,
`handle_workflow_trigger`, `handle_approval_grant`, `handle_approval_deny`),
`check_approver_spec`, and `resume_workflow_after_approval`. Cross-check the
upstream call site (`ingest.rs`'s scope gate at `required_scope_for_kind`,
lines 542-544) and the five kept unit tests (three plain `#[test]`s plus two
`#[ignore = "requires Postgres"]` integration tests) that exercise this file.
**Done when:** every claim in the drafted node cites a path/line range that
was actually opened in this step.

## STEP 2 — Draft the corpus node

Write `launchpad/docs/corpus/platforms/relay/command-executor.md` with
`type: platforms`, `status: draft`, `origin: launchpad`, `audiences: [agent,
developer]`, following `component.md`'s required sections: Purpose/scope,
Responsibility, Public interface (the seven-kind dispatch table), Dependencies
(depends-on: buzz-core, buzz-db, buzz-deletion, buzz-datastore-tracing,
buzz-workflow, per `Cargo.toml`; depended-on-by: `ingest.rs` only, per
crate-wide grep), Boundary (explicitly not: workflow step execution — see the
referenced flow node; not workflow YAML schema/validation itself; not the DB
schema), Relationships (`references: architecture-flows-workflow-execution`),
and Scope and omissions (naming what was expected but not verified, e.g. the
`#[ignore]`d Postgres tests were read but not run).
**Done when:** every DoD bullet from issue #1265 is satisfied by a specific
section, and every evidence entry is classified FACT/INFERENCE/TEAM_KNOWLEDGE
per `AGENTS.md`.

## STEP 3 — Validate: zero new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py`, note the
result, then temporarily move the new file out, re-run, and diff the FAIL
sets to confirm the new node introduces none.
**Done when:** the FAIL set with and without the new file is identical, and
the file is restored.

## STEP 4 — Earn the commit gate

Run the corpus unit-test command as the sole content of one Bash call, then
`git add` + `git commit -s` as a second call. Retry once on a stamp-attribution
refusal per finding #6, otherwise stop and report BLOCKED.
**Done when:** a local commit exists on `task/1265-relay-command-executor`.

## STEP 5 — Re-verify

Re-read the diff against issue #1265's DoD checklist and re-open every cited
file/line one more time before reporting back.
**Done when:** every DoD bullet maps to a body section and every citation
resolves.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `python3 launchpad/project-intelligence/corpus/validate.py` → zero *new* FAIL entries versus the file-removed baseline.
- Every evidence citation opened and read in Step 1, not paraphrased from a summary.

## OPEN

- Whether `type: platforms` is the eventual settled convention or will be
  revised once a platforms-specific template lands — following the batch's
  own documented inference (finding #4), not an independent decision made
  here.
- Whether the two `#[ignore = "requires Postgres"]` tests actually pass today
  was not established (no local Postgres run in this task) — read only.

## LEFT OUT

- No second corpus node. Any newly discovered second concept (e.g. a
  standalone node for `buzz_workflow::executor`) is out of scope and would be
  filed separately.
- No changes to runtime code, tests, or the referenced flow node.
