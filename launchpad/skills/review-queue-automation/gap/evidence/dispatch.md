# RQA gap analysis — evidence: dispatch

Cluster `dispatch` per [`../clusters.md`](../clusters.md): turning a queued job into a
run — the dispatcher and its runtime-operations subcommands, model runners, the
plan, and isolated author worktrees. Revision `9267b6308714454a3b987622d90cda03a8972827`.
Paths are relative to `launchpad/skills/review-queue-automation/`, per
[`../methodology.md`](../methodology.md).

Files owned by this cluster (11, from `../clusters.md`): `scripts/dispatcher.py`,
`scripts/planner.py`, `scripts/runners.py`, `scripts/worktree.py`,
`tests/test_dispatch_flow.py`, `tests/test_dispatch_observability.py`,
`tests/test_planner.py`, `tests/test_runners.py`, `tests/test_runtime_ops.py`,
`tests/test_runtime_ownership.py`, `tests/test_worktree.py`.

---

### U-DISPATCH-01 — Onboarding/config fail-closed gate

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `main` refuses every subcommand when `load_repo_config` reports no valid repo-local config: it prints status `onboarding_required` with the missing-config reason and the onboarding command, and exits 1 without any GitHub or model activity. | scripts/dispatcher.py:2242-2255 | RQA-NFR-018 |

---

### U-DISPATCH-02 — Exclusive, crash-recoverable runtime lock

Files: scripts/dispatcher.py, tests/test_runtime_ownership.py

Rationale: `tests/test_runtime_ownership.py` asserts exactly the lock-exclusivity
and crash-release guarantee that `common.State.try_runtime_lock` provides and
`main` acquires before any subcommand runs, so the acquisition call site and the
lock's own guarantee are one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| Every subcommand first acquires `state.try_runtime_lock(args.command)`; a second command targeting the same state directory receives `sweep_already_running` and exits 0 without touching state, rather than running concurrently with the first. | scripts/dispatcher.py:2259-2266 | RQA-NFR-010 |
| The lock is process-scoped, not application-scoped: `try_runtime_lock` acquires an exclusive, non-blocking `fcntl.flock` (`LOCK_EX` plus `LOCK_NB`) on `runtime.lock` whose own docstring states "flock is the authority and is released by the kernel on crash"; a crashed owner process therefore does not permanently block a later command against the same state directory, which `tests/test_runtime_ownership.py` confirms by killing the owner and showing a second process then acquires the lock. | scripts/common.py:156-165, tests/test_runtime_ownership.py:33-57 | RQA-NFR-010 |

---

### U-DISPATCH-03 — Local health and status diagnostics (no network, mutation, or model calls)

Files: scripts/dispatcher.py, tests/test_runtime_ops.py

Rationale: `runtime_health` and `runtime_status` are wired through the same
`_LOCAL_COMMANDS` table and asserted together in `tests/test_runtime_ops.py`'s
health section, and both exist to let an operator confirm the state directory's
condition without touching GitHub or a model.

| claim | evidence | requirements |
| --- | --- | --- |
| `runtime_health` reports `healthy` only when the database integrity check passes, the state and log directories are writable, and no circuit breaker is open; otherwise it reports `degraded` and names the open breakers and the oldest unfinished job. | scripts/dispatcher.py:2056-2122 | RQA-NFR-010 |
| `runtime_status` returns per-status job counts, the lease count, and the state directory path, read entirely from local SQLite with no network activity. | scripts/dispatcher.py:2125-2137 | RQA-NFR-010 |

---

### U-DISPATCH-04 — Backup: a consistent local copy of the state database and snapshot archive

Files: scripts/dispatcher.py, tests/test_runtime_ops.py

Rationale: `tests/test_runtime_ops.py`'s `test_backup_produces_a_readable_copy_of_the_state`
is the only assertion of this command's behaviour, so the code and its proof are
one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `backup_state` uses `sqlite3.Connection.backup` — not a raw file copy — to take a backup of `state.sqlite3` into a timestamped destination, specifically so the copy stays consistent even while a WAL write is in flight, and separately copies the `snapshots` archive alongside it. | scripts/dispatcher.py:2032-2053 | RQA-NFR-010 |

---

### U-DISPATCH-05 — Cooldown/circuit-breaker reset

Files: scripts/dispatcher.py, tests/test_runtime_ops.py

Rationale: `tests/test_runtime_ops.py`'s `test_cooldown_reset_clears_providers_and_breakers`
is the only assertion of this command's behaviour, so the code and its proof are
one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `reset_cooldowns` deletes rows from the local `providers` table (all, or one `scope`) and clears circuit breakers via `budget.reset_breakers`; it is an explicit operator command — nothing under `scripts/` calls it automatically or on a timer — so a breaker opened by repeated provider failures cannot wedge the harness with no recorded path back to a working state. | scripts/dispatcher.py:2012-2029 | RQA-NFR-010 |

---

### U-DISPATCH-06 — Retention purge of terminal-job artifacts, dry-run by default

Files: scripts/dispatcher.py, tests/test_runtime_ops.py

Rationale: the dry-run default and the audit-trail-survives-a-purge guarantee are
asserted together by `tests/test_runtime_ops.py`'s retention tests, and both
describe the single `retention_sweep` responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `retention_sweep` is dry-run unless called with `apply=True`, and even when applied it purges only artifact bytes (model output, evidence copies, JSONL logs) — the `jobs` row, every `ledger_entries` row, `mutations`, `approval_decisions` and `human_requests` all survive. A `retention_manifest` ledger entry records, per artifact, its size and sha256 hash when the file reads cleanly, or a bare path-plus-error marker when reading it raises `OSError` — either way the file is still purged. | scripts/dispatcher.py:1941-1998, scripts/dispatcher.py:1917-1921 | RQA-FR-012 |
| Retention only considers jobs already in one of the eight `TERMINAL_STATUSES`, older than the configured (or overridden) retention window; a job that could still be resumed is never eligible. | scripts/dispatcher.py:1882-1885, scripts/dispatcher.py:1961-1970 | RQA-NFR-010 |

---

### U-DISPATCH-07 — Crash recovery: releasing stranded leases and safe-stopping interrupted jobs without re-deciding

Files: scripts/dispatcher.py, tests/test_runtime_ops.py, tests/test_runtime_ownership.py

Rationale: `recover_interrupted`'s guarantee — release verified leases, safe-stop
without re-running a decision — is exercised from two angles across these two
test files (a crashed worker that had claimed a lease, and one that had not), so
they corroborate one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `recover_interrupted` REST-verifies and releases every lease recorded in the state directory through the normal lease helper, then safe-stops the job if its status is a legal predecessor of `safe_stop` — it never re-runs the job's model or approval decision. | scripts/dispatcher.py:1808-1843 | RQA-NFR-010 |
| A job left in one of the eight `ACTIVE_WORKER_STATUSES` with no recorded lease (killed before, or without, claiming one) is also safe-stopped by `recover_interrupted`, while jobs waiting on a person (`human_approval_pending`, `human_required`, `degraded_draft`, `held`, `retryable`, queued `detected`) are deliberately left untouched. | scripts/dispatcher.py:1852-1865, scripts/dispatcher.py:1868-1878 | RQA-FR-027 |

---

### U-DISPATCH-08 — Bounded managed sweep: queue reconciliation, FIFO job selection, and cadence gating

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_managed_sweep` reconciles the queue, then selects up to a caller-supplied `limit` of `detected` jobs for one lane in a stable FIFO order (`created_at, id`); `limit` bounds batch size, not parallelism, and processing is serial per state directory. | scripts/dispatcher.py:2140-2164 | RQA-BR-012 |
| `tick` sweeps only when the persisted cadence (`cadence_read`/`cadence_due`) says a sweep is due, or `--force` is given; otherwise it reports `not_due`, and it always reschedules the next run via `cadence_decide`/`schedule_after` after a real sweep. | scripts/dispatcher.py:2323-2372 | RQA-BR-012 |

---

### U-DISPATCH-09 — Snapshot pinning and capability-clamped authority: a job never runs with more authority than its pinned snapshot or proven GitHub capability grants

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `resolve_snapshot` returns a job's already-pinned config/policy snapshot on resume rather than the caller's current (possibly newer) config, so editing the repo-local config mid-flight cannot retroactively change an in-flight job's authority, thresholds or model routes. | scripts/dispatcher.py:1556-1571 | RQA-FR-004, RQA-NFR-005 |
| When a job's pinned snapshot hash no longer resolves in the snapshot archive, `resolve_snapshot` refuses to silently upgrade it to the caller's current config and instead returns the caller's config with the missing-archive reason recorded. | scripts/dispatcher.py:1567-1571 | RQA-NFR-010 |
| GitHub capability is probed at most once per CLI invocation, never once per job, and the resulting `capability_mode` can only reduce the authority a job's pinned snapshot already grants — it is never able to widen it. | scripts/dispatcher.py:1640-1644, scripts/dispatcher.py:1659-1665, scripts/dispatcher.py:2286-2307 | RQA-NFR-018 |

---

### U-DISPATCH-10 — Review-lease claim and guaranteed release around one job's dispatch

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| Before any model spend, `run_job` claims the PR's review lease and refuses to proceed (returns `gated`) when the lease is already held by a different job, so two concurrent sweeps cannot dispatch duplicate reviewer work against the same PR at the same time. | scripts/dispatcher.py:1684-1720 | RQA-NFR-010 |
| The lease is released in a `finally` block on every exit path, including an unexpected exception, so a crash never permanently strands a PR's review lease. | scripts/dispatcher.py:1732-1754 | RQA-NFR-010 |

---

### U-DISPATCH-11 — Canary/lane gating before any dispatch work begins

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `canary_allowed` reads a live per-lane approved status from the SQLite `canaries` table when a row exists, and otherwise falls back to a repo-local config key (`incoming_canary_approved` / `author_canary_approved`); `run_job` returns a `gated` status with no GitHub or model activity whenever this reads false, and because the fallback is an ordinary config key, flipping the gate takes effect on the very next dispatch with no rebuild or redeploy. | scripts/dispatcher.py:1797-1805, scripts/dispatcher.py:1670-1678 | RQA-FR-004, RQA-NFR-005 |

---

### U-DISPATCH-12 — Pre-spend budget reservation gates the panel

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_reserve_budget` reserves the strategy's declared `budget_tokens` BEFORE the panel runs; a refusal downgrades the job to `human_required` or `degraded_draft` and records the reason, without ever letting the panel spend. | scripts/dispatcher.py:1108-1150, scripts/dispatcher.py:1252-1286 | RQA-FR-022, RQA-FR-039 |

---

### U-DISPATCH-13 — Post-panel spend recording uses the reservation as a stand-in when no actual token count is available

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| After the panel completes, the recorded spend is the panel result's own token count when the runner reports one, and otherwise falls back to the pre-panel reservation itself — the code's own comment states "runners do not report token counts" — so for most panels the recorded consumption is the estimate, not a measurement of what was actually spent. | scripts/dispatcher.py:1323-1329 | RQA-FR-021 |

---

### U-DISPATCH-14 — Panel-driving evidence and degradation loop

Files: scripts/dispatcher.py, tests/test_dispatch_flow.py

Rationale: `tests/test_dispatch_flow.py` drives exactly this state machine end to
end through fake panels (missing-evidence, partial-panel, job-blocking paths), so
the orchestration code and its behavioural proof are one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| The panel is driven via `drive(minimum, assess, max_steps=6)`; a panel verdict signalling `MISSING_EVIDENCE` raises `EvidenceIncompleteError` rather than re-running the identical model loop. | scripts/dispatcher.py:1339-1345, scripts/dispatcher.py:1395-1397 | RQA-BR-012 |
| `_evidence_missing` performs exactly one bounded, deterministic evidence gather; if that gather itself raises, the job escalates to `human_required`, naming the failure in the escalation reason, rather than retrying. | scripts/dispatcher.py:347-369 | RQA-FR-026 |
| A panel that completes with a reviewer slot producing no fresh verdict after its fallback chain ran (`PartialPanel`) degrades the job to `degraded_draft` — a non-authoritative, explicitly incomplete artifact, never a mutation. | scripts/dispatcher.py:69-76, scripts/dispatcher.py:1369-1384 | RQA-FR-038, RQA-NFR-007 |
| A `JobBlockingError` raised from within the panel-driving loop transitions the job to `human_required`, using the exception's own message as the reason. | scripts/dispatcher.py:1385-1394 | RQA-NFR-010 |

---

### U-DISPATCH-15 — Approval evaluation and human-escalation routing

Files: scripts/dispatcher.py, tests/test_dispatch_flow.py

Rationale: `tests/test_dispatch_flow.py`'s draft/non-identity-author test
exercises exactly the human-escalation branch this unit evidences, and the
approval-evaluation call that branch's disposition depends on is part of the
same decision-routing responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| A complete, successful panel advances the job through `adjudication` -> `approval_evaluation` and calls `eval_approval` with the persisted PR facts and collected verdicts before any action is taken. | scripts/dispatcher.py:1399-1434 | RQA-FR-011, RQA-FR-028, RQA-FR-037 |
| When approval evaluation returns `human_escalation` (for example a draft PR or a non-identity author), the job enqueues a durable human request naming the risk score/band and a rationale; a delivery failure is logged and reported but never removes the request from the pending queue. | scripts/dispatcher.py:1482-1512, scripts/dispatcher.py:399-421 | RQA-FR-026, RQA-NFR-010 |

---

### U-DISPATCH-16 — Live-approval mutation execution and its guarded failure paths

Files: scripts/dispatcher.py, tests/test_dispatch_flow.py

Rationale: `tests/test_dispatch_flow.py`'s live-path tests (executes-and-completes,
denial-queues-human, uncertain-safe-stops, missing-node-id-safe-stops) exercise
exactly the branches `_execute_live_approval` implements, so the mutation code
and its guarded-failure proof are one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `_execute_live_approval` calls `approval_action.approve`, which re-validates the PR head over REST immediately before mutating; on success the job advances `approval_action` -> `completed_auto_approved`. | scripts/dispatcher.py:631-665 | RQA-FR-028 |
| A `DENIED` or `STALE` outcome enqueues a durable human request naming the risk score/band, failed gates and the outcome as rationale, then transitions to `human_approval_pending`; `UNCERTAIN` or any other failure safe-stops without retry. | scripts/dispatcher.py:667-698 | RQA-FR-026, RQA-NFR-010 |
| The approve mutation is idempotency-keyed on the decision id (`approve-{decision_id}`), so re-entering after a crash mid-call re-validates the head rather than duplicating the mutation. | scripts/dispatcher.py:593-596, scripts/approval_action.py:166 | RQA-NFR-010 |

---

### U-DISPATCH-17 — CHANGES_REQUESTED execution: corroboration, per-activity authority, and a revalidation gate before any mutation

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_execute_request_changes` requires every acted-on finding to be corroborated (two distinct provider families, or one family citing a check that actually failed) before any authority check; uncorroborated findings escalate to `human_required` instead of blocking the PR. | scripts/dispatcher.py:910-939 | RQA-FR-010, RQA-BR-008 |
| The `request_changes` authority is checked via `mode_for(local_cfg, repo, "request_changes")` independently of every other activity; when it is not `live`, verified defects still escalate to a human rather than being acted on. | scripts/dispatcher.py:941-950 | RQA-NFR-017 |
| The deterministic `request_changes_gate` (bounded revalidation against a fresh head) must pass before the mutation runs; a denial enqueues a human request naming the failed gates rather than posting. | scripts/dispatcher.py:964-999 | RQA-NFR-010, RQA-FR-026 |
| The posted CHANGES_REQUESTED body lists only corroborated findings and states that uncorroborated ones are excluded and escalated to a human instead. | scripts/dispatcher.py:1041-1063 | RQA-BR-008 |

---

### U-DISPATCH-18 — Advisory-mode review posting (shadow / disabled dispositions)

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_post_advisory_review` posts a comment naming verified vs. unverified findings, the achieved assurance, and the routes/activities actually executed — read back from the ledger rather than from configuration. | scripts/dispatcher.py:801-831 | RQA-BR-008 |
| Posting is idempotent per job, so re-dispatching the same PR revision does not duplicate the advisory comment. | scripts/dispatcher.py:787-789 | RQA-BR-007 |
| Both the `shadow` disposition (would-approve recorded, no mutation) and the `disabled` approval mode post this advisory and transition to `completed_advisory`, never mutating GitHub's review state. | scripts/dispatcher.py:1471-1481, scripts/dispatcher.py:1513-1523 | RQA-NFR-017 |

---

### U-DISPATCH-19 — Observability: one otel-jsonl event per orchestration milestone

Files: scripts/dispatcher.py, tests/test_dispatch_observability.py

Rationale: `tests/test_dispatch_observability.py` (T26) asserts exactly the event
vocabulary, ordering and redaction that these `_emit_*`/`_log` helpers produce,
so the emission code and its behavioural proof are one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `_log` validates every `event` name against the fixed `logging_otel.JOB_EVENTS` registry and raises `SafeStopSignal` for an unregistered name, so no ad-hoc event name can drift into the trace. | scripts/dispatcher.py:154-157 | RQA-BR-003 |
| `_emit_panel_trace` emits exactly one `strategy` event and one `planner` event per panel run, and one `route_selection` event per recorded route (bounded by `_MAX_LOGGED_ROUTES=4`) — or a single distinct `unrouted` warning event when no route was recorded — reading the planner's activities and the executed routes back from the ledger rather than re-deriving them. | scripts/dispatcher.py:1153-1218, scripts/dispatcher.py:1200-1217 | RQA-FR-012 |
| Any exception raised while emitting a log event is converted to `SafeStopSignal`, so an audit-logging failure safe-stops the job rather than leaving a silent gap in the trace. | scripts/dispatcher.py:158-168 | RQA-NFR-010 |

---

### U-DISPATCH-20 — Ledger recording of every decision, action, assurance computation and finding

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_ledger_record` appends one ledger entry per decision, action, finding or assurance computation, tagged with the job's pinned snapshot hash and policy version; a write failure is silently swallowed by a bare `except Exception: pass` — the function's own docstring claims failures "surface in the JSONL log", but no logging call exists anywhere in the write path at this revision, so that documented guarantee does not hold. | scripts/dispatcher.py:202-218 | RQA-FR-012, RQA-NFR-032 |

---

### U-DISPATCH-21 — Safe-stop containment: a state-persistence or audit-logging failure stops only the affected job

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_transition_guarded` converts any exception from `state.transition` other than `JobBlockingError` into `SafeStopSignal`, so a state-persistence failure safe-stops the job rather than propagating an unhandled error. | scripts/dispatcher.py:129-134 | RQA-NFR-010 |
| `run_job` catches `SafeStopSignal` and best-effort-transitions the job to `safe_stop` via `_arrive_safe_stop`, swallowing any secondary failure so the caller still returns a result. | scripts/dispatcher.py:179-198, scripts/dispatcher.py:1727-1728 | RQA-NFR-010 |

---

### U-DISPATCH-22 — Managed-sweep per-job batch-error isolation

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `_managed_sweep` catches a per-job exception and records it as that job's own `error` result, without aborting the rest of the batch — one job's failure does not stop the sweep from reaching the remaining FIFO jobs. | scripts/dispatcher.py:2166-2176 | RQA-NFR-007 |

---

### U-DISPATCH-23 — Degradation-ladder helper (`degrade()`), reachable only from a resilience-cluster test

Files: scripts/dispatcher.py

| claim | evidence | requirements |
| --- | --- | --- |
| `degrade()` moves a job exactly one reachable rung down a fixed ladder (live -> shadow -> human pending -> advisory -> degraded evidence -> safe stop), refuses a nonexistent job or an unranked (terminal) status, and is a no-op once the job is already at the floor. | scripts/dispatcher.py:83-97, scripts/dispatcher.py:424-459 | RQA-NFR-010 |
| No file under `scripts/` calls `degrade`; the only caller found in the tree is `tests/test_degradation.py`, which `gap/clusters.md` assigns to the `resilience` cluster, not `dispatch`. | scripts/dispatcher.py:424, tests/test_degradation.py:57 | RQA-NFR-010 |

---

### U-DISPATCH-24 — Deterministic review-activity planning

Files: scripts/planner.py, tests/test_planner.py

Rationale: the selection logic in `planner.py` and the property tests in
`test_planner.py` (determinism, per-activity omission recording, terse prompt
rendering) assert one activity-selection contract; splitting the file from the
tests that establish its guarantees would separate a mechanism from its proof.

| claim | evidence | requirements |
| --- | --- | --- |
| `plan_review` derives every activity selection from observable PR facts (changed paths, diff size, whether a check is failing, whether this is a rereview, whether reviewers previously disagreed, whether a blocker is already verified) rather than from any model's judgement, and records a reason for every selected activity AND a reason for every omitted one. | scripts/planner.py:129-137, scripts/planner.py:183-186, scripts/planner.py:194-247 | RQA-BR-014 |
| Given identical inputs, `plan_review` always returns an identical plan: the module imports no `random`, `time`, `uuid` or other nondeterministic source, and `classify_changes`/`plan_review` decide every selection from exactly the explicit keyword arguments supplied to the call, with no hidden module-level state read. | scripts/planner.py:17-21, scripts/planner.py:129-137, scripts/planner.py:162-181, tests/test_planner.py:168 | RQA-BR-002 |
| A change made only of documentation and/or test files omits the baseline `DECOMPOSE` and `FALSIFY_CORRECTNESS` questions, recording why; a change with any code path alongside docs/tests keeps them. | scripts/planner.py:188-200 | RQA-FR-019 |
| `RED_TEAM_SECURITY`, `CHECK_COMPATIBILITY` and `PREMORTEM_RELIABILITY` are each selected only when the changed paths match a specific pattern class (security/auth paths; migration/schema/dependency files; infrastructure/CI/concurrency paths respectively), each recorded with its own reason, and each omitted with its own reason otherwise. | scripts/planner.py:202-219 | RQA-BR-014 |
| `INVESTIGATE_HYPOTHESIS` is selected when a required check is failing, asking the reviewer to establish the cause from evidence before judging the change. | scripts/planner.py:231-234 | RQA-BR-009 |

---

### U-DISPATCH-25 — Reviewer runner adapters: read-only, auditable invocations per transport

Files: scripts/runners.py, tests/test_runners.py

Rationale: `runners.py`'s adapter contract and `test_runners.py`'s per-transport
assertions (read-only proof, effort honesty, no bypass flag, prompt-position)
describe and prove the same three-adapter interface together.

| claim | evidence | requirements |
| --- | --- | --- |
| `runners.py` provides three interchangeable CLI transports (`omp`, `claude`, `codex`) behind one `RunnerAdapter`/`build_invocation` interface, so the reviewer invocation is not hardcoded to a single harness. | scripts/runners.py:138-157, scripts/runners.py:174-208 | RQA-NFR-001 |
| `adapter_for` raises `UnknownRunnerError` for any runner name outside the fixed three-entry `ADAPTERS` mapping; there is no plugin or config-driven path admitting a harness that is not already coded here. | scripts/runners.py:164-171, scripts/runners.py:138-157 | RQA-FR-030 |
| `build_invocation` records `effort_enforced=False` whenever the requested reasoning-effort level is outside a transport's `enforceable_efforts` (always false for `claude`, which exposes no such flag), rather than letting the built invocation claim an assurance axis its transport did not actually apply — the record states what actually ran, not what was requested. | scripts/runners.py:192-198, scripts/runners.py:145-150 | RQA-BR-003 |
| Every built `Invocation` carries its runner, selector, effort, whether that effort was enforced, and the exact flags relied on for the read-only claim (`read_only_proof`), so a later audit can reconstruct what was actually run without a second lookup. | scripts/runners.py:41-59 | RQA-FR-012 |

---

### U-DISPATCH-26 — Isolated author-triage worktree operations (unreachable from any product entrypoint)

Files: scripts/worktree.py, tests/test_worktree.py

Rationale: `worktree.py`'s `create`/`commit`/`push`/`clean` functions and
`test_worktree.py`'s fakes-only assertions of their exact behaviour are one
mechanism, and the reachability finding below applies to the whole file, not to
one function in isolation.

| claim | evidence | requirements |
| --- | --- | --- |
| `create` builds the worktree at `<repo_root>/.worktrees/rqa-<job>` — a directory separate from the repository's own working tree — from the exact configured PR head SHA or head branch, and raises `WorktreeError` rather than falling back to the base branch when neither is configured. | scripts/worktree.py:47-49, scripts/worktree.py:121-134, scripts/worktree.py:143-148 | RQA-NFR-020 |
| `push` only ever pushes the exact configured PR head branch with a plain fast-forward; it refuses to push an internal `rqa/` branch to the PR remote and refuses `force=True` outright. | scripts/worktree.py:213-222 | RQA-NFR-021 |
| `references/contracts.md`, `SKILL.md` and `references/classification.md` describe an author-triage lane that fixes findings and pushes to the PR branch inside an isolated worktree; no file under `scripts/` imports or calls `worktree.create`/`commit`/`push`/`clean` at this revision — the only occurrence of the string "worktree" in another script is a comment, and the module's only importers are two test files. | references/contracts.md:16, SKILL.md:76, references/classification.md:21, scripts/runners.py:120, tests/test_worktree.py:20, tests/test_integration.py:133 | RQA-NFR-020, RQA-NFR-021 |
