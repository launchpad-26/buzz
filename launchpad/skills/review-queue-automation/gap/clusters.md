# RQA gap analysis — clusters

The 121 assessed files of [`manifest.md`](manifest.md), partitioned into seven
file-disjoint clusters. One cluster is the unit of evidence ownership: the lane
that owns a cluster must be able to evidence **every** file in it, and no file
belongs to two clusters.

Revision: 9267b6308714454a3b987622d90cda03a8972827

The seven cluster names are fixed: `queue`, `dispatch`, `policy`, `verdict`,
`authority`, `resilience`, `docs`. Disposition-unit identifiers derive from them
(`U-QUEUE-01`, `U-DISPATCH-01`, …) as defined in
[`methodology.md`](methodology.md) §4.

## What each cluster is

| cluster | responsibility |
| --- | --- |
| `queue` | Detecting work and holding it: queue reconciliation, leases, the job state machine, cadence, snapshots and history — plus the timer that fires the tick. |
| `dispatch` | Turning a queued job into a run: the dispatcher and its runtime-operations subcommands, model runners, the plan, and isolated author worktrees. |
| `policy` | What the system is configured to do: config load and validation, policy, strategies, routing, modes, the model registry, and onboarding. |
| `verdict` | Judging a change: reviewer verdicts and their schema, findings, evidence collection, the checks vocabulary, risk banding, assurance, the panel and shadow mode. |
| `authority` | Acting on GitHub and deciding who may: authority and the action gate, approval evaluation and execution, the GitHub auth/query/mutate/REST surface, notification, and the human queue. |
| `resilience` | Staying up and staying explicable: budget, fallback, error taxonomy, logging and OTel, explain, the ledger, advisories, and the shared config/common entry resolution. |
| `docs` | The operator-facing contract — `SKILL.md`, `OPERATORS.md`, `references/**` — together with the cross-cutting suites that assert the system end to end rather than any one behaviour, and the test harness itself. |

## Placement rule

A file sits in the cluster where **the behaviour it evidences** lives. For a
script that is where the behaviour is implemented; for a test that is where the
code under test lives. A cross-cutting suite that asserts several clusters at
once — no single behavioural cluster could own it without reading another
cluster's code — sits in `docs`, which is where this analysis already keeps the
end-to-end and regression suites (`test_integration.py`, `test_regression.py`,
`test_e2e_outcomes.py`, `test_deterministic.py`, `test_phase1..4.py`) and the
harness (`conftest.py`, `run_all.py`).

## Placement decisions taken here

The starting table supplied by the orchestrator placed **119** of the 121
assessed files. That table was reconciled row by row against the `git ls-tree`
output at `9267b6308`: every one of the 48 `scripts/` files, all 10 root, doc
and schema files, and 59 of the 61 `tests/test_*.py` were placed, and **no other
discrepancy was found** — no duplicate placement, no placement of a path that is
not tracked, no assessed file placed twice. The two unplaced files were decided
as follows.

**`tests/test_runtime_ops.py` → `dispatch`.** It is the T27 retention, recovery,
backup and health suite, and every behaviour it exercises is implemented in
`scripts/dispatcher.py` and wired to a `dispatcher.main` subcommand of its own.
The five pairings, read off the local-command table at
`scripts/dispatcher.py:2269-2277` and the `recover` branch at
`scripts/dispatcher.py:2309-2310`, are: `recover` → `recover_interrupted`
(`scripts/dispatcher.py:1808`); `retention` → `retention_sweep`
(`scripts/dispatcher.py:1941`); `backup` → `backup_state`
(`scripts/dispatcher.py:2032`); `health` → `runtime_health`
(`scripts/dispatcher.py:2056`); and `cooldown-reset` → `reset_cooldowns`
(`scripts/dispatcher.py:2012`). They are five distinct commands, not three
— the file's final test (`tests/test_runtime_ops.py:274`) asserts wiring for
`health`, `retention` and `cooldown-reset` only, and never invokes `recover` or
`backup`; those two are exercised by the recovery and backup tests earlier in the
same file (`tests/test_runtime_ops.py:50`, `tests/test_runtime_ops.py:208`). It
imports `dispatcher` directly and reuses the dispatch suite's own fixtures
(`tests/test_runtime_ops.py:26`, `tests/test_runtime_ops.py:28`). `resilience`
was the alternative — the file touches `budget` and `ledger`, and
retention/health read as operational robustness — but the code that must be
evidenced to judge it is the dispatcher's, so the `dispatch` lane is the only one
that can evidence it without reading another cluster's files.

**`tests/test_repairs.py` → `docs`.** It is a cross-cutting regression suite by
construction. Its 19 tests were attributed module by module against this
document's own cluster assignments — by the module that actually **defines** each
symbol under test, not by the symbol's name — and they land in four different
clusters: `verdict` (`risk`, `verdict`), `authority` (`approval_evaluate`,
`github_mutate`), `queue` (`lease`, `states`) and `resilience` (`errors`, and
`common`, which defines both `State.transition` and the `GithubRest` transport
the ETag test exercises at `scripts/common.py:488` — that test imports
`GithubRest` from `common`, not from `scripts/github_rest.py`, whose `RestReader`
it never touches). **No single behavioural cluster holds a majority of the
file**, and whichever of the four owned it would have to read the other three
clusters' code to evidence it. Its own docstring describes it as regression
coverage for a list of headline defects spanning the system, and it is the same
kind of artefact as `tests/test_regression.py`, which the starting table already
places in `docs`. Placing it in `docs` — where this analysis already keeps the
cross-cutting suites — keeps the partition honest.

Note for the `docs` lane, recorded here because it will meet it: that file's
docstring (`tests/test_repairs.py:5`, `tests/test_repairs.py:7`) claims coverage
of "worktree, supersede, config shapes, onboarding no-overwrite", for none of
which the file contains a test at `9267b6308` — the supersede test was moved out
and the docstring left behind (`tests/test_repairs.py:311`). A
documentation-versus-code divergence to evidence, not to fix.

## Cluster counts

| cluster | files |
| --- | --- |
| queue | 18 |
| dispatch | 11 |
| policy | 18 |
| verdict | 18 |
| authority | 21 |
| resilience | 17 |
| docs | 18 |

18 + 11 + 18 + 18 + 21 + 17 + 18 = **121** assessed files, matching the 121 assessed rows of
[`manifest.md`](manifest.md) exactly: every assessed path appears in the table
below exactly once, and the table below contains no path that is not an assessed
manifest row.

## Assignments

| path | cluster |
| --- | --- |
| OPERATORS.md | docs |
| SKILL.md | docs |
| config.example.json | policy |
| onboarding/SKILL.md | policy |
| references/classification.md | docs |
| references/contracts.md | docs |
| references/model-fallbacks.md | docs |
| references/runtime-ops.md | docs |
| schemas/author-triage.json | verdict |
| schemas/reviewer-verdict.json | verdict |
| scripts/action_gate.py | authority |
| scripts/advisory.py | resilience |
| scripts/approval.py | authority |
| scripts/approval_action.py | authority |
| scripts/approval_evaluate.py | authority |
| scripts/assurance.py | verdict |
| scripts/authority.py | authority |
| scripts/budget.py | resilience |
| scripts/cadence.py | queue |
| scripts/checks.py | verdict |
| scripts/cli.py | resilience |
| scripts/common.py | resilience |
| scripts/config.py | policy |
| scripts/dispatcher.py | dispatch |
| scripts/errors.py | resilience |
| scripts/evidence.py | verdict |
| scripts/explain.py | resilience |
| scripts/fallback.py | resilience |
| scripts/findings.py | verdict |
| scripts/github_auth.py | authority |
| scripts/github_mutate.py | authority |
| scripts/github_query.py | authority |
| scripts/github_rest.py | authority |
| scripts/history.py | queue |
| scripts/human_cli.py | authority |
| scripts/launchd.plist.example | queue |
| scripts/lease.py | queue |
| scripts/ledger.py | resilience |
| scripts/logging_otel.py | resilience |
| scripts/model_registry.py | policy |
| scripts/modes.py | policy |
| scripts/notify.py | authority |
| scripts/onboarding.py | policy |
| scripts/panel.py | verdict |
| scripts/planner.py | dispatch |
| scripts/policy.py | policy |
| scripts/queue.py | queue |
| scripts/risk.py | verdict |
| scripts/route_probe.py | policy |
| scripts/routing.py | policy |
| scripts/runners.py | dispatch |
| scripts/scheduled-tick.sh | queue |
| scripts/shadow.py | verdict |
| scripts/snapshot.py | queue |
| scripts/states.py | queue |
| scripts/strategies.py | policy |
| scripts/verdict.py | verdict |
| scripts/worktree.py | dispatch |
| tests/conftest.py | docs |
| tests/run_all.py | docs |
| tests/test_advisory.py | resilience |
| tests/test_approval_evidence.py | verdict |
| tests/test_approval_policy.py | authority |
| tests/test_assurance.py | verdict |
| tests/test_budget_controls.py | resilience |
| tests/test_cadence.py | queue |
| tests/test_checks_vocabulary.py | verdict |
| tests/test_config_onboarding.py | policy |
| tests/test_degradation.py | resilience |
| tests/test_deterministic.py | docs |
| tests/test_dispatch_flow.py | dispatch |
| tests/test_dispatch_observability.py | dispatch |
| tests/test_docs_contract.py | docs |
| tests/test_e2e_outcomes.py | docs |
| tests/test_errors_states.py | queue |
| tests/test_fallback.py | resilience |
| tests/test_fallback_recipes.py | resilience |
| tests/test_github_auth.py | authority |
| tests/test_github_query.py | authority |
| tests/test_history.py | queue |
| tests/test_human_execution.py | authority |
| tests/test_human_queue.py | authority |
| tests/test_integration.py | docs |
| tests/test_lease.py | queue |
| tests/test_lease_lifecycle.py | queue |
| tests/test_ledger.py | resilience |
| tests/test_logging.py | resilience |
| tests/test_logging_concurrency.py | resilience |
| tests/test_model_registry.py | policy |
| tests/test_modes.py | policy |
| tests/test_mutations.py | authority |
| tests/test_notify.py | authority |
| tests/test_onboarding.py | policy |
| tests/test_panel_policy.py | policy |
| tests/test_phase1.py | docs |
| tests/test_phase2.py | docs |
| tests/test_phase3.py | docs |
| tests/test_phase4.py | docs |
| tests/test_planner.py | dispatch |
| tests/test_policy_reload.py | policy |
| tests/test_queue.py | queue |
| tests/test_regression.py | docs |
| tests/test_repairs.py | docs |
| tests/test_request_changes.py | authority |
| tests/test_rest_cache.py | authority |
| tests/test_rest_reader_surface.py | authority |
| tests/test_risk.py | verdict |
| tests/test_route_config.py | policy |
| tests/test_runners.py | dispatch |
| tests/test_runtime_ops.py | dispatch |
| tests/test_runtime_ownership.py | dispatch |
| tests/test_shadow_calibration.py | verdict |
| tests/test_shadow_cli.py | verdict |
| tests/test_snapshot.py | queue |
| tests/test_snapshot_pinning.py | queue |
| tests/test_stale_head.py | queue |
| tests/test_state_persistence.py | queue |
| tests/test_strategy_metadata.py | policy |
| tests/test_verdict_fence.py | verdict |
| tests/test_verdict_schema.py | verdict |
| tests/test_worktree.py | dispatch |
