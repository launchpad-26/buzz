# RQA gap evidence — docs cluster

Evidence base for the `docs` cluster: `SKILL.md`, `OPERATORS.md`, `references/**`,
and the cross-cutting test suites and harness (`tests/conftest.py`,
`tests/run_all.py`, `tests/test_deterministic.py`, `tests/test_docs_contract.py`,
`tests/test_e2e_outcomes.py`, `tests/test_integration.py`,
`tests/test_phase1.py`..`test_phase4.py`, `tests/test_regression.py`,
`tests/test_repairs.py`) — the 18 files `gap/clusters.md` assigns to `docs`.
Revision `9267b6308`. Paths are relative to
`launchpad/skills/review-queue-automation/`, per `gap/methodology.md`.

This document records what the code does and cites it; it assigns no gap
degree, root cause or disposition (wave 2 / wave 3).

**Wording convention, round 3.** A row that claims **product behaviour**
implemented elsewhere in the tree cites the `scripts/*.py` line that decides it,
per methodology §3 rule 1, whichever cluster the test happens to sit in. A row
whose true subject is **what one of this cluster's own assessed test files
asserts and covers** states that plainly ("`test_X.py` asserts and covers...")
and cites only that test file. Two units whose content silently vanished in the
round-2 delta — snapshot pinning and budget reserve — are restored here
(U-DOCS-14, U-DOCS-15). Two findings carried a disputed 1-vs-2-seat question
pending a human ruling; the maintainer has ruled on both (`DOCS-JOBID-COVERAGE`,
`DOCS-RISK-SPLIT`) and neither carries a `PENDING-HUMAN` marker any longer.
U-DOCS-25's job-id claim was reworded per that ruling to name only the two axes
the suite actually varies. The risk-banding/protected-trigger split the ruling
decided is applied as U-DOCS-43 (kept, numeric risk-banding) and U-DOCS-58
(appended at the end of the file, protected-trigger detection); the separate
U-DOCS-43/U-DOCS-44 risk-banding/approval-gate boundary is unaffected.

---

### U-DOCS-01 — Authorization/refusal and single-transport GitHub boundary

Files: SKILL.md, references/contracts.md, references/classification.md
Rationale: all three restate one shared boundary — the agent's own GitHub-facing
action set is capped to advisory comment and finding-issue creation, the three
review mutations are named, fixed templates, and reads/mutations are split into
allowlisted transports — so a change to that boundary in one forces the same
change in the other two.

Read transport allowlisting (SKILL.md:33-37, references/contracts.md:20-31,39,
references/classification.md:16,26) is genuine product behaviour, but no
requirement in the frozen specification addresses which internal transport a
read or mutation travels through — RQA-NFR-030 concerns the scope of the held
token, not the code path — so the observation is recorded here rather than
forced into a row. The behaviour itself is cited: an operation outside the
mutation allowlist is refused by `github_mutate.post` (`scripts/github_mutate.py:224-225`,
"unsupported mutation operation"), which is how an unnameable operation becomes
a hard stop rather than a hand-built call.

| claim | evidence | requirements |
| --- | --- | --- |
| The APPROVE mutation is executed only by loading a persisted, non-expired decision record from SQLite by ID — never from caller-supplied JSON or model output — and is refused when no such record exists. | SKILL.md:26-30, references/contracts.md:35-38, scripts/approval_action.py:39-46, scripts/approval_action.py:152-154 | RQA-NFR-017, RQA-NFR-032 |
| The three **review** mutations SKILL.md scopes this claim to ("the only GitHub review mutations are fixed internally", SKILL.md:242-244) each have a hard-coded event in their GraphQL template rather than an accepted variable (`add_comment_review`->COMMENT, `approve_review`->APPROVE, `request_changes_review`->CHANGES_REQUESTED); `github_mutate.MUTATIONS` (scripts/github_mutate.py:99-108) carries nine entries in total — the three review mutations plus six non-review ones (`create_issue`, `add_labels`, `request_review`, `thread_reply`, `add_assignee`, `remove_assignee`), none of which fixes an event because none posts a formal review. | SKILL.md:242-244, scripts/github_mutate.py:99-108, scripts/github_mutate.py:112-113 | RQA-NFR-032 |

---

### U-DOCS-02 — Pipeline entrypoint and escalation-on-`human_required` documentation

Files: SKILL.md, OPERATORS.md
Rationale: SKILL.md's "Run the pipeline"/"Escalation" sections and OPERATORS.md
§5 document the same single-command lifecycle entrypoint and the same
stop-on-`human_required` behaviour; a change to one is a change to the other.

| claim | evidence | requirements |
| --- | --- | --- |
| The five commands SKILL.md/OPERATORS.md walk through in the core running-the-pipeline narrative (`sweep`, `tick`, `dispatch-one`, `status`, `recover`) are a documented subset, not the complete set: `dispatcher.main` registers nine subcommands in total (also `health`, `retention`, `cooldown-reset`, `backup`), and every one is documented somewhere in this pair — the four non-core commands are covered by OPERATORS.md §11's maintenance walkthrough (`OPERATORS.md:466-505`; `recover` is already in the core five, not a fourth non-core command). | SKILL.md:39-63, OPERATORS.md:168-201,466-505, scripts/dispatcher.py:2191,2198,2209,2214,2219,2220,2222,2232,2237 | RQA-NFR-006 |
| On `human_required` the documented behaviour matches the code's own stop-and-return shape: a transition to `human_required` is immediately followed by a structured `warning` log and a `return` with no further action, e.g. the missing-evidence escalation path. | SKILL.md:83-86, OPERATORS.md:187-190, scripts/dispatcher.py:360-369 | RQA-FR-026, RQA-BR-013 |

---

### U-DOCS-03 — Entry-point index: operator-invoked commands vs. internal modules

Files: OPERATORS.md

OPERATORS.md's own text settles this, per `gap/methodology.md` §2.2: the second
script table at §14 sits under an explicit disclaimer ("**not** operator
commands ... taking the step outside the state-directory ownership boundary
that `dispatcher.py` enforces"), which defeats E3 for all twelve of its rows; the
first table at §14 maps seven scripts to numbered runbook sections that *do*
instruct an operator to run them (E3/E4). The disclaimed table also states that
two of its twelve members (`github_mutate.py`, `approval_action.py`) write to
GitHub, so "internal, not an operator command" is a reachability disclaimer, not
a claim of being side-effect-free. No row of the disclaimed table is used as E3
evidence anywhere in this file.

| claim | evidence | requirements |
| --- | --- | --- |
| The seven scripts an operator is instructed to run locally are enumerated in one runbook-linked table, kept separate from a second, disclaimed table of twelve internal modules. | OPERATORS.md:546-579 | RQA-NFR-006 |

---

### U-DOCS-04 — Approval modes and per-activity configurable authority ladder

Files: SKILL.md, OPERATORS.md, references/contracts.md
Rationale: SKILL.md's "Approval modes & authority"/"Configurable authority", OPERATORS.md §3, and contracts.md's "Severity and authority" section document one conjunctive authority model — `approval.mode` and `authority.<activity>` both gate independently, and request-changes has its own corroboration/authority/gate sequence — so the three are one responsibility.

| claim | evidence | requirements |
| --- | --- | --- |
| `authority.mode_for` resolves per-activity mode by precedence (repo override, then activity-level key, then a global default, then fail-closed `disabled`); `can_act` additionally requires a passed hard gate for a mutating activity and treats `shadow`/`human_escalation` as never-acting regardless of the hard gate. Independently, `approval_evaluate.evaluate`'s `live` branch denies on a protected trigger or any failed gate before it ever persists an eligible decision. | SKILL.md:130-153,220-236, OPERATORS.md:113-127, scripts/authority.py:97-121,128-146, scripts/approval_evaluate.py:276-288 | RQA-NFR-017, RQA-NFR-026 |
| `action_gate.request_changes_gate` denys independently on missing `request_changes` authority, a stale head, an unverified blocker, insufficient blocker evidence, insufficient assurance, or an absent/failed final revalidation — six independent fail-closed deny-sites before a `CHANGES_REQUESTED` action is allowed (the two adjacent blocker denials are `scripts/action_gate.py:72-75`; full gate `scripts/action_gate.py:63-83`). | references/contracts.md:108-119, scripts/action_gate.py:63-83 | RQA-NFR-017, RQA-FR-009 |

---

### U-DOCS-05 — Human decisions, execution states, and the human-approval CLI

Files: SKILL.md, OPERATORS.md
Rationale: SKILL.md's "Human decisions & execution states"/"Human approval CLI" and OPERATORS.md §6 describe the same decision-record vocabulary and the same CLI, executing through the same guarded resume path.

| claim | evidence | requirements |
| --- | --- | --- |
| `approval.enqueue` persists a decision record keyed by repo/number/head_sha/policy_hash/job_id (deduplicating an identical request rather than doubling it). `approval.set_execution_state` restricts the execution-state field to `execution_pending`/`executed`/`execution_failed`/`cancelled`/`withdrawn` and rejects anything else; this helper's only callers at `9267b6308` are tests, so the accepted-state vocabulary is established as a suite-covered contractual fact, not a reached product invariant. | SKILL.md:281-289, OPERATORS.md:257-266, scripts/approval.py:85-131,298-309 | RQA-FR-013 |
| `approval.decide` only records the decision and "does not mutate a PR itself" by its own docstring; `human_cli._cmd_resume` drives execution — it reads the **live** PR head by default (`live_head_sha`, scripts/human_cli.py:50-59) and revalidates against that live head and the current policy hash before transitioning to `approval_revalidation`, then runs the same guarded APPROVE executor as the automatic path (approval_action.py:152-154 no-decision refusal; github_mutate.py:402-406 REST verification). A caller-supplied `current_head_sha` or the explicit `allow_recorded_head` "recorded (unverified)" escape is the well-documented exception, not the default (scripts/human_cli.py:88-112), and either still refuses on a head mismatch. | SKILL.md:155-165, OPERATORS.md:249-266, scripts/approval.py:233-248, scripts/human_cli.py:50-59,88-124, scripts/approval_action.py:152-154, scripts/github_mutate.py:402-406 | RQA-FR-013, RQA-BR-011 |

---

### U-DOCS-06 — Documented job lifecycle / state model

Files: SKILL.md, references/contracts.md
Rationale: SKILL.md's "Lifecycle" section and contracts.md's "Job identity and states" section describe the identical state sequence and its supersession rule.

| claim | evidence | requirements |
| --- | --- | --- |
| The documented state sequence (`detected` through `preflight`, then `held` or `evidence`, on to `assurance`, then `degraded_draft` or `adjudication`, then `action`, then `completed`, with `retryable`/`human_required`/`superseded` sinks) matches the transition table's own state set and its `can_transition` guard, which rejects any pair not present in that table. | SKILL.md:293-297, references/contracts.md:9-11, scripts/states.py:78-79,118,121-126 | RQA-FR-016 |
| A changed head marks every older nonterminal job of the same PR `superseded` — `queue._supersede_old` updates each nonterminal job's status to `superseded` with reason `"head changed"` (`scripts/queue.py:163-174`). | references/contracts.md:11, scripts/queue.py:163-174 | RQA-FR-016, RQA-BR-007 |

---

### U-DOCS-07 — Model routing and fallback policy documentation

Files: SKILL.md, references/model-fallbacks.md, OPERATORS.md
Rationale: SKILL.md's "Reasoning strategies & model routing", the fallback-lane table in model-fallbacks.md, and OPERATORS.md §4 all describe the one subscription-first routing ladder and its qualification probe.

The documented default two-reviewer fallback table (native Claude/Codex
preferred, then named OpenRouter slugs — references/model-fallbacks.md:1-15) is
a policy artefact only: nothing in `scripts/` enforces these specific model
names; `routing.py`'s ladder operates over whatever `models.primary`/
`models.secondary` configuration supplies.

| claim | evidence | requirements |
| --- | --- | --- |
| `routing.resolve_route` walks configured rungs in order, skips a rung already attempted (fallback-loop guard) or currently cooled down (`is_route_available`), and only reaches the `"human"` rung when every configured rung is exhausted — never substituting an alternative that was not explicitly configured. | SKILL.md:264-269, scripts/routing.py:140-183 | RQA-NFR-009, RQA-FR-023, RQA-FR-024 |
| `route_probe.probe_route` classifies each candidate as `ok`/`transport_failed`/`verdict_rejected`/`timeout`/`config_error` from a real subprocess invocation and a real verdict-schema check (`scripts/route_probe.py:97-107`), and `persist_probe_result` records the outcome as real transport health into the `providers` table (`scripts/route_probe.py:113-114`), called on the main probe path (`scripts/route_probe.py:194-195`) — a failing probe result is a persisted, real transport-health signal, not read from history. | OPERATORS.md:148-158, scripts/route_probe.py:97-107,113-114,194-195 | RQA-FR-024 |

---

### U-DOCS-08 — Required/achieved assurance computation documentation

Files: SKILL.md, references/contracts.md
Rationale: SKILL.md's "Assurance, evidence, uncertainty" and contracts.md's "Assurance router" describe the identical achieved/required-assurance computation.

| claim | evidence | requirements |
| --- | --- | --- |
| `risk.compute_assurance` weights achieved assurance by evidence completeness times a reviewer-completion ratio, halves both when evidence is not fresh, adds residual uncertainty for incomplete evidence/disagreement/unknown outcome, and requires `completeness >= 0.8` and `uncertainty <= 0.2` with no blocker before `can_approve` is true — never an average of failure-mode severities, which `effective_risk` (U-DOCS-43) computes separately as a maximum. | SKILL.md:271-276, scripts/risk.py:392-415 | RQA-BR-008, RQA-BR-014 |

---

### U-DOCS-09 — Panel completeness, `MISSING_EVIDENCE`, and stale-verdict clearing documentation

Files: references/contracts.md

| claim | evidence | requirements |
| --- | --- | --- |
| `panel.run_panel`'s `complete` condition requires the signal count, filled-slot count, and counted-mode-result length to each meet the profile's required slot count; a fresh attempt clears every prior slot file first, so an escalated re-attempt can never consume a stale, lower-profile verdict left from an earlier try. | references/contracts.md:63, scripts/panel.py:626-629,746-749 | RQA-FR-010, RQA-FR-011 |

---

### U-DOCS-10 — Policy-as-data validation and atomic snapshot activation documentation

Files: SKILL.md

| claim | evidence | requirements |
| --- | --- | --- |
| `snapshot.build_snapshot` raises `SnapshotError` before returning a `RuntimeSnapshot` when the supplied `validate_policy` callback reports any issue, so an invalid candidate is rejected before it can become the active payload; the schema/semantic validation, versioning and content-hashing SKILL.md describes are what `validate_policy` and `content_hash` (policy cluster) supply into that same call. | SKILL.md:246-253, scripts/snapshot.py:134-146 | RQA-NFR-005, RQA-NFR-018 |

---

### U-DOCS-11 — Shadow backtest / current-head calibration contract

Files: SKILL.md, OPERATORS.md
Rationale: SKILL.md's "Shadow backtest" and OPERATORS.md §8 describe the identical read-only calibration mechanism and the same gate-fails-closed behaviour.

| claim | evidence | requirements |
| --- | --- | --- |
| `shadow.shadow_cfg` (module function, `def` at scripts/shadow.py:183) overrides `approval.mode` to `"shadow"` on an in-memory clone of the config only (nothing is written back to source config). Each product caller reaches evaluation with that forced clone: `backtest` builds `scfg = shadow_cfg(cfg)` at scripts/shadow.py:471 and `current_shadow` passes `shadow_cfg(cfg)` into `evaluate_before_merge` at scripts/shadow.py:606-609. `evaluate_before_merge` always constructs an explicit `ApprovalEvidence` before calling `evaluate` and returns a plain dict — no decision record is persisted in its body and no GitHub transport is imported by this module. | SKILL.md:167-218, OPERATORS.md:298-406, scripts/shadow.py:183-194,306-325,471,606-609 | RQA-FR-011, RQA-FR-037 |
| `shadow.historical_evidence` builds the five gates needing explicit evidence (`bounded_change`, `audit_writable`, `assurance_met`, `revalidation_ok`, `rate_limit_ok`) strictly from what the historical sample and a supplied assessment can prove, so an absent value fails the corresponding gate closed rather than defaulting it open. | SKILL.md:180-192, OPERATORS.md:366-384, scripts/shadow.py:214-281 | RQA-FR-010, RQA-NFR-010 |

---

### U-DOCS-12 — Canary gating documentation

Files: SKILL.md, OPERATORS.md
Rationale: SKILL.md's brief mention of operator-approved canaries and OPERATORS.md §7's full canary table describe the same two-gate mechanism and the same table-over-config-key precedence.

| claim | evidence | requirements |
| --- | --- | --- |
| Continuous dispatch on a lane stays gated until that lane's canary is approved; the SQLite `canaries` table is authoritative and the config key (`incoming_canary_approved`/`author_canary_approved`) is only the fallback used when no table row exists. | SKILL.md:31-32, OPERATORS.md:273-290, scripts/dispatcher.py:1677,1801-1805 | RQA-NFR-026 |

---

### U-DOCS-13 — Author-triage isolated-worktree claim (documentation with no implementing code)

Files: SKILL.md, references/contracts.md, references/classification.md
Rationale: all three describe the identical absent behaviour — the author-triage lane fixing a valid finding "in an isolated worktree" — so they are judged as one documentation artefact per `gap/methodology.md` §2.4's own worked example.

**No code implements this behaviour at `9267b6308`.** `scripts/worktree.py` defines `create`/`commit`/`push`/`clean` (`scripts/worktree.py:102,170,195,229`) and a `__main__` CLI (`scripts/worktree.py:262,265`), but no file under `scripts/` imports or calls it — the only occurrence in another script is a comment (`scripts/runners.py:120`) — and `dispatcher.py` treats the author-triage lane as a generic `lane` parameter (`scripts/dispatcher.py:2162`) gated only by `author_canary_approved` (`scripts/dispatcher.py:1797-1800`), never invoking `worktree`. The only callers are `tests/test_worktree.py:20` and `tests/test_integration.py:133`, which `gap/methodology.md` §2.3 holds confers no reachability. Per §2.2 its only documentation citation is the disclaimed inventory row at `OPERATORS.md:575` (U-DOCS-03), not an instruction to run it — so E3 fails too, and no other entrypoint class reaches it either.

| claim | evidence | requirements |
| --- | --- | --- |
| SKILL.md and references/contracts.md/classification.md describe the author-triage lane fixing valid findings "in an isolated worktree" and list "set up and remove isolated author worktrees" as a Script-class action, but no code path from a product entrypoint reaches `scripts/worktree.py`'s create/commit/push/clean functions; the only callers are two test modules. | SKILL.md:75-76, references/contracts.md:16, references/classification.md:21, scripts/worktree.py:102,170,195,229,262,265, scripts/dispatcher.py:2162,1797-1800, scripts/runners.py:120 | RQA-NFR-020, RQA-BR-006, RQA-FR-017, RQA-FR-018 |

---

### U-DOCS-14 — Snapshot-pinning guarantee documentation

Files: references/runtime-ops.md

| claim | evidence | requirements |
| --- | --- | --- |
| `config.policy_defaults` derives the inline `policy` section verbatim from the repo-local config (authority, approval thresholds, risk bands, protected triggers), falling back on the same defaults `onboarding_defaults` uses so a derived policy can never fail validation and silently unpin a job; the derived policy is what `dispatcher.resolve_snapshot` pins via `build_snapshot` (`scripts/dispatcher.py:1591`). A config with no `policy` section is still dispatchable but is reported as unpinned with a reason (`scripts/dispatcher.py:1593`, `{"pinned": false, "reason": ...}`), never silently treated as pinned. | references/runtime-ops.md:96-124, scripts/config.py:366-403, scripts/dispatcher.py:1591,1593 | RQA-NFR-005 |

---

### U-DOCS-15 — Budget reserve-before-spend and rate-limit control documentation

Files: references/runtime-ops.md

| claim | evidence | requirements |
| --- | --- | --- |
| `dispatcher._reserve_budget` calls `budget.reserve` before `drive(minimum, assess, ...)` runs the panel, and its own comment states the ordering explicitly ("nothing above this line costs a model call, so a refusal here downgrades BEFORE any budget can be exceeded", `scripts/dispatcher.py:1358-1361`); the caller then applies the returned downgrade by returning early via `_budget_refused` when `reservation.allowed` is false (`scripts/dispatcher.py:1363-1365`) rather than proceeding to spend. `reserve` itself refuses on a breached limit, an unproven REST floor, the retry ceiling, or the concurrency cap (`scripts/budget.py:327-393`, projection-and-refuse `scripts/budget.py:410-420`). After the panel call inside `assess` (`scripts/dispatcher.py:1316`), `budget.record_spend` is charged with `result.get("budget_tokens") or reserved_tokens` — the reservation as an upper bound, never a measured count (`scripts/dispatcher.py:1323-1330`, `scripts/budget.py:217-231`). A reached budget is therefore respected before spend, never exceeded and then noticed. | references/runtime-ops.md:127-137, scripts/dispatcher.py:1358-1365,1313-1330, scripts/budget.py:217-231,327-393,410-420 | RQA-BR-012, RQA-FR-021 |

---

### U-DOCS-16 — "Why did this PR get this outcome" explain-procedure documentation

Files: SKILL.md, OPERATORS.md
Rationale: SKILL.md's short pointer and OPERATORS.md §9's full numbered procedure document the same read-only `explain.py` reconstruction.

| claim | evidence | requirements |
| --- | --- | --- |
| `explain.main`'s body calls only `resolve_or_onboarding`, `make_state`, `revisions`, `explain` and `render_explanation` — no `github_rest`/`github_query`/`github_mutate` import and no model-runner call anywhere in the module (`scripts/explain.py:47-81`) — matching the documented "no GitHub call, no model call, no change to the job" claim empirically rather than by module docstring alone. | SKILL.md:109-119, OPERATORS.md:409-442, scripts/explain.py:47-81 | RQA-FR-012 |

---

### U-DOCS-17 — Job-trace event schema and redaction documentation

Files: references/runtime-ops.md

| claim | evidence | requirements |
| --- | --- | --- |
| The documented event set (`queueing`, `preflight`, `lease_acquired`, ..., `safe_stop`) matches `logging_otel.JOB_EVENTS`, and the documented required subset matches `logging_otel.REQUIRED_JOB_EVENTS` — the vocabulary a single command needs in order to reconstruct a job's route, plan, budget, decision and external actions. | references/runtime-ops.md:42-64, scripts/logging_otel.py:54-64,75-78 | RQA-FR-012 |

The redaction allowlist exempting `cost.tokens`/`cost.tokens_reserved` from the
general `token`-substring redaction rule (`scripts/logging_otel.py:90-91`,
documented at `references/runtime-ops.md:77-84`) does not itself bear on any
credential-inventory requirement (RQA-NFR-024/025/030 concern what a held
credential may scope to, not which log attribute is masked) and no other
requirement's text covers attribute-shaped redaction, so it is recorded here as
an observation rather than forced into the row: the allowlist is closed and
explicit, and its effect (a legitimate metric is not silently eaten by the
redaction rule) is what keeps a job-trace event usable as reconstruction
evidence.

---

### U-DOCS-18 — Retention purge-with-manifest guarantee documentation

Files: references/runtime-ops.md, OPERATORS.md
Rationale: references/runtime-ops.md §4 and OPERATORS.md §11 document the identical `retention` command and its manifest-before-delete invariant.

| claim | evidence | requirements |
| --- | --- | --- |
| `dispatcher.retention_sweep` writes the `retention_manifest` ledger entry (naming, sizing and SHA-256-hashing every artifact) *before* deleting anything (`scripts/dispatcher.py:1986-2001`), and is a dry run unless `apply=True`; the `jobs` row, every `ledger_entries` row, and `mutations`/`approval_decisions`/`human_requests` are never touched by the purge — only artifact bytes under `jobs/<job-id>/` are removed. | references/runtime-ops.md:210-230, OPERATORS.md:466-505, scripts/dispatcher.py:1986-2001 | RQA-BR-003 |

---

### U-DOCS-19 — Recovery: lease release without replay documentation

Files: references/runtime-ops.md, OPERATORS.md
Rationale: references/runtime-ops.md §4 and OPERATORS.md §10 document the identical `recover` command and its lease-release-without-replay invariant.

| claim | evidence | requirements |
| --- | --- | --- |
| `dispatcher.recover_interrupted` releases only leases recorded in this state directory via the normal `_lease_release` helper, safe-stops a job whose status is transitionable to `safe_stop` (`scripts/dispatcher.py:1822-1843`), and separately rescues jobs stranded with no lease row by selecting `ACTIVE_WORKER_STATUSES` jobs without a lease and safe-stopping them (`scripts/dispatcher.py:1852-1869`); `ACTIVE_WORKER_STATUSES` itself excludes the states legitimately waiting on somebody else — `detected`, `human_approval_pending`, `human_required`, `degraded_draft`, `held`, `retryable` (`scripts/dispatcher.py:1871-1877`). It never replays a model call. | references/runtime-ops.md:232-247, OPERATORS.md:446-462, scripts/dispatcher.py:1822-1843,1852-1869,1871-1877 | RQA-NFR-010 |

---

### U-DOCS-20 — Backup, health, and cooldown-reset: local-only maintenance commands documentation

Files: references/runtime-ops.md, OPERATORS.md
Rationale: `backup`, `health` and `cooldown-reset` share one property this document needs about them — none reads or writes a pull request — and are grouped against retention (U-DOCS-18) and recovery (U-DOCS-19); each body is cited directly below.

| claim | evidence | requirements |
| --- | --- | --- |
| `backup` (`sqlite3.Connection.backup`, consistent under WAL — `scripts/dispatcher.py:2032-2053`), `health` (database/disk/breaker/budget status — `scripts/dispatcher.py:2056-2075`), and `cooldown-reset` (clears `circuit_breakers`/provider cooldowns — `scripts/dispatcher.py:2012-2029`) are each local-state-directory operations — none imports or calls a GitHub transport — closing the account of all nine `dispatcher.main` subcommands this cluster's documentation covers (sweep/tick/dispatch-one/status/recover in U-DOCS-02; retention in U-DOCS-18; recover in U-DOCS-19; backup/health/cooldown-reset here). | references/runtime-ops.md:193-262, OPERATORS.md:466-505, scripts/dispatcher.py:2012-2029,2032-2053,2056-2075 | RQA-BR-003 |

---

### U-DOCS-21 — Strategy-metadata field-liveness audit documentation

Files: references/runtime-ops.md

| claim | evidence | requirements |
| --- | --- | --- |
| `strategies.Strategy` declared ten fields; five that nothing read have been removed, while `disagreement_handling` was kept and given a consumer — every surviving field has a runtime reader named in the documented consumer table. The "dedicated audit" that scans `scripts/` for a reader of each declared field exists, but as a **CI-time test, not a product code path** — it lives as `tests/test_strategy_metadata.py` (policy cluster) — so it is a suite-cover fact, not runtime protection; the five-removed/one-kept count is established directly by the doc's own consumer table. | references/runtime-ops.md:265-272 | RQA-FR-019 |

---

### U-DOCS-22 — Documentation-to-code drift detection (`test_docs_contract.py`)

Files: tests/test_docs_contract.py

**RESOLVED (`DOCS-FR001`).** The maintainer struck the `RQA-FR-001` mapping:
FR-001's fit criterion requires a verdict be checkable against the single
protocol definition's six named concepts, and this suite checks name/string
cross-references between docs and code — it never constructs or validates a
review verdict; the "however it is packaged" clause governs how that
definition is packaged, not what counts as checking a verdict against it. No
other requirement in the frozen specification obliges this documentation-to-code
naming check either (verified: `grep -inE 'drift|out.of.sync|out-of-date|single.
{0,20}(published|protocol).{0,20}definition' requirements/requirements-specification.md`
returns exactly one hit — line 162, FR-001's own fit criterion, the mapping just
struck). Both rows below are thereby wave-3 `bin` candidates: the disposition
lane must weigh them as such rather than inherit a stretched mapping that makes
the unit look required.

| claim | evidence | requirements |
| --- | --- | --- |
| The suite asserts SKILL.md/OPERATORS.md name only mutation templates, panel artifact filenames, shadow CLI flags, human_cli subcommands, and `scripts/*.py` modules that actually exist in code, and separately asserts every executable script is named in one of the two documents — catching drift in both directions. No requirement in the frozen specification bears on this claim; `RQA-FR-001` was struck per the maintainer's ruling (`DOCS-FR001`). | tests/test_docs_contract.py:35-52,55-61,76-99,144-158 | - |
| A dedicated assertion enforces that SKILL.md documents the `history.py` ingest step textually before the `--samples` invocation that consumes its output, so the published protocol document cannot present a samples file as though it materialised on its own. No requirement in the frozen specification bears on this claim; `RQA-FR-001` was struck per the maintainer's ruling (`DOCS-FR001`). | tests/test_docs_contract.py:117-123 | - |

---

### U-DOCS-23 — Fixture-free test harness: discovery/execution (run_all.py)

Files: tests/run_all.py

`run_all.py` and `conftest.py` do not cooperate at runtime at `9267b6308`
(verified directly: `tests/run_all.py` contains zero occurrences of `conftest`;
no `tests/test_*.py` file imports it), so they are judged as separate units
(U-DOCS-23/24) under methodology §4 — one is a working tracked runner, the
other is dead code under the documented invocation.

| claim | evidence | requirements |
| --- | --- | --- |
| `run_all.py` imports every `tests/test_*.py` by path, runs each zero-argument `test_*` function it defines, and raises a hard error for a function requiring an argument (a pytest fixture), rather than silently skipping it — the one local invocation a contributor needs to validate the whole suite. | tests/run_all.py:48-63 | RQA-NFR-006 |

---

### U-DOCS-24 — conftest.py guards are dead under the tracked runner

Files: tests/conftest.py

**Gap recorded, not smoothed.** `conftest.py` sets a non-token-shaped
`GITHUB_TOKEN`/`GH_TOKEN` sentinel and replaces `socket.socket` with a class
that raises on construction (`tests/conftest.py:26-46`), but both are bare
module-level code, not pytest fixtures or hooks, and they only execute if
something imports `conftest.py`. Nothing on the documented, tracked runner path
does: `run_all.py` loads each test via `importlib.util.spec_from_file_location`
(no conftest discovery) and its module glob (`tests.glob("test_*.py")`) does not
match `conftest.py`; no `tests/test_*.py` file imports it either. pytest would
auto-discover it, but the suite's own docs (SKILL.md:123-126, OPERATORS.md:528-532,
runtime-ops.md:295-298) prescribe `run_all.py`, which never loads it — so the
hermetic-isolation guarantee the file's docstring promises is not in effect
under the documented runner.

| claim | evidence | requirements |
| --- | --- | --- |
| `tests/conftest.py`'s guards are module-level code that only execute when something imports conftest — under `tests/run_all.py`, nothing does, so the suite-isolation guarantee they describe does not hold for the documented, tracked runner at `9267b6308`. | tests/conftest.py:26-46, tests/run_all.py:1-77 | RQA-NFR-006 |

---

### U-DOCS-25 — Job-identity determinism coverage (`test_deterministic.py`)

Files: tests/test_deterministic.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_deterministic.py` asserts and covers `job_id` stability for an identical `(repo, pr, head_sha, lane)` tuple and distinctness when `head_sha` or `lane` changes — the suite does not independently vary `repo` or `pr` (`number`), so it exercises only two of the four axes of the identity `classification.md` row 2 calls "one idempotent job per repo, PR, head, and lane" — and separately asserts `mutation_id` determinism for identical inputs. | tests/test_deterministic.py:19-31 | RQA-BR-007, RQA-FR-005 |

---

### U-DOCS-26 — Nonce-enveloped untrusted content coverage (`test_deterministic.py`)

Files: tests/test_deterministic.py

Narrowed per round-3 gate: the suite passes untrusted content carrying an
instruction-looking token into `nonce_envelope` and asserts the opening marker
`<<<body:n2>>>` and closing marker `<<<END:body:n2>>>` are both present; it
does not assert the content is retained verbatim between them, so this unit
covers the delimiter contract only.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_deterministic.py` asserts and covers that `nonce_envelope` emits matching `<<<name:nonce>>>`/`<<<END:name:nonce>>>` open/close markers for both a benign body and a tainted instruction-shaped one — the marker delimiter contract is what makes wrapped content recognisably delimited rather than free-floating. | tests/test_deterministic.py:34-42 | RQA-NFR-015 |

---

### U-DOCS-27 — Candidate-pool ordering under unavailability coverage (`test_deterministic.py`)

Files: tests/test_deterministic.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_deterministic.py` asserts and covers that `select_candidate_pools` preserves the configured order within each lane, and that a model marked unavailable via `mark_unavailable` is removed from its lane's candidates — never substituting an unconfigured alternative. | tests/test_deterministic.py:57-84 | RQA-NFR-009, RQA-FR-024 |

---

### U-DOCS-28 — Canary-approval default coverage (`test_deterministic.py`)

Files: tests/test_deterministic.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_deterministic.py` asserts and covers that a freshly created state directory has no `canaries` row marked `approved` for `incoming_review`. | tests/test_deterministic.py:97-105 | RQA-NFR-026 |

---

### U-DOCS-29 — Per-activity authority resolution and fail-closed defaults coverage (phase1)

Files: tests/test_phase1.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase1.py` asserts and covers that with no config every activity's mode is `disabled`, that `can_act({}, "o/r", "approve")` is `False`, that a repo-level override wins over the activity-level default with every unmentioned activity still defaulting to `disabled`, that `live` mode additionally requires a passed hard gate before `can_act` returns `True`, and that an unknown mode string is rejected by `validate_authority`. | tests/test_phase1.py:33-67 | RQA-NFR-017, RQA-NFR-026, RQA-NFR-018 |

---

### U-DOCS-30 — Policy validation and content-hash pinning coverage (phase1)

Files: tests/test_phase1.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase1.py` asserts and covers that `canonicalize` pins a 64-character content hash reproducible from `content_hash` on the same input, and that `validate_policy`/`canonicalize` reject a policy whose risk bands are non-monotonic. | tests/test_phase1.py:88-104 | RQA-NFR-018 |

---

### U-DOCS-31 — Atomic snapshot activation and last-known-good retention coverage (phase1)

Files: tests/test_phase1.py

Narrowed per gate: the test builds and activates a *good* snapshot first, then
shows the malformed candidate fails in `build_snapshot` — before any
activation — leaving the active payload's bytes/hash unchanged; it does not show
`SnapshotStore.activate` itself validating a supplied snapshot, and this row
does not claim it does.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase1.py` asserts and covers that `build_snapshot` rejects a malformed candidate (missing `approval`) with `SnapshotError`, that `SnapshotStore.activate` accepts the previously built good snapshot, and that the malformed candidate never alters the active payload's bytes or content hash. | tests/test_phase1.py:107-138 | RQA-NFR-018, RQA-NFR-005 |

---

### U-DOCS-32 — Required/achieved assurance computation coverage (phase1)

Files: tests/test_phase1.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase1.py` asserts and covers that lower evidence completeness yields strictly lower achieved assurance and can flip `can_approve` from true to false; that a required RPN of 10000 (a single maximum failure mode) drives `required_assurance` to `high`; that reviewer disagreement strictly raises residual uncertainty; that every field is JSON round-trippable; and that an explicit blocker denies approval regardless of otherwise-sufficient evidence. | tests/test_phase1.py:142-191 | RQA-BR-008, RQA-BR-014 |

---

### U-DOCS-33 — Request-changes eligibility gate and authority independence coverage (phase2)

Files: tests/test_phase2.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase2.py` asserts and covers that disabling `authority.request_changes` does not disable `authority.approve` and vice versa (the two run through separate code paths), and that the request-changes gate independently rejects an unverified blocker, insufficient blocker evidence, a stale head, and a revalidation that returns `False` or is entirely absent (`None` is treated as a denial, never a pass). | tests/test_phase2.py:69-136 | RQA-NFR-017, RQA-FR-009 |

---

### U-DOCS-34 — Lifecycle-transition legality coverage (phase2)

Files: tests/test_phase2.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase2.py` asserts and covers that `can_transition` allows the documented edges exercised here (`detected -> ready_for_review`, `changes_requested -> requested_changes_fixed`, `author_triage -> changes_requested`, `detected -> author_triage/closed/merged`) and rejects an undocumented jump (`detected -> approval_evaluation`, `merged -> detected`) — in particular a jump straight from `detected` to an approval-adjacent state, which is what keeps a disposition from becoming successful before the intervening evidence/assurance steps run. | tests/test_phase2.py:179-199 | RQA-FR-011, RQA-FR-037 |

---

### U-DOCS-35 — Human-decision execution-state tracking coverage (phase2)

Files: tests/test_phase2.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase2.py` asserts and covers that `set_execution_state` accepts and persists the two execution states it exercises (`execution_pending`, `executed`) on the `human_requests` row, and rejects an unrecognised state string by raising `RequestQueueError`; the product-reachable confirmation-before-`executed` guarantee is enforced separately by the guarded APPROVE executor (U-DOCS-05 row 2), not by this helper. | tests/test_phase2.py:203-239 | RQA-FR-013, RQA-NFR-010 |

---

### U-DOCS-36 — Reasoning-strategy registry and deterministic selection coverage (phase3)

Files: tests/test_phase3.py

| claim | evidence | requirements |
| --- | --- | --- |
| `scripts/strategies.STRATEGIES` contains exactly twelve entries, each with roles, a recognised aggregation mode, an output schema, disagreement handling, and positive budget/timeout — directly confirmed by reading the registry, not only by the test. | tests/test_phase3.py:25-45, scripts/strategies.py:63-90 | RQA-BR-012, RQA-FR-019 |
| `test_phase3.py` asserts and covers that `select_strategy` (a fixed specificity walk over specialist-need/prior-disagreement/independence/risk signals, `scripts/strategies.py:150-181`) is deterministic for a fixed signal set and falls back to a safe default (`direct_analysis`) when every requested candidate is unrecognised. | tests/test_phase3.py:48-69, scripts/strategies.py:150-181 | RQA-BR-012, RQA-FR-019 |

---

### U-DOCS-37 — Subscription-first model-route resolution and fallback-loop guard coverage (phase3)

Files: tests/test_phase3.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase3.py` asserts and covers that `resolve_route` selects the first configured lane when available, advances to the next configured lane only once the prior provider is marked unavailable in state, exhausts to a `"human"` final result when every configured provider is unavailable (with nothing attempted), and never selects more than one candidate from the same provider even when several share it. | tests/test_phase3.py:84-134 | RQA-NFR-009, RQA-FR-023, RQA-FR-024 |

---

### U-DOCS-38 — Error-category metadata coverage (phase4)

Files: tests/test_phase4.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase4.py` asserts and covers that an unknown error category is not retryable and has `authority_impact: no_mutate`, and that every named category's `authority_impact` is one of `none`/`no_mutate`/`safe_stop`. The unknown case is not the most restrictive the vocabulary admits: `invariant_violation` carries `authority_impact: safe_stop` and `severity: CRITICAL` (scripts/errors.py:227), each a step beyond the fallback's `no_mutate`/`ERROR` on the module's own documented ordering `none < no_mutate < escalate < safe_stop`. Every assertion in this unit reads `category_meta` and nothing else. | tests/test_phase4.py:22-37, tests/test_phase4.py:65-68, scripts/errors.py:227, scripts/errors.py:244-252 | RQA-NFR-010 |

---

### U-DOCS-39 — Job-log schema and redaction coverage (phase4)

Files: tests/test_phase4.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase4.py` asserts and covers that a logged event carries `schema_version`, the given `event_name`, and required envelope fields (`timestamp`, `severity_text`, `body`, `resource`). | tests/test_phase4.py:46-54 | RQA-FR-012 |
| `test_phase4.py` asserts and covers that an attribute keyed `ai.token` is replaced with `<redacted>` in the persisted JSONL (`test_log_redaction`, `tests/test_phase4.py:57-63`) — the same redaction contract U-DOCS-17 documents from `references/runtime-ops.md`. | tests/test_phase4.py:57-63, references/runtime-ops.md:77-84 | RQA-BR-003 |

---

### U-DOCS-40 — Shadow-backtest read-only guarantee and historical-cutoff enforcement coverage (phase4)

Files: tests/test_phase4.py

Narrowed per gate: the suite checks only that `shadow` exposes `backtest` and
`evaluate_before_merge` attributes and that one constructed `HistoricalSample`
preserves `head_sha`/`files`/`merged_at` with no `merged_after` attribute; it
does not invoke either entrypoint or compare facts against a cutoff, so this
unit keys on the interface/data shape the test actually asserts.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_phase4.py` asserts and covers that `shadow` exposes `backtest` and `evaluate_before_merge` attributes and that `HistoricalSample.before_merge_facts()` reconstructs facts pinned to the sample's own head (`head_sha`/`files`) with no post-merge marker (`merged_after` absent) — the data shape that keeps a backtest from seeing post-cutoff evidence. | tests/test_phase4.py:71-94 | RQA-FR-037 |

---

### U-DOCS-41 — Panel completion and fallback/stale-verdict handling coverage (regression)

Files: tests/test_regression.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_regression.py` asserts and covers that a panel missing a required slot is `complete: False` with only the completed reviewers listed; that a failing candidate inside one slot falls over to the next configured candidate in that slot and the panel still completes; that when every candidate fails no signal is recorded and a stale verdict file is removed rather than consumed; and that, wired through `dispatcher.run_job`, a partial panel lands in `degraded_draft` with decision `PARTIAL_PANEL`, never `human_required` and never a success. | tests/test_regression.py:93-191 | RQA-FR-011, RQA-FR-037, RQA-NFR-010 |

---

### U-DOCS-42 — Assurance-profile floor for sensitive paths and large diffs coverage (regression)

Files: tests/test_regression.py

Narrowed per gate: the suite distinguishes the two triggers — a sensitive path
(`security/`) is floored to frontier/high/challenger; a large diff is asserted
to floor capability to frontier only (no high-effort or challenger-independence
assertion for that case); a plain change floors to workhorse/medium.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_regression.py` asserts and covers that a PR touching `assurance.sensitive_paths` is floored to `capability: frontier`/`effort: high`/`independence: challenger`, that a PR exceeding `assurance.large_diff_lines` is floored at least to `capability: frontier`, and that a plain change floors only to `workhorse`/`medium`. | tests/test_regression.py:132-162 | RQA-BR-014, RQA-BR-008 |

---

### U-DOCS-43 — Risk banding coverage (repairs)

Files: tests/test_repairs.py

**RESOLVED (`DOCS-RISK-SPLIT`).** The maintainer ruled this decided under §4's
existing `CADENCE-SPLIT` rule: `risk_band`/`effective_risk`/`validate_bands`
operate on numeric scores and configured band thresholds, while
`protected_triggered` operates on changed-file paths against regex patterns —
disjoint inputs and independently reworkable code. Split into this unit
(numeric risk-banding) and U-DOCS-58 (protected-trigger detection), appended
at the end of the file rather than inserted here so no existing unit id
renumbers.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `risk_band` places a score exactly at a band boundary in the lower band (24 -> low, 25 -> medium, 100 -> high) and that `effective_risk` returns the maximum RPN across failure modes (10000), never an average of a low mode and a high mode; and that `validate_bands` rejects non-monotonic bands. | tests/test_repairs.py:64-85 | RQA-BR-014, RQA-NFR-018 |

---

### U-DOCS-44 — Approval-gate conjunction across live/shadow/disabled dispositions coverage (repairs)

Files: tests/test_repairs.py
Rationale: this is a separate responsibility from U-DOCS-43's numeric risk primitives — it is about the gate-conjunction *behaviour* those primitives feed, and could be reworked independently of them (e.g. the gate sequencing could change without the risk-banding math changing).

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `evaluate` returns disposition `live` only when every configured gate passes for two corroborating verdicts from distinct provider families; that it is denied (non-`live`) for a draft PR even with a clean verdict; that a protected-trigger match on a changed file forces `human_escalation` regardless of verdict; and that `shadow` and `disabled` modes never persist a row in `approval_decisions`. | tests/test_repairs.py:100-180 | RQA-FR-009, RQA-NFR-017 |

---

### U-DOCS-45 — Mutation-event fixation and approval-record-required guard coverage (repairs)

Files: tests/test_repairs.py

Narrowed per gate: both executor tests call `execute_approval` with a decision
dict that is empty/absent; neither seeds a persisted decision record whose
required field is empty, so the separate "required field is empty" branch is not
exercised, and this row says only the absent/empty-caller case.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `fixed_event_of` returns the hard-coded event for a mutation name (`COMMENT` for `add_comment_review`, `APPROVE` for `approve_review`), that the GraphQL query templates embed `event:COMMENT`/`event:APPROVE` literally, and that `execute_approval` raises `ApprovalRecordRequiredError` for an absent/empty decision dict. | tests/test_repairs.py:184-232 | RQA-NFR-017 |

---

### U-DOCS-46 — Lease claim assigns the GitHub user node id, not the PR node id (repairs)

Files: tests/test_repairs.py

A fixed test-quality note applies: the prior version of this test named a
nonexistent function inside `if False` and asserted nothing
(tests/test_repairs.py:239-245); this rewrite drives `lease.claim` itself.
**RESOLVED (`DOCS-BR003`).** The maintainer struck the `RQA-BR-003` mapping:
BR-003 obliges a persisted review-provenance record naming performer, protocol
and basis, and `lease.claim`'s `assigneeIds`/`assignableId` swap is concurrency
control over who may claim a PR, no part of that record. No other requirement
in the frozen specification obliges this behaviour either (verified:
`grep -inE 'lease|assignee|concurrenc|GraphQL|node id'
requirements/requirements-specification.md` returns exactly one hit — line 1341,
RQA-FR-035's GitHub-vs-other-SCM fit criterion, unrelated). A behaviour serving
no frozen requirement is thereby a wave-3 `bin` candidate: the disposition lane
must weigh it as one rather than inherit this row's stretched wave-1 mapping as
though the unit were required.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `lease.claim` REST-verifies the assignment (re-reading current assignees) before recording the local lease row, and asserts `assigneeIds == [<user node id>]` while `assignableId == <PR node id>` — the defect this test exists to catch is those two being swapped. No requirement in the frozen specification bears on this claim; `RQA-BR-003` was struck per the maintainer's ruling (`DOCS-BR003`). | tests/test_repairs.py:270-307 | - |

---

### U-DOCS-47 — State-transition guard coverage (repairs)

Files: tests/test_repairs.py

Tested-case wording per gate: the `None -> detected` creation rule is asserted
for the two cases the suite varies (`None -> detected`, `None -> action`), a
terminal successor, an unknown target, and an unknown source; the "every
transition the table declares is legal" half is a control that walks
`transition_entries`.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `can_transition` accepts `(None, "detected")` as a from-scratch creation, refuses the `None -> action` jump, refuses a terminal state's successor and an unknown state name on either side, and that every transition the table itself declares is separately confirmed legal. | tests/test_repairs.py:321-341 | RQA-FR-011, RQA-FR-037 |

---

### U-DOCS-48 — Verdict-signal parsing coverage (repairs)

Files: tests/test_repairs.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `signal_from_verdict` returns empty for a signal token embedded in prose and for malformed JSON, and that only a real `signal` field in a valid JSON object counts. | tests/test_repairs.py:345-355 | RQA-FR-010, RQA-FR-037 |

---

### U-DOCS-49 — Unknown-job and missing-evidence classification coverage (repairs)

Files: tests/test_repairs.py
Rationale: distinct from U-DOCS-47/48 — this unit is about how the system reacts to a job/evidence state that should not occur at all.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that a transition attempted on a job id that does not exist raises `JobBlockingError` and leaves `current_status` at `None` rather than creating a phantom row, and that `classify_disposition("missing evidence")` maps to `"evidence_incomplete"` while an unrelated disposition string does not. | tests/test_repairs.py:359-389 | RQA-FR-010, RQA-NFR-010 |

**A documentation-vs-code divergence in this same file, noted here because it
belongs to no separate reference doc:** the module docstring (tests/test_repairs.py:5,7)
claims coverage of "worktree, supersede, config shapes, onboarding no-overwrite"
— none of which this file tests at `9267b6308`. A code comment (tests/test_repairs.py:311-320)
explains the supersede half: the test that once lived here asserted a
hand-written status string, and was deleted once the same behaviour was found
covered in `tests/test_queue.py` (queue cluster). This is a divergence to
evidence, not to fix, per `gap/methodology.md` §3 rule 6.

---

### U-DOCS-50 — REST ETag 304 pagination via `common.GithubRest` (repairs)

Files: tests/test_repairs.py

`GithubRest` is defined in `scripts/common.py`, not `scripts/github_rest.py` —
the class this test imports and subclasses (`from common import GithubRest`, tests/test_repairs.py:394)
is `common.py`'s transport, and `github_rest.py`'s `RestReader` is never touched
by this test. This unit keeps a `scripts/` citation deliberately: its point is
the misattribution trap itself, and stating it as coverage alone would not show
where the pagination behaviour lives.

| claim | evidence | requirements |
| --- | --- | --- |
| `GithubRest.get(..., paginate=True)` (`scripts/common.py:488` class, pagination body `scripts/common.py:535-567`) walks the full page chain by following the cached `Link` header from each page's cached row rather than stopping at the first 304, returning both pages' concatenated results in order — the standard HTTP pagination convention `references/contracts.md:32` documents rather than a bespoke format. | tests/test_repairs.py:393-441, scripts/common.py:488,535-567, references/contracts.md:32 | RQA-NFR-003 |

---

### U-DOCS-51 — Onboarding config generation and no-overwrite guarantee coverage (integration)

Files: tests/test_integration.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_integration.py` asserts and covers that `onboarding.py init`'s generated config is loadable by `config.load_repo_config` with no validation issues and normalizes to include the configured slug, that a `State`/`job_id` constructed against it works with no legacy `KeyError`, and that a second `init` against an already-onboarded repo refuses (non-zero exit, `"already exists"` in the JSON error) and leaves the original slug untouched rather than overwriting it — the onboarding step a single local operator uses to stand the workflow up at all. | tests/test_integration.py:35-79 | RQA-NFR-006 |

---

### U-DOCS-52 — Human-queue pending/expiry handling coverage (integration)

Files: tests/test_integration.py

The expiry sub-claim is limited to what the test varies — two simultaneous
pending requests, one decision, one request forced past expiry and reported
`is_expired` — and the success/disposition coupling is stated through the
product path that actually refuses an expired record (U-DOCS-05 row 2) rather
than asserted of this suite alone.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_integration.py` asserts and covers that two human requests for different PRs stay simultaneously pending with distinct request IDs, that deciding one leaves the other still pending, and that a request whose `expires_at` is forced into the past is reported `is_expired` — the kind of record the resume path refuses (U-DOCS-05) and that a successful disposition cannot rest on. | tests/test_integration.py:82-128 | RQA-FR-011 |

---

### U-DOCS-53 — Worktree create/clean exercised only under a fake runner, no production caller (integration)

Files: tests/test_integration.py

This test corroborates the U-DOCS-13 finding from the integration suite's own
side: it proves the mechanism functions correctly under a fully faked `runner`
callable, which is exactly the "reachable only from a test module" condition
`gap/methodology.md` §2.3 holds confers no product reachability (the test
imports `worktree` directly at tests/test_integration.py:133). RQA-BR-006 was
dropped because no end-to-end remediation cycle is exercised; RQA-NFR-020
remains since the worktree mechanism is what that requirement is about.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_integration.py` asserts and covers that `worktree.create` refuses to create from a bare base-branch argument (raising `WorktreeError` with "refusing to create") and only proceeds given an explicit `head_sha`, recording the branch as `rqa/<job>` and the exact head SHA; and that `worktree.clean` is idempotent, returning `True`/`False` without raising on a repeated call against an already-clean state — demonstrated entirely under a fake runner, with no assertion that any product code path invokes these functions. | tests/test_integration.py:131-157 | RQA-NFR-020 |

---

### U-DOCS-54 — Shadow-mode evaluation persists no decision record coverage (integration)

Files: tests/test_integration.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_integration.py` asserts and covers that `approval_evaluate.evaluate` under `approval.mode: shadow` returns disposition `"shadow"` and leaves the `approval_decisions` table with no row, for a PR that would otherwise be a clean, low-risk candidate — shadow mode cannot manufacture a persisted successful disposition. | tests/test_integration.py:160-182 | RQA-FR-037 |

---

### U-DOCS-55 — Concurrent attempt-log writers allocate distinct artifact numbers coverage (integration)

Files: tests/test_integration.py

| claim | evidence | requirements |
| --- | --- | --- |
| `test_integration.py` asserts and covers that eight concurrent threads calling `JobLogger.attempt` each receive a distinct attempt number with no duplicate and no exception, and that each writes one valid-JSON `attempt-NNN.json` file — no attempt file is overwritten or corrupted by a racing writer. | tests/test_integration.py:185-211 | RQA-NFR-010 |

---

### U-DOCS-56 — Dispatcher terminal-outcome to GitHub-mutation-set mapping coverage (e2e)

Files: tests/test_e2e_outcomes.py

The count is twelve (ten terminal-outcome tests plus two gated precondition
tests) and RQA-FR-029 has been dropped (no test in range configures or asserts
merge-after-review). Recorded precisely: `Harness.mutations` appends a mutation
name **only after the fake mutation returns**, so on the failed request-changes
path `rc_execute` raises before appending and `h.mutations == []` proves no
*successful* mutation was recorded, not which operation was attempted.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_e2e_outcomes.py` asserts and covers, across twelve distinct terminal paths through `dispatcher.run_job` (auto-approved, advisory, shadow-advisory, changes-requested, uncorroborated-defect human-required, human-escalation-pending, uncertain-approval safe-stop, missing-node-id safe-stop, failed-mutation safe-stop, partial-panel degraded-draft, and the two gated cases), that each terminal status is reached with exactly the intended **successfully-recorded** GitHub mutation set and no others — a gated run records none, and on the failed request-changes path the empty record proves no success was recorded, not that no operation was attempted. | tests/test_e2e_outcomes.py:140-294 | RQA-FR-028, RQA-FR-037, RQA-NFR-010 |

---

### U-DOCS-57 — Cross-cutting dispatch invariants: lease release, conjunctive authority, explainability coverage (e2e)

Files: tests/test_e2e_outcomes.py
Rationale: the three invariants are the e2e file's own "cross-cutting invariants" section and are each independently removable guarantees that together form the corpus of what that section asserts; splitting them further would erase their common "every terminal path" framing under the same harness.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_e2e_outcomes.py` asserts and covers that every one of five representative terminal outcomes (auto-approved, advisory, human-escalation, uncertain-approval safe-stop, partial-panel degraded-draft) claims exactly one lease and releases exactly one. | tests/test_e2e_outcomes.py:298-316 | RQA-NFR-010 |
| `test_e2e_outcomes.py` asserts and covers that across all four authority modes (`disabled`/`shadow`/`human_escalation`/`live` with `authority.approve = disabled`), `approve_review` never appears in the mutation record — the conjunctive rule (`approval.mode` AND `authority.approve`) holds regardless of `approval.mode`. | tests/test_e2e_outcomes.py:319-328 | RQA-NFR-017 |
| `test_e2e_outcomes.py` asserts and covers that for three representative outcomes, `ledger.explain` reports `explained: True` with a non-null `final_decision`. | tests/test_e2e_outcomes.py:331-347 | RQA-FR-012 |

---

### U-DOCS-58 — Protected-trigger detection coverage (repairs)

Files: tests/test_repairs.py

Split from U-DOCS-43 per the maintainer's ruling on `DOCS-RISK-SPLIT`, decided
under §4's `CADENCE-SPLIT` rule: `protected_triggered` operates on changed-file
paths against regex patterns, disjoint from the numeric score/threshold inputs
U-DOCS-43's primitives consume, with no shared data dependency and independent
removability. Appended here, rather than inserted after U-DOCS-43, so no
existing citation to `U-DOCS-44`..`U-DOCS-57` renumbers.

| claim | evidence | requirements |
| --- | --- | --- |
| `test_repairs.py` asserts and covers that `protected_triggered` flags a changed-files list against configured trigger regexes and names the first match. | tests/test_repairs.py:88-90 | RQA-BR-014 |
