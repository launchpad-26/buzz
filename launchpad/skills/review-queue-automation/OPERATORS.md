# Operator guide — review-queue-automation

Everything an operator needs to run this skill, read its output, and recover
from a bad run, without reading the implementation.

**Safety posture as shipped:** `approval.mode` is `disabled`, every entry in
`authority` is `disabled`, and both dispatch canaries are `false`. In that state
nothing can mutate a pull request. Each section below says explicitly what can
and cannot write to GitHub.

Contents:

1. [Onboarding](#1-onboarding)
2. [Config reference](#2-config-reference)
3. [Policy and authority](#3-policy-and-authority)
4. [Model routes](#4-model-routes)
5. [Running the pipeline](#5-running-the-pipeline)
6. [The human queue](#6-the-human-queue)
7. [Canaries](#7-canaries)
8. [Historical ingest and shadow calibration](#8-historical-ingest-and-shadow-calibration)
9. [“Why did this PR get this outcome?”](#9-why-did-this-pr-get-this-outcome)
10. [Recovery](#10-recovery)
11. [Retention](#11-retention)
12. [Shutdown](#12-shutdown)
13. [Tests](#13-tests)
14. [Entry-point index](#14-entry-point-index)

Paths below are relative to the skill directory
(`launchpad/skills/review-queue-automation/`). `<repo>` is the repository being
reviewed — the same path you pass to `--repo-root`.

---

## 1. Onboarding

The authoritative config is **repo-local**, git-ignored, and never committed:

```
<repo>/.review-queue-automation/config.json
```

Create it:

```bash
python3 scripts/onboarding.py init <repo> --slug launchpad-26/buzz --login <github-login>
python3 scripts/onboarding.py check <repo>      # re-validate without writing
python3 scripts/onboarding.py update <repo>     # amend an existing config
```

`init` writes the config only after it validates, adds
`.review-queue-automation/` and the log directory to `.gitignore`, and reports
`runtime_ready: false` until you have filled in the model pools. Onboarding
performs no GitHub call, approves no canary, and mutates nothing.

Every other command refuses to run against a missing, unreadable, invalid,
tracked, or un-ignored config. It prints

```json
{"status": "onboarding_required", "reason": "...", "onboarding": "..."}
```

and exits **1**. That is the expected failure, not a crash — if you ever see a
Python traceback here instead, that is a bug worth reporting.

---

## 2. Config reference

| Key | Meaning |
|---|---|
| `version` | Config schema version; integer ≥ 1. |
| `login` | The automation identity's GitHub login. It can never approve its own PR. |
| `state_dir` | SQLite state + job artifacts. **One worker per state directory.** |
| `repository.slug` | `OWNER/REPO`. Default for every command's `--repo`. |
| `repository.root` | Absolute path to the checkout. |
| `repository.base` | Base branch. |
| `repository.preflight` | Optional preflight script path. |
| `logging.directory` | JSONL logs. Must be git-ignored and writable. |
| `logging.format` | Must be `otel-jsonl`. |
| `logging.max_stderr_bytes` | Cap on captured runner stderr. |
| `poll.active_seconds`, `poll.idle_seconds` | Scheduler cadence hints. |
| `poll.rest_remaining_floor` | Minimum REST budget before acting. `0` disables the floor. See §8 — a non-zero floor cannot be reconstructed by the backtest. |
| `models.primary`, `models.secondary` | Ordered reviewer lanes. Each entry needs `runner`, `selector`, `provider_family`, `capability`, and a non-empty `efforts` list. |
| `models.cooldown_seconds`, `models.timeout_seconds` | Per-provider cooldown and per-call timeout. |
| `assurance.sensitive_paths` | Regexes that raise required assurance. |
| `assurance.large_diff_lines` | The `bounded_change` limit. |
| `assurance.full_rereview_ratio` | Churn ratio that forces a full re-review. |
| `dispatch.incoming_concurrency`, `dispatch.author_concurrency_per_repo` | **Must be `1`.** A state directory has exactly one worker. |
| `dispatch.incoming_canary_approved`, `dispatch.author_canary_approved` | Per-lane canary gates. See §7. |
| `authority.*` | Per-activity authority. See §3. |
| `approval.mode` | `disabled` \| `shadow` \| `human_escalation` \| `live`. |
| `approval.live_canary_approved` | Required before `mode: live` validates at all. |
| `approval.effective_risk_max` | Risk ceiling for auto-approval. |
| `approval.complexity_max`, `approval.file_limit`, `approval.line_limit` | Eligibility limits. |
| `approval.approval_rate_max` | Number in `[0,1]`. |
| `approval.daily_limit` | Optional cap on approvals per day. |
| `approval.decision_ttl_minutes` | Lifetime of an eligible decision record (default 720). |
| `risk.bands` | `low` / `medium` / `high` cutoffs. |
| `risk.protected_triggers` | Regexes that permanently suppress auto-approval. Required when `mode` is `live`. |
| `human_queue.expiry_minutes` | How long a pending human request stays actionable. |
| `shadow.history_window_months`, `shadow.evaluated_sha_only` | Historical ingest bounds. |
| `github.api_version`, `github.timeout_seconds`, `github.read_only` | REST transport. |
| `notifications` | Optional. `transport` is `none` \| `file` \| `command`. Absent means no delivery; **malformed is an error**, so a typo can never silently disable your only alert path. |

No secret may appear anywhere in this file. Keys that look like credentials
(`token`, `api_key`, `password`, `secret`, `private_key`, …) are rejected at
load. Authentication lives in the environment or keychain.

---

## 3. Policy and authority

Two independent switches guard approval, and they are **conjunctive** — turning
off either one disables auto-approval:

* `approval.mode` — the approval-specific mode; and
* `authority.approve` — the per-activity switch.

Per-activity modes (`review`, `comment`, `approve`, `request_changes`, `triage`,
`fix`), each one of:

| Mode | Behaviour |
|---|---|
| `disabled` | Never acts. The default. |
| `shadow` | Runs the full decision, performs no mutation. |
| `human_escalation` | Files a durable request in the human queue. |
| `live` | Acts, and only when its gate passes for the exact revalidated HEAD. |

Approval and request-changes are separate. Requesting changes needs a verified
blocking defect tied to the current HEAD and its own `live` authority.

The approval gate set is defined once, in `scripts/approval_evaluate.py`, and is
the same set used by the live path, the human-queue path, and the shadow
backtest. Five of those gates cannot be derived from PR facts and require
explicit evidence — `bounded_change`, `audit_writable`, `assurance_met`,
`revalidation_ok`, `rate_limit_ok`. They fail closed. §8 explains what the
backtest can and cannot prove about them.

---

## 4. Model routes

`models.primary` and `models.secondary` are ordered fallback lanes. A route's
identity is provider + exact model/version + effort + execution mode + tools +
prompt version + policy version. Change any of those and new jobs route to
shadow until the route is re-qualified; in-flight jobs keep their original pin.

Check that the configured routes actually answer, before spending a review on
them:

```bash
python3 scripts/route_probe.py --repo-root <repo> --json
python3 scripts/route_probe.py --runner claude --selector sonnet --effort medium
```

A probe **does** spend a small number of model tokens. It touches no PR. A fully
passing probe set qualifies the current route material; any failure leaves the
routes unqualified and per-provider cooldowns recorded in state.

---

## 5. Running the pipeline

One command owns the whole lifecycle. Do **not** hand-chain queue, lease,
evidence, and panel steps — that bypasses the state-directory ownership
boundary.

```bash
python3 scripts/dispatcher.py --repo-root <repo> sweep --lane incoming_review --limit 2
python3 scripts/dispatcher.py --repo-root <repo> dispatch-one --number <pr> --job <job-id> --lane incoming_review
python3 scripts/dispatcher.py --repo-root <repo> status
python3 scripts/dispatcher.py --repo-root <repo> recover
```

`--limit` is the batch size, not parallelism. A second concurrent command
against the same state directory returns `sweep_already_running` and spends
nothing. `status` is local-only: no network. It reports the state directory, the job
count per status, the number of outstanding leases, and `worker_concurrency: 1`.
It does **not** report whether a worker is currently running — outstanding
leases with no live worker is the signal to run `recover` (§10).

Each job writes an immutable artifact directory under
`<state_dir>/jobs/<job-id>/` containing the evidence bundle and the panel
outputs `review-A.txt` and `review-B.txt`. Read those before trusting a
`degraded` or `human_required` result.

**Escalation.** On `human_required` — a blocker, a policy question, an
unresolved panel, an unknown thread state, or an unsupported mutation — the
evidence is written to the job directory and the run stops. Do not improvise a
GitHub operation to get past it.

### 5.1 Running it on a timer

`sweep` discovers work only when you run it. `tick` is the same sweep with a
schedule attached, and it is what a timer should call:

```bash
python3 scripts/dispatcher.py --repo-root <repo> tick --lane incoming_review --limit 2
python3 scripts/dispatcher.py --repo-root <repo> tick --dry-run   # decision only
python3 scripts/dispatcher.py --repo-root <repo> tick --force     # ignore the schedule
```

`tick` reads its own schedule from the `cadence` table and reports `not_due`
without touching the network on most firings. When it is due it sweeps, then
picks the next interval from `poll`:

| Situation | Next interval | `reason` |
|---|---|---|
| REST budget below `poll.rest_remaining_floor`, or unreadable | longest `poll.idle_seconds` | `rate_limit_floor` |
| Work pending | `poll.active_seconds` | `work_pending` |
| Nothing pending | one step further along `poll.idle_seconds` | `idle_backoff` |

A rate-limited sweep does **not** reset the idle streak: it learned nothing
about whether work is waiting. An unreadable REST budget counts as below the
floor, because the alternative is sweeping on the assumption that budget you
could not read is budget you have.

Cadence is stored per `<repo>:<lane>` scope, so two repositories — or the two
lanes of one repository — back off independently.

**The timer.** `scripts/scheduled-tick.sh <repo-root> [<repo-root> ...]` ticks
each repository in turn and exits with the worst status. It holds no
repository-specific knowledge; add a repository by onboarding it and passing its
root. `RQA_LANES` (default `incoming_review`) and `RQA_LIMIT` (default 2) tune
it. On macOS, copy `scripts/launchd.plist.example`, replace every
`<REPLACE:...>`, and load it with `launchctl`.

Set `StartInterval` to the **shortest** interval the cadence can choose
(`poll.active_seconds`), not to how often you want a sweep — launchd cannot vary
an interval, so backoff lives in the `cadence` table and most firings do
nothing. A longer `StartInterval` silently caps how quickly work is picked up.

A timer job rather than a sleeping daemon: the runtime lock is held only while
work happens, so the one-worker-per-state-directory invariant holds, and a
crash, reboot or closed lid costs one interval instead of ending the automation
silently.

**This spends money when it dispatches.** Configure `budget` before loading a
timer, keep `authority.*` at `disabled` until each canary is approved (§7), and
note that `RunAtLoad` is `false` in the template on purpose — loading an agent
should not immediately spend tokens.

---

## 6. The human queue

Durable, file-backed, no interactive stdin:

```bash
python3 scripts/human_cli.py --repo-root <repo> list
python3 scripts/human_cli.py --repo-root <repo> show <request_id>
python3 scripts/human_cli.py --repo-root <repo> decide <request_id> approve --actor <you> [--reason "..."]
python3 scripts/human_cli.py --repo-root <repo> resume <request_id> [--head <sha>] [--no-execute]
python3 scripts/human_cli.py --repo-root <repo> supersede <repo> <pr> <head_sha>
```

`decide` accepts `approve`, `decline`, or `request_changes`. Approving does not
post anything: it records a human-authorized decision that then runs through the
same guarded executor as the automatic path, including the mandatory live REST
revalidation immediately before the mutation and REST verification after.

`resume` drives that execution. `--no-execute` revalidates and transitions
without posting — use it to check a decision is still valid. `--head` overrides
the head used for stale-SHA revalidation, and `--allow-recorded-head` accepts
the recorded head when the live head cannot be read: that is **unsafe if the PR
has advanced**, so prefer re-running when GitHub is reachable.

Expired, stale-SHA, and stale-policy decisions cannot approve. A new HEAD
supersedes incompatible pending decisions; `supersede` does that explicitly.

---

## 7. Canaries

Three independent gates, all closed by default:

| Gate | Unblocks | Where it is read |
|---|---|---|
| incoming-review canary | The incoming-review lane. | The `canaries` table row for `incoming_review`, if present; otherwise `dispatch.incoming_canary_approved`. |
| author-triage canary | The author-triage lane. | The `canaries` table row for `author_triage`, if present; otherwise `dispatch.author_canary_approved`. |
| live-approval canary | `approval.mode: live` — the config will not validate as `live` without it. | `approval.live_canary_approved`. |

For the two lane canaries the **SQLite `canaries` table is authoritative** and
the config key is only the fallback used when no row exists. No command writes
that table today, so in practice the config keys are what you set — but if a lane
stays gated after you flip its config key, check the table:

```bash
sqlite3 <state_dir>/state.sqlite3 'SELECT lane, status FROM canaries;'
```

A canary run spends model tokens and, outside shadow mode, writes to a real PR.
Approve one deliberately, on a named PR, with the outcome recorded — not as a
step in enabling something else.

---

## 8. Historical ingest and shadow calibration

Two steps. **`history.py` produces the samples file; `shadow.py` consumes it.**
Nothing else produces it — a `--samples` file does not materialise on its own.

### 8.1 Ingest (`scripts/history.py`)

Read-only: allowlisted REST reads, no mutation, no lease, no model calls.

```bash
python3 scripts/history.py --repo-root <repo> --limit 100 \
    --with-files --with-checks --out samples.json
```

| Flag | Effect |
|---|---|
| `--repo` | `OWNER/REPO`; defaults to the configured slug. |
| `--limit` | How many closed PRs to ingest (default 50). |
| `--with-files` | One extra REST call per PR. **Without it there is no protected-trigger or file-limit evidence for any sample.** |
| `--with-checks` | One extra REST call per PR. **Without it no check evidence is ingested, `checks_complete_ok` fails closed for every sample, and the backtest can only ever report a 0% would-approve rate.** |
| `--out` | Write the entries array here (this is the `--samples` file). Without it the full report goes to stdout. |

Outcome labels are **independent of the evaluator**:

| Label | Assigned when |
|---|---|
| `contested` | A human requested changes before merge. |
| `adverse` | A later revert PR names this number, or it closed unmerged after human review. |
| `clean` | Merged with human review activity and no changes ever requested. |
| `unknown` | Merged with no human review signal — it proves nothing. |

A PR nobody reviewed is `unknown`, never `clean`. Absence of objection is not
approval, and counting it as one would inflate the measured accuracy.

### 8.2 Backtest (`scripts/shadow.py`)

```bash
python3 scripts/shadow.py --repo-root <repo> --samples samples.json \
    --verdicts v.json --assessments a.json --train-ratio 0.7 --out report.json
```

`--verdicts` maps PR number to the reviewer verdict list; `--assessments` maps
PR number to that PR's assessment. Both are JSON objects; **string keys are
fine** — they are coerced to integers at load, and a key that is not an integer
is rejected rather than silently dropped.

`--assessments` carries three things per PR:

```jsonc
{"104": {
  "assurance_met": true,                 // required, see below
  "failure_modes": [ ... ],              // FMEA-C inputs -> deterministic risk floor
  "model_observed_effective": 0          // a model may RAISE risk, never lower it
}}
```

Current-head shadow, for one open PR:

```bash
python3 scripts/shadow.py --repo-root <repo> --mode current \
    --pr-facts facts.json --verdicts v.json --assessments a.json
```

It prints `WOULD_AUTO_APPROVE` or `FAILED_GATES [...]`. Both modes force
`approval.mode = shadow` **in memory only**: no config is edited, no decision
record is persisted, no GitHub call is made, and live mode is never enabled.
Config suggestions in the report are advisory text; nothing applies them.

### 8.3 What the backtest can and cannot prove

The backtest grades against the **same gate set as the live path**. For the five
gates that need explicit evidence it proves what the historical record supports
and fails closed on the rest:

| Gate | How the backtest establishes it |
|---|---|
| `bounded_change` | The recorded addition count against `assurance.large_diff_lines`. A sample with no recorded additions fails closed rather than reading as "small". |
| `audit_writable` | A real write probe of the run's state directory. |
| `assurance_met` | **Not reconstructible from GitHub.** The assurance ladder is computed by the panel, not recorded on the PR. Supply it per sample in `--assessments`; absent, it fails closed. |
| `revalidation_ok` | A closed PR's head is frozen, so `head_frozen_at` at-or-before the cutoff (set by `history.py`) stands in for the live pre-mutation REST read. Absent — an open PR in `--mode current` — it fails closed. |
| `rate_limit_ok` | The daily approval cap is replayed as a counterfactual over the run. The **REST remaining floor cannot be reconstructed at all**, so a configured `poll.rest_remaining_floor > 0` fails closed for every sample. |

Practical consequence: a first backtest straight off `history.py`, with no
`--assessments` file and a non-zero REST floor, reports **0% would-approve and
100% escalation**. That is an absence of evidence, not a safety result. The
report says so — `universally_failed_gates` names the gate that blocked every
sample, and a matching `WARNING` appears in the summary.

### 8.4 Reading the report

| Field | Meaning |
|---|---|
| `sample_count` / `train_count` / `calibrate_count` | Whole input set, the fitted half, the evaluated half. |
| `total` | The **evaluated** (calibration) count — this is what the rate fields divide by. |
| `samples_with_verdicts`, `verdict_coverage`, `decision_capable` | Reviewer coverage. `decision_capable: false` means the run cannot support an autonomy decision. |
| `verdict_numbers_supplied` | Every PR number in the `--verdicts` file. Compare against your samples if coverage looks wrong. |
| `approval_candidate_count` | Would-approve count on the evaluated half. |
| `false_auto_approval_candidates` | Would-approve **and** independently `adverse` or `contested`. The number the whole exercise exists to produce. |
| `escalation_rate`, `coverage`, `unknown_rate` | Rates over the evaluated half. |
| `blocking_gate_counts` | Per-gate failure counts. Read this before concluding anything from the escalation rate. |
| `universally_failed_gates` | Gates that failed for *every* sample — an environment or evidence problem, not a PR-quality result. |
| `learned_threshold` | The risk ceiling fitted on the train half, plus `held_out` and `configured` scores on the calibration half. The fit only ever **lowers** the configured ceiling. |
| `threshold_sensitivity` | The full approval/false-auto tradeoff sweep. |
| `policy_hash`, `pinned_heads` | Exactly which policy and which commits produced this report. |
| `warnings`, `suggestions` | Warnings are about the run's validity; suggestions are advisory calibration text only. |

A threshold change is only reviewable with this report attached: a diff to
`approval.effective_risk_max` on its own does not show what it would have done.

---

## 9. “Why did this PR get this outcome?”

`scripts/explain.py` reconstructs a decision from the local ledger. It is
read-only: it never contacts GitHub, never invokes a model, and never changes a
job.

```bash
python3 scripts/explain.py --repo-root <repo> pr <number>
python3 scripts/explain.py --repo-root <repo> pr <number> --all-revisions
python3 scripts/explain.py --repo-root <repo> pr <number> --json
python3 scripts/explain.py --repo-root <repo> job <job-id>
```

Procedure:

1. `explain.py pr <number>` — the latest reviewed revision. It prints the
   pinned head, the snapshot hash and policy version, the strategies and routes
   that ran, the assurance required/achieved, verified vs unverified findings,
   the decision disposition with its failed gates, the final action and whether
   GitHub confirmed it, and any human-queue events.
2. `"error": "no ledger entries for ..."` and exit 1 means this automation never
   reviewed that PR. Whatever happened on it came from somewhere else.
3. If the outcome was an escalation, read `failed_gates`. Each name maps to a
   row in §3/§8.3.
4. If the outcome was `degraded` or `human_required`, open
   `<state_dir>/jobs/<job-id>/` and read `review-A.txt` and `review-B.txt` —
   the explanation says which participants counted, but not what they said.
5. `--all-revisions` when the PR was reviewed more than once: a later HEAD
   supersedes an earlier decision, and the earlier one is often the interesting
   record.
6. `--json` to attach the reconstruction to an issue or a report.

Exit code 1 also means "this job has no complete explanation", not only "not
found" — check the `explained` field before treating the output as final.

---

## 10. Recovery

After a worker is killed, times out, or the machine restarts:

```bash
python3 scripts/dispatcher.py --repo-root <repo> status    # local, no network
python3 scripts/dispatcher.py --repo-root <repo> recover
```

`recover` is an explicit operator action. It releases only leases recorded by
*this* state directory, REST-verifies each release, and safe-stops an incomplete
job. It never re-runs an unknown partial decision — if a mutation may have
landed, the job goes to `safe_stop` and stays there for a human.

If two workers ever shared one state directory, stop both, then run `recover`
once. Do not raise `dispatch.incoming_concurrency` above `1` to work around a
stuck lease; parallel workers need separate state directories.

---

## 11. Retention

What exists today:

* **Job artifacts** — immutable directories under `<state_dir>/jobs/<job-id>/`.
  Safe to archive or delete once the corresponding ledger entry is no longer
  needed; deleting them does not corrupt the state database, but it does make
  `explain.py` step 4 impossible for that job.
* **State database** — `<state_dir>/state.sqlite3`. Use `backup` below rather
  than copying the file by hand.
* **Logs** — JSONL under `logging.directory`, rotated by nothing. Prune them
  yourself.

Four maintenance commands exist. This section previously said none did — it
claimed *"no automated retention, cleanup, cooldown-reset, or backup command
yet (backlog item T27)"* after they had landed, which is worse than saying
nothing:

```bash
python3 scripts/dispatcher.py --repo-root <repo> retention          # dry run
python3 scripts/dispatcher.py --repo-root <repo> retention --apply  # actually delete
python3 scripts/dispatcher.py --repo-root <repo> retention --days 7 # override the window
python3 scripts/dispatcher.py --repo-root <repo> health
python3 scripts/dispatcher.py --repo-root <repo> backup [--dest <dir>]
python3 scripts/dispatcher.py --repo-root <repo> cooldown-reset [--scope <key>]
```

* `retention` purges artifacts for **terminal** jobs past `retention.artifact_days`
  (30 by default). A job that could still be resumed keeps its artifacts. It is a
  dry run unless `--apply`, and it writes a `retention_manifest` ledger entry
  naming and hashing everything it removed — **the audit trail is never purged**,
  only the artifacts it points at.
* `health` is local-only: database, disks, breakers, budget. It does not report
  whether a worker is live.
* `backup` takes a consistent copy of `state.sqlite3` plus the snapshot store.
* `cooldown-reset` clears provider cooldowns and circuit breakers, all scopes
  unless `--scope` names one.

All four are local and side-effect-free with respect to GitHub: none of them
reads or writes a pull request.

---

## 12. Shutdown

1. Stop the scheduler so no new `sweep` starts.
2. Wait for the current command to exit. There is no command that reports the
   runtime lock; a second dispatcher command against the same state directory
   returning `sweep_already_running` is the reliable signal that one is still
   held. Do not `kill -9` a worker mid-mutation.
3. If a worker was killed anyway, run `recover` (§10) before starting again.
4. To halt all activity without stopping the scheduler, set every `authority.*`
   entry and `approval.mode` to `disabled`. The next command picks that up; it
   does not require a restart.
5. To halt *everything* including reads, remove or invalidate the repo-local
   config. Every entry point then exits `onboarding_required` without touching
   GitHub.

---

## 13. Tests

The suite has no pytest dependency and is not covered by `just ci`. Run it
directly:

```bash
python3 launchpad/skills/review-queue-automation/tests/run_all.py \
        launchpad/skills/review-queue-automation
```

It imports every `tests/test_*.py`, runs each zero-argument `test_*` function,
prints `PASSED: N test(s)`, and exits non-zero on any failure. A test function
that requires a fixture argument is a hard error — this suite is deliberately
fixture-free.

No test contacts GitHub, spends model tokens, or writes outside a temporary
directory.

---

## 14. Entry-point index

Operator commands, documented above:

| Script | Section |
|---|---|
| `scripts/onboarding.py` | §1 |
| `scripts/route_probe.py` | §4 |
| `scripts/dispatcher.py` | §5, §10 |
| `scripts/human_cli.py` | §6 |
| `scripts/history.py` | §8.1 |
| `scripts/shadow.py` | §8.2 |
| `scripts/explain.py` | §9 |

**Internal modules that are also executable.** Each of these has a `__main__`
block used for debugging and by the harness's own tests. They are **not**
operator commands: running them by hand takes the step outside the
state-directory ownership boundary that `dispatcher.py` enforces, and
`approval_action.py` and `github_mutate.py` can write to GitHub.

| Script | What it is |
|---|---|
| `scripts/queue.py` | Queue reconciliation for one repo. |
| `scripts/scheduled-tick.sh` | The trigger a timer calls: one `tick` per repo per lane. Holds no repo-specific knowledge. |
| `scripts/launchd.plist.example` | macOS timer template. Copy, replace every `<REPLACE:...>`, `launchctl load`. |
| `scripts/cadence.py` | The sweep-interval decision and its persisted schedule. Not run by hand. |
| `scripts/lease.py` | Lease claim / release / verify. |
| `scripts/evidence.py` | Evidence-bundle assembly for one PR. |
| `scripts/panel.py` | The reviewer panel for one PR. Spends model tokens. |
| `scripts/worktree.py` | Isolated worktree create / commit / push / clean. |
| `scripts/github_rest.py` | The allowlisted per-PR read transport (REST GET). |
| `scripts/github_query.py` | The allowlisted bulk read transport: one read-only GraphQL inventory query per page of open PRs. Read `queue_inventory` by hand to see exactly what the reconciler sees. |
| `scripts/github_mutate.py` | The single allowlisted mutation transport. **Writes to GitHub.** |
| `scripts/approval_action.py` | The guarded APPROVE executor. **Writes to GitHub**, and only with a matching eligible decision record. |

If a runtime-operations reference (`references/runtime-ops.md`) is present in
your checkout, read it alongside §5 and §10 for logging, metrics, and dispatch
observability.

---

See also: [SKILL.md](SKILL.md) · [references/contracts.md](references/contracts.md)
· [references/classification.md](references/classification.md)
· [references/model-fallbacks.md](references/model-fallbacks.md)
