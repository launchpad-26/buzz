# RQA gap analysis — dispositions: resilience

### U-RESILIENCE-01 — Pre-spend budget reservation and spend accounting
Disposition: rework
Requirements: RQA-FR-021, RQA-FR-022, RQA-FR-039, RQA-BR-012
Root cause: built contrary (RQA-FR-022/RQA-FR-039); not built (RQA-FR-021/RQA-BR-012)
Retain the intent that a reservation is decided before work can spend capacity and that each refusal carries a non-success downgrade. Rework the ceiling decision: it must cover every configured bound, treat reaching a bound as a refusal where required, and distinguish measured consumption from a reservation estimate. The current two-axis, strictly-greater check is a reachable outcome RQA-FR-022 and RQA-FR-039 forbid, while the responsibility itself remains required.

### U-RESILIENCE-02 — Circuit breaker: per-scope failure counting, cooldown and reset
Disposition: keep
Requirements: RQA-FR-038, RQA-NFR-010
Root cause: not built (RQA-FR-038); built contrary (RQA-NFR-010, outside this unit)
Keep the per-scope consecutive-failure counter, persisted cooldown deadline, and explicit reset because RQA-FR-038 requires an unavailable configured route without fallback to stop recoverably rather than repeatedly attempt it. A simpler process-wide boolean or permanent disable cannot preserve independent scopes, establish when retry is permissible, and allow recovery without treating an outage as a successful outcome. RQA-FR-038's unmet credential-observability obligation is outside this breaker mechanism.

### U-RESILIENCE-03 — Provider-diverse fallback recipe ordering
Disposition: salvage
Requirements: RQA-FR-023, RQA-FR-019, RQA-BR-012, RQA-NFR-009
Root cause: not built (RQA-FR-019/RQA-BR-012); - (RQA-FR-023/RQA-NFR-009)
Salvage the stable ordering mechanism that preserves an explicitly configured candidate list's relative order while assigning its declared fallback tier. RQA-FR-023 and RQA-NFR-009 need an already-configured alternative to be selected predictably, and a simpler unordered or re-derived list could select an unconfigured route or erase the operator's order. Do not retain the hard-coded subscription/cost recipe policy: RQA-FR-019 requires every strategy and higher-cost method to follow stated assurance, which this unit does not consult.

### U-RESILIENCE-04 — Error taxonomy: disposition classification, typed exceptions, and the coarse failure vocabulary the estate acts on
Disposition: rework
Requirements: RQA-BR-009, RQA-FR-023, RQA-NFR-010
Root cause: not built (RQA-BR-009); - (RQA-FR-023); built contrary (RQA-NFR-010, outside this unit)
Retain the intent of a typed, ordered failure vocabulary that lets a caller distinguish retry, provider retirement, and job blocking without a human. Rework the taxonomy around the required automated-review and check attribution vocabulary: the three legacy dispositions and the nine fine-grained ones are not the six-value attribution RQA-BR-009 names, and the typed signal `dispatcher.degrade()` raises plus the coarse constants `panel.py` branches on are what the estate actually acts on, so the rework must preserve those consumers while replacing the vocabulary they carry.

This unit was split on 2026-09-08 and the disposition metadata registry left it. `RES04-META-UNREACHED` asked whether the register was right to credit `CATEGORY_META` as consumed safe-degradation signalling; the maintainer ruled that it is not, that the registry is `bin` rather than reworked into the active path, and that `panel.py` consuming the coarse constants directly (scripts/panel.py:51-58, scripts/panel.py:381-403) is the real mechanism. Those are his citations, and for completeness they cover the import block, the `JobBlockingError` re-raise at scripts/panel.py:383, the TRANSIENT return at scripts/panel.py:393 and the PROVIDER_TERMINAL return at scripts/panel.py:404; the two CANDIDATE_TERMINAL returns sit just past their end, at scripts/panel.py:413 and scripts/panel.py:424. The registry is therefore U-RESILIENCE-17, appended at the end of this file and of `../evidence/resilience.md` so that no existing unit id moves. Per methodology §4 the third separability test is what fires: the registry could be removed and every responsibility named above would still be required, because `dispatcher.degrade()` and `panel.py`'s fallback loop consume the typed exception and the coarse constants and never the registry. `scripts/errors.py` stays in both units' scope with each naming its own line ranges, as §4 requires of two units of one file; `tests/test_fallback.py` and `tests/test_degradation.py` stay here, because what they exercise is the typed `JobBlockingError` path.

`RES04-PREJUDGED-ESCALATION` is resolved by the same ruling, on 2026-09-08. A review seat had objected that the sentence then standing here — "make its safe-degradation semantics the active path rather than a parallel registry" — asserted as settled the very fact the escalation parked, namely that `CATEGORY_META` is not the active path; a second seat passed the same lines because the marker one sentence later kept the question live. The objection was recorded rather than acted on precisely because whoever answered the escalation would answer it, and that is what happened: the ruling settles the presupposed question, and settles it in the direction the objection said must not be presupposed, so the offending sentence is gone rather than merely reworded. It was never given a marker of its own, and it needs none now.

### U-RESILIENCE-05 — Advisory review comment: content and posting
Disposition: rework
Requirements: RQA-BR-005, RQA-BR-008, RQA-BR-014, RQA-FR-012, RQA-NFR-010, RQA-NFR-017, RQA-NFR-026
Root cause: not built (RQA-BR-005/RQA-BR-008/RQA-BR-014/RQA-FR-012); built contrary (RQA-NFR-010/RQA-NFR-017); not built (RQA-NFR-026, whose absent merge activity the maintainer's 2026-09-08 ruling records as a partial gap)
Retain the intent that advisory output is visibly non-authoritative, separates corroborated from unconfirmed findings, and records a withheld or failed post rather than disappearing silently. Rework its required record rendering and authority boundary: the current body cannot distinguish the finding categories or per-obligation evidence states the record needs, and the wider authority design permits activities without their own enforcement. The compliant comment gate alone cannot make the whole responsibility satisfy those requirements.

### U-RESILIENCE-06 — Durable ledger: append-only recording and revision reconstruction
Disposition: rework
Requirements: RQA-BR-003, RQA-BR-014, RQA-FR-012, RQA-NFR-028
Root cause: built against superseded intent (RQA-BR-003); not built (RQA-BR-014/RQA-FR-012/RQA-NFR-028)
Retain the intent of validating revision identity before append, recording corrections as new entries, and reconstructing one revision without borrowing another's record. Rework the durable provenance responsibility because an append-only SQLite row without tamper detection, protocol identity, or reliable failure handling cannot establish an authoritative record under RQA-NFR-028 and RQA-FR-012. Append-only storage alone is insufficient when an unauthorised change is accepted as authentic.

### U-RESILIENCE-07 — Explain: read-only operator reconstruction of a job's outcome
Disposition: keep
Requirements: RQA-BR-003, RQA-FR-012
Root cause: built against superseded intent (RQA-BR-003); not built (RQA-FR-012)
Keep the read-only, single-command reconstruction boundary: RQA-FR-012 requires one command to return the review record without contacting GitHub, invoking a model, or mutating the job. A simpler status summary or a command that consults live external state cannot reconstruct the exact historical outcome from its authoritative provenance. The missing protocol field and reliable ledger append are ledger/dispatch gaps; once the required record exists, this reader can surface it without changing its responsibility.

### U-RESILIENCE-08 — Structured JSONL job trace and its safe artifact writers
Disposition: keep
Requirements: RQA-BR-003, RQA-FR-021, RQA-NFR-010
Root cause: built against superseded intent (RQA-BR-003); not built (RQA-FR-021); built contrary (RQA-NFR-010, outside this unit)
Keep the canonical event vocabulary plus the cross-process JSONL lock, exclusive attempt-number allocation, and temp-file replacement. RQA-BR-003 needs a common trace consumer can inspect, while RQA-NFR-010 cannot accept an interleaved JSON object or partially visible attempt artifact as a valid outcome. A plain append or process-local counter is materially simpler but fails under concurrent writers; the missing cost-measurement provenance and ledger failure path are separate gaps.

### U-RESILIENCE-09 — Config normalization
Disposition: keep
Requirements: RQA-FR-004, RQA-NFR-005
Root cause: -
Keep normalize-on-load plus per-call re-reading because RQA-FR-004 and RQA-NFR-005 require the next review to use an edited repository policy without a build, reinstall, deploy, or explicit cache invalidation. A simpler cached configuration would make freshness depend on a reload path, while removing shape normalization would push legacy-shape handling into each consumer and make the same next-review guarantee non-uniform.

### U-RESILIENCE-10 — GitHub token resolution
Disposition: keep
Requirements: RQA-NFR-006
Root cause: -
Keep local environment-first credential resolution with the existing local GitHub CLI fallback and an explicit failure when neither source exists. RQA-NFR-006 requires one contributor to operate locally without a hosted RQA credential service; requiring a newly provisioned single token source would add an out-of-band dependency instead of using the contributor's existing local authentication. Proceeding anonymously is not a simpler complete workflow because it fails only later on platform access.

### U-RESILIENCE-11 — Durable SQLite state: persistence-failure typing and the transition guard
Disposition: keep
Requirements: RQA-NFR-010
Root cause: built contrary (outside this unit)
Keep the wrapped persistence failures, pre-write transition guard, and non-blocking state-directory lock. RQA-NFR-010 needs a storage failure or illegal transition to stop before an ambiguous state write, and it needs concurrent sweeps not to mutate one state directory simultaneously. A raw driver exception plus an unlocked write path leaves every caller to invent its own containment; a PID-file lock also cannot provide the kernel crash-release property of the advisory lock. The conflicting ledger-swallow path is outside this unit.

### U-RESILIENCE-12 — The sole GitHub REST read transport (GithubRest)
Disposition: keep
Requirements: RQA-FR-020, RQA-FR-021
Root cause: not built (RQA-FR-020/RQA-FR-021), in each case for obligations outside this unit
Keep the URL-scoped ETag/body cache, cached-Link pagination discipline, and response-header rate-limit recording. RQA-FR-020 needs a valid REST result reused rather than regenerated, including a cached page's next cursor; a simpler unconditional fetch discards that valid result, and a cache that omits Link loses a paginated traversal after a 304. RQA-FR-021's missing actual token provenance and FR-020's missing reviewer-result reuse are separate responsibilities.

### U-RESILIENCE-13 — Stable job and mutation identity
Disposition: keep
Requirements: RQA-BR-007
Root cause: -
Keep the deterministic hash of the logical job or mutation inputs. RQA-BR-007 needs independently arriving reconciliation or mutation attempts to resolve to the same identity before the uniqueness/deduplication controls can reject duplicate work. A generated UUID or database sequence is simpler locally but assigns the same unchanged revision a fresh identity on each attempt, so it cannot establish that the work is already the same. RQA-FR-005's material-change obligation is not served by this mechanism; the register expressly corrects that inherited mapping.

### U-RESILIENCE-14 — Crash-safe durable file write
Disposition: keep
Requirements: RQA-NFR-010
Root cause: built contrary (outside this unit)
Keep same-directory temporary writing, flush/fsync, and atomic replacement. RQA-NFR-010 requires an interrupted review not to leave a corrupted artifact accepted as a completed one; a direct write to the destination can expose a truncated file if the process stops between writes. A rename without a same-directory prepared file also loses the atomic visibility property required for readers to distinguish old complete content from new complete content. The conflicting authoritative ledger continuation is elsewhere.

### U-RESILIENCE-15 — Untrusted-content nonce envelope
Disposition: keep
Requirements: RQA-NFR-015
Root cause: not built (outside this unit)
Keep the per-run nonce-bound opening and closing envelope as the boundary for untrusted PR-derived evidence. RQA-NFR-015 needs a reviewer prompt to distinguish externally supplied data from the surrounding control text; a fixed delimiter is materially simpler but can be forged by PR content, whereas a per-run nonce lets the receiver identify the exact envelope it created. The absent instruction-handling rule in the prompt remains a separate gap and must be added without dropping this boundary.

### U-RESILIENCE-16 — Unified CLI config-resolution entrypoint helper
Disposition: keep
Requirements: RQA-FR-016, RQA-NFR-005, RQA-NFR-006
Root cause: not built (RQA-FR-016); - (RQA-NFR-005/RQA-NFR-006)
Keep the shared config-resolution and State construction boundary. RQA-NFR-005 requires every CLI invocation to see the current repository configuration, and RQA-NFR-006 requires locally run commands to share one authoritative state directory; a simpler per-command default calculation can split one contributor's records across directories and make a later command unable to see a job created by another. RQA-FR-016 remains a missing, distinct per-PR disposition command, not a defect corrected by discarding this helper.

### U-RESILIENCE-17 — Disposition metadata registry: retryability, authority impact and escalation per disposition
Disposition: bin
Requirements: RQA-NFR-010
Root cause: built contrary (RQA-NFR-010, outside this unit)
Remove the registry. This is §7's second limb — the requirement it serves is better met without it — and not the first: `RQA-NFR-010` genuinely bears on the claim, because `authority_impact` is an attempt at exactly the never-partially-authoritative outcome that requirement governs. The maintainer ruled on 2026-09-08, closing `RES04-META-UNREACHED`, that the registry is binned rather than reworked into the active path, on this reasoning: the product-source consumer search returns nothing outside `errors.py` (exit 1, as quoted in this unit's evidence), and #2006 §6 requires every retained component to materially serve a criterion with no materially simpler approach sufficing — a registry with no consumers fails that on its face. The obligations it appeared to serve are outcome properties, not vocabulary: AC11 forbids a resource bound producing a successful review, and AC12 requires either a configured fallback or a clear, safe, recoverable non-success state. Those are provable only where terminal outcomes are minted, so degradation becomes an obligation of the single place that produces non-success outcomes, and is not a registry other parts consult.

Where the obligation lands instead, so nothing is dropped along with the code: the reachable safe-stop and refusal behaviour the register credits for `RQA-NFR-010` is in the units that mint outcomes — the typed `JobBlockingError` refusal before any state write (U-RESILIENCE-04), the wrapped persistence failures and transition guard (U-RESILIENCE-11), the crash-safe durable write (U-RESILIENCE-14) and the ledger and JSONL paths the register's own row names (U-DISPATCH-19, U-DISPATCH-20, U-DISPATCH-21). `RQA-NFR-010` is `conflicting` and not `fit`, so §7's bar on binning the only unit serving a `fit` requirement does not arise at all — and this unit is far from the only one serving that row. Quoted as the search returned, run from `launchpad/skills/review-queue-automation/`:

```
$ grep -rc "^Requirements:.*RQA-NFR-010" gap/dispositions/*.md
gap/dispositions/authority.md:6
gap/dispositions/dispatch.md:16
gap/dispositions/docs.md:9
gap/dispositions/policy.md:0
gap/dispositions/queue.md:7
gap/dispositions/resilience.md:7
gap/dispositions/verdict.md:3
```

6 + 16 + 9 + 0 + 7 + 7 + 3 = 48 units name `RQA-NFR-010` on their `Requirements:` line, this one included, so 47 others serve the row. Corrected on re-review: an earlier revision of this paragraph said "six other units", which was the number of units the preceding sentence enumerates rather than the number serving the row. It did not reproduce against its own subject, and a bare figure a reader can only check by redoing the search is what the standing rule forbids.
