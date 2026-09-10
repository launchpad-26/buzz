# RQA gap dispositions — docs cluster

### U-DOCS-01 — Authorization/refusal and single-transport GitHub boundary
Disposition: rework
Requirements: RQA-NFR-017, RQA-NFR-032
Root cause: RQA-NFR-017 is conflicting (built contrary); RQA-NFR-032 is fit.
Retain the persisted-decision and fixed-event intent that satisfies NFR-032, but replace the documented authority boundary. Its activity vocabulary and enforcement claim follow code that omits required merge authority, includes unmatched triage, and leaves declared activities unenforced.

### U-DOCS-02 — Pipeline entrypoint and escalation-on-`human_required` documentation
Disposition: rework
Requirements: RQA-NFR-006, RQA-FR-026, RQA-BR-013
Root cause: RQA-NFR-006 is fit; RQA-FR-026 is partial gap (not built); RQA-BR-013 is conflicting (built contrary).
Retain the complete local command entrypoint, but revise escalation documentation to distinguish judgement-requiring escalation from mechanical gate failure and to name the concrete cause records FR-026 requires.

### U-DOCS-03 — Entry-point index: operator-invoked commands vs. internal modules
Disposition: keep
Requirements: RQA-NFR-006
Root cause: RQA-NFR-006 is fit.
The runbook-linked command table and explicit non-operator disclaimer serve NFR-006 by defining the supported local surface without exposing debugging modules as state-owning commands. A simpler executable-file list or generated help output cannot distinguish invocable code from an operator-authorised procedure, so it would defeat the documented ownership boundary.

### U-DOCS-04 — Approval modes and per-activity configurable authority ladder
Disposition: rework
Requirements: RQA-NFR-017, RQA-NFR-026, RQA-FR-009
Root cause: RQA-NFR-017 is conflicting (built contrary); RQA-NFR-026 is a partial gap (not built); RQA-FR-009 is fit.
Retain conjunctive mode-and-activity gating, fail-closed defaults, and the independent request-changes deny conditions. Rework the published activity vocabulary and enforcement account: the existing ladder documents controls that do not correspond to the required activities or product call paths. The documented fail-closed defaults serve the part of RQA-NFR-026 that is met — the five activities the code declares — and the same vocabulary defect is why the rest of that requirement is not: `merge` is documented nowhere as an activity because it is not one, which is what the maintainer's 2026-09-08 ruling made a `partial gap` rather than a `fit`.

### U-DOCS-05 — Human decisions, execution states, and the human-approval CLI
Disposition: rework
Requirements: RQA-FR-013, RQA-BR-011
Root cause: both requirements are partial gaps (not built).
Retain live-head revalidation and the explicit recorded-head exception, but rebuild the documented record contract around fields the authoritative decision record can carry. Actor/basis persistence and product-reached execution-state handling are absent rather than established by the current test-only helper.

### U-DOCS-06 — Documented job lifecycle / state model
Disposition: rework
Requirements: RQA-FR-016, RQA-BR-007
Root cause: RQA-FR-016 is a full gap (not built); RQA-BR-007 is fit.
Retain the internal transition model and head-change supersession rule. Rework the account so it does not present internal job states as the required per-PR disposition vocabulary, which no reachable command currently exposes or maps.

### U-DOCS-07 — Model routing and fallback policy documentation
Disposition: keep
Requirements: RQA-NFR-009, RQA-FR-023, RQA-FR-024
Root cause: all requirements are fit.
The ordered configured-rung and exhaustion-to-human account serves the no-unconfigured-substitution guarantees. A shorter list of preferred models or configuration defaults cannot state the negative boundary when a route is unavailable; the explicit policy-versus-enforcement distinction prevents readers from treating the fallback table as runtime control.

### U-DOCS-08 — Required/achieved assurance computation documentation
Disposition: rework
Requirements: RQA-BR-008, RQA-BR-014
Root cause: both requirements are partial gaps (not built).
Retain the required-versus-achieved distinction, freshness effect, and hard approval preconditions. Rework the published assurance account to include the per-obligation evidence-state vocabulary missing from FR-010; aggregate completeness and uncertainty alone cannot demonstrate which obligations were verified or examined.

### U-DOCS-09 — Panel completeness, `MISSING_EVIDENCE`, and stale-verdict clearing documentation
Disposition: keep
Requirements: RQA-FR-011, RQA-FR-037
Root cause: both requirements are conflicting (built contrary) through the separate human-resume bypass.
The slot-count completeness predicate and fresh-attempt clearing remain required safeguards on the automatic path. A simpler present-verdict count cannot prevent a reattempt from consuming stale lower-profile output, whereas clearing all slot files before assessment makes incomplete evidence incapable of becoming a successful panel result.

### U-DOCS-10 — Policy-as-data validation and atomic snapshot activation documentation
Disposition: rework
Requirements: RQA-NFR-005, RQA-NFR-018
Root cause: RQA-NFR-005 is fit; RQA-NFR-018 is conflicting (built contrary).
Retain validation-before-activation and content-hash pinning intent, but rework the document around the caller-visible failure path. A build rejection does not preserve authority when snapshot resolution falls back to an unclamped local configuration.

### U-DOCS-11 — Shadow backtest / current-head calibration contract
Disposition: keep
Requirements: RQA-FR-011, RQA-FR-037, RQA-FR-010, RQA-NFR-010
Root cause: RQA-FR-011, RQA-FR-037, and RQA-NFR-010 are conflicting (built contrary); RQA-FR-010 is a full gap (not built), all outside this shadow mechanism.
The in-memory shadow clamp, explicit evidence construction, and no-persistence/no-GitHub calibration contract serve the non-manufactured-success side of FR-037. A simpler historical report would not force approval mode to shadow or fail absent historical facts closed, and could therefore exercise live authority while appearing read-only.

### U-DOCS-12 — Canary gating documentation
Disposition: keep
Requirements: RQA-NFR-026
Root cause: RQA-NFR-026 is a partial gap (not built).
The table-over-config precedence documents the actual two-source canary gate required for fail-closed operation. A single flag description cannot tell an operator which source governs when they disagree, while that distinction is necessary to avoid treating a lane as continuously dispatchable before its authoritative canary row is approved. The requirement is `partial gap` after the maintainer's 2026-09-08 ruling, and what this unit serves is its met portion — the restrictive default for a gate the system actually has. The unmet portion is the `merge` activity, which is absent from the activity model altogether and which no documentation of a default could supply.

### U-DOCS-13 — Author-triage isolated-worktree claim (documentation with no implementing code)
Disposition: rework
Requirements: RQA-NFR-020, RQA-BR-006, RQA-FR-017, RQA-FR-018
Root cause: all are full gaps built then orphaned.
Retain the isolated, head-pinned, non-force-push remediation intent, but remove the assertion that the author-triage lane performs it. The worktree mechanism exists only behind test callers and no product entrypoint invokes the described remediation cycle.

### U-DOCS-14 — Snapshot-pinning guarantee documentation
Disposition: rework
Requirements: RQA-NFR-005, RQA-BR-003, RQA-NFR-018
Root cause: RQA-NFR-005 is fit; the related RQA-BR-003 is a partial gap built against superseded intent and RQA-NFR-018 is conflicting built contrary.
Retain explicit pinned-versus-unpinned reporting, but rework the dispatchable-unpinned contract. It preserves optional-policy intent superseded by the frozen specification and cannot be presented as an acceptable activation guarantee alongside the unclamped snapshot failure path.

### U-DOCS-15 — Budget reserve-before-spend and rate-limit control documentation
Disposition: rework
Requirements: RQA-BR-012, RQA-FR-021
Root cause: both requirements are partial gaps (not built).
Retain reserve-before-panel ordering and refusal before projected overrun. Rework the cost account because reservation is recorded as spend without a measured-token marker, and no policy-assurance-to-consumption comparison exists.

### U-DOCS-16 — "Why did this PR get this outcome" explain-procedure documentation
Disposition: keep
Requirements: RQA-FR-012
Root cause: RQA-FR-012 is a partial gap (not built).
The read-only reconstruction procedure serves FR-012's existing explainability obligation: it imports neither GitHub transport nor a model runner and does not mutate job state. A simpler status display would not reconstruct the decision basis while preserving that no-call/no-spend boundary; protocol recording and durable ledger writes are additive writer-side gaps.

### U-DOCS-17 — Job-trace event schema and redaction documentation
Disposition: rework
Requirements: RQA-FR-012
Root cause: RQA-FR-012 is a partial gap (not built).
Retain the reconstruction event vocabulary and closed redaction allowlist, but rework the trace contract to carry the missing protocol identity and to describe failure durability honestly. The current event list cannot make an incomplete, silently dropped ledger entry reconstructable.

### U-DOCS-18 — Retention purge-with-manifest guarantee documentation
Disposition: bin
Requirements: -
Root cause: no frozen requirement bears on this claim — `br.md:143` records that wave 1's RQA-BR-003 tag on `U-DOCS-18` ("retention manifests") is "not inherited here".
A `-` requirements cell makes this unit a bin candidate as a starting point, and nothing argues it off that starting point: BR-003 obliges a persisted performer/protocol/basis record, which a manifest-before-delete purge does not establish, and no other register row depends on retention documentation. What is lost is the destructive-maintenance walkthrough for the `retention` command; the code-level purge behaviour remains assessed in its own cluster, so binning this documentation removes no requirement's only support.

### U-DOCS-19 — Recovery: lease release without replay documentation
Disposition: keep
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is conflicting (built contrary) through swallowed ledger writes, not recovery.
The state-directory-scoped lease release and active-worker safe-stop rules preserve the no-replay recovery invariant. A blanket lease clear would release work owned elsewhere and miss stranded active jobs lacking lease rows; the explicit status exclusions are what prevent recovery from stopping legitimate waiting states.

### U-DOCS-20 — Backup, health, and cooldown-reset: local-only maintenance commands documentation
Disposition: bin
Requirements: -
Root cause: no frozen requirement bears on this claim — `br.md:143` records that wave 1's RQA-BR-003 tag on `U-DOCS-20` ("local maintenance commands") is "not inherited here".
A `-` requirements cell makes this unit a bin candidate as a starting point, and the case for keeping it does not arise: command locality establishes that `backup`, `health` and `cooldown-reset` touch no pull request, which is not the performer/protocol/basis record BR-003 requires, and no other register row rests on this documentation. What is lost is the descriptive walkthrough of three local maintenance commands, none of which any frozen requirement obliges the estate to document.

### U-DOCS-21 — Strategy-metadata field-liveness audit documentation
Disposition: rework
Requirements: RQA-FR-019
Root cause: RQA-FR-019 is a partial gap (not built).
Retain field-liveness discipline and the consumer inventory, but rework the claim that a CI-time audit is runtime protection. The missing policy-assurance comparison means deterministic strategy metadata cannot yet show that the selected method is no more costly than required.

### U-DOCS-22 — Documentation-to-code drift detection (`test_docs_contract.py`)
Disposition: bin
Requirements: -
Root cause: no frozen requirement maps to this suite (DOCS-FR001 ruling).
No frozen requirement obliges documentation-to-code naming checks. Removing this suite loses textual consistency assertions, but the frozen specification does not depend on that responsibility and the maintainer explicitly struck the nearest-fit FR-001 mapping.

### U-DOCS-23 — Fixture-free test harness: discovery/execution (run_all.py)
Disposition: keep
Requirements: RQA-NFR-006
Root cause: RQA-NFR-006 is fit.
The tracked runner provides the local whole-suite invocation NFR-006 needs, importing every test module and refusing a required fixture argument rather than silently narrowing execution. A generic file loop cannot prove which callable tests ran or reject a newly introduced fixture dependency that would make the documented invocation incomplete.

### U-DOCS-24 — conftest.py guards are dead under the tracked runner
Disposition: salvage
Requirements: -
Root cause: no frozen requirement bears on this claim — `nfr.md:406` records that the RQA-NFR-006 tag on `U-DOCS-24` bears on test-suite isolation, "not on whether one contributor can run the workflow locally, so it is not inherited here".
A `-` requirements cell makes this a bin candidate as a starting point, and the argument off that starting point is a hazard the estate creates for itself rather than a specification clause: the harness is the one place where the real GitHub transports are constructed with the developer's own environment in scope, and several assessed suites import those modules by name, so a suite that regressed into a live call would authenticate as a real account against a real pull request. The mechanism worth lifting is the pairing of a deliberately non-token-shaped credential with a socket constructor that raises on construction, which turns such a reach into a deterministic failure at the point of the call. No materially simpler approach reaches that: a documented convention or a README warning cannot fail an attempt, and an after-the-fact log cannot prevent the mutation. The module as it stands is not retained, because the documented runner never imports it and the guards therefore never execute.

### U-DOCS-25 — Job-identity determinism coverage (`test_deterministic.py`)
Disposition: keep
Requirements: RQA-BR-007, RQA-FR-005
Root cause: RQA-BR-007 is fit; RQA-FR-005 is a full gap (not built).
The identity differential assertions preserve BR-007's stable repo/PR/head/lane key while making input changes observable. A fixed expected hash or one happy-path job cannot catch an axis being omitted from identity; FR-005's separate proof-of-zero-reviewer-calls gap does not make key determinism dispensable.

### U-DOCS-26 — Nonce-enveloped untrusted content coverage (`test_deterministic.py`)
Disposition: salvage
Requirements: RQA-NFR-015
Root cause: RQA-NFR-015 is a partial gap (not built).
Salvage matching per-invocation open/close nonce delimiters as the specific envelope mechanism. A fixed sentinel can be forged by embedded content and an opening-marker-only test cannot establish closure; the present test must be rebuilt because it does not assert verbatim content retention or address the missing injection-handling protection.

### U-DOCS-27 — Candidate-pool ordering under unavailability coverage (`test_deterministic.py`)
Disposition: keep
Requirements: RQA-NFR-009, RQA-FR-024
Root cause: both requirements are fit.
Configured-order and unavailable-route assertions serve the no-unconfigured-substitution guarantees. A test of only the selected first candidate cannot distinguish exhaustion from an illicit fallback; removing an unavailable configured member is the negative case that proves route choice remains bounded by configuration.

### U-DOCS-28 — Canary-approval default coverage (`test_deterministic.py`)
Disposition: keep
Requirements: RQA-NFR-026
Root cause: RQA-NFR-026 is a partial gap (not built).
The fresh-state assertion establishes the restrictive default before any canary approval exists. A configuration-default check cannot detect an unexpectedly prepopulated authoritative SQLite row, so it cannot establish that a new state directory begins with the dispatch gate closed. That is coverage of the met portion of a `partial gap` requirement: the maintainer's 2026-09-08 ruling leaves the `merge` activity's default unmet because `merge` is not an activity, which no test of the canary table bears on either way.

### U-DOCS-29 — Per-activity authority resolution and fail-closed defaults coverage (phase1)
Disposition: keep
Requirements: RQA-NFR-017, RQA-NFR-026, RQA-NFR-018
Root cause: RQA-NFR-017 and RQA-NFR-018 are conflicting (built contrary); RQA-NFR-026 is a partial gap (not built).
The precedence and hard-gate cases retain NFR-026's fail-closed default guarantee for the five activities the code declares — the portion of that requirement which is met — despite activity-vocabulary and snapshot-fallback defects elsewhere, and despite the absent `merge` activity that makes the row `partial gap` under the maintainer's 2026-09-08 ruling. Checking a static default cannot catch an override losing to an activity-level value or a live mode acting without its gate; those precedence transitions are the required protection.

### U-DOCS-30 — Policy validation and content-hash pinning coverage (phase1)
Disposition: salvage
Requirements: RQA-NFR-018
Root cause: RQA-NFR-018 is conflicting (built contrary).
Salvage canonical-bytes hashing plus monotonic-band validation before a hash is accepted. A version label or post-hash validation cannot prove reproducible policy identity or prevent an incoherent policy from receiving a valid pin; isolated validation coverage must not stand in for the broken snapshot-resolution authority boundary.

### U-DOCS-31 — Atomic snapshot activation and last-known-good retention coverage (phase1)
Disposition: salvage
Requirements: RQA-NFR-018, RQA-NFR-005
Root cause: RQA-NFR-018 is conflicting (built contrary); RQA-NFR-005 is fit.
Salvage byte-and-content-hash comparison of the active payload before and after a rejected candidate. An exception assertion alone cannot detect partial activation, whereas exact unchanged bytes and hash express the last-known-good invariant; build-only coverage must not imply the caller retains the clamp.

### U-DOCS-32 — Required/achieved assurance computation coverage (phase1)
Disposition: keep
Requirements: RQA-BR-008, RQA-BR-014
Root cause: both requirements are partial gaps (not built).
The directional completeness, disagreement, maximum-risk, and blocker-dominance assertions preserve the compatible assurance computation. Fixed arithmetic examples would miss sign inversions or require recalibration churn; the unmet per-obligation evidence-state contract is additive and does not simplify these monotonic safeguards.

### U-DOCS-33 — Request-changes eligibility gate and authority independence coverage (phase2)
Disposition: keep
Requirements: RQA-NFR-017, RQA-FR-009
Root cause: RQA-NFR-017 is conflicting (built contrary); RQA-FR-009 is fit.
Independent denial of each request-changes conjunct serves FR-009's fixed severity-plus-gate model. One failing case could pass a degenerate gate that ignores other conditions; explicit stale, unverified, insufficient-evidence, false, and absent-revalidation cases establish fail-closed conjunction, separate from the activity-set conflict.

### U-DOCS-34 — Lifecycle-transition legality coverage (phase2)
Disposition: keep
Requirements: RQA-FR-011, RQA-FR-037
Root cause: both requirements are conflicting (built contrary) through the separate human-resume bypass.
The transition whitelist prevents direct entry into approval-adjacent states before evidence and assurance stages. Positive-edge testing alone proves no restriction; rejected detected-to-approval and terminal-to-entry edges show the guard is restrictive, while the human authorization bypass that must change is outside this table.

### U-DOCS-35 — Human-decision execution-state tracking coverage (phase2)
Disposition: salvage
Requirements: RQA-FR-013, RQA-NFR-010
Root cause: RQA-FR-013 is a partial gap (not built); RQA-NFR-010 is conflicting (built contrary).
Salvage the closed accepted-state set enforced at write time, so an invalid execution state is unrepresentable rather than merely rejected by a later reader. A free-text state field cannot supply this boundary; the current helper is test-only and belongs outside the eventual actor-and-basis decision record.

### U-DOCS-36 — Reasoning-strategy registry and deterministic selection coverage (phase3)
Disposition: rework
Requirements: RQA-BR-012, RQA-FR-019
Root cause: both requirements are partial gaps (not built).
Retain deterministic strategy selection intent, but rework it to evaluate the strategy and higher-cost method against policy-stated assurance. The current fixed walk is deterministic over internal signals only, so it cannot establish required proportionality.

### U-DOCS-37 — Subscription-first model-route resolution and fallback-loop guard coverage (phase3)
Disposition: keep
Requirements: RQA-NFR-009, RQA-FR-023, RQA-FR-024
Root cause: all requirements are fit.
The exhausted-configured-route and provider-family non-repetition cases prove the required negative fallback boundary. A happy-path first-route check cannot show that failure ends at human rather than an unconfigured provider, so these unavailability cases cannot be replaced by simpler selection coverage.

### U-DOCS-38 — Error-category metadata coverage (phase4)
Disposition: bin
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is conflicting (built contrary), in the swallowed ledger writes the register locates in U-DISPATCH-20, outside this unit.
Remove this coverage with the responsibility it covers. Every assertion in it reads `category_meta` and nothing else — the unknown-category fallback and the closed `authority_impact` vocabulary (tests/test_phase4.py:22-37, tests/test_phase4.py:65-68) — and that registry is `bin` as U-RESILIENCE-17 under the maintainer's 2026-09-08 ruling on `RES04-META-UNREACHED`, having no product consumer at all. Keeping the coverage would restate the error that ruling exists to correct: the safety floor `RQA-NFR-010` requires is an outcome property, provable only where terminal outcomes are minted, not a metadata table's shape. This is §7's second limb — the requirement it serves is better met without it — and `gap-analysis.md` §6.3 already states the general form: coverage that asserts behaviour which does not survive must not be carried over as evidence of anything.

Re-disposed on re-review; it read `keep` before. Two independent grounds, either sufficient. First, the ruling above. Second, and prior to it, §7 on its own terms: this unit's `Requirements:` line names exactly one requirement and its own `Root cause:` line records that requirement as `conflicting`, so every requirement it names is `conflicting` — and §7 makes `keep` for such a unit a contradiction. Padding the `Requirements:` line with a non-`conflicting` id would escape the rule without answering it and is not done here.

Nothing reachable is lost. What survives of `RQA-NFR-010`'s safety floor is covered elsewhere and not by this unit: no assertion here touches the coarse constants `panel.py` branches on (scripts/panel.py:383, scripts/panel.py:393, scripts/panel.py:404, scripts/panel.py:413, scripts/panel.py:424) or the `JobBlockingError` refusal `dispatcher.degrade()` raises before any state write (scripts/dispatcher.py:442). `tests/test_phase4.py` stays mapped through U-DOCS-39 and U-DOCS-40, so no assessed file loses its unit.

### U-DOCS-39 — Job-log schema and redaction coverage (phase4)
Disposition: keep
Requirements: RQA-FR-012
Root cause: RQA-FR-012 is a partial gap (not built). The redaction sub-claim is unmapped — `br.md:143` records that wave 1's RQA-BR-003 tag on `U-DOCS-39` ("log redaction") is "not inherited here" — so this unit is partly `-` and the keep rests on the FR-012 half alone.
For FR-012 the mapped claim is envelope emission: a schema declaration cannot establish that the writer actually emits `schema_version`, the event name and the required envelope fields on every event, and only writing one and reading the persisted line back does, so no simpler check keeps the trace reconstructable. The redaction sub-claim carries no frozen requirement and starts as a bin candidate; it is nonetheless retained because FR-012 makes the persisted trace the reconstruction artefact, and an on-disk artefact that may carry a bearer token is a credential store rather than a record — a dependency on a required behaviour, not an appeal to incumbency. Protocol identity and write-failure durability remain separate trace-contract gaps.

### U-DOCS-40 — Shadow-backtest read-only guarantee and historical-cutoff enforcement coverage (phase4)
Disposition: salvage
Requirements: RQA-FR-037
Root cause: RQA-FR-037 is conflicting (built contrary) through the separate human-resume bypass.
Salvage the decision that cutoff facts are pinned to the historical sample's own head and file set. Attribute-existence checks cannot prove either entrypoint is read-only or enforces the cutoff, so the current superficial suite must not be retained as coverage of that guarantee.

### U-DOCS-41 — Panel completion and fallback/stale-verdict handling coverage (regression)
Disposition: keep
Requirements: RQA-FR-011, RQA-FR-037, RQA-NFR-010
Root cause: all three are conflicting (built contrary) through paths outside panel completeness.
Missing-slot, fallback, and stale-file-removal cases preserve the automatic path's no-manufactured-success guarantee. A completed-panel happy path cannot show stale output is excluded when every candidate fails; asserting no signal and removal before degraded draft is the non-simplifiable safety boundary.

### U-DOCS-42 — Assurance-profile floor for sensitive paths and large diffs coverage (regression)
Disposition: keep
Requirements: RQA-BR-014, RQA-BR-008
Root cause: both requirements are partial gaps (not built).
The floor assertions preserve policy-sensitive minimum capability, effort, and independence without freezing a maximum. Equality expectations would reject legitimate profile escalation while a plain-change test would miss protected-path under-review; the missing evidence-state vocabulary is an additive gap.

### U-DOCS-43 — Risk banding coverage (repairs)
Disposition: keep
Requirements: RQA-BR-014, RQA-NFR-018
Root cause: RQA-BR-014 is a partial gap (not built); RQA-NFR-018 is conflicting (built contrary) through snapshot fallback.
Boundary placement, maximum-RPN aggregation, and monotonic-band rejection preserve deterministic risk classification. Average-risk coverage would dilute a severe failure mode and interior values miss threshold errors; snapshot authority widening is separate from the numeric band mechanism.

### U-DOCS-44 — Approval-gate conjunction across live/shadow/disabled dispositions coverage (repairs)
Disposition: keep
Requirements: RQA-FR-009, RQA-NFR-017
Root cause: RQA-FR-009 is fit; RQA-NFR-017 is conflicting (built contrary).
The gate conjunction and no-decision-row cases protect FR-009 across live, shadow, and disabled modes. A returned-disposition assertion cannot detect a dormant eligible record persisted in a non-live mode; the activity-vocabulary conflict is separate from the approve gate that this suite exercises.

### U-DOCS-45 — Mutation-event fixation and approval-record-required guard coverage (repairs)
Disposition: keep
Requirements: RQA-NFR-017, RQA-NFR-032
Root cause: RQA-NFR-017 is conflicting (built contrary); RQA-NFR-032 is fit.
For NFR-032 the property is that the submitted review event is not caller-controlled, and the load-bearing assertion is the literal `event:COMMENT`/`event:APPROVE` inside the GraphQL text: checking `fixed_event_of`'s return value alone would pass on a template that interpolates the event from a variable, so no simpler check establishes it. This is a satisfaction claim this unit makes rather than one the register already records — `nfr.md:391` credits only `U-DOCS-01` in NFR-032's evidence. For NFR-017 the same suite's `ApprovalRecordRequiredError` on an absent or empty decision dict is a refusal at the executor's own entry rather than at its callers, which is the only placement a newly added caller cannot bypass; the activity-vocabulary conflict NFR-017 records is separate from this mutation-specific safeguard.

### U-DOCS-46 — Lease claim assigns the GitHub user node id, not the PR node id (repairs)
Disposition: bin
Requirements: -
Root cause: no frozen requirement maps to this lease node-id check (DOCS-BR003 ruling).
No frozen requirement obliges this particular REST assignment representation. Removing the test loses the swapped-node-id regression check, but the maintainer explicitly struck BR-003 and the evidence identifies no other specification obligation for the behavior.

### U-DOCS-47 — State-transition guard coverage (repairs)
Disposition: keep
Requirements: RQA-FR-011, RQA-FR-037
Root cause: both requirements are conflicting (built contrary) through the separate human-resume bypass.
Creation-only-at-detected, terminal refusal, unknown-name refusal, and declared-edge controls preserve a genuine transition whitelist. Positive transition coverage alone would not reveal an arbitrary action entry; the rejected None-to-action case proves a new job cannot be manufactured directly into authority.

### U-DOCS-48 — Verdict-signal parsing coverage (repairs)
Disposition: keep
Requirements: RQA-FR-010, RQA-FR-037
Root cause: RQA-FR-010 is a full gap (not built); RQA-FR-037 is conflicting (built contrary).
Valid-JSON-object-only signal parsing preserves the fail-closed verdict boundary. Substring matching would treat prose such as a negated signal as authority, while a lenient malformed-input fallback could manufacture a default disposition; the evidence-state vocabulary remains a separate missing contract.

### U-DOCS-49 — Unknown-job and missing-evidence classification coverage (repairs)
Disposition: keep
Requirements: RQA-FR-010, RQA-NFR-010
Root cause: RQA-FR-010 is a full gap (not built); RQA-NFR-010 is conflicting (built contrary).
The no-phantom-row and absent-status assertions protect against partial authority on an unknown job. An upsert is simpler but creates the object it was asked to transition; requiring both an error and unchanged absent state proves no authoritative record was written before failure.

### U-DOCS-50 — REST ETag 304 pagination via `common.GithubRest` (repairs)
Disposition: keep
Requirements: RQA-NFR-003
Root cause: RQA-NFR-003 is a partial gap (not built).
Two-page cached-Link pagination through a 304 preserves the standard integration behavior NFR-003 meets. A one-page or non-304 test cannot distinguish a correct full walk from a truncating early stop; hard-coded runner CLI contracts are a separate, additive boundary gap.

### U-DOCS-51 — Onboarding config generation and no-overwrite guarantee coverage (integration)
Disposition: keep
Requirements: RQA-NFR-006
Root cause: RQA-NFR-006 is fit.
Loadable generated configuration plus refusal to overwrite an existing slug preserve a contributor's local setup boundary. A successful initial init alone cannot show a second invocation protects the established repository identity; the refusal-and-unchanged-slug pair is necessary to distinguish non-destructive onboarding.

### U-DOCS-52 — Human-queue pending/expiry handling coverage (integration)
Disposition: keep
Requirements: RQA-FR-011
Root cause: RQA-FR-011 is conflicting (built contrary) through the separate human-resume bypass.
Distinct concurrent pending requests and explicit expiry state preserve the queue-side prerequisites for an approval that may proceed. A single request test cannot expose cross-PR state interference, and return disposition alone cannot establish that an expired record is distinguishable for the guarded resume path.

### U-DOCS-53 — Worktree create/clean exercised only under a fake runner, no production caller (integration)
Disposition: salvage
Requirements: RQA-NFR-020
Root cause: RQA-NFR-020 is a full gap built then orphaned.
Salvage explicit-head worktree creation at `rqa/<job>` and idempotent cleanup as the mechanism that pins remediation to a revision and makes cleanup safely repeatable. A bare branch argument or cleanup that raises on an already-clean state cannot supply those guarantees; the fake-runner-only test must not represent product reachability.

### U-DOCS-54 — Shadow-mode evaluation persists no decision record coverage (integration)
Disposition: keep
Requirements: RQA-FR-037
Root cause: RQA-FR-037 is conflicting (built contrary) through the separate human-resume bypass.
The otherwise-clean shadow evaluation with an empty decision table proves shadow cannot leave an executable-looking success behind. Checking only the returned `shadow` value would pass even if an eligible row were silently persisted; state absence is the necessary non-manufactured-success assertion.

### U-DOCS-55 — Concurrent attempt-log writers allocate distinct artifact numbers coverage (integration)
Disposition: keep
Requirements: RQA-NFR-010
Root cause: RQA-NFR-010 is conflicting (built contrary) through swallowed ledger writes.
Concurrent distinct-number and valid-JSON assertions preserve artifact integrity under contention. Sequential logging cannot expose a read-then-increment race, and uniqueness alone cannot rule out a corrupted file; both properties are needed to prevent partially authoritative attempt evidence.

### U-DOCS-56 — Dispatcher terminal-outcome to GitHub-mutation-set mapping coverage (e2e)
Disposition: rework
Requirements: RQA-FR-028, RQA-FR-037, RQA-NFR-010
Root cause: all are conflicting (built contrary).
Retain exact successfully-recorded mutation-set accounting and its distinction from an attempted mutation, but rework the terminal expectations. The suite currently pins advisory outcomes that FR-028 forbids for satisfied reviews and therefore defends a reachable contrary path.

### U-DOCS-57 — Cross-cutting dispatch invariants: lease release, conjunctive authority, explainability coverage (e2e)
Disposition: keep
Requirements: RQA-NFR-010, RQA-NFR-017, RQA-FR-012
Root cause: RQA-NFR-010 and RQA-NFR-017 are conflicting (built contrary); RQA-FR-012 is a partial gap (not built).
Paired lease claim/release counts, authority-mode mutation absence, and explained final decisions preserve cross-terminal-path invariants. For NFR-010, checking either lease half alone misses leaks or unclaimed releases. For NFR-017, one authority-mode case cannot prove conjunction across modes. For FR-012, asserting explainability on a single representative outcome would leave a terminal path whose reconstruction returns a null `final_decision` undetected; requiring `explained: True` with a non-null decision across three distinct outcomes is what makes reconstructability a property of every terminal shape rather than of the path that happens to be exercised. Ledger completeness remains a separate writer-side defect.

### U-DOCS-58 — Protected-trigger detection coverage (repairs)
Disposition: keep
Requirements: RQA-BR-014
Root cause: RQA-BR-014 is a partial gap (not built).
Configured-regex matching and first-match naming preserve deterministic protected-trigger explanation. A boolean-only assertion cannot establish which policy trigger caused escalation, and prefix matching cannot represent the configured regex patterns; the missing per-obligation evidence-state vocabulary is additive.
