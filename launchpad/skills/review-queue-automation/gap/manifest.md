# RQA gap analysis — estate manifest

The pinned inventory of the estate this analysis assesses. Every file the
analysis may cite, cluster or dispose of appears below; nothing outside this
table is in scope, and nothing in this table is silently skipped.

Revision: 9267b6308714454a3b987622d90cda03a8972827
Count: 135

Generated from, and reproducible with:

```
git ls-tree -r --name-only 9267b6308714454a3b987622d90cda03a8972827 -- launchpad/skills/review-queue-automation
```

Rows are in `git ls-tree` order (the tree's own sorted path order). Paths are
written relative to `launchpad/skills/review-queue-automation/`,
as every path under `gap/` is.

## Assessed scope

**In scope — 121 files, `scope = assessed`.** Everything tracked under the skill
that is part of the *implementation* being assessed: `SKILL.md`, `OPERATORS.md`,
`onboarding/SKILL.md`, `config.example.json`, and everything under
`references/`, `schemas/`, `scripts/` and `tests/`. Each of these is placed in
exactly one cluster by [`clusters.md`](clusters.md) and must be evidenced by the
lane that owns that cluster.

**Excluded — 14 files, `scope = excluded`.** Everything under `requirements/`:
the frozen #2069 requirements specification and its supporting documents
(`clause-inventory.md`, `methodology.md`, `prd-2006-normative-extract.md`,
`requirements-quality-assessment.md`, `requirements-specification.md`,
`revision-history.md`, `set-assessment.md`, `singular-splits.md`,
`traceability.md`, `validate.py`, and the four files under `adr-drafts/`).

They are excluded because **they are this analysis's future state, not its
subject.** The requirements specification is the standard the estate is measured
against; measuring it against itself is meaningless, and disposing of it would
be editing the specification, which issue #2070 places out of scope. They are
read constantly — every register row is keyed by an ID defined there — and
assessed never.

**Exclusion is recorded, not assumed.** Every one of the 135 tracked files has a
row. An excluded file carries a non-empty reason in its row, so a later reader
can always tell an exclusion (deliberate, reasoned) from an omission (a file
nobody looked at). A tracked file with no row is a defect in this document.

## Count arithmetic

- Tracked under `launchpad/skills/review-queue-automation/` at `9267b6308`: **135**.
- Excluded (`requirements/**`, including `requirements/adr-drafts/**`): **14**.
- Assessed: 135 − 14 = **121**.
- Assessed by area: `scripts/` 48 + `tests/` 63 + root, docs and schemas 10 = 121,
  where the 10 are `SKILL.md`, `OPERATORS.md`, `config.example.json`,
  `onboarding/SKILL.md`, the 4 files under `references/` and the 2 under
  `schemas/`. The 63 files under `tests/` are 61 `test_*.py` plus `conftest.py`
  and `run_all.py`.
- [`clusters.md`](clusters.md) assigns all **121** assessed files to exactly one
  of seven clusters, and its per-cluster counts sum to 121.

## Manifest

| path | scope | reason |
| --- | --- | --- |
| OPERATORS.md | assessed | - |
| SKILL.md | assessed | - |
| config.example.json | assessed | - |
| onboarding/SKILL.md | assessed | - |
| references/classification.md | assessed | - |
| references/contracts.md | assessed | - |
| references/model-fallbacks.md | assessed | - |
| references/runtime-ops.md | assessed | - |
| requirements/adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/adr-drafts/ADR-B-credential-scope-vs-merge-capability.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/adr-drafts/ADR-C-external-harness-provenance-authentication.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/adr-drafts/README.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/clause-inventory.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/methodology.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/prd-2006-normative-extract.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/requirements-quality-assessment.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/requirements-specification.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/revision-history.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/set-assessment.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/singular-splits.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/traceability.md | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| requirements/validate.py | excluded | frozen #2069 requirements specification — this analysis's future state, not part of the assessed estate |
| schemas/author-triage.json | assessed | - |
| schemas/reviewer-verdict.json | assessed | - |
| scripts/action_gate.py | assessed | - |
| scripts/advisory.py | assessed | - |
| scripts/approval.py | assessed | - |
| scripts/approval_action.py | assessed | - |
| scripts/approval_evaluate.py | assessed | - |
| scripts/assurance.py | assessed | - |
| scripts/authority.py | assessed | - |
| scripts/budget.py | assessed | - |
| scripts/cadence.py | assessed | - |
| scripts/checks.py | assessed | - |
| scripts/cli.py | assessed | - |
| scripts/common.py | assessed | - |
| scripts/config.py | assessed | - |
| scripts/dispatcher.py | assessed | - |
| scripts/errors.py | assessed | - |
| scripts/evidence.py | assessed | - |
| scripts/explain.py | assessed | - |
| scripts/fallback.py | assessed | - |
| scripts/findings.py | assessed | - |
| scripts/github_auth.py | assessed | - |
| scripts/github_mutate.py | assessed | - |
| scripts/github_query.py | assessed | - |
| scripts/github_rest.py | assessed | - |
| scripts/history.py | assessed | - |
| scripts/human_cli.py | assessed | - |
| scripts/launchd.plist.example | assessed | - |
| scripts/lease.py | assessed | - |
| scripts/ledger.py | assessed | - |
| scripts/logging_otel.py | assessed | - |
| scripts/model_registry.py | assessed | - |
| scripts/modes.py | assessed | - |
| scripts/notify.py | assessed | - |
| scripts/onboarding.py | assessed | - |
| scripts/panel.py | assessed | - |
| scripts/planner.py | assessed | - |
| scripts/policy.py | assessed | - |
| scripts/queue.py | assessed | - |
| scripts/risk.py | assessed | - |
| scripts/route_probe.py | assessed | - |
| scripts/routing.py | assessed | - |
| scripts/runners.py | assessed | - |
| scripts/scheduled-tick.sh | assessed | - |
| scripts/shadow.py | assessed | - |
| scripts/snapshot.py | assessed | - |
| scripts/states.py | assessed | - |
| scripts/strategies.py | assessed | - |
| scripts/verdict.py | assessed | - |
| scripts/worktree.py | assessed | - |
| tests/conftest.py | assessed | - |
| tests/run_all.py | assessed | - |
| tests/test_advisory.py | assessed | - |
| tests/test_approval_evidence.py | assessed | - |
| tests/test_approval_policy.py | assessed | - |
| tests/test_assurance.py | assessed | - |
| tests/test_budget_controls.py | assessed | - |
| tests/test_cadence.py | assessed | - |
| tests/test_checks_vocabulary.py | assessed | - |
| tests/test_config_onboarding.py | assessed | - |
| tests/test_degradation.py | assessed | - |
| tests/test_deterministic.py | assessed | - |
| tests/test_dispatch_flow.py | assessed | - |
| tests/test_dispatch_observability.py | assessed | - |
| tests/test_docs_contract.py | assessed | - |
| tests/test_e2e_outcomes.py | assessed | - |
| tests/test_errors_states.py | assessed | - |
| tests/test_fallback.py | assessed | - |
| tests/test_fallback_recipes.py | assessed | - |
| tests/test_github_auth.py | assessed | - |
| tests/test_github_query.py | assessed | - |
| tests/test_history.py | assessed | - |
| tests/test_human_execution.py | assessed | - |
| tests/test_human_queue.py | assessed | - |
| tests/test_integration.py | assessed | - |
| tests/test_lease.py | assessed | - |
| tests/test_lease_lifecycle.py | assessed | - |
| tests/test_ledger.py | assessed | - |
| tests/test_logging.py | assessed | - |
| tests/test_logging_concurrency.py | assessed | - |
| tests/test_model_registry.py | assessed | - |
| tests/test_modes.py | assessed | - |
| tests/test_mutations.py | assessed | - |
| tests/test_notify.py | assessed | - |
| tests/test_onboarding.py | assessed | - |
| tests/test_panel_policy.py | assessed | - |
| tests/test_phase1.py | assessed | - |
| tests/test_phase2.py | assessed | - |
| tests/test_phase3.py | assessed | - |
| tests/test_phase4.py | assessed | - |
| tests/test_planner.py | assessed | - |
| tests/test_policy_reload.py | assessed | - |
| tests/test_queue.py | assessed | - |
| tests/test_regression.py | assessed | - |
| tests/test_repairs.py | assessed | - |
| tests/test_request_changes.py | assessed | - |
| tests/test_rest_cache.py | assessed | - |
| tests/test_rest_reader_surface.py | assessed | - |
| tests/test_risk.py | assessed | - |
| tests/test_route_config.py | assessed | - |
| tests/test_runners.py | assessed | - |
| tests/test_runtime_ops.py | assessed | - |
| tests/test_runtime_ownership.py | assessed | - |
| tests/test_shadow_calibration.py | assessed | - |
| tests/test_shadow_cli.py | assessed | - |
| tests/test_snapshot.py | assessed | - |
| tests/test_snapshot_pinning.py | assessed | - |
| tests/test_stale_head.py | assessed | - |
| tests/test_state_persistence.py | assessed | - |
| tests/test_strategy_metadata.py | assessed | - |
| tests/test_verdict_fence.py | assessed | - |
| tests/test_verdict_schema.py | assessed | - |
| tests/test_worktree.py | assessed | - |
