---
name: review-queue-automation
description: Automate PR review and author-triage across launchpad-26/buzz and
  launchpad-26/buzz-infrastructure. Deterministic scripts own every GitHub read
  (REST only) and mutation (optimized GraphQL only), model selection with
  fallback pools, lease idempotency, and assurance escalation. Use when PRs need
  reviewing, your PRs carry change requests, or a review queue must be polled.
---

# Review queue automation

Deterministic scripts perform every GitHub interaction, model dispatch, lease, and
state transition. The judgment work — issue contract interpretation, correctness,
severity, adversarial triage, and rebuttal prose — is the only AI work here.

Read in this order before acting:

1. `references/contracts.md` — job states, transport rules, assurance ladder,
   severity and authority, canary gate.
2. `references/classification.md` — deterministic / judgment split.
3. `references/model-fallbacks.md` — default reviewer lanes and the current
   cost-to-quality rationale for their OpenRouter fallbacks.

## Authorization and refusal

- You post advisory PR comments and file `by:agent` finding issues. Auto-approval
  happens only through the deterministic guarded path (`approval.mode = live`), never
  as an act of agent judgment: the agent itself never approves, requests changes,
  merges, arms auto-merge, dismisses a review, bypasses protection, force-pushes, or
  requests a thread.
- The operator approved both canaries (`canaries` table) before continuous
  dispatch. Until then, only the requested canary job may run end to end.
- You never call GitHub directly. Every read goes through `scripts/github_rest.py`;
  every mutation through `scripts/github_mutate.py`. Unknown operations become a
  held job, never a hand-built `gh`, REST, GraphQL, curl, MCP, or browser call.

## Run the pipeline

The managed harness owns the whole incoming-review lifecycle. A scheduler invokes
one command; it reconciles queue facts, selects FIFO jobs, claims/releases each
lease, and runs the guarded lifecycle. Do **not** manually chain queue, lease,
evidence, and panel commands: that bypasses the state-dir ownership boundary.

```bash
python3 scripts/dispatcher.py --repo-root <repo> sweep \
  --lane incoming_review --limit 2
```

`limit` is the number of FIFO jobs in this batch, not parallelism. A state
directory permits exactly one worker; a concurrent `sweep` or `dispatch-one`
returns `sweep_already_running` without spending model tokens. The scheduler may
invoke the command again after the current run exits.

Useful noninteractive commands:

```bash
python3 scripts/dispatcher.py --repo-root <repo> status
python3 scripts/dispatcher.py --repo-root <repo> dispatch-one \
  --number <pr> --job <job-id> --lane incoming_review
python3 scripts/dispatcher.py --repo-root <repo> recover
```

`recover` is an explicit operator action after a terminated worker. It releases
only leases recorded by this state directory, REST-verifies each release, and
safe-stops an incomplete job; it never reruns an unknown partial decision.

Each job's immutable artifact directory contains the evidence bundle and the
panel outputs `review-A.txt` and `review-B.txt`; inspect those before judging a
degraded or human-required result.

### Author-triage lane (your PRs)

Follow contracts' `author_triage` path: hold when thread resolution is unknown,
evaluate each finding adversarially, fix valid findings in an isolated worktree,
run scoped verification, commit/push/reply/re-request, rebut invalid findings, and
escalate after 24h or a reassert. Same policy: never approve/merge/bypass/force-push/
resolve a thread.

## Escalation

On `human_required` (blocker, policy question, unresolved panel, unknown thread
state, or unsupported mutation), write the evidence to the job dir and surface a
one-line report naming the holding reason and the exact input. Do not improvise a
GitHub operation.

## Must

- The authoritative config is **repo-local**:
  `<repo>/.review-queue-automation/config.json`, created by
  `scripts/onboarding.py init` (see "Approval modes & authority" below and
  [OPERATORS.md](OPERATORS.md) §1). `config.example.json` is the tracked
  template; it is never itself a populated config.
- Job state and leases are SQLite under `$STATE dir`. A non-blocking OS lock
  serializes every dispatcher command per state directory; progress artifacts are
  immutable files under `jobs/<job-id>/`.
- Panel provider config and cooldowns live in `config, models`; never hardcode a
  model in this file or any prompt. `primary` and `secondary` are ordered
  fallback lanes: keep native Claude then Codex as the preferred pair, followed
  by distinct-provider OpenRouter coding/reasoning options selected for
  cost-to-quality value.

The rest of the engineering policy is in `references/contracts.md`; the script/AI
split is in `references/classification.md`. Full operator procedures —
onboarding, config fields, routes, canaries, human queue, recovery, retention,
shutdown — are in [OPERATORS.md](OPERATORS.md).

## Why did this PR get this outcome?

```bash
python3 scripts/explain.py --repo-root <path> pr <number>
python3 scripts/explain.py --repo-root <path> pr <number> --all-revisions --json
python3 scripts/explain.py --repo-root <path> job <job-id>
```

Read-only reconstruction from the local ledger: no GitHub call, no model call, no
change to the job. See [OPERATORS.md](OPERATORS.md) for the full triage
procedure.

## Tests

The suite has no pytest dependency and is not covered by `just ci`:

```bash
python3 launchpad/skills/review-queue-automation/tests/run_all.py \
        launchpad/skills/review-queue-automation
```

## Approval modes & authority

The authoritative config is the repo-local file at
`<repo>/.review-queue-automation/config.json`, git-ignored, created by
`scripts/onboarding.py`. Defaults are **fail-closed**: `approval.mode` is
`disabled` unless changed, so no automated approval is possible by omission.

`approval.mode` values:

- `disabled` — advisory comments only; no approval decision is ever recorded.
- `shadow` — run the full evaluation, emit `WOULD_AUTO_APPROVE` or the failed
  gates, and perform **no** approval mutation.
- `human_escalation` — durable human request in the SQLite queue; a human decides
  via the deterministic CLI.
- `live` — one `APPROVE` review is posted only when EVERY gate in
  `scripts/approval_evaluate.py` passes, a persisted eligible decision record is
  present, and final live revalidation reconfirms SHA/draft/checks/protected
  triggers/rate limits.

Automated approval never merges, arms auto-merge, bypasses protection, dismisses
reviews, resolves another reviewer's thread, force-pushes, or approves the
automation identity's own PR. The advisory mutation is fixed to `COMMENT`; the
approval mutation is fixed to `APPROVE` and cannot run without a matching
eligible decision record.

## Human approval CLI (no interactive stdin)

```bash
python3 scripts/human_cli.py --repo-root <path> list                 # pending requests
python3 scripts/human_cli.py --repo-root <path> show <request_id>
python3 scripts/human_cli.py --repo-root <path> decide <request_id> approve --actor <you> [--reason ...]
python3 scripts/human_cli.py --repo-root <path> supersede <repo> <pr> <head_sha>
```

An approved request resumes through final revalidation, never directly at
mutation. Expired, stale-SHA, or stale-policy decisions cannot approve.

## Shadow backtest (read-only calibration)

Pure read-only, plus a deterministic time-based train/calibration split. Every
historical sample must carry a independently sourced outcome
(`clean|adverse|contested|unknown`), an evidence source, and a cutoff timestamp.
Only evidence timestamped at or before the cutoff is reconstructed — no future
data. Each sample's head and the current policy hash are pinned in the report.
Labels are never derived from the evaluator or from the fact the PR merged; a
merged PR without an independent outcome is `unknown`. The report includes
machine-readable rates (coverage, escalation, unknown), per-gate blocking counts,
a threshold fitted on the train half and scored on the held-out half, and a real
threshold-sensitivity sweep.

**No gate is hardcoded true, and none is defaulted open.** The backtest grades
against the *same* gate set as the live path: it builds an explicit
`ApprovalEvidence` from what the historical record can prove and fails closed on
the rest. `checks_ok` / `adjudication_complete` / `evidence_fresh` come from
timestamps at-or-before the cutoff. Of the five external-evidence gates,
`bounded_change` comes from the recorded diff size, `audit_writable` from a real
write probe, `revalidation_ok` from the frozen head of a closed PR,
`rate_limit_ok` from a replayed daily cap (a configured
`poll.rest_remaining_floor` is *not* reconstructible and fails closed), and
`assurance_met` must be supplied per sample in `--assessments`. A first run
straight off `history.py` therefore reports 0% would-approve; that is an absence
of evidence, and the report names the blocking gate rather than letting it read
as a safety result.

`scripts/history.py` is the **only** producer of the `--samples` file — ingest
first, then backtest:

```bash
python3 scripts/history.py --repo-root <path> --limit 100 \
    --with-files --with-checks --out history.json

python3 scripts/shadow.py --repo-root <path> --samples history.json \
    --verdicts v.json --assessments a.json --out report.json
```

Without `--with-checks` no check evidence is ingested and `checks_complete_ok`
stays fail-closed for every sample. `--verdicts` and `--assessments` are JSON
objects keyed by PR number; string keys are accepted and coerced, and a
non-integer key is rejected rather than dropped.

Current-head shadow (no mutation, no decision record):

```bash
python3 scripts/shadow.py --repo-root <path> --mode current \
    --pr-facts facts.json --verdicts v.json --assessments a.json
```

Prints `WOULD_AUTO_APPROVE` or the failed gates. The backtest and current mode
force `approval.mode = shadow` in memory only. The backtest never edits config and never enables live mode; any config suggestions are advisory text only.

## Configurable authority (per repo, per activity)

Each action has its own authority mode, resolved per repository and per activity,
so commenting is not the same as approving. Modes: `disabled` (default; never
acts), `shadow` (full decision, no mutation), `human_escalation` (async human
queue), `live` (acts when its gate passes for the exact revalidated HEAD).

```jsonc
"authority": {
  "review": "live",
  "comment": "live",
  "approve": "disabled",        // guarded live path only
  "request_changes": "disabled",// separate verified-blocker gate
  "triage": "human_escalation",
  "fix": "disabled"
}
```

Approval and request-changes are independent. Requesting changes requires a
**verified blocking defect** tied to the current HEAD, sufficient evidence, and
its own `live` authority; suggestions and uncertain findings stay comments or
human recommendations. Final revalidation is always injected (fresh GitHub
state), never hardcoded to success. The only GitHub review mutations are fixed
internally: `add_comment_review` (COMMENT), `approve_review` (APPROVE),
`request_changes_review` (CHANGES_REQUESTED); a caller can supply no event.

## Policy-as-data

Policy (authority, risk bands, approval thresholds, reviewer requirements,
routes) is carried as data in `scripts/policy.py`. It is schema- and
semantically validated, versioned, and content-hashed; reload is atomic and
retains last-known-good on failure. In-flight decisions are pinned to the exact
policy version + hash that produced them and are not silently altered by a later
reload. Malformed policy never widens authority.

## Reasoning strategies & model routing

`scripts/strategies.py` provides 12 named reasoning strategies (direct analysis,
decomposition, checklist, hypothesis testing, adversarial, debate, independent
parallel, specialist panel, sequential refinement, critique & revision,
evidence synthesis, uncertainty calibration). Selection is deterministic from
review signals and records the reason. Failed/timed-out/invalid participants
never count as agreement.

`scripts/routing.py` resolves the requested model through the subscription-first
ladder — configured Claude subscription → Codex subscription → provider-diverse
OpenRouter → economic fallback → human escalation / read-only failure — and
records the requested alias, resolved canonical model, provider, and fallback
position for every step. A fallback-loop guard prevents reselecting an
unavailable provider, and per-provider cooldowns are held in state.

## Assurance, evidence, uncertainty

`scripts/risk.py` computes required assurance (from the maximum applicable RPN,
never an average), achieved assurance (evidence completeness × reviewer
completion, reduced by missing/fresh-failure and uncertainty), evidence
completeness, and residual uncertainty. Missing evidence lowers achieved
assurance. `scripts/action_gate.py` turns these into deterministic `approve` and
`request_changes` gates that separate recommendation from attempted action from
confirmed action.

## Human decisions & execution states

Human requests carry a stable decision ID, exact HEAD, review-cycle id, policy
version + hash, strategy/model provenance, and idempotency key. Decisions
support pending / approved / rejected / expired / superseded / cancelled and
execution states (execution_pending / executed / execution_failed). An action is
only marked `executed` after GitHub confirms it; a new HEAD supersedes
incompatible pending decisions. Multiple requests may pend without blocking
unrelated reviews.

## Lifecycle

`scripts/states.py` models the explicit lifecycle: detected, ready-for-review,
evidence, assurance, adjudication, approval-evaluation, changes-requested /
requested-changes-fixed, author-triage, human-decision, closed, merged, plus the
degradation/safe-stop sinks. Invalid and unknown transitions never become
approval candidates.
