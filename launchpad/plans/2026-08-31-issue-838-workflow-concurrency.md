# Plan: issue #838 — document capabilities/workflows/workflow-concurrency.md

Parent PRD: #613. Repo revision: commit `131b02f989684117d9ab1dd426f1673fa638e523`
(origin/launchpad tip at worktree creation).

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet on origin/launchpad —
  no merged sibling sets a `type` precedent for this Feature's `capabilities/workflows/*`
  batch. 49 sibling task issues exist under the same path prefix (#829-#844 etc.),
  none merged as corpus nodes yet.
- `crates/buzz-workflow` implements exactly one concurrency-limiting mechanism: a
  process-wide `tokio::sync::Semaphore` (`WorkflowEngine.run_semaphore`), sized from
  `WorkflowConfig.max_concurrent` (default 100), acquired via `try_acquire()`
  (non-blocking, no queue) at the top of both `executor::execute_run` and
  `executor::execute_from_step`. Failure to acquire returns
  `WorkflowError::CapacityExceeded` (`error.rs`), which `finalize_run` persists as a
  `Failed` run with `code: "capacity_exceeded"`.
- Every production call site constructs `WorkflowConfig::default()` (confirmed via
  repo-wide grep: `main.rs`, `router.rs`, `state.rs`, `workflow_sink.rs`, and all
  `api/*` admin/test builders) — there is no env var or config field overriding
  `max_concurrent` today, so the limit is a fixed global 100 concurrent runs per relay
  process, not a per-workflow-definition or per-channel concurrency group.
- No dedicated automated test exercises semaphore exhaustion / `CapacityExceeded`
  end-to-end; the only tests assert the default and a custom value of
  `max_concurrent` round-trip through `WorkflowConfig`.
- The "claim row" dedupe mechanism near `lib.rs:693` (scheduled-fire at-most-once
  claims) is a *different* concept — trigger-level dedup for cron/interval firing,
  not run-level concurrency throttling — and is covered by other sibling tasks
  (e.g. #832 schedule-trigger, #841 workflow-run). It will be mentioned only as an
  explicit non-goal, not folded into this node.

## STEP 1 — Draft the node

Create `launchpad/docs/corpus/capabilities/workflows/workflow-concurrency.md` with:
- Front matter: `id: capabilities-workflows-workflow-concurrency`, `type: capabilities`
  (INFERENCE — no merged sibling precedent exists yet; `capabilities` is the schema
  enum member matching the `capabilities/` path segment this whole batch is filed
  under, and no other enum member fits a runtime behavior/limit like this), `status:
  draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`.
- Evidence citations as `path:line`/`path:start-end` only (no `#symbol=`/`#line=`
  fragments — validate.py can't resolve those).
- Body: what the capability is (global fail-fast concurrency ceiling), the actors
  (WorkflowEngine, any code path that creates a run: `on_event`, the cron/interval
  loop, approval-resume), behavioral rules (try_acquire, no queueing, fail-closed to
  `Failed`/`capacity_exceeded`, default 100, single process-wide scope, not
  configurable in production today), explicit non-goals (no per-definition group, no
  per-channel/per-owner limit, not the scheduled-fire dedup claim), links to
  implementation (executor.rs, error.rs, lib.rs), and a Maturity/Verification section
  stating no automated test exercises exhaustion behavior.
- No `relationships` — no other corpus node for this Feature is merged yet.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm the new
node adds zero new FAIL entries beyond the known 21 pre-existing ones (#1951).

## STEP 3 — Earn the gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own call. On `OK`, commit the new doc + this
plan with `git commit -s`.

## GATES

- `validate.py`: zero new FAIL entries.
- `unittest discover` on corpus tests: `OK`.
- Every DoD bullet in issue #838 satisfied line by line in self-review.

## BUDGET

Single doc, single commit, no code changes. ~3 tool-call steps after research.

## OPEN

- Whether `type: capabilities` will match what other agents in this batch converge
  on for sibling `capabilities/workflows/*` nodes — flagged as INFERENCE in the
  node's own evidence so a later integration pass can reconcile if a different
  precedent emerges from a sibling merging first.

## LEFT OUT

- Any change to `crates/buzz-workflow` runtime behavior (e.g. making
  `max_concurrent` configurable) — out of scope per issue #838, would be a separate
  implementation issue if wanted.
- Documenting the scheduled-fire claim/dedupe mechanism — a distinct concept, left
  to its own sibling task.
