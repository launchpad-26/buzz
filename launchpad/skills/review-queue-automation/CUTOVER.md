# CUTOVER.md — legacy estate to replacing part map

This document maps every legacy `scripts/*` module and every legacy `tests/*` file to the part
package (`rqa.<part>`) or disposition unit that replaces or retires it. It is the deletion
authority for wave 2 (#2213) and the reconciliation of what wave 3 (#2214) still owns in prose.

**This Feature now discharges `architecture/components.md` §7.** Task #2273 restored the one
`keep`-recommended unit the original cutover found missing: U-DISPATCH-19's closed fifteen-event
registry, nine-event required subset, rejection at emission, and lifecycle callers now live in
`rqa.record.trace` and `rqa.lifecycle`. The legacy `scripts/logging_otel.py` reference is therefore
deleted; §2 and §7.3 name and test the replacement that made deletion sound.

Guarded by `tests/test_cutover_map.py`, which runs inside `tests/run_all.py` automatically (any
file named `tests/test_*.py` is discovered and its zero-argument `test_*` functions are run — see
that file's own module docstring for why no edit to `run_all.py` was needed).

## 0. Three independent columns: `disposition`, `status`, and what each vocabulary word means

Every row below carries two columns that must never be collapsed into one:

- **`disposition`** — the owning lane's classification of the *responsibility*, reconciled
  against that lane's handoff (§4) and against `architecture/components.md` §7's placement table.
  It never changes after this document lands. The common values map from `components.md` §7's own
  vocabulary (`keep`/`rework`/`salvage`/`bin`) as follows — **and the mapping is corrected here
  from round 1, which mis-stated it:**
  - `keep → migrated` (the behaviour carries into the new package unchanged);
  - `rework → rewritten` (the contract changed);
  - `salvage → rewritten` (every lane that performed a salvage wrote "rewritten from (salvage
    source)" in its own handoff — the mechanism is rebuilt, not carried verbatim);
  - `bin → retired`, but **`retired` never means "no part covers it."** `components.md` §7's own
    preamble defines `bin` as **replaced by** a named part — "the part whose behaviour now covers
    the concern the unit addressed, or the part that makes the concern moot" — so a `bin` unit
    *does* have a named replacing part by construction (round 1's four `U-POLICY-07` rows, e.g.
    `scripts/config.py`'s, correctly cite `replacement: rqa.intake.admission` under
    `disposition: retired`; only round 1's prose describing the mapping was wrong, not those rows).
    `retired` with `replacement: none (binned: U-XXX-NN)` is reserved for the narrower case where
    *no* part covers the concern at all — the twelve rows so marked in §2, each a genuine absence,
    never a part's own behaviour making it moot.
  - `kept` is reserved for the ten root/doc/schema files of §6, where a handoff found nothing to
    rewrite.
  - A `keep`-recommended unit with no successor is a defect rather than a retirement. The one such
    case found during this cutover, U-DISPATCH-19, was repaired by #2273 before its reference file
    was deleted.
- **`status`** ∈ `present` | `deleted` — the map's claim about the filesystem
  *and* about what wave 2 may do with the file:
  - `present` — on disk today; wave 2 may delete it if `disposition` authorises that.
  - `deleted` — wave 2 deleted it; the file must genuinely be absent. #2213 flips a row to
    `deleted` in the same commit that deletes the file.
  - All rows for one `file` must agree on `status`; the guard enforces that (§8, condition 3).
    Every doc/schema row (§6) is additionally held to `status: present` **unconditionally**,
    checked against the row text alone rather than the filesystem — the guard's fourth condition
    (§8) — because condition 3 alone would accept a doc/schema file that was genuinely deleted with
    its row honestly flipped to `deleted` in the same commit, and that file must never be deletable
    at all, by any lane, ever.

**The map authorises deletion only under `scripts/` and `tests/`.** The ten root/docs/schema files
in §6 are recorded — several handoffs handed them to this document — but never marked `retired`
here and never counted as deletion targets: `onboarding/SKILL.md`, `SKILL.md`, `OPERATORS.md`,
`config.example.json` and every `references/*.md` file are wave 3's (#2214) to rewrite, and
`schemas/*.json` is recorded but likewise outside this map's deletion authority (it is not a
wave-3 file either — see §6's note).

## 0.1 DoD item 1's "exactly one row" reconciled against the shared-lane row model

The issue's own checklist says "every legacy module and test file has exactly one row." Taken
literally this contradicts the orchestrator's binding row shape (§2 below, "one row per `(file,
owning part)` pair"), which is what makes `scripts/dispatcher.py` — cited by eight distinct parts
per `components.md` §7 (§4.4 below measures this precisely against the issue's own "nine") —
representable at all without collapsing eight different lanes' dispositions into one cell. This
document follows the shared-lane row model: "exactly one row" is read as "exactly one row per
`(file, owning part)` pair, and every such pair that exists has one," which is checkable (condition
1 of the guard, §10) and is not satisfied by the literal single-row reading for any multiply-owned
file.

## 1. Two count reconciliations against the issue text

**"48 `scripts/*.py` modules."** There are 48 *files* in `scripts/`, but only 46 are `.py`. The
other two — `scripts/launchd.plist.example` and `scripts/scheduled-tick.sh` — are mapped in §2
below (both `U-QUEUE-08`, `P-01`, `migrated`) because they are load-bearing estate the same way the
Python modules are: `launchd.plist.example` is the launchd job description and
`scheduled-tick.sh` is the script it invokes, together implementing E-21's external-timer half of
U-QUEUE-08. Excluding them because they are not `.py` would leave two tracked, disposition-bearing
files with no row, which is exactly the defect this document exists to prevent.

**"71 `tests/*` files."** 70 were present at the run's actual base (`3fdafab0c`); the 71st present
in this worktree today, `tests/lifecycle_cascade_bench.py`, was added *by this run*: its first
commit is `028ef9211` ("feat(rqa): implement P-02 — lifecycle drive and resume", 2026-09-13),
part of the same P-02 batch as `#2199`/`#2200`, well after `3fdafab0c`. It is recorded in §7 as
**new estate, not legacy, not retired**, so its absence from the 70-row legacy table below is
never mistaken for an omission. This document maps the 70.

## 2. The map

One row per `(file, owning part)` pair — a file whose responsibility several parts placed a unit
in carries one row per part, so a shared file is retired only when every part's row says so.
`unit(s)` cites the `U-<AREA>-NN` id(s) from `gap/dispositions/*.md` (placement per
`architecture/components.md` §7) that justify the row, or, for the seven files no disposition unit
names (§5), the replacing part's own §1 module list. `lane (issue #)` is the child Task whose
handoff (`.workmux/handoff-*.md` in the main repository, read at the paths named in this Task's
prompt §6) declared the classification, or `pre-batch (P-0N, <sha>)` for the three parts (P-03,
P-04, P-12) whose code landed before this run's batch-1 handoff convention began and which
therefore have no handoff of their own on record (§4.3). `replacement` is a dotted `rqa.*` module
path, a `tests/test_rqa_*.py` path, or `none (binned: <unit>)` for a responsibility with no
successor. `unknown` appears nowhere in this table.

| file | part | lane (issue #) | unit(s) | disposition | replacement | status |
|---|---|---|---|---|---|---|
| `OPERATORS.md` | — | #2214 | U-DOCS-02,03,04,05,07,11,12,16,18,19,20 | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `SKILL.md` | — | #2214 | U-DOCS-01,02,04,05,06,07,08,10,11,12,13,16 | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `config.example.json` | P-03 | #2214 | U-POLICY-03 | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `onboarding/SKILL.md` | — | #2214 | U-DOCS-02,04,05,06,07,08,09,11,12,13; U-POLICY-06,07 (cross-cutting; cited by 11+ parts) | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `references/classification.md` | — | #2214 | U-DOCS-01,13,25 | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `references/contracts.md` | — | #2214 | U-DOCS-01,04,06,08,09,13 | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `references/model-fallbacks.md` | P-05 | #2214 | U-DOCS-07 | kept | (nothing rewrites it beyond #2205's aliases.py; NOT deletion-authorized by this map) | present |
| `references/runtime-ops.md` | — | #2214 | U-DOCS-14,15,17,18,19,20,21,24 | rewritten | (#2214 rewrite; NOT deletion-authorized by this map) | present |
| `schemas/author-triage.json` | P-04 | pre-batch (P-04, 0d313897d) | U-VERDICT-03 | retired | none (binned: U-VERDICT-03 — author-triage lane dropped; NOT deletion-authorized by this map) | present |
| `schemas/reviewer-verdict.json` | P-04 | pre-batch (P-04, 0d313897d) | U-VERDICT-02 | rewritten | rqa.protocol.schema (NOT deletion-authorized by this map — only scripts/ and tests/ are) | present |
| `scripts/action_gate.py` | P-07 | #2191 | U-AUTHORITY-04 | migrated | rqa.judgement.judge | deleted |
| `scripts/advisory.py` | P-07 | #2191 | U-RESILIENCE-05 | rewritten | rqa.judgement.render | deleted |
| `scripts/approval.py` | P-11 | #2195 | U-AUTHORITY-05 | rewritten | rqa.escalation.escalate | deleted |
| `scripts/approval_action.py` | P-09 | #2193 | U-AUTHORITY-08 | migrated | rqa.github.writes | deleted |
| `scripts/approval_evaluate.py` | P-07 | #2191 | U-AUTHORITY-03 | rewritten | rqa.judgement.judge | deleted |
| `scripts/assurance.py` | P-06 | #2190 | U-VERDICT-08 | migrated | rqa.harness.panel | deleted |
| `scripts/authority.py` | P-08 | #2192 | U-AUTHORITY-01 | rewritten | rqa.authority.gate | deleted |
| `scripts/budget.py` | P-05 | #2205 | U-RESILIENCE-02 | migrated | rqa.supply.breakers | deleted |
| `scripts/budget.py` | P-05 | #2206 | U-RESILIENCE-01 | rewritten | rqa.supply.budget | deleted |
| `scripts/cadence.py` | P-01 | #2197, #2198 | U-QUEUE-05, U-QUEUE-07 | rewritten | rqa.intake.tick | deleted |
| `scripts/cadence.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-QUEUE-06 | migrated | rqa.policy.validate | deleted |
| `scripts/checks.py` | P-07 | #2191 | U-VERDICT-05 | migrated | rqa.judgement.findings | deleted |
| `scripts/checks.py` | P-09 | #2193 | U-VERDICT-06 | rewritten | rqa.github.conclusions | deleted |
| `scripts/cli.py` | P-01 | #2197, #2198 | U-RESILIENCE-16 | migrated | rqa.cli.composition | deleted |
| `scripts/common.py` | P-01 | #2197, #2198 | U-RESILIENCE-13 | migrated | rqa.intake.identity | deleted |
| `scripts/common.py` | P-02 | #2199 | U-RESILIENCE-11 | migrated | rqa.lifecycle.transition | deleted |
| `scripts/common.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-RESILIENCE-09 | migrated | rqa.policy.validate | deleted |
| `scripts/common.py` | P-06 | #2190 | U-RESILIENCE-15 | migrated | rqa.harness.bundle | deleted |
| `scripts/common.py` | P-08 | #2192 | U-RESILIENCE-10 | migrated | rqa.authority.capability | deleted |
| `scripts/common.py` | P-09 | #2193 | U-RESILIENCE-12 | migrated | rqa.github.transport | deleted |
| `scripts/common.py` | P-12 | pre-batch (P-12, 458c500d2) | U-RESILIENCE-14 | migrated | rqa.record.writer | deleted |
| `scripts/config.py` | P-01 | #2197, #2198 | U-POLICY-07 | retired | rqa.intake.admission | deleted |
| `scripts/config.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-POLICY-01, U-POLICY-02, U-POLICY-05, U-POLICY-06 | rewritten | rqa.policy.validate, rqa.policy.onboard | deleted |
| `scripts/dispatcher.py` | P-01 | #2197, #2198 | U-DISPATCH-01, U-DISPATCH-02, U-DISPATCH-08, U-DISPATCH-10, U-DISPATCH-22 | rewritten | rqa.intake.admission, rqa.intake.lock, rqa.intake.tick, rqa.intake.lease | deleted |
| `scripts/dispatcher.py` | P-02 | #2199 | U-DISPATCH-03, U-DISPATCH-07, U-DISPATCH-21, U-DISPATCH-23 | rewritten | rqa.lifecycle.status, rqa.lifecycle.admit, rqa.lifecycle.errors, rqa.lifecycle.states | deleted |
| `scripts/dispatcher.py` | P-02 | #2200 | U-DISPATCH-17, U-DISPATCH-18 | rewritten | rqa.lifecycle.steps | deleted |
| `scripts/dispatcher.py` | P-05 | #2205 | U-DISPATCH-05 | retired | none (binned: U-DISPATCH-05) | deleted |
| `scripts/dispatcher.py` | P-05 | #2206 | U-DISPATCH-12, U-DISPATCH-13 | rewritten | rqa.supply.budget, rqa.supply.spend | deleted |
| `scripts/dispatcher.py` | P-06 | #2190 | U-DISPATCH-14 | migrated | rqa.harness.panel | deleted |
| `scripts/dispatcher.py` | P-07 | #2191 | U-DISPATCH-15 | rewritten | rqa.judgement.judge | deleted |
| `scripts/dispatcher.py` | P-08 | #2192 | U-DISPATCH-09, U-DISPATCH-11 | rewritten | rqa.authority.gate | deleted |
| `scripts/dispatcher.py` | P-09 | #2193 | U-DISPATCH-16 | migrated | rqa.github.writes | deleted |
| `scripts/dispatcher.py` | P-12 | pre-batch (P-12, 458c500d2) | U-DISPATCH-04, U-DISPATCH-06 | retired | none (binned: U-DISPATCH-04, U-DISPATCH-06) | deleted |
| `scripts/dispatcher.py` | P-12 | #2273 | U-DISPATCH-19 | migrated | rqa.lifecycle, rqa.record.trace | deleted |
| `scripts/dispatcher.py` | P-12 | pre-batch (P-12, 458c500d2) | U-DISPATCH-20 | rewritten | rqa.record.writer | deleted |
| `scripts/errors.py` | P-02 | #2199 | U-RESILIENCE-17 | retired | none (binned: U-RESILIENCE-17) | deleted |
| `scripts/errors.py` | P-06 | #2190 | U-RESILIENCE-04 | rewritten | rqa.harness.panel | deleted |
| `scripts/evidence.py` | P-06 | #2190 | U-VERDICT-07 | migrated | rqa.harness.bundle | deleted |
| `scripts/explain.py` | P-12 | pre-batch (P-12, 458c500d2) | U-RESILIENCE-07 | migrated | rqa.record.explain | deleted |
| `scripts/fallback.py` | P-05 | #2205 | U-RESILIENCE-03 | rewritten | rqa.supply.ladder | deleted |
| `scripts/findings.py` | P-07 | #2191 | U-VERDICT-04, U-VERDICT-05 | migrated | rqa.judgement.findings | deleted |
| `scripts/github_auth.py` | P-08 | #2192 | U-AUTHORITY-02 | rewritten | rqa.authority.capability | deleted |
| `scripts/github_mutate.py` | P-09 | #2193 | U-AUTHORITY-08, U-AUTHORITY-09 | rewritten | rqa.github.writes | deleted |
| `scripts/github_query.py` | P-09 | #2193 | U-AUTHORITY-10 | migrated | rqa.github.reads | deleted |
| `scripts/github_rest.py` | P-09 | #2193 | U-AUTHORITY-11 | migrated | rqa.github.transport | deleted |
| `scripts/history.py` | P-12 | pre-batch (P-12, 458c500d2) | U-QUEUE-13 | retired | none (binned: U-QUEUE-13) | deleted |
| `scripts/human_cli.py` | P-02 | #2200 | U-AUTHORITY-07 | rewritten | rqa.lifecycle.resume | deleted |
| `scripts/human_cli.py` | P-11 | #2195 | U-AUTHORITY-06 | rewritten | rqa.escalation.decide | deleted |
| `scripts/launchd.plist.example` | P-01 | #2197, #2198 | U-QUEUE-08 | migrated | rqa.intake.tick | deleted |
| `scripts/lease.py` | P-01 | #2197, #2198 | U-QUEUE-03, U-QUEUE-04 | migrated | rqa.intake.lease | deleted |
| `scripts/ledger.py` | P-12 | pre-batch (P-12, 458c500d2) | U-RESILIENCE-06 | rewritten | rqa.record.writer | deleted |
| `scripts/logging_otel.py` | P-12 | #2273 | U-RESILIENCE-08, U-DISPATCH-19 | migrated | rqa.record.trace, rqa.lifecycle | deleted |
| `scripts/model_registry.py` | P-05 | #2205 | U-POLICY-11, U-POLICY-12 | migrated | rqa.supply.aliases | deleted |
| `scripts/modes.py` | P-06 | #2190 | U-POLICY-09 | migrated | rqa.harness.panel | deleted |
| `scripts/notify.py` | P-11 | #2195 | U-AUTHORITY-12 | retired | none (binned: U-AUTHORITY-12) | deleted |
| `scripts/onboarding.py` | P-01 | #2197, #2198 | U-POLICY-07 | retired | rqa.intake.admission | deleted |
| `scripts/onboarding.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-POLICY-06 | rewritten | rqa.policy.onboard | deleted |
| `scripts/panel.py` | P-05 | #2205 | U-VERDICT-09 | migrated | rqa.supply.ladder | deleted |
| `scripts/panel.py` | P-06 | #2190 | U-VERDICT-10, U-VERDICT-11, U-VERDICT-12 | migrated | rqa.harness.panel | deleted |
| `scripts/planner.py` | P-06 | #2190 | U-DISPATCH-24 | migrated | rqa.harness.risk | deleted |
| `scripts/policy.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-POLICY-04 | migrated | rqa.policy.snapshot | deleted |
| `scripts/queue.py` | P-01 | #2197, #2198 | U-QUEUE-01, U-QUEUE-02, U-QUEUE-14 | migrated | rqa.intake.store, rqa.intake.inventory | deleted |
| `scripts/risk.py` | P-07 | #2191 | U-VERDICT-13, U-VERDICT-14, U-VERDICT-15, U-VERDICT-16, U-VERDICT-18 | rewritten | rqa.judgement.evidence, rqa.judgement.findings, rqa.judgement.judge | deleted |
| `scripts/risk.py` | P-12 | pre-batch (P-12, 458c500d2) | U-VERDICT-17 | retired | none (binned: U-VERDICT-17) | deleted |
| `scripts/route_probe.py` | P-05 | #2205 | U-POLICY-12, U-POLICY-13 | migrated | rqa.supply.probe | deleted |
| `scripts/routing.py` | P-05 | #2205 | U-POLICY-10 | migrated | rqa.supply.ladder | deleted |
| `scripts/runners.py` | P-06 | #2190 | U-DISPATCH-25 | rewritten | rqa.harness.adapters | deleted |
| `scripts/scheduled-tick.sh` | P-01 | #2197, #2198 | U-QUEUE-08 | migrated | rqa.intake.tick | deleted |
| `scripts/shadow.py` | P-07 | #2191 | U-VERDICT-19, U-VERDICT-20 | rewritten | rqa.judgement.judge | deleted |
| `scripts/shadow.py` | P-12 | pre-batch (P-12, 458c500d2) | U-VERDICT-21 | retired | none (binned: U-VERDICT-21) | deleted |
| `scripts/snapshot.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-QUEUE-09, U-QUEUE-10 | migrated | rqa.policy.snapshot | deleted |
| `scripts/states.py` | P-02 | #2199 | U-QUEUE-11, U-QUEUE-12 | migrated | rqa.lifecycle.states | deleted |
| `scripts/strategies.py` | P-06 | #2190 | U-POLICY-08 | rewritten | rqa.harness.risk | deleted |
| `scripts/verdict.py` | P-04 | pre-batch (P-04, 0d313897d) | U-VERDICT-01, U-VERDICT-02 | rewritten | rqa.protocol.fence, rqa.protocol.validate | deleted |
| `scripts/worktree.py` | P-10 | #2194 | U-DISPATCH-26 | rewritten | rqa.remediation.worktree | deleted |
| `tests/conftest.py` | P-09 | #2193 | U-DOCS-24 | rewritten | rqa.github.testing | present |
| `tests/run_all.py` | P-01 | #2197, #2198 | U-DOCS-23 | migrated | tests/run_all.py | present |
| `tests/test_advisory.py` | P-07 | #2191 | U-RESILIENCE-05 | rewritten | rqa.judgement.render | deleted |
| `tests/test_approval_evidence.py` | P-07 | #2191 | U-VERDICT-16 | rewritten | rqa.judgement.judge | deleted |
| `tests/test_approval_policy.py` | P-07 | #2191 | U-AUTHORITY-03 | rewritten | rqa.judgement.judge | deleted |
| `tests/test_approval_policy.py` | P-09 | #2193 | U-AUTHORITY-08 | migrated | rqa.github.writes | deleted |
| `tests/test_assurance.py` | P-06 | #2190 | U-VERDICT-08 | migrated | rqa.harness.panel | deleted |
| `tests/test_budget_controls.py` | P-05 | #2205 | U-RESILIENCE-02 | migrated | rqa.supply.breakers | deleted |
| `tests/test_budget_controls.py` | P-05 | #2206 | U-RESILIENCE-01 | rewritten | rqa.supply.budget | deleted |
| `tests/test_cadence.py` | P-01 | #2197, #2198 | U-QUEUE-05, U-QUEUE-07 | rewritten | rqa.intake.tick | deleted |
| `tests/test_cadence.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-QUEUE-06 | migrated | rqa.policy.validate | deleted |
| `tests/test_checks_vocabulary.py` | P-09 | #2193 | U-VERDICT-06 | rewritten | rqa.github.conclusions | deleted |
| `tests/test_config_onboarding.py` | P-01 | #2197, #2198 | U-POLICY-07 | retired | rqa.intake.admission | deleted |
| `tests/test_config_onboarding.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-POLICY-01, U-POLICY-02, U-POLICY-03, U-POLICY-06 | rewritten | rqa.policy.validate, rqa.policy.schema, rqa.policy.onboard | deleted |
| `tests/test_counterexample_authority.py` | P-08 | #2192 | — (no disposition unit cites this file; justified via P-08 §1 module list: rqa.authority.gate; also exercises P-09 github_mutate.py and P-03 policy.py/snapshot.py) | retired | tests/test_rqa_authority_gate.py | deleted |
| `tests/test_counterexample_migration.py` | P-03 | pre-batch (P-03, 576a6e9f4) | — (no disposition unit cites this file; justified via P-03 §1 module list: rqa.policy.validate, rqa.policy.snapshot) | retired | tests/test_rqa_policy_snapshot.py | deleted |
| `tests/test_counterexample_modes.py` | P-06 | #2190 | — (no disposition unit cites this file; justified via P-06 §1 module list: rqa.harness.risk, rqa.harness.panel) | retired | tests/test_rqa_harness_plan.py | deleted |
| `tests/test_counterexample_routing.py` | P-05 | #2205 | — (no disposition unit cites this file; justified via P-05 §1 module list: rqa.supply.ladder, rqa.supply.aliases) | retired | tests/test_rqa_supply_route.py | deleted |
| `tests/test_counterexample_schemas.py` | P-04 | pre-batch (P-04, 0d313897d) | — (no disposition unit cites this file; justified via P-04 §1 module list: rqa.protocol.validate; also exercises P-03 config.py/policy.py) | retired | tests/test_rqa_protocol_validate.py | deleted |
| `tests/test_counterexample_transitions.py` | P-02 | #2199 | — (no disposition unit cites this file; justified via P-02 §1 module list: rqa.lifecycle.states) | retired | tests/test_rqa_lifecycle_states.py | deleted |
| `tests/test_degradation.py` | P-06 | #2190 | U-RESILIENCE-04 | rewritten | rqa.harness.panel | deleted |
| `tests/test_deterministic.py` | P-01 | #2197, #2198 | U-DOCS-25 | migrated | tests/test_rqa_intake_identity.py | deleted |
| `tests/test_deterministic.py` | P-05 | #2205 | U-DOCS-27 | migrated | tests/test_rqa_supply_route.py | deleted |
| `tests/test_deterministic.py` | P-06 | #2190 | U-DOCS-26 | rewritten | rqa.harness.bundle | deleted |
| `tests/test_deterministic.py` | P-08 | #2192 | U-DOCS-28 | migrated | tests/test_rqa_authority_gate.py | deleted |
| `tests/test_dispatch_flow.py` | P-06 | #2190 | U-DISPATCH-14 | migrated | rqa.harness.panel | deleted |
| `tests/test_dispatch_flow.py` | P-07 | #2191 | U-DISPATCH-15 | rewritten | rqa.judgement.judge | deleted |
| `tests/test_dispatch_flow.py` | P-09 | #2193 | U-DISPATCH-16 | migrated | rqa.github.writes | deleted |
| `tests/test_dispatch_observability.py` | P-12 | #2273 | U-DISPATCH-19 | migrated | tests/test_rqa_record_trace.py, tests/test_rqa_lifecycle_steps.py | deleted |
| `tests/test_docs_contract.py` | P-04 | pre-batch (P-04, 0d313897d) | U-DOCS-22 | retired | none (binned: U-DOCS-22) | deleted |
| `tests/test_e2e_outcomes.py` | P-02 | #2200 | U-DOCS-56, U-DOCS-57 | rewritten | tests/test_rqa_lifecycle_paths.py | deleted |
| `tests/test_errors_states.py` | P-02 | #2199 | U-QUEUE-11, U-QUEUE-12 | migrated | rqa.lifecycle.states | deleted |
| `tests/test_fallback.py` | P-06 | #2190 | U-RESILIENCE-04 | rewritten | rqa.harness.panel | deleted |
| `tests/test_fallback_recipes.py` | P-05 | #2205 | U-RESILIENCE-03 | rewritten | rqa.supply.ladder | deleted |
| `tests/test_github_auth.py` | P-08 | #2192 | U-AUTHORITY-02 | rewritten | rqa.authority.capability | deleted |
| `tests/test_github_query.py` | P-09 | #2193 | U-AUTHORITY-10 | migrated | rqa.github.reads | deleted |
| `tests/test_history.py` | P-12 | pre-batch (P-12, 458c500d2) | U-QUEUE-13 | retired | none (binned: U-QUEUE-13) | deleted |
| `tests/test_human_execution.py` | P-02 | #2200 | U-AUTHORITY-07 | rewritten | rqa.lifecycle.resume | deleted |
| `tests/test_human_queue.py` | P-11 | #2195 | U-AUTHORITY-05 | rewritten | rqa.escalation.escalate | deleted |
| `tests/test_integration.py` | P-02 | #2200 | U-DOCS-54 | migrated | tests/test_rqa_lifecycle_paths.py | deleted |
| `tests/test_integration.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-DOCS-51 | migrated | tests/test_rqa_policy_snapshot.py | deleted |
| `tests/test_integration.py` | P-10 | #2194 | U-DOCS-53 | rewritten | rqa.remediation.remediate | deleted |
| `tests/test_integration.py` | P-11 | #2195 | U-DOCS-52 | migrated | tests/test_rqa_escalation_raise.py | deleted |
| `tests/test_integration.py` | P-12 | pre-batch (P-12, 458c500d2) | U-DOCS-55 | migrated | tests/test_rqa_record_trace.py | deleted |
| `tests/test_lease.py` | P-01 | #2197, #2198 | U-QUEUE-03 | migrated | rqa.intake.lease | deleted |
| `tests/test_lease_lifecycle.py` | P-01 | #2197, #2198 | U-QUEUE-04 | migrated | rqa.intake.lease | deleted |
| `tests/test_ledger.py` | P-12 | pre-batch (P-12, 458c500d2) | U-RESILIENCE-06 | rewritten | rqa.record.writer | deleted |
| `tests/test_logging.py` | P-12 | #2273 | U-RESILIENCE-08 | migrated | tests/test_rqa_record_trace.py | deleted |
| `tests/test_logging_concurrency.py` | P-12 | #2273 | U-RESILIENCE-08 | migrated | tests/test_rqa_record_trace.py | deleted |
| `tests/test_model_registry.py` | P-05 | #2205 | U-POLICY-11, U-POLICY-12, U-POLICY-13 | migrated | rqa.supply.aliases, rqa.supply.probe | deleted |
| `tests/test_modes.py` | P-06 | #2190 | U-POLICY-09 | migrated | rqa.harness.panel | deleted |
| `tests/test_mutations.py` | P-09 | #2193 | U-AUTHORITY-08 | migrated | rqa.github.writes | deleted |
| `tests/test_notify.py` | P-11 | #2195 | U-AUTHORITY-12 | retired | none (binned: U-AUTHORITY-12) | deleted |
| `tests/test_onboarding.py` | P-01 | #2197, #2198 | U-POLICY-07 | retired | rqa.intake.admission | deleted |
| `tests/test_onboarding.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-POLICY-01, U-POLICY-06 | rewritten | rqa.policy.validate, rqa.policy.onboard | deleted |
| `tests/test_panel_policy.py` | P-05 | #2205 | U-POLICY-14 | migrated | rqa.supply.ladder | deleted |
| `tests/test_phase1.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-DOCS-30, U-DOCS-31 | rewritten | tests/test_rqa_policy_validate.py, tests/test_rqa_policy_snapshot.py | deleted |
| `tests/test_phase1.py` | P-07 | #2191 | U-DOCS-32 | migrated | tests/test_rqa_judgement_judge.py | deleted |
| `tests/test_phase1.py` | P-08 | #2192 | U-DOCS-29 | migrated | tests/test_rqa_authority_gate.py | deleted |
| `tests/test_phase2.py` | P-02 | #2199 | U-DOCS-34 | migrated | tests/test_rqa_lifecycle_states.py | deleted |
| `tests/test_phase2.py` | P-07 | #2191 | U-DOCS-33 | migrated | tests/test_rqa_judgement_disposition.py | deleted |
| `tests/test_phase2.py` | P-11 | #2195 | U-DOCS-35 | rewritten | rqa.escalation.store | deleted |
| `tests/test_phase3.py` | P-05 | #2205 | U-DOCS-37 | migrated | tests/test_rqa_supply_route.py | deleted |
| `tests/test_phase3.py` | P-06 | #2190 | U-DOCS-36 | rewritten | rqa.harness.risk | deleted |
| `tests/test_phase4.py` | P-02 | #2199 | U-DOCS-38 | retired | none (binned: U-DOCS-38) | deleted |
| `tests/test_phase4.py` | P-12 | pre-batch (P-12, 458c500d2) | U-DOCS-39, U-DOCS-40 | rewritten | tests/test_rqa_record_store.py, rqa.record.explain | deleted |
| `tests/test_planner.py` | P-06 | #2190 | U-DISPATCH-24 | migrated | rqa.harness.risk | deleted |
| `tests/test_policy_reload.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-POLICY-04 | migrated | rqa.policy.snapshot | deleted |
| `tests/test_queue.py` | P-01 | #2197, #2198 | U-QUEUE-01, U-QUEUE-02 | migrated | rqa.intake.store, rqa.intake.inventory | deleted |
| `tests/test_regression.py` | P-06 | #2190 | U-DOCS-41 | migrated | rqa.harness.panel | deleted |
| `tests/test_regression.py` | P-07 | #2191 | U-DOCS-42 | migrated | tests/test_rqa_judgement_judge.py | deleted |
| `tests/test_repairs.py` | P-01 | #2197, #2198 | U-DOCS-46 | retired | none (binned: U-DOCS-46) | deleted |
| `tests/test_repairs.py` | P-02 | #2199 | U-DOCS-47 | migrated | tests/test_rqa_lifecycle_transition.py | deleted |
| `tests/test_repairs.py` | P-04 | pre-batch (P-04, 0d313897d) | U-DOCS-48 | migrated | tests/test_rqa_protocol_validate.py | deleted |
| `tests/test_repairs.py` | P-07 | #2191 | U-DOCS-43, U-DOCS-49, U-DOCS-58 | migrated | tests/test_rqa_judgement_findings.py, tests/test_rqa_judgement_judge.py | deleted |
| `tests/test_repairs.py` | P-08 | #2192 | U-DOCS-44 | migrated | tests/test_rqa_authority_gate.py | deleted |
| `tests/test_repairs.py` | P-09 | #2193 | U-DOCS-45, U-DOCS-50 | migrated | tests/test_rqa_github_writes.py, tests/test_rqa_github_transport.py, rqa.github.transport | deleted |
| `tests/test_request_changes.py` | P-07 | #2191 | U-AUTHORITY-04 | migrated | rqa.judgement.judge | deleted |
| `tests/test_rest_cache.py` | P-09 | #2193 | U-AUTHORITY-11 | migrated | rqa.github.transport | deleted |
| `tests/test_rest_reader_surface.py` | P-09 | #2193 | U-AUTHORITY-11 | migrated | rqa.github.transport | deleted |
| `tests/test_risk.py` | P-07 | #2191 | U-VERDICT-13, U-VERDICT-15 | migrated | rqa.judgement.evidence | deleted |
| `tests/test_risk.py` | P-12 | pre-batch (P-12, 458c500d2) | U-VERDICT-17 | retired | none (binned: U-VERDICT-17) | deleted |
| `tests/test_route_config.py` | P-05 | #2205 | U-POLICY-10 | migrated | rqa.supply.ladder | deleted |
| `tests/test_runner_adapters.py` | P-06 | #2190 | — (no disposition unit cites this file; justified via P-06 §1 module list: rqa.harness.adapters; also exercises P-03 config.py, P-12 ledger.py, P-05 route_probe.py) | retired | tests/test_rqa_harness_adapters.py | deleted |
| `tests/test_runners.py` | P-06 | #2190 | U-DISPATCH-25 | rewritten | rqa.harness.adapters | deleted |
| `tests/test_runtime_ops.py` | P-02 | #2199 | U-DISPATCH-03, U-DISPATCH-07 | rewritten | rqa.lifecycle.status, rqa.lifecycle.admit | deleted |
| `tests/test_runtime_ops.py` | P-05 | #2205 | U-DISPATCH-05 | retired | none (binned: U-DISPATCH-05) | deleted |
| `tests/test_runtime_ops.py` | P-12 | pre-batch (P-12, 458c500d2) | U-DISPATCH-04, U-DISPATCH-06 | retired | none (binned: U-DISPATCH-04, U-DISPATCH-06) | deleted |
| `tests/test_runtime_ownership.py` | P-01 | #2197, #2198 | U-DISPATCH-02 | rewritten | rqa.intake.lock | deleted |
| `tests/test_runtime_ownership.py` | P-02 | #2199 | U-DISPATCH-07 | rewritten | rqa.lifecycle.admit | deleted |
| `tests/test_shadow_calibration.py` | P-07 | #2191 | U-VERDICT-19, U-VERDICT-20 | rewritten | rqa.judgement.judge | deleted |
| `tests/test_shadow_cli.py` | P-12 | pre-batch (P-12, 458c500d2) | U-VERDICT-21 | retired | none (binned: U-VERDICT-21) | deleted |
| `tests/test_snapshot.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-QUEUE-09, U-QUEUE-10 | migrated | rqa.policy.snapshot | deleted |
| `tests/test_snapshot_pinning.py` | P-03 | pre-batch (P-03, 576a6e9f4) | U-QUEUE-10 | migrated | rqa.policy.snapshot | deleted |
| `tests/test_stale_head.py` | P-01 | #2197, #2198 | U-QUEUE-14 | migrated | rqa.intake.store | deleted |
| `tests/test_state_persistence.py` | P-02 | #2199 | U-QUEUE-11 | migrated | rqa.lifecycle.states | deleted |
| `tests/test_strategy_metadata.py` | P-06 | #2190 | U-POLICY-08 | rewritten | rqa.harness.risk | deleted |
| `tests/test_verdict_fence.py` | P-04 | pre-batch (P-04, 0d313897d) | U-VERDICT-01 | migrated | rqa.protocol.fence | deleted |
| `tests/test_verdict_schema.py` | P-04 | pre-batch (P-04, 0d313897d) | U-VERDICT-02 | rewritten | rqa.protocol.validate | deleted |
| `tests/test_worktree.py` | P-10 | #2194 | U-DISPATCH-26 | rewritten | rqa.remediation.worktree | deleted |

## 3. The fifteen SQLite tables — quoted verbatim from `gap/gap-analysis.md` §6.3

> **State.** All persistence is one SQLite database plus a snapshot archive and per-job artefact
> directories. `State._migrate` declares fifteen tables, and which of them carries over is decided
> per table, not per database:
>
> | table | `path:line` | carries over? |
> |---|---|---|
> | `jobs` | `scripts/common.py:231` | **Yes** — the `UNIQUE (repo, number, head_sha, lane)` constraint at `:244` *is* `RQA-BR-007`'s at-most-one-job guarantee (U-QUEUE-01). Plus the `snapshot_hash` column added by migration at `scripts/common.py:375`, which is the per-job pin (U-QUEUE-10) |
> | `leases` | `scripts/common.py:246` | **Yes** — exclusivity under `RQA-BR-007` (U-QUEUE-03, U-QUEUE-04) |
> | `ledger_entries` | `scripts/common.py:321` | **Yes** — the record `RQA-FR-012`'s reconstruction reads (U-RESILIENCE-06, U-RESILIENCE-07). Carrying the rows over does not close `RQA-NFR-028`: no row carries an integrity field, so authenticity is unverifiable for history as well as for new entries |
> | `mutations` | `scripts/common.py:260` | **Yes** — `client_mutation_id` as primary key is the idempotency `RQA-BR-007` rests on (U-AUTHORITY-09) |
> | `prs` | `scripts/common.py:221` | **Yes** — the persisted PR-fact cache is the sole source of the observed head used to detect a stale review (U-QUEUE-14) |
> | `human_requests` | `scripts/common.py:288` | **Yes** — the durable ask survives even though delivery does not (U-AUTHORITY-05, §6.2). It already carries `decision_actor` at `:311` and `rationale` at `:308` |
> | `approval_decisions` | `scripts/common.py:268` | **Yes, but not unchanged.** Its DDL declares exactly `id, job_id, repo, number, head_sha, policy_hash, status, mode, risk_score, created_at, expires_at` (`scripts/common.py:268-281`) — **no actor and no basis column**. That is `RQA-FR-013`'s unmet obligation, so this table needs a migration, not a copy |
> | `cadence` | `scripts/common.py:360` | **Yes** — one row per swept scope is what makes `RQA-NFR-004`'s per-scope isolation hold across a short-lived timer (U-QUEUE-07) |
> | `etags` | `scripts/common.py:204` | **Yes** — the 304 cache is one of `RQA-FR-020`'s three met reuse classes (U-RESILIENCE-12) |
> | `route_qualifications` | `scripts/common.py:282` | **No** — it is the store behind the binned route-material shadow lock (U-POLICY-12) |
> | `providers`, `circuit_breakers` | `scripts/common.py:254`, `scripts/common.py:348` | **Yes** — the breaker responsibility is `keep` for `RQA-FR-038` (U-RESILIENCE-02); only the manual reset command goes (U-DISPATCH-05) |
> | `canaries` | `scripts/common.py:315` | **Yes** — canary/lane gating is `rework`, not `bin` (U-DISPATCH-11) |
> | `cost_ledger` | `scripts/common.py:334` | **Yes as rows, no as a contract.** Its declared columns are `id` plus `recorded_at, job_id, repo, number, model, provider_family, kind, tokens, latency_ms` (`scripts/common.py:334-345`), and the insert writes the latter nine (`scripts/budget.py:223-231`): `kind` separates a reservation row from a spend row and **nothing separates an estimated spend from a measured one**, which is `RQA-FR-021`'s unmet obligation and, through it, `RQA-BR-001`'s and `RQA-BR-012`'s substrate edges (§5) |
> | `api_calls` | `scripts/common.py:211` | **Yes** — rate-limit consumption recorded from response headers is `RQA-FR-021`'s met half (U-DISPATCH-13) |

The table's own emphasis is preserved: `route_qualifications` **does not** carry over (its
responsibility, U-POLICY-12, is `bin` — see §2's row for `scripts/route_probe.py` and
`scripts/model_registry.py`, both `retired`/superseded by `rqa.supply`'s live probe with no shadow
lock). `approval_decisions` migrates, not copies — its DDL has neither an actor nor a basis column,
which is `RQA-FR-013`'s unmet obligation; the new estate carries this responsibility as
`rqa.escalation`'s `human_requests`/`escalation` record entry, which does record both (§2's rows
for `scripts/approval.py`, `scripts/approval_action.py`).

## 4. How `lane (issue #)` was assigned per part

### 4.1 Single-lane parts

P-06 → #2190. P-07 → #2191. P-08 → #2192. P-09 → #2193. P-10 → #2194. P-11 → #2195. P-13 → #2196
(placed no disposition unit at all — `components.md` §7 has zero `| P-13 |` rows; confirmed by the
lane's own handoff, which searched the table and found none).

### 4.2 Split-lane parts, with the exact unit partition each pair's handoffs state

- **P-02** — `#2199` (states/errors/entry-point half) owns U-QUEUE-11, U-RESILIENCE-11, U-DOCS-34,
  U-DOCS-47, U-DOCS-06, U-DISPATCH-03, U-DOCS-02, U-DISPATCH-07, U-DISPATCH-21, U-DISPATCH-23,
  U-QUEUE-12, U-RESILIENCE-17, U-DOCS-38, U-DOCS-20. `#2200` (steps/resume/rest half) owns
  U-DOCS-19, U-DOCS-54, U-DOCS-57, U-AUTHORITY-07, U-DISPATCH-17, U-DISPATCH-18, U-DOCS-56 — this
  exact partition is `#2199`'s own handoff's "Disposition units honoured by this half" section, and
  `#2200`'s handoff agrees on every unit named. `rqa-b5-resume` (a third P-02 commit) touches only
  `rqa/lifecycle/resume.py` and its own handoff states plainly "this defect touches no legacy
  estate unit" — it contributes no row here.
- **P-05** — `#2205` (routing half) owns U-DOCS-07, U-DOCS-27, U-DOCS-37, U-POLICY-10, U-POLICY-11,
  U-POLICY-12, U-POLICY-13, U-POLICY-14, U-RESILIENCE-02, U-RESILIENCE-03, U-VERDICT-09,
  U-DISPATCH-05. `#2206` (budget half) owns U-DISPATCH-12, U-DISPATCH-13, U-DOCS-15,
  U-RESILIENCE-01 — again the handoffs' own explicit per-unit table, cross-checked against each
  other (both list the same sixteen units split the same way).
- **P-01** — `#2197` and `#2198` are recorded jointly as `#2197, #2198` for every P-01 unit.
  Unlike P-02 and P-05, neither `.workmux/handoff-2197-P01.md` nor `handoff-2198-P01.md` carries a
  "disposition units honoured by this half" table (both files are 18-line Estate-classification-only
  documents with no `status:`/`touched:`/`verified:` header, unlike every other handoff read for
  this task) — they are cross-references of each other on every shared file (`#2197`: "the claim/release
  mechanism... is #2198's `lease.py`"; `#2198`: "read for reference only, per the lane's explicit
  instruction"), so a clean per-unit split cannot be reconstructed from what is on record. This is
  disclosed, not guessed around: see the handoff's own Disclosures section.

### 4.3 Pre-batch parts with no handoff on record

P-03 (`rqa/policy`), P-04 (`rqa/protocol`) and P-12 (`rqa/record`) were implemented before this
run's batch-1 handoff convention began — `git log --diff-filter=A` on each package's `__init__.py`
shows `576a6e9f4` (2026-09-11, P-03), `0d313897d` (2026-09-11, P-04) and `458c500d2` (2026-09-12,
P-12), all predating every handoff timestamp this Task was given. None of the 17 handoff files
named in this Task's prompt §6 discusses these three parts. Their rows above cite `lane: pre-batch
(P-0N, <sha>)` rather than an issue number, and their disposition/replacement columns are derived
from `architecture/components.md` §7 plus direct verification that the named `rqa.<part>.<module>`
file exists on disk (not from a handoff's own classification prose, because none exists). This is
the single largest documentation gap this task found — see §7's Unclaimed section, which lists
every P-03/P-04/P-12-owned file this applies to, and the handoff's Disclosures.

### 4.4 `scripts/dispatcher.py`'s cited-lane count, measured against the issue's "nine lanes"

`components.md` §7 places `scripts/dispatcher.py`'s units in **eight** distinct parts: P-01, P-02,
P-05, P-06, P-07, P-08, P-09, P-12 (verified by resolving every unit whose `Files:` line names
`scripts/dispatcher.py` through the placement table). Counting individual **implementing lanes**
rather than parts gives **ten** distinct issue numbers, since P-01, P-02 and P-05 each split across
two lanes (§4.2): `#2197, #2198, #2199, #2200, #2205, #2206, #2190, #2191, #2192, #2193`, plus P-12
pre-batch with no issue number. Neither figure is nine. Individual handoffs' own self-reported
counts vary too — `#2193` says "cited by nine other parts," `#2199` says "cited by eight other
parts" — neither matches the other, and neither matches this measurement. Reported as a finding,
not reconciled by picking whichever number sounds closest.

## 5. The seven legacy test files no disposition unit cites

Derived by resolving every one of the 162 units' `Files:` line (`gap/evidence/*.md`) against the
70 legacy test files and the 46 legacy `.py` scripts: seven test files resolve to none.
`git log --diff-filter=A` shows all seven were added in commit `62b1c503b` ("test(rqa): add
requirements counterexample suites and architecture reference", 2026-09-11) — **after** the gap
analysis's own revision anchor `9267b6308`, so the analysis never had the chance to assess them.
Each imports one or more superseded `scripts/` modules directly (confirmed by reading each file's
imports), so each is mapped in §2 via the replacing part's §1 module list rather than a unit id, as
row 2 of the issue's DoD permits:

| file | modules it imports | replacing part |
|---|---|---|
| `tests/test_counterexample_transitions.py` | `states` | P-02 |
| `tests/test_counterexample_authority.py` | `authority`, `github_mutate`, `policy`, `snapshot` | P-08 (primary), P-09, P-03 |
| `tests/test_counterexample_migration.py` | `config`, `policy`, `snapshot` | P-03 |
| `tests/test_counterexample_routing.py` | `model_registry`, `routing` | P-05 |
| `tests/test_counterexample_modes.py` | `modes`, `strategies` | P-06 |
| `tests/test_counterexample_schemas.py` | `config`, `policy`, `verdict` | P-04 (primary), P-03 |
| `tests/test_runner_adapters.py` | `config`, `ledger`, `route_probe`, `runners` | P-06 (primary), P-03, P-05, P-12 |

## 6. Documents and schemas — recorded, never deletion-authorized

Nine lane handoffs hand `onboarding/SKILL.md` "to `CUTOVER.md`", several saying "for deletion".
That is not what happens: `onboarding/SKILL.md` is in **#2214**'s impacted components and #2214
**rewrites** it. So `onboarding/SKILL.md`, `SKILL.md`, `OPERATORS.md`, `config.example.json` and
every `references/*.md` file a handoff handed to this document are recorded with disposition
**`rewritten`** and lane **#2214** (`references/model-fallbacks.md` is recorded **`kept`** — no
handoff found anything in it that needed rewriting beyond what `#2205`'s `rqa/supply/aliases.py`
already carries) — **never `retired`**, and their `replacement` cell says explicitly that this map
does not authorise their deletion.

`schemas/reviewer-verdict.json` and `schemas/author-triage.json` are **not** among the ten files
wave 3 (#2214) owns (its impacted-components list is exactly `SKILL.md`, `OPERATORS.md`,
`onboarding/SKILL.md`, `config.example.json`) and are not under `references/` either, so §5.4's
carve-out does not apply to them by name. They are recorded in §2 with the ordinary
unit-derived disposition (`U-VERDICT-02` rework/`rewritten`, `U-VERDICT-03` bin/`retired`) — but
their `replacement` cell still states plainly that deletion authority under this map is scoped to
`scripts/` and `tests/` alone, so a `retired` schema row is not read as permission either.

## 7. Unclaimed — a defect, not a default

"Any file no lane claimed is listed as unclaimed with the lane that should have — an unclaimed row
is a defect, not a default" (issue DoD). Two distinct kinds of unclaimed were found, and they are
not conflated:

### 7.1 Estate-classification-table omissions (code verified present; documentation gap only)

For every `(file, part)` row above whose `lane` is a real numbered issue, this task grepped that
issue's own `.workmux/handoff-*.md` for the file's path. Sixteen `scripts/` rows (counting each
part-share of a multiply-owned file separately) never appear anywhere in their own lane's handoff —
not merely absent from the Estate-classification table, absent from the whole document — even
though the corresponding `rqa/<part>/*.py` file was directly verified present on disk in this
worktree and the responsibility is otherwise well-evidenced by `components.md` §7 plus the lane's
own "What landed" prose about the *package*, just never tied back to the specific legacy file name:

| file | part | lane | unit(s) | verified replacement |
|---|---|---|---|---|
| `scripts/approval_action.py` | P-09 | #2193 | U-AUTHORITY-08 | `rqa/github/writes.py` (exists) |
| `scripts/assurance.py` | P-06 | #2190 | U-VERDICT-08 | `rqa/harness/panel.py` (exists) |
| `scripts/authority.py` | P-08 | #2192 | U-AUTHORITY-01 | `rqa/authority/gate.py` (exists) |
| `scripts/cli.py` | P-01 | #2197, #2198 | U-RESILIENCE-16 | `rqa/cli/composition.py` (exists) |
| `scripts/common.py` (P-01 share) | P-01 | #2197, #2198 | U-RESILIENCE-13 | `rqa/intake/identity.py` (exists) |
| `scripts/common.py` (P-06 share) | P-06 | #2190 | U-RESILIENCE-15 | `rqa/harness/bundle.py` (exists) |
| `scripts/common.py` (P-08 share) | P-08 | #2192 | U-RESILIENCE-10 | `rqa/authority/capability.py` (exists) |
| `scripts/config.py` | P-01 | #2197, #2198 | U-POLICY-07 | `rqa/intake/admission.py` (exists) |
| `scripts/dispatcher.py` (P-05 share) | P-05 | #2205, #2206 | U-DISPATCH-05, 12, 13 | `rqa/supply/budget.py`, `rqa/supply/spend.py` (exist) |
| `scripts/dispatcher.py` (P-08 share) | P-08 | #2192 | U-DISPATCH-09, 11 | `rqa/authority/gate.py` (exists) |
| `scripts/errors.py` | P-06 | #2190 | U-RESILIENCE-04 | `rqa/harness/panel.py` (exists) |
| `scripts/evidence.py` | P-06 | #2190 | U-VERDICT-07 | `rqa/harness/bundle.py` (exists) |
| `scripts/human_cli.py` (P-11 share) | P-11 | #2195 | U-AUTHORITY-06 | `rqa/escalation/decide.py` (exists) |
| `scripts/onboarding.py` | P-01 | #2197, #2198 | U-POLICY-07 | `rqa/intake/admission.py` (exists) |
| `scripts/shadow.py` (P-07 share) | P-07 | #2191 | U-VERDICT-19, 20 | `rqa/judgement/judge.py` (exists) |

The `P-08` (`#2192`) handoff is the sharpest instance: its own Estate-classification table lists
exactly six files (`onboarding/SKILL.md`, `references/contracts.md`, `tests/test_deterministic.py`,
`tests/test_github_auth.py`, `tests/test_phase1.py`, `tests/test_repairs.py`) and never names
`scripts/authority.py`, `scripts/common.py` or `scripts/dispatcher.py` at all — the three
production files whose units (`U-AUTHORITY-01`, `U-RESILIENCE-10`, `U-DISPATCH-09/11`)
`components.md` §7 places squarely in P-08. A further **31** legacy **test**-row omissions (the
companions of scripts files a handoff *did* name, sharing the identical unit — counted the same
way as the sixteen scripts rows above, one instance per `(file, part)` omission, so a file with two
unclaimed part-shares counts twice) show the same pattern one level down — `tests/test_advisory.py`
alongside `scripts/advisory.py` under `#2191`'s U-RESILIENCE-05, `tests/test_model_registry.py`
alongside `scripts/model_registry.py` under `#2205`'s U-POLICY-11, and so on. This document infers
those test files' disposition from their scripts-file counterpart (same unit, same lane, same
disposition) rather than escalating each as an independent unclaimed row, since the `Files:` line
in `gap/evidence/*.md` already names the pair as one responsibility. Round 1 undercounted this
list at 25 names for a stated 31 (`test_advisory.py` itself was the missing name, along with the
`(...share)` instances of four files cited under more than one part/lane); recounted and
enumerated in full, all 31 instances, 26 distinct files:

`test_advisory.py`, `test_approval_policy.py`, `test_assurance.py`, `test_budget_controls.py`
(#2205 share), `test_budget_controls.py` (#2206 share), `test_cadence.py`,
`test_config_onboarding.py`, `test_degradation.py`, `test_dispatch_flow.py` (#2190 share),
`test_dispatch_flow.py` (#2191 share), `test_dispatch_flow.py` (#2193 share),
`test_errors_states.py`, `test_fallback.py`, `test_fallback_recipes.py`, `test_lease.py`,
`test_lease_lifecycle.py`, `test_model_registry.py`, `test_modes.py`, `test_mutations.py`,
`test_onboarding.py`, `test_panel_policy.py`, `test_queue.py`, `test_route_config.py`,
`test_runtime_ops.py` (#2199 share), `test_runtime_ops.py` (#2205 share),
`test_runtime_ownership.py` (#2197, #2198 share), `test_runtime_ownership.py` (#2199 share),
`test_shadow_calibration.py`, `test_stale_head.py`, `test_state_persistence.py`,
`test_strategy_metadata.py`.

**None of this is a "nobody built it" defect** — every replacement module above was directly
verified present in this worktree. It is a documentation gap in the handoff record this task was
asked to reconcile against, and it is reported by name rather than silently smoothed over.

### 7.2 Whole parts with no handoff at all (P-03, P-04, P-12)

Every file `components.md` §7 places in P-03, P-04 or P-12 is, by construction, unclaimed under a
literal reading of "reconciled against every part Task's declared file classification (#2190-#2208)"
— none of the 17 handoffs this task was given covers these three parts (§4.3). Listed here in full
so a reader cannot mistake the gap for an oversight of this document rather than of the handoff
record:

- **P-03** (should have been claimed by whichever Task implemented `rqa/policy`, landed pre-batch
  at `576a6e9f4`): `scripts/cadence.py`, `scripts/common.py` (policy share), `scripts/config.py`,
  `scripts/onboarding.py`, `scripts/policy.py`, `scripts/snapshot.py`, `tests/test_cadence.py`,
  `tests/test_config_onboarding.py`, `tests/test_integration.py` (policy share),
  `tests/test_onboarding.py`, `tests/test_phase1.py`, `tests/test_policy_reload.py`,
  `tests/test_snapshot.py`, `tests/test_snapshot_pinning.py`.
- **P-04** (`rqa/protocol`, landed pre-batch at `0d313897d`): `scripts/verdict.py`,
  `tests/test_docs_contract.py`, `tests/test_repairs.py` (protocol share),
  `tests/test_verdict_fence.py`, `tests/test_verdict_schema.py`.
- **P-12** (`rqa/record`, landed pre-batch at `458c500d2`): `scripts/common.py` (record share),
  `scripts/dispatcher.py` (record share), `scripts/explain.py`, `scripts/history.py`,
  `scripts/ledger.py`, `scripts/logging_otel.py` (§7.3 — migrated and deleted by #2273),
  `scripts/risk.py` (record share),
  `scripts/shadow.py` (record share), `tests/test_dispatch_observability.py`,
  `tests/test_history.py`, `tests/test_integration.py` (record share), `tests/test_ledger.py`,
  `tests/test_logging.py`, `tests/test_logging_concurrency.py`, `tests/test_phase4.py` (record
  share), `tests/test_risk.py` (record share), `tests/test_runtime_ops.py` (record share),
  `tests/test_shadow_cli.py`.

### 7.3 `scripts/logging_otel.py` — the retained reference is now replaced (#2273)

Round 2 review (`F-B6-1`) correctly prevented this file's deletion while U-DISPATCH-19 had no
successor. Task #2273 paid that debt. `rqa.record.trace` now declares the exact fifteen
`JOB_EVENTS`, the nine-name `REQUIRED_JOB_EVENTS` subset, and rejects unregistered names before a
write. It also prevents caller fields from replacing `job`, `event`, or `at`.

The real lifecycle calls the published `rqa.record.append_trace` surface. A completed review emits
every required milestone; branch-specific paths emit lease, re-review, human-queue, mutation, and
safe-stop events. Route diagnostics are derived from the attempts that actually ran and capped at
four. The concurrency, crash-safety, registry, rejection, and completed-lifecycle properties are
exercised by `tests/test_rqa_record_trace.py` and `tests/test_rqa_lifecycle_steps.py`.

Those replacements justify deleting `scripts/logging_otel.py`; its map row is now `migrated` and
`deleted`. No legacy module is retained under `scripts/`.

## 8. Coverage debt paid by #2273

| deleted legacy test | exercised replacement |
|---|---|
| `tests/test_logging.py` | `tests/test_rqa_record_trace.py` covers complete-line appends, canonical serialization, and atomic replacement |
| `tests/test_logging_concurrency.py` | `tests/test_rqa_record_trace.py` races eight writers and proves distinct attempt numbers plus valid JSON |
| `tests/test_dispatch_observability.py` | `tests/test_rqa_record_trace.py` pins the exact registries and rejection path; `tests/test_rqa_lifecycle_steps.py` proves a completed review emits every required milestone |

## 9. The 44 disposition units whose evidence cites no resolvable file (issue says 55; round 1 said 46 and was wrong — measured again, corrected)

**Round 1's methodology did not match what it claimed, and the corrected count is 44, not 46.**
Round 1's prose said each citation was attributed "to every `U-<AREA>-NN` id named in that same
row's `evidence` cell" for register rows, and "to the unit whose heading precedes it" for evidence
cells — but round 1's *code* read `evidence` **and** `notes` together for register rows (matching
`gap/validate.py:406`'s own `cited_path_line_pairs(evidence) + cited_path_line_pairs(notes)`
correctly), while its evidence-cell attribution used the citation's own `line` field as if it were
an offset **into the cluster file**, when that `line` is the offset into the **cited file**
(`approval_action.py:152-154` means line 152 of `approval_action.py`, not line 152 of
`gap/evidence/docs.md`). That bug misattributed every one of the ten evidence-cell citations —
`U-DOCS-08` (codex's specific flag) was one of six units wrongly included from it, and six correct
units (`U-DOCS-05` twice over, `U-POLICY-01`, `U-POLICY-06`, `U-QUEUE-02`, `U-VERDICT-06`) were
missing.

**Corrected methodology**, reproducible by a reader:

1. Run `gap/validate.py`'s check 3 machinery: `check_register_staleness` and
   `check_evidence_staleness` populate `excluded_register_citations` (62 entries) and
   `excluded_evidence_citations` (10 entries) — 72 total, unchanged from round 1.
2. **Register citations** (in `gap/register/{br,fr,nfr}.md`): for each `(class, requirement_id,
   path, line)`, find that requirement's row and take the union of every `U-<AREA>-NN` token
   found anywhere in its `evidence` **and** `notes` cells (both, matching step 1's own extraction;
   this part of round 1 was correct). A register row pools several units against several citations
   in one flat cell with no positional link between which citation belongs to which unit, so this
   is the least precise attribution the row's own structure allows — never finer. **40 units.**
3. **Evidence-file citations** (in `gap/evidence/*.md`): for each `(cluster, path, line)`, find the
   **literal textual occurrence** of the substring `f"{path}:{line}"` inside that cluster file (not
   the `line` value read as an offset — the fix), then take the last `### U-<AREA>-NN` heading
   whose position precedes that occurrence. One of the ten occurrences (`requirements-specification.
   md:1240` at `gap/evidence/policy.md:35`) sits in the cluster's own methodology preamble, before
   any unit heading — genuinely unattributable to a single unit, and left out of the count honestly
   rather than forced onto whichever heading happens to be nearest. The other nine resolve to
   **7 units**: `U-QUEUE-02`, `U-POLICY-01`, `U-POLICY-02`, `U-POLICY-06`, `U-VERDICT-06`,
   `U-DOCS-05` (twice), `U-DOCS-24`.
4. Union the two sets: **44 distinct units**, not 55, not round 1's 46.

Every one of the 44 already has a resolvable `Files:` line in `gap/evidence/*.md` (verified: all
162 units' `Files:` lines resolve to real paths on disk) — the shorthand limitation is confined to
inline prose citations, never to the formal per-unit file attribution the rest of this map is built
from. Each is listed below with the file(s) the map assigns it via that resolvable `Files:` line:

| unit | cluster | file(s) the map assigns it |
|---|---|---|
| U-AUTHORITY-01 | authority | scripts/authority.py |
| U-AUTHORITY-03 | authority | scripts/approval_evaluate.py, tests/test_approval_policy.py |
| U-AUTHORITY-06 | authority | scripts/human_cli.py |
| U-AUTHORITY-07 | authority | scripts/human_cli.py, tests/test_human_execution.py |
| U-AUTHORITY-08 | authority | scripts/approval_action.py, scripts/github_mutate.py, tests/test_mutations.py, tests/test_approval_policy.py |
| U-AUTHORITY-11 | authority | scripts/github_rest.py, tests/test_rest_reader_surface.py, tests/test_rest_cache.py |
| U-DISPATCH-01 | dispatch | scripts/dispatcher.py |
| U-DISPATCH-07 | dispatch | scripts/dispatcher.py, tests/test_runtime_ops.py, tests/test_runtime_ownership.py |
| U-DISPATCH-09 | dispatch | scripts/dispatcher.py |
| U-DISPATCH-13 | dispatch | scripts/dispatcher.py |
| U-DISPATCH-16 | dispatch | scripts/dispatcher.py, tests/test_dispatch_flow.py |
| U-DISPATCH-17 | dispatch | scripts/dispatcher.py |
| U-DISPATCH-18 | dispatch | scripts/dispatcher.py |
| U-DISPATCH-20 | dispatch | scripts/dispatcher.py |
| U-DISPATCH-24 | dispatch | scripts/planner.py, tests/test_planner.py |
| U-DOCS-01 | docs | SKILL.md, references/contracts.md, references/classification.md |
| U-DOCS-05 | docs | SKILL.md, OPERATORS.md |
| U-DOCS-09 | docs | references/contracts.md |
| U-DOCS-22 | docs | tests/test_docs_contract.py |
| U-DOCS-24 | docs | tests/conftest.py |
| U-DOCS-48 | docs | tests/test_repairs.py |
| U-DOCS-49 | docs | tests/test_repairs.py |
| U-POLICY-01 | policy | scripts/config.py, tests/test_config_onboarding.py, tests/test_onboarding.py |
| U-POLICY-02 | policy | scripts/config.py, tests/test_config_onboarding.py |
| U-POLICY-04 | policy | scripts/policy.py, tests/test_policy_reload.py |
| U-POLICY-06 | policy | scripts/config.py, scripts/onboarding.py, onboarding/SKILL.md, tests/test_config_onboarding.py, tests/test_onboarding.py |
| U-POLICY-08 | policy | scripts/strategies.py, tests/test_strategy_metadata.py |
| U-POLICY-09 | policy | scripts/modes.py, tests/test_modes.py |
| U-POLICY-12 | policy | scripts/model_registry.py, scripts/route_probe.py, tests/test_model_registry.py |
| U-QUEUE-02 | queue | scripts/queue.py, tests/test_queue.py |
| U-RESILIENCE-01 | resilience | scripts/budget.py, tests/test_budget_controls.py |
| U-RESILIENCE-03 | resilience | scripts/fallback.py, tests/test_fallback_recipes.py |
| U-RESILIENCE-06 | resilience | scripts/ledger.py, tests/test_ledger.py |
| U-RESILIENCE-07 | resilience | scripts/explain.py |
| U-RESILIENCE-12 | resilience | scripts/common.py |
| U-RESILIENCE-16 | resilience | scripts/cli.py |
| U-VERDICT-01 | verdict | scripts/verdict.py, tests/test_verdict_fence.py |
| U-VERDICT-02 | verdict | scripts/verdict.py, schemas/reviewer-verdict.json, tests/test_verdict_schema.py |
| U-VERDICT-04 | verdict | scripts/findings.py |
| U-VERDICT-06 | verdict | scripts/checks.py, tests/test_checks_vocabulary.py |
| U-VERDICT-07 | verdict | scripts/evidence.py |
| U-VERDICT-11 | verdict | scripts/panel.py |
| U-VERDICT-12 | verdict | scripts/panel.py |
| U-VERDICT-16 | verdict | scripts/risk.py, tests/test_approval_evidence.py |


## 10. Wave-3 out-of-scope reminder

Nothing in this document authorises editing `<skill>/scripts/**`, any pre-existing
`<skill>/tests/*.py` (including `tests/run_all.py`), `<skill>/architecture/**`, or `<skill>/SKILL.md`
/ `OPERATORS.md` / `onboarding/SKILL.md` / `config.example.json`. This lane touched only this file
and `tests/test_cutover_map.py`.
