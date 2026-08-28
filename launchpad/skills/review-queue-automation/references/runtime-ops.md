# Runtime operations: observability, cost controls, retention

This is the operator reference for the orchestrator's runtime surface — the
JSONL trace a job emits, the cost and rate-limit controls that bound its spend,
and the maintenance commands that keep a state directory healthy.

It covers `dispatcher.py`, `budget.py`, `logging_otel.py`, `strategies.py` and
the `policy`, `budget` and `retention` sections of the repo-local config. For
what the skill *is*, start at `SKILL.md`; for day-to-day operation, `OPERATORS.md`.

Everything here is local: SQLite in the configured `state_dir` and JSON Lines
under `logging.directory`. No exporters, no network, no SDKs.

---

## 1. The job trace

### What changed

`JobLogger` was constructed by the dispatcher and **never called on**. Across all
of `scripts/` there were five `logger.*` call sites, none of them in the
orchestrator, so the only trace of a job was whatever state transitions
`common.State.transition` happened to write. A job's route, plan, budget,
decision and external actions were invisible.

The orchestrator now emits a named event for every state change and every
external action. The names live in `logging_otel.JOB_EVENTS` — one authority for
what a complete trace looks like — and `dispatcher._log` rejects a name outside
that registry, so a free-form string cannot quietly drift into the trace.

### Where it lands

```
<logging.directory>/jobs/<job-id>/
  events.jsonl                      append-only, one JSON object per line
  attempts/attempt-001.json         immutable, one per panel invocation
  diagnostics/…                     capped (8 KB), redacted stderr excerpts
```

Read it back with `logging_otel.read_events(path)`.

### The event set

| Event | When | Key attributes |
|---|---|---|
| `queueing` | the job is selected for dispatch | `job.lane`, `github.head.sha`, `job.status` |
| `preflight` | config, snapshot, capability and canary checks concluded | `preflight.canary_approved`, `preflight.snapshot_pinned`, `policy.version`, `github.capability_mode`, `latency.ms` |
| `lease_acquired` | the review lease is claimed, **before** any model spend | `lease.login`, `latency.ms` |
| `lease_released` | the lease is released, on every exit path | `latency.ms` |
| `evidence` | the evidence bundle backing the job | `evidence.present`, `evidence.fresh`, `evidence.checks`, `evidence.collected_at` |
| `rereview` | this head supersedes a previously reviewed revision | `review.prior_revisions` |
| `budget` | the pre-spend reservation and its headroom | `budget.limit`, `budget.downgrade`, `budget.breaker`, `budget.headroom.*`, `cost.tokens_reserved`, `review.attempts` |
| `planner` | the deterministic review plan | `planner.activities`, `planner.focus`, `planner.rereview` |
| `strategy` | which strategy and fallback recipe ran | `reasoning.strategy`, `reasoning.recipe`, `reasoning.roles`, `reasoning.disagreement`, `cost.tokens`, `latency.ms` |
| `route_selection` | which model route actually executed (one per slot, capped at 4) | `route.key`, `route.slot`, `route.provider_family`, `route.effort_enforced` |
| `decision` | the disposition the job reached, and why | `decision.disposition`, `decision.reason`, `risk.score`, `approval.failed_gates` |
| `human_queue` | a durable human request was enqueued | `human.request_id`, `human.action`, `human.policy_hash` |
| `mutation` | an external (GitHub) action was attempted | `mutation.operation`, `mutation.outcome`, `mutation.verified` |
| `verify` | a revalidation of the reviewed head | `verify.subject`, `verify.ok`, `verify.detail` |
| `safe_stop` | the job stopped safely without completing | `job.reason` |

`logging_otel.REQUIRED_JOB_EVENTS` is the subset every job reaching a terminal
decision must emit. `mutation`, `human_queue`, `rereview` and `safe_stop` are
branch-dependent and therefore not required.

`tests/test_dispatch_observability.py` reads a faked end-to-end dispatch back and
fails if any required event is missing. Each one has been confirmed load-bearing
by removing it and watching the suite go red.

### Cost, token and latency attributes

`logging_otel.metric_attributes()` is the only producer. Every value is coerced
to a non-negative integer and clamped to `MAX_METRIC_VALUE` (1e9); a value that
was never measured is **omitted** rather than logged as zero, because "not
measured" and "zero" are different facts.

> **Trap.** `_is_sensitive_key` matches `token` as a substring, so `cost.tokens`
> and `cost.tokens_reserved` were being written to the log as `<redacted>` — an
> observability control silently eaten by a security control. Those two exact
> names are allowlisted in `logging_otel.SAFE_METRIC_KEYS`; the allowlist is
> closed. Budget headroom attributes drop the `_tokens` suffix
> (`budget.headroom.per_pr`) for the same reason. **If you add a metric whose
> name contains a hint word, it will be redacted unless you allowlist it — and
> allowlist it only when the value is provably a number.**

### Redaction

Unchanged and still enforced: no token, bearer, JWT, raw env, PR body, or
nonce-enveloped evidence can reach an event, an attempt artifact, or a
diagnostic. `test_dispatch_observability.py` drives a hostile panel result
carrying a `ghp_` token and a JWT through the orchestrator and asserts neither
appears in the trace.

---

## 2. Snapshot pinning actually engages

The shipped config had **no `policy` section**, so `snapshot.build_snapshot`
raised `SnapshotError`, `dispatcher.resolve_snapshot` degraded to
`{"pinned": false, …}`, and every job ran unpinned with a blank `policy_version`
in the ledger. The pinning guarantee and the atomic policy reload were both
implemented, tested, and inert.

`config.policy_defaults(config)` now **derives** the inline policy from the
config, mirroring it verbatim — authority, approval thresholds, risk bands and
protected triggers, human-queue expiry, assurance. It invents nothing and widens
nothing. `onboarding_defaults` calls it, so every new install pins.

Any required approval key the source config omits falls back to the same default
`onboarding_defaults` uses, because a *present but invalid* policy fails
validation and leaves the job unpinned anyway — the same silent failure wearing a
different hat.

Verify pinning on a live config:

```bash
python3 scripts/dispatcher.py --repo-root <repo> status   # state dir is reachable
# then, after a dispatch, the result carries:
#   "snapshot": {"pinned": true, "policy_version": "v1", "snapshot_hash": "…"}
```

A config with no policy is still dispatchable — it is **reported** as unpinned
with a reason, never silently treated as pinned.

---

## 3. Cost and rate-limit controls

`scripts/budget.py`. The rule is **reserve before you spend**:

1. `reserve()` runs in the orchestrator **before** the panel. It projects
   `already spent + the strategy's declared budget_tokens` against every limit.
   A projection that would breach a limit is refused, and the job downgrades —
   so a budget is reached and respected, never exceeded and then noticed.
2. `record_spend()` runs after the panel, charging the reservation as an
   **upper bound** (runners do not report token counts). It over-counts rather
   than under-counts, which makes the next reservation stricter, never looser.

### Config

```jsonc
"budget": {
  "per_pr_tokens":          2000000,   // 0 disables this axis only
  "per_repo_daily_tokens": 40000000,
  "per_model_daily_tokens":20000000,
  "max_attempts_per_job":         6,   // retry ceiling
  "max_concurrent_jobs":          1,   // in-flight cap
  "rest_remaining_floor":         0,   // 0 = off; see the note below
  "circuit_breaker": { "failure_threshold": 3, "cooldown_seconds": 900 }
}
```

A malformed section is a config **error**, not a silent fallback — a typo can
never quietly remove a spend ceiling. An absent section applies `budget.DEFAULTS`,
which are generous but finite.

> `rest_remaining_floor` defaults to **0 (off)** and deliberately does **not**
> inherit `poll.rest_remaining_floor`. The approval gate already fails closed on
> that floor immediately before a mutation, which is the more precise place; a
> pre-spend copy would pre-empt it and turn a `human_escalation` into a plain
> refusal. Set it only if you want *spend itself* gated on REST headroom.

> `budget.per_*_tokens` key names contain `token`, which `config.find_secret_keys`
> flags as credential-like. They are allowlisted by exact path in
> `config.SECRET_KEY_ALLOWLIST`. Without that, a config carrying a budget section
> could not load at all.

### Downgrade targets

| Refusal | Downgrade | Job lands in |
|---|---|---|
| `per_pr_tokens`, `per_repo_daily_tokens` | `draft` | `degraded_draft` |
| `max_concurrent_jobs` | `draft` | `degraded_draft` |
| `max_attempts_per_job` | `human` | `human_required` |
| `rest_remaining_floor` (below, or unknown) | `human` | `human_required` |
| `circuit_breaker` open | `human` | `human_required` |

Every refusal path is asserted to have invoked the panel **zero** times; a
downgrade that still spent the money would be no control at all.

### Circuit breaker

Scoped per repo. Consecutive panel failures open it; while open, `reserve()`
refuses pre-spend, so a provider outage stops costing full timeouts. After
`cooldown_seconds` it half-opens: one attempt is permitted, and its outcome
either closes it or re-opens it for another cooldown. A complete panel closes it
and clears the failure count.

State lives in the `circuit_breakers` table; spend lives in `cost_ledger`.

---

## 4. Retention, recovery, backup, health

All local and side-effect-free apart from `retention --apply` and `backup`. Each
takes the state directory's exclusive runtime lock, so none can race a sweep.

```bash
python3 scripts/dispatcher.py --repo-root <repo> status          # job + lease counts
python3 scripts/dispatcher.py --repo-root <repo> health          # db, disks, breakers, budget
python3 scripts/dispatcher.py --repo-root <repo> retention       # DRY RUN — reports only
python3 scripts/dispatcher.py --repo-root <repo> retention --apply
python3 scripts/dispatcher.py --repo-root <repo> retention --days 7 --apply
python3 scripts/dispatcher.py --repo-root <repo> cooldown-reset  # all scopes
python3 scripts/dispatcher.py --repo-root <repo> cooldown-reset --scope claude:opus
python3 scripts/dispatcher.py --repo-root <repo> backup --dest /path/to/backups
python3 scripts/dispatcher.py --repo-root <repo> recover
```

### `retention`

Purges artifact **bytes** for jobs in a terminal state whose `updated_at` is
older than `retention.artifact_days` (default 30).

**Dry-run by default.** `--apply` is required to delete anything: a retention
command that deletes on first invocation is one operators run once by accident.

What survives a purge, always:

- the `jobs` row — identity, head, lane, final status, timestamps
- every `ledger_entries` row — the decision trail
- `mutations`, `approval_decisions`, `human_requests` — what was done, and on
  whose authority
- a `retention_manifest` ledger entry naming, sizing and **SHA-256 hashing**
  every artifact removed

The manifest is written *before* the delete. A crash between the two leaves a
manifest for artifacts that still exist (harmless); the reverse would leave
deleted artifacts with no audit record at all. The hash is what lets a later
reader tell a purged artifact from one that was never written.

### `recover`

Releases leases stranded by a crashed worker and safe-stops the incomplete job,
without replaying any model work.

It also rescues jobs stranded **without** a lease — the mid-panel window, and any
dispatch run with `claim_lease=False`. Those have no lease row, so the original
implementation never saw them and they sat non-terminal forever, waiting on a
process that was gone. `recover` holds the exclusive runtime lock, so nothing is
in flight and stopping them is sound. This is what makes a crash recoverable with
no manual DB surgery.

Only `dispatcher.ACTIVE_WORKER_STATUSES` are rescued. States legitimately waiting
on somebody else — `detected` (queued), `human_approval_pending`,
`human_required`, `degraded_draft`, `held`, `retryable` — are **not** stranded,
and stopping them would silently discard pending human work.

### `backup`

Uses `sqlite3.Connection.backup`, not a file copy, so the result is consistent
even with WAL writes in flight. Copies the snapshot archive alongside it, so a
restored database can still resume jobs pinned to an earlier snapshot.

### `health`

Reports the things that actually stop the harness: database integrity, state and
log directory writability, open circuit breakers, provider cooldowns, the oldest
unfinished job, and the last day's spend against the configured limits.
`status` is `degraded` when the database is not `ok`, the state directory is not
writable, or any breaker is open.

---

## 5. Strategy metadata has no dead fields

`strategies.Strategy` declared ten fields that nothing read. Six are gone
(`parallel`, `min_participants`, `required_inputs`, `degraded_form`,
`assurance_contribution`, `disagreement_handling` — the last one was kept and
given a consumer). Every surviving field has a runtime reader:

| Field | Consumer |
|---|---|
| `name` | selection, attempt log, `fallback.recipe_for` |
| `roles` | `panel._slot_role` — slot role labels, from the strategy rather than re-invented |
| `aggregation` | `modes.mode_for` — execution mode |
| `disagreement_handling` | `panel.run_panel` when counted signals diverge |
| `output_schema` | `panel.run_panel` schema guard — a mismatch is **fail-closed** |
| `budget_tokens` | `budget.reserve` — the pre-spend reservation |
| `timeout_seconds` | `panel.run_panel` — the panel takes `min(operator, strategy)`, so a strategy can only ever *shorten* a run |
| `model_route` | `fallback.recipe_for` — candidate ordering |

`tests/test_strategy_metadata.py` scans `scripts/` for a reader of each declared
field and fails if one has none, so the next dead field fails CI rather than
shipping. It has been confirmed to fail on an injected dead field.

The strategy is selected once, by `strategies.strategy_for_profile`, shared
between the orchestrator (which reserves the budget) and the panel (which
executes it), so the two can never pick different strategies for one job.

---

## 6. Running the tests

The suite has no pytest dependency. Use the tracked runner:

```bash
python3 tests/run_all.py                       # from the skill directory
```

Green output is `PASSED: <n> test(s)`. Never commit over a red suite.
