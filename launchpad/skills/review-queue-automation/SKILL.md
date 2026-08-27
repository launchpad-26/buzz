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

Each phase is a script that reads its artifacts and ends on a checkable condition.
Only perform the named judgment between phases.

### Incoming review lane (someone else's PR)

1. Reconcile the queue:

   ```bash
   python3 scripts/queue.py --config $CONFIG $REPO
   ```

   Transitions are JSON jobs keyed by `repo + PR + head_sha + lane`. Read them. A held
   or `pr_review_batch.py`-blocked PR is reported, not dispatched.

2. Run the deterministic preflight when the repo configures one:

   ```bash
   python3 <repo>/launchpad/scripts/pr_review_batch.py --repo $REPO --pr $PR
       --self tucktuck101 --session-since $SESSION_SINCE --json
   ```

   If `blocks_review` is true or `DO NOT DISPATCH` is set, hold the job and spend no
   reviewer tokens on it.

3. Claim the PR:

   ```bash
   python3 scripts/lease.py --config $config claim $REPO $PR --job $JOB
   python3 scripts/lease.py --config $config verify $REPO $PR
   ```

   Claim first, release on every exit path. Release is not optional.

4. Gather evidence once:

   ```bash
   python3 scripts/evidence.py --config $config $REPO $PR --lane incoming_review --job $JOB
   ```

   This writes `evidence.json`, `evidence.txt` (the nonce-enveloped bundle), and
   `context.json` into `$STATE/jobs/$JOB/`. Reviewers read only `evidence.txt`.

5. Run the panel with the assurance router:

   ```bash
   python3 scripts/panel.py --config $config $REPO $PR --lane incoming_review --job $JOB
   ```

   This chooses the minimum capability/effort/independence, applies the fallback
   pools and cooldowns, and leaves `review-A.txt`, `review-B.txt`. Panel result as
   its `completed_reviewers` count tells you whether it is full, degraded, or a
   draft.

6. Adjudicate (judgment). Two independent verdicts; verify each blocker against its
   primary source; drop unsupported findings; deduplicate.

7. Post only an advisory comment with GraphQL mutation `add_comment_review` (event COMMENT), with
   `body` pulled from a file path and all PR content nonce-enveloped. Create
   deduplicated `by:agent` issues only for confirmed High/Medium/Low findings, each
   once per fingerprint.

8. Release the lease (mandatory), verify it is off, mark the job `completed`.

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

- `$CONFIG` defaults to `~/.config/review-queue-automation/config.json`. Copy
  `config.example.json` there and fill paths, login, model pools.
- Job state and leases are SQLite under `$STATE dir`. Only one process writes a job
  at a time; use the JSON state file under `jobs/` for progress notes.
- Records every phase in the job dir: which script, when, exit status, output path.
- Re-reviews are single model when mechanically narrow, otherwise a full panel.
- Panel provider config and cooldowns live in `config, models`; never hardcode a
  model in this file or any prompt. `primary` and `secondary` are ordered
  fallback lanes: keep native Claude then Codex as the preferred pair, followed
  by distinct-provider OpenRouter coding/reasoning options selected for
  cost-to-quality value.

The rest of the engineering policy is in `references/contracts.md`; the script/AI
split is in `references/classification.md`.

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
data, and checks/adjudication/evidence are never hardcoded true. Each sample's
head and the current policy hash are pinned in the report. Labels are never
derived from the evaluator or from the fact the PR merged; a merged PR without an
independent outcome is `unknown`. The report includes machine-readable rates
(coverage, escalation, unknown) and a real threshold-sensitivity sweep.

```bash
python3 scripts/shadow.py --repo-root <path> --samples history.json \
    --verdicts v.json --assessments a.json --out report.json
```

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
