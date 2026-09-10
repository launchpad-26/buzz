# RQA gap analysis — evidence: `verdict` cluster

Evidence base for the `verdict` cluster (review output contract: verdicts and
their schema fence, findings, evidence handling, the checks vocabulary, risk
banding, assurance, the reviewer panel, and shadow mode with its calibration),
per [`../methodology.md`](../methodology.md) and the 18 files
[`../clusters.md`](../clusters.md) assigns to `verdict`. Revision
`9267b6308714454a3b987622d90cda03a8972827`. All paths are relative to
`launchpad/skills/review-queue-automation/`, as `../methodology.md` requires.

This document records what the code does and which requirement text a claim
bears on. It assigns no gap degree, no root cause and no disposition — that is
wave 2's and wave 3's work.

---

### U-VERDICT-01 — Reviewer-verdict text parsing and markdown-fence normalisation

Files: scripts/verdict.py, tests/test_verdict_fence.py

Rationale: `strip_code_fence`/`parse_verdict`/`signal_from_verdict` and the
dedicated fence test are one responsibility — normalising the raw text a model
returns into parseable JSON without ever widening what counts as a real
verdict — separate from the schema-driven structural check in U-VERDICT-02,
which runs only after this step succeeds.

| claim | evidence | requirements |
|---|---|---|
| `strip_code_fence` removes exactly one markdown fence only when it wraps the entire payload (anchored at both start and end); text with any prose before or after the fence is returned unstripped, so a verdict cannot be extracted out of surrounding prose. | scripts/verdict.py:57-63,66-80 | RQA-FR-001 |
| `parse_verdict` raises `VerdictError` on any input that is not strict JSON after fence-stripping, rather than attempting a lenient or partial parse. | scripts/verdict.py:83-88 | RQA-FR-001 |
| `signal_from_verdict` returns a non-empty signal only when the parsed object is a dict, its `signal` key is itself a JSON string, and that string is one of the six `VALID_SIGNALS`; a signal token appearing only in surrounding prose, or in unparseable text, yields `""`. | scripts/verdict.py:22-30,91-104 | RQA-FR-001 |
| Two verdict fences in one payload, or one fence left unclosed, are never merged or completed — the anchored `\A...\Z` fence match (`scripts/verdict.py:57-63`) cannot match either shape, so both fall through unstripped to a JSON-decode failure and an empty signal, confirmed for a payload with two adjacent fences and for a payload whose closing fence is missing. | scripts/verdict.py:57-80, tests/test_verdict_fence.py:100-106 | RQA-FR-001 |

---

### U-VERDICT-02 — Reviewer-verdict schema-driven validation and contradiction detection

Files: scripts/verdict.py, schemas/reviewer-verdict.json, tests/test_verdict_schema.py

Rationale: `validate_verdict` is a partial, hand-written mirror of
`schemas/reviewer-verdict.json` — it enforces the schema's required-field list
and its `signal`/`recommendation` enums, but not the schema's finding-level
`severity` enum, its `location` pattern, its `minLength` constraints, or its
`additionalProperties: false` — and `test_verdict_schema.py` is what
establishes exactly that boundary, including the one case where the two
diverge (an extra top-level field the schema forbids but `validate_verdict`
accepts).

| claim | evidence | requirements |
|---|---|---|
| `validate_verdict` accepts a candidate verdict only when it is strict JSON, every schema-required field is present, `signal` is one of the six enumerated values, `recommendation` is one of `clean`/`findings`/`human`, `summary`/`good`/`missing_evidence` are well-typed, every finding object carries all five of its own required fields, and none of the six `_CONTRADICTIONS` predicates holds (e.g. a `SUPPORTED` signal carrying findings, or a `DEFECTS_FOUND` signal with none) — a schema-shaped but internally contradictory verdict is rejected. | scripts/verdict.py:31,34-45,149-197 | RQA-FR-001, RQA-FR-002 |
| The schema itself fixes a finding's `location` to a `path:line`-shaped pattern, forbids properties outside its six declared top-level keys and five declared finding keys (`additionalProperties: false`), and enumerates `signal` to the same six values `verdict.py` checks against. | schemas/reviewer-verdict.json:4-5,16-21 | RQA-FR-001 |
| `validate_verdict` does not enforce every constraint `schemas/reviewer-verdict.json` declares: it never checks a finding's `severity` against the schema's four-value enum, its `location` against the schema's `path:line` pattern, any `minLength`, or the schema's `additionalProperties: false` at either the top level or the finding level — confirmed for the top-level case, where a verdict carrying an extra field the schema forbids still validates `ok`. | scripts/verdict.py:149-197, schemas/reviewer-verdict.json:4-5,16-21, tests/test_verdict_schema.py:103-110 | RQA-FR-001 |
| A second, lighter structural check, `validate_structure`, duplicates part of this validation (checks only `signal`/`summary`/`findings`/`good`) but is never called by `panel.py` or `dispatcher.py` at this revision — its only callers in the tree are `tests/test_verdict_schema.py` and `tests/test_repairs.py` (docs cluster); the gate `panel.py` actually uses to fill a reviewer slot is `validate_verdict`. | scripts/verdict.py:107-130, scripts/panel.py:406-416, tests/test_verdict_schema.py:39-43 | RQA-FR-034 |
| `read_verdict`, which reads and parses a verdict file from disk, has no caller anywhere in `scripts/` or `tests/` at this revision — not even a test. | scripts/verdict.py:200-204 | RQA-FR-034 |

---

### U-VERDICT-03 — Author-triage verdict schema

Files: schemas/author-triage.json

| claim | evidence | requirements |
|---|---|---|
| `schemas/author-triage.json` declares a three-key top-level shape (`signal`, `summary`, `findings`) whose `findings` array items each carry five required keys (`comment_id`, `classification`, `location`, `evidence`, `action`), with `classification` a four-value enum (`VALID`/`VALID_BUT_DIFFERENT_FIX`/`INVALID`/`OUT_OF_SCOPE`) scoped per finding rather than to the verdict as a whole, for per-review-comment triage — separate from the six-key reviewer-verdict shape U-VERDICT-02 covers — but no script in `scripts/` loads, parses or validates against this file at this revision: every one of the twelve strategies in `strategies.py` declares `output_schema: "reviewer-verdict"`, and `panel.py`'s own `VERDICT_SCHEMA` constant names only that one schema, refusing any strategy that names a different one. | schemas/author-triage.json:5-24, scripts/panel.py:84-86,566-574 | RQA-FR-034 |

---

### U-VERDICT-04 — Finding extraction with an evidence-completeness filter

Files: scripts/findings.py

| claim | evidence | requirements |
|---|---|---|
| `extract_findings` silently drops any raw finding object missing a non-empty `severity`, `location`, `evidence` or `primary_source`, so a defect a model merely asserts without a location or a cited source never reaches corroboration. | scripts/findings.py:88-90,92-121 | RQA-BR-008, RQA-BR-014 |
| `Finding.fingerprint` matches two findings as the same defect using severity plus whitespace/case-normalised location alone; two reviewers whose titles or prose differ still fingerprint identically provided severity and location agree. | scripts/findings.py:43-61,84-85 | RQA-FR-002 |

---

### U-VERDICT-05 — Finding corroboration: two-family or check-backed blocking rule

Files: scripts/findings.py, scripts/checks.py

Rationale: `findings.py` owns the corroboration rule that decides which
asserted defects are trustworthy enough to support a formal change request, and
`checks.py` owns the single check-conclusion vocabulary the rule's
check-backed branch queries to answer "did the cited check actually fail" —
changing what counts as a genuine check failure directly changes which
findings corroborate, so the two are one responsibility.

| claim | evidence | requirements |
|---|---|---|
| `corroborate` verifies a blocking-severity finding only when either (a) at least two distinct provider families independently reported the same fingerprint, or (b) one family's finding cites, within its own `evidence`/`primary_source` text, the name of a check whose conclusion is in `FAILING`; every other blocking-severity finding is returned `verified=False` with basis `single_family_uncorroborated`. | scripts/findings.py:146-197, scripts/findings.py:133-143 | RQA-BR-008, RQA-BR-014 |
| The `FAILING` conclusion set a check-backed corroboration requires is the single vocabulary `checks.py` defines once (`FAILURE`/`TIMED_OUT`/`CANCELLED`/`ACTION_REQUIRED`/`STALE`), deliberately narrower than "not passing" so a pending or unrecognised check conclusion can never itself corroborate a finding. | scripts/checks.py:49-51, scripts/findings.py:26,32-35 | RQA-BR-008 |
| `blocking_summary` exposes only a verified/unverified split with per-finding basis, provider families and citation — the compact record `dispatcher.py` reuses for logs, human packets and PR bodies. | scripts/findings.py:64-81,200-221, scripts/dispatcher.py:791,803,879,916 | RQA-BR-003, RQA-FR-012 |

---

### U-VERDICT-06 — Canonical check-conclusion vocabulary

Files: scripts/checks.py, tests/test_checks_vocabulary.py

Rationale: `checks.py` defines the vocabulary once, and
`test_checks_vocabulary.py`'s own stated purpose is asserting that no other
module re-implements it — the test and the module it pins are inseparable.

| claim | evidence | requirements |
|---|---|---|
| `checks.py` is the one canonicalisation (`canonical`: strip + upper-case) and the one `PASSING` set (`SUCCESS`, `NEUTRAL`, `SKIPPED`); `is_passing`/`is_failing`/`is_pending`/`all_passing` are the implementations `dispatcher.py`, `findings.py`, `history.py` and `github_query.py` import, replacing four previously-independent literal sets that disagreed (`launchpad-26/buzz#1963`), confirmed reachable at `dispatcher.py:297` where `all_passing` feeds the `checks_complete_ok` approval gate. | scripts/checks.py:1-37,47,54-61,88-123, scripts/dispatcher.py:36,290-297 | RQA-BR-009 |
| `all_passing` fails closed on an empty check list and on any single pending check — an empty or partial evidence set is never treated as a passing gate. | scripts/checks.py:115-123, tests/test_checks_vocabulary.py:93-102 | RQA-NFR-010 |
| `conclusion_from_status` maps a commit-status `StatusState` onto the same canonical vocabulary a check-run uses, with `PENDING` mapping to `""` (not a conclusion) and an unrecognised state passed through un-mapped so `is_failing` treats it as standing in the way rather than silently green; `github_query.py`'s inventory reader is confirmed to call this exact function object, not a re-implementation. | scripts/checks.py:64-85, scripts/github_query.py:37, tests/test_checks_vocabulary.py:222-249 | RQA-BR-009 |

---

### U-VERDICT-07 — Evidence bundle collection for one PR

Files: scripts/evidence.py

| claim | evidence | requirements |
|---|---|---|
| `collect` fails closed with `EvidenceIncompleteError` when the fetched PR metadata is empty, when the head SHA is missing, or when the check-runs read returns `None` — the evidence bundle is never written partially in any of these three cases. | scripts/evidence.py:37-50 | RQA-NFR-010, RQA-BR-014 |
| The written artefact set is fixed to three names (`evidence.json`, `evidence.txt`, `context.json`) that the panel and dispatcher read by that exact contract, written atomically, with the linked-issue number extracted only from a close/fix/resolve keyword directly followed by `#<number>` in the PR body. | scripts/evidence.py:17,19-23,52-63,90-91,125-126, scripts/panel.py:477,538-540, scripts/dispatcher.py:235 | RQA-FR-012 |
| `evidence.txt` wraps every GitHub-sourced field (PR meta, reviews, review comments, issue comments, changed filenames, checks, and any linked issue) in a nonce-delimited envelope keyed by the job id, so the reviewer prompt can distinguish untrusted content sections from its own instructions. | scripts/evidence.py:93-124 | RQA-NFR-015 |

---

### U-VERDICT-08 — Assurance escalation ladder (capability / effort / independence)

Files: scripts/assurance.py, tests/test_assurance.py

Rationale: the escalation ladder's logic and its dedicated unit-test module are
the same responsibility split across a module and its tests; no other file in
this cluster calls `classify` or `drive` (`scripts/panel.py:48` imports and
constructs `Profile` values throughout `run_panel`/`decide_assurance`, but
never calls the escalation functions themselves).

| claim | evidence | requirements |
|---|---|---|
| `classify` maps a set of reviewer signals to exactly one of seven decisions: `HUMAN_RESERVED` always routes to `HUMAN` regardless of any other signal present; `DEFECTS_FOUND`+`SUPPORTED` together, and `MATERIAL_DISAGREEMENT` alone, route to `CONVENE_PANEL` from `single`/`challenger` independence and to `HUMAN` once already at `panel` independence; `INSUFFICIENT_CAPABILITY` raises effort before capability and only reaches `HUMAN` once both are at their cap. | scripts/assurance.py:94-134 | RQA-NFR-007, RQA-FR-023, RQA-FR-024 |
| `raised` only ever moves a profile one step up a named axis and returns `None` at that axis's cap, so `drive`'s loop cannot escalate a profile past `frontier`/`xhigh`/`panel`; `drive` always terminates (within `max_steps`) at `SUCCESS`, `REQUEST_CHANGES` or `HUMAN`, never looping past its bound. | scripts/assurance.py:69-86,144-184 | RQA-NFR-007 |
| `minimum_profile` raises capability to `frontier` only for a sensitive or large PR, whether or not it is in the `author_triage` lane; independent of sensitivity, every `author_triage`-lane PR gets a `high`-effort floor in place of the `medium` floor other lanes start at — so a plain, non-sensitive `author_triage` PR gets `workhorse` capability with `high` effort, not `frontier`. `dispatcher.py` is confirmed to actually drive this escalation loop, not only this module's own tests. | scripts/assurance.py:187-194, scripts/dispatcher.py:1367 | RQA-NFR-007 |

---

### U-VERDICT-09 — Panel candidate-pool selection, capability/effort qualification and cooldown tracking

Files: scripts/panel.py

| claim | evidence | requirements |
|---|---|---|
| `select_candidate_pools` returns only primary/secondary model entries not currently cooled down (`_available`, keyed by `runner:selector` in the `providers` table); `run_panel`'s `_qualifying` predicate additionally excludes any entry whose declared capability rank is below the profile's required rank or whose declared efforts exclude the profile's requested effort, and a lane with zero qualifying entries after filtering is dropped rather than falling back to an unfiltered, lower-quality lane. | scripts/panel.py:266-271,287-298,549-557,576-582 | RQA-FR-024, RQA-FR-038 |
| A failing candidate is recorded unavailable for a configured cooldown window keyed by `runner:selector`; a provider-scoped failure (a genuine timeout or a non-zero exit / OSError) additionally retires every model sharing that provider family for the remainder of the run, so a sibling model is not retried after a correlated provider outage. | scripts/panel.py:274-284,393,404,718-722 | RQA-FR-023, RQA-FR-024 |

Also observed: a slot is only ever filled by a candidate whose selector, and whose declared provider family where one is declared, has not already filled an earlier slot this run, so two slots can never be filled by the same concrete model or the same provider family (scripts/panel.py:657-664,708-710). This invariant is not itself named by any requirement in the frozen specification.

---

### U-VERDICT-10 — Candidate attempt execution, error-class taxonomy and the slot-fill validation gate

Files: scripts/panel.py

| claim | evidence | requirements |
|---|---|---|
| `_run_reviewer` invokes exactly one candidate through `runners.build_invocation` and raises `ReviewerError` (carrying bounded stderr) on a non-zero exit; only a genuine subprocess timeout is retried once on the *same* candidate — every other failure (non-zero exit, `OSError`, an invalid returned verdict) is terminal for that candidate and falls through to the next one in the ordered lane, never treated as a blanket "transient" failure. | scripts/panel.py:301-332,358-424 | RQA-FR-023, RQA-FR-024, RQA-NFR-009 |
| A slot is filled only when the candidate's raw stdout passes `validate_verdict`; a returned-but-invalid verdict (malformed JSON, missing or contradictory schema fields, or a prose-embedded signal) never fills the slot — its partial output file is deleted and the candidate is cooled down as `candidate_terminal`. | scripts/panel.py:344-356,406-424 | RQA-FR-001, RQA-FR-037 |
| An unknown runner adapter or an effort the runner cannot enforce is raised as `JobBlockingError`, not silently treated as one candidate's failure that falls through to the next model. | scripts/panel.py:301-314 | RQA-FR-038 |

---

### U-VERDICT-11 — Trust boundary between machinery-attested identity and model-controlled verdict content

Files: scripts/panel.py

| claim | evidence | requirements |
|---|---|---|
| `_trust_meta` writes runner/model/`provider_family`/capability/effort identity to a `.meta.json` sidecar produced entirely by this code, written immediately after a slot is filled, outside the model-controlled verdict JSON. | scripts/panel.py:249-263,711-715 | RQA-NFR-022, RQA-NFR-032 |
| `_mode_participants` reads `provider_family` for independence-mode aggregation from that trusted sidecar, never from the verdict content itself, so a model cannot assert an independence it does not have; a slot with no verdict file on disk contributes an explicitly invalid participant rather than being silently omitted from the count. | scripts/panel.py:215-246 | RQA-NFR-022, RQA-NFR-032 |

---

### U-VERDICT-12 — Panel run orchestration and completeness predicate

Files: scripts/panel.py

| claim | evidence | requirements |
|---|---|---|
| `run_panel` reports `complete` only when the number of parsed signals, the number of filled slots, and the number of mode-counted participants are each at least the profile's required count; any lesser outcome is `degraded` (something completed) or `retryable` (nothing did) — never silently upgraded to `complete`. | scripts/panel.py:726-751 | RQA-FR-037, RQA-FR-011 |
| A strategy whose declared `output_schema` is not exactly `"reviewer-verdict"` raises `JobBlockingError` before any candidate is invoked, rather than validating panel output against the wrong schema. | scripts/panel.py:566-574 | RQA-FR-001 |
| Every panel attempt clears any pre-existing slot files before running, so an escalated re-run can never be satisfied by a verdict written under a weaker, prior profile. | scripts/panel.py:626-631 | RQA-FR-037 |

Also observed: the reviewer prompt demands a single strict JSON object with exactly the schema's six keys and an enumerated signal, and explicitly instructs the model not to call GitHub or modify files, paired with the `--no-tools` invocation flag that is the strictest read-only profile the runner supports (scripts/panel.py:88-97,594-616). This invariant is not itself named by any requirement in the frozen specification.

---

### U-VERDICT-13 — FMEA-C risk scoring and band classification

Files: scripts/risk.py, tests/test_risk.py

Rationale: `FailureMode`/`effective_risk`/`combined_risk`/`risk_band` and
`validate_bands` are the deterministic risk-scoring responsibility, and
`test_risk.py`'s corresponding tests are its only exercise within this
cluster.

| claim | evidence | requirements |
|---|---|---|
| `FailureMode.rpn` multiplies four 1-10-bounded integer FMEA-C inputs (severity, likelihood, detectability, complexity), rejecting any input outside that range at construction; `effective_risk` takes the **maximum** `rpn` over a PR's failure modes, never the mean, so one severe mode is never diluted by several mild ones. | scripts/risk.py:59-76,110-112, tests/test_risk.py:55-61 | RQA-BR-004 |
| `combined_risk` returns the maximum of a deterministic floor and a model-observed score, so a model's own risk observation can only raise the effective risk above the deterministic floor, never lower it. | scripts/risk.py:115-122, tests/test_risk.py:64-67 | RQA-BR-004 |
| `risk_band` classifies a score against configurable Low ≤ 24 / Medium 25-99 / High ≥ 100 bands, and `validate_bands` raises `ConfigBandError` on any configured band set that is not strictly increasing and continuous — a malformed band configuration fails closed rather than silently misclassifying risk lower. | scripts/risk.py:26-28,42-56,125-131 | RQA-NFR-018, RQA-BR-004 |

---

### U-VERDICT-14 — Protected-path trigger detection

Files: scripts/risk.py

| claim | evidence | requirements |
|---|---|---|
| `protected_triggered` matches each changed path against each configured pattern (regex by default) and returns the first `(path, pattern)` match or `(None, None)`; a pattern that fails to compile is skipped rather than raised, so one malformed pattern in policy cannot crash the check — the trigger decision is a deterministic policy match, never an individual reviewer's judgement call. | scripts/risk.py:138-152 | RQA-BR-004 |
| `DEFAULT_PROTECTED` (nine patterns naming security/auth/migrations/schema/deploy/workflow/infra/release paths) and the `ProtectedTriggerError` exception class are both defined but referenced nowhere else in `scripts/` or `tests/` at this revision — `ProtectedTriggerError` is imported into `tests/test_risk.py` but never raised there either, and `protected_triggered` itself never raises it. The patterns a live repository's protected-trigger gate actually matches against come only from that repository's own `risk.protected_triggers` policy config. | scripts/risk.py:134-136,155-165, scripts/config.py:275-293, tests/test_risk.py:22-23 | RQA-FR-034 |

---

### U-VERDICT-15 — Bounded-change assessment: seven named gates aggregated into one bounded verdict

Files: scripts/risk.py, tests/test_risk.py

Rationale: `BoundedChange`'s definition in `risk.py` and its one test in
`test_risk.py` are the entire footprint of this mechanism in the tree; the
claim (that nothing else in the cluster or the wider `scripts/` tree
instantiates it) is inseparable from citing both.

| claim | evidence | requirements |
|---|---|---|
| `BoundedChange` aggregates seven named boolean gates (`one_clear_purpose`, `bounded_blast_radius`, `no_protected_trigger`, `straightforward_rollback`, `adequate_tests`, `no_unexplained_deps`, `no_unresolved_ambiguity`) behind `passes()`/`failed()`. The single `bounded_change` boolean that `ApprovalState`/`ApprovalEvidence` actually consume elsewhere in the tree is a separate, coarser field computed directly from an addition-count threshold (e.g. `scripts/shadow.py:259`), not from this class. | scripts/risk.py:168-201, tests/test_risk.py:115-121 | RQA-FR-034 |
| Nothing under `scripts/` outside `risk.py` reaches the class, so no product path instantiates it. Quoted as the searches returned, both run from `launchpad/skills/review-queue-automation/`: `grep -rn BoundedChange scripts/ --exclude=risk.py` → no output, exit 1; `grep -rn BoundedChange tests/` → three lines, all in tests/test_risk.py, at :20, :116 and :119. Under methodology §2.1(b) and §2.3 that makes the behaviour unreached, which is a fact about the code and not a root-cause judgement — the register decides degree and cause from it. | scripts/risk.py:169, tests/test_risk.py:115-121 | RQA-FR-034 |

---

### U-VERDICT-16 — `ApprovalState`: the canonical fail-closed 22-gate auto-approval predicate

Files: scripts/risk.py, tests/test_approval_evidence.py

Rationale: `risk.py` declares the one canonical gate object and its
all-must-be-true predicate; `test_approval_evidence.py` is the corroborating
check that the dispatcher always supplies real, non-default values for the
five gates this object cannot fill from PR facts alone — the two together are
what makes the fail-closed guarantee actually hold on the dispatch path.

| claim | evidence | requirements |
|---|---|---|
| `ApprovalState.passed()` is a conjunction over 22 named gates with no other path to a `True` result; twenty-one of those gates default to `False` on the dataclass itself — the sole exception is `no_protected_trigger`, which defaults to `True` (satisfied in the absence of a matched protected path) rather than fail-closed — so auto-approval is unreachable unless every one of the other twenty-one gates is explicitly set true and no protected path is subsequently matched. | scripts/risk.py:204-262 | RQA-FR-011, RQA-FR-037, RQA-NFR-018 |
| The dispatcher's approval-evidence assembly always supplies an explicit, non-`None` value for each of the five externally-evidenced gate names `ApprovalState` declares, confirmed for a stale/moved observed head (`revalidation_ok` becomes `False`) and for a PR with no persisted diff payload at all (`bounded_change` becomes `False`). | scripts/dispatcher.py:556-564, tests/test_approval_evidence.py:142-162,165-187,189-206 | RQA-FR-011 |

---

### U-VERDICT-17 — Versioned `risk-assessment.json` persistence: write, read and version-mismatch refusal

Files: scripts/risk.py, tests/test_risk.py

Rationale: the versioned-envelope writer/reader and its one round-trip test
are a single persistence mechanism; establishing that nothing else calls it
requires citing both the definition and its only caller.

| claim | evidence | requirements |
|---|---|---|
| `serialize_assessment`/`write_assessment`/`read_assessment` persist a versioned `risk-assessment.json` envelope, and `read_assessment` raises `ValueError` when the file's `version` field does not match the module's current `RISK_ASSESSMENT_VERSION` rather than reinterpreting a payload written under another version. | scripts/risk.py:33-35,279-316 | RQA-FR-034 |
| Nothing under `scripts/` outside `risk.py` calls the writer or the reader, and no reachable dispatch path produces or consumes the artefact. Quoted as the searches returned, all run from `launchpad/skills/review-queue-automation/`: `grep -rn -e write_assessment -e read_assessment -e serialize_assessment scripts/ --exclude=risk.py` → no output, exit 1; `grep -rn risk-assessment.json scripts/ --exclude=risk.py` → no output, exit 1; `grep -rn -e write_assessment -e read_assessment -e serialize_assessment tests/` → five lines, all in tests/test_risk.py, at :27, :30, :127, :131 and :140. Under methodology §2.1(b) and §2.3 the behaviour is unreached, stated here as the code fact it is and left to the register to convert into degree and root cause. | scripts/risk.py:288, scripts/risk.py:301, tests/test_risk.py:124-143 | RQA-FR-034 |

---

### U-VERDICT-18 — Deterministic assurance evaluation (evidence completeness, residual uncertainty, assurance-met floor)

Files: scripts/risk.py

| claim | evidence | requirements |
|---|---|---|
| `compute_assurance` derives `required_assurance` from the FMEA risk band, computes `achieved_assurance` as evidence completeness times a reviewer-completion ratio (halving both when evidence is not fresh), adds residual uncertainty for incomplete evidence, disagreement and unknown outcomes, and sets `assurance_met` by comparing achieved assurance against a fixed floor per required band (`none`→0.0, `low`→0.4, `medium`→0.7, `high`→1.0). `action_gate.request_changes_gate` is confirmed to read this exact `assurance_met` property as one of its own six deny conditions before a change-request action is allowed. | scripts/risk.py:349-355,391-412, scripts/action_gate.py:76-77 | RQA-BR-014, RQA-FR-037 |
| `compute_assurance` also derives `can_approve`/`can_request_changes`/`can_comment` booleans, but at this revision `dispatcher.py` and `action_gate.py` read only `.assurance_met` and `.required_assurance` off the returned object (serializing the rest only into ledger/log output via `.as_dict()`) — the three action-eligibility booleans are computed and recorded but drive no branch anywhere in `scripts/`. | scripts/risk.py:341-343,357-371,414-417, scripts/dispatcher.py:561,750-768,984 | RQA-FR-034 |
| `action_recommended`/`action_attempted`/`action_confirmed` are declared fields of `AssuranceEvaluation`, but `compute_assurance`'s own return never sets any of them away from their `"none"` default, and no other constructor call in `scripts/` supplies them either. | scripts/risk.py:344-347,418-427 | RQA-FR-034 |

---

### U-VERDICT-19 — Shadow-mode historical evidence reconstruction (fail-closed, pre-cutoff only)

Files: scripts/shadow.py, tests/test_shadow_calibration.py

Rationale: `HistoricalSample.before_merge_facts`/`historical_evidence`'s
pre-cutoff evidence reconstruction and the calibration test module that pins
its fail-closed behaviour for each of the five external gates are one
responsibility — proving only what the historical record can actually
support and never defaulting a gate open.

| claim | evidence | requirements |
|---|---|---|
| `HistoricalSample.before_merge_facts` marks `checks_ok`/`adjudication_complete`/`evidence_fresh` true only when the corresponding timestamp is set **and** is at or before the sample's own `cutoff`; evidence timestamped after the cutoff, or with no cutoff recorded at all, leaves the fact `False` — the same fail-closed posture the five external evidence gates below require. | scripts/shadow.py:125-150 | RQA-FR-011 |
| `historical_evidence` proves `bounded_change` from the recorded addition count against the configured `large_diff_lines` limit, proves `audit_writable` via a real filesystem write probe, and requires `assurance_met`/`revalidation_ok`/`rate_limit_ok` to come from explicit per-sample input or a frozen-head timestamp at or before cutoff — confirmed that calling the underlying `approval_evaluate.evaluate` with no evidence object at all defaults all five of these same gate names to `True`, and this module's `evaluate_before_merge` never omits the evidence argument for exactly that reason. | scripts/shadow.py:214-281,306-311, scripts/approval_evaluate.py:175-180 | RQA-FR-011 |
| The five-gate fail-closed contract this module builds is confirmed identical, by gate name, to the live dispatch path's own gate set — the legacy no-evidence call is pinned as a regression guard rather than a code path this module still reaches. | scripts/shadow.py:67-73, scripts/approval_evaluate.py:175-180, scripts/dispatcher.py:556-564, tests/test_shadow_calibration.py:302-337 | RQA-FR-011 |

---

### U-VERDICT-20 — Shadow backtest calibration: time-ordered train/calibrate split, fitted threshold, absence-of-evidence warnings

Files: scripts/shadow.py, tests/test_shadow_calibration.py

Rationale: `backtest`'s split/fit/report logic and the calibration tests that
pin the split ordering, the fitted-threshold behaviour and the warning text
are one responsibility — the read-only calibration report and the guarantee
that it never misrepresents an absence of evidence as a safety finding.

| claim | evidence | requirements |
|---|---|---|
| The backtest report emits an explicit warning — distinguishing "no verdicts supplied", "verdicts supplied but none matched a sample", and "a gate failed for every evaluated sample" — rather than presenting a resulting 0% would-approve rate as a safety finding when it is really an absence of evidence. | scripts/shadow.py:512-547, tests/test_shadow_calibration.py:367-374,428-445 | RQA-BR-014 |

Also observed: `backtest` sorts samples by `merged_at`, splits the ordered list at `train_ratio` into a train half used only to fit a threshold and a calibration half that is actually scored, and `_evaluate_split` replays the daily approval cap statefully within the run (scripts/shadow.py:455-497,342-374, tests/test_shadow_calibration.py:199-206). `learn_threshold` only ever lowers the configured risk ceiling, never raises it, fitting a value just below the lowest risk score among train samples with an adverse/contested outcome that cleared every non-risk gate (scripts/shadow.py:395-437, tests/test_shadow_calibration.py:450-475). Neither mechanism is itself named by any requirement in the frozen specification.

---

### U-VERDICT-21 — Shadow CLI entrypoints (backtest and current-shadow)

Files: scripts/shadow.py, tests/test_shadow_cli.py

Rationale: `shadow.py`'s two documented CLI modes and the test module that
drives `main()` itself (rather than the underlying functions) are one
responsibility: the operator-facing entrypoint surface, as opposed to the
calibration logic those modes wrap (U-VERDICT-19/20).

| claim | evidence | requirements |
|---|---|---|
| The `--mode current` path evaluates one live PR head and prints `WOULD_AUTO_APPROVE` or `FAILED_GATES [...]` plus an explicit "performs no mutation" note; it persists no decision record and calls no GitHub mutation transport. | scripts/shadow.py:591-609,753-767, tests/test_shadow_cli.py:242-258 | RQA-NFR-010 |

Also observed: `scripts/shadow.py`'s `__main__` CLI is a documented operator command — `OPERATORS.md`'s entry-point index maps it to §8.2, and §8.2 gives the exact backtest and `--mode current` invocations (OPERATORS.md:557,332-359, scripts/shadow.py:725-788) — and `main()` exits cleanly, with no traceback, when the target repo's config is rejected at onboarding, coercing string-keyed `--verdicts`/`--assessments` JSON objects to integer PR numbers rather than silently discarding them (scripts/shadow.py:76-98,740-751, tests/test_shadow_cli.py:119-124). Neither observation is itself named by any requirement in the frozen specification.
