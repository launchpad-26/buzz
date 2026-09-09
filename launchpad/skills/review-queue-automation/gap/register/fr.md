# RQA gap register — functional requirements

The 39 functional requirements of the frozen specification, one row each. What the system must do — the functional obligations.
Sibling registers hold the other two classes:
[`br.md`](br.md), [`fr.md`](fr.md), [`nfr.md`](nfr.md).

**This file is the skeleton.** Every requirement of this class has a row, in the
order the specification lists them, with `gap degree`, `root cause`, `evidence`
and `depends on` set to `TBD`. A `TBD` means *not yet evaluated* — it is not a
degree, and it is not a claim that the requirement is met or unmet. The
evaluation lane replaces the four `TBD` cells of each row in place, using the
definitions in [`methodology.md`](../methodology.md); it does not restructure the
table, reorder it, add columns to it, or write a new file.

## Why the register is keyed by requirement ID

The requirement identifier is the only key in this analysis that is stable
across revisions. Files get renamed, split and deleted; clusters and disposition
units are this analysis's own constructs and will change when the estate does;
requirement IDs are fixed by the frozen specification, which
[`methodology.md`](../methodology.md) §1 forbids this analysis to edit. Keying on
the ID gives three properties the analysis depends on:

- **Completeness is checkable.** 14 + 39 + 33 = 86 rows against 86 `### RQA-…`
  headings in
  [`requirements-specification.md`](../../requirements/requirements-specification.md).
  A requirement with no row is a mechanical failure, not a judgement call.
- **A row is addressable.** Any later document, issue or decision cites
  `RQA-FR-NNN` and lands on exactly one row.
- **Re-evaluation is diffable.** Re-running the analysis at a later revision
  updates the same rows, so the diff shows what *changed about the assessment*
  rather than what changed about the document's layout.

## How a row is updated

The register is **updated in place, never superseded by a new document.** There
is one register per requirement class, for the life of this analysis.

1. Re-read the requirement in the frozen specification and the code it concerns
   at the revision being evaluated.
2. Apply the "implements" test ([`methodology.md`](../methodology.md) §2), then set
   `gap degree` (§5), `root cause` (§6) and `evidence` (§3) from what that test
   found. `root cause` is `-` when and only when `gap degree` is `fit`.
3. Set `depends on` to the requirement IDs whose gaps must close before this
   one's can (§9), or `-`. Never a priority, never a sequence number.
4. **Set `revision` to the short SHA the row was evaluated against.** The
   `revision` cell records when this row was last *evaluated*, not when the
   register file was last touched. A row still reading an older SHA than its
   siblings is a row nobody has re-checked — that is the cell's whole purpose,
   so it is only ever bumped by an evaluation that actually re-read the code.
5. Where the evaluation runs into something a person must decide, add
   `PENDING-HUMAN:<short-id>` to `notes` and leave the rest of the row at its
   honest value. An escalation never justifies changing the specification.

Rows are **never deleted**: the frozen specification defines the row set, so a
row disappears only if the specification does, and nothing in this analysis may
edit it. A requirement that turns out to be met needs its degree changed to
`fit`, not its row removed.

## Column meanings

| column | meaning |
| --- | --- |
| `id` | The requirement identifier from the frozen specification. The row's key. |
| `gap degree` | `fit`, `partial gap`, `full gap` or `conflicting`, as defined in [`methodology.md`](../methodology.md) §5. Exactly one, always present. |
| `root cause` | `-` for `fit`; otherwise `not built`, `built against superseded intent`, `built then orphaned` or `built contrary` — [`methodology.md`](../methodology.md) §6. |
| `evidence` | Disposition-unit IDs (`U-<CLUSTER>-NN`) and/or `path:line` citations relative to `launchpad/skills/review-queue-automation/`, at the row's `revision`. Never empty. A `fit` row never rests on a test or a document alone ([`methodology.md`](../methodology.md) §3). |
| `depends on` | Requirement IDs whose gaps must close before this one's can, or `-`. A technical precedence only — [`methodology.md`](../methodology.md) §9. |
| `revision` | Short SHA the row was last evaluated against. `9267b6308` throughout this skeleton. |
| `notes` | Free text; `-` when there is nothing to say. `PENDING-HUMAN:<short-id>` marks an escalation to a person. |

There is deliberately **no priority column**. Every requirement in the frozen
specification is mandatory, so ranking them is a planning decision this analysis
does not make ([`methodology.md`](../methodology.md) §9).

## Row order

Rows follow the order in which the specification lists the requirements of this
class — the order of the `### RQA-FR-NNN` headings in
[`requirements-specification.md`](../../requirements/requirements-specification.md),
which is thematic and **is not** ascending numeric order. This is the order the
mechanical conformance check requires, and it keeps the register readable
alongside the specification it mirrors. **Do not re-sort this table**: a
numerically sorted register fails the check.

## The split-AC rule applies to every row here

A source clause that produced several requirements is satisfied only when
**all** of them are satisfied. Never record or summarise a clause as covered
because one child row reads `fit` while a sibling does not
([`methodology.md`](../methodology.md) §8). Degrees are assigned per requirement;
nothing in this file is a clause-level judgement.

## What this class's rows turn on

Fourteen source clauses each derive two or more requirements of this class, per
[`singular-splits.md`](../../requirements/singular-splits.md): CL-028, CL-029,
CL-030, CL-031, CL-032, CL-033, CL-034, CL-036, CL-037, CL-038, CL-039, CL-040,
CL-041 and CL-044. (CL-035 is not in that list: `RQA-FR-016` is its only
child in this class.) The split-AC rule bites hardest where a `fit` child sits
beside an unmet sibling, and three clauses are in that position — **CL-028**
(`RQA-FR-002` fit beside `RQA-FR-001` partial), **CL-031** (`RQA-FR-009` fit
beside `RQA-FR-008` full gap) and **CL-039** (`RQA-FR-023` and `RQA-FR-024` fit
beside `RQA-FR-038` partial). None of those clauses is covered. Of these
fourteen, only **CL-029** (`RQA-FR-003`, `RQA-FR-004`) and **CL-044**
(`RQA-FR-032`, `RQA-FR-033`) have every child `fit` and derive no requirement
outside this class, so they are the only two of the fourteen this register can
report as covered. (Single-child clauses are outside this paragraph's subject;
CL-043, for one, derives `RQA-FR-031` alone and is covered by that row.) CL-036,
CL-039 and CL-040 additionally derive non-FR children whose degrees belong to
the sibling registers, so no coverage claim about them can be made from here.

`depends on` is `-` on 36 of the 39 rows. Four edges survive across three rows,
each stated as one of [`methodology.md`](../methodology.md) §9's three
admissible categories and no other: **substrate** for `RQA-FR-017` on
`RQA-FR-008` (the population "a finding classified as mechanical" cannot exist
until a finding carries a category); **authority** for `RQA-FR-029` on
`RQA-NFR-017` (merging before a separately-authorised merge activity exists
ships the action without its check); and **contract** for `RQA-FR-038` on
`RQA-NFR-024` and `RQA-NFR-030` (FR-038's own fit criterion defines the stop
state against those credential invariants, which cannot be observed while
nothing inspects the token's granted scopes — the search establishing that is
quoted on `RQA-FR-038`'s own row).

Eleven edges recorded in the first evaluation were dropped as inadmissible under
that test, because the dependent obligation has a truthful realisation
independent of the named prerequisite: `RQA-FR-007` on `RQA-FR-006` (a record
reading "reused = none, regenerated = all" satisfies FR-007 with no invalidation
computation), `RQA-FR-015` on `RQA-FR-014` (FR-014's own fit criterion declares
the classification testable "independent of whether that classification is yet
persisted in or exposed from the review record"), `RQA-FR-036` on `RQA-FR-014`
(mutually entailing, not ordered — one change closes both), `RQA-FR-011` on
`RQA-FR-010` (singular-splits.md's CL-032 entry: "one could hold without the
other"), `RQA-FR-011` and `RQA-FR-037` on `RQA-FR-013` (both close by refusing
the bypass outright, with no basis record), `RQA-FR-025` on `RQA-FR-008` (a
prohibition satisfiable by issuing no immediate request at all), `RQA-FR-012` on
`RQA-FR-001` (a protocol identifier can be recorded against the definition that
already exists), `RQA-FR-030` on `RQA-FR-001` (FR-001 establishes the review
protocol, not the harness interaction contract), `RQA-FR-029` on
`RQA-NFR-008` (implementing the biconditional creates the switch; coupled, not
ordered) and `RQA-FR-018` on `RQA-FR-017` (dropped in round 2: FR-018 requires
only non-invalidation, while FR-017 can fail on an unnecessary-intervention
ground of its own, so a mechanism that preserves every unrelated artefact while
still generating one unnecessary human request closes FR-018 with FR-017 open —
the separating world singular-splits.md's CL-036 entry states in its own words,
"a system could satisfy either alone". The round-1 substrate reason was the same
reasoning this register rejected when dropping `RQA-FR-025` on `RQA-FR-008`, and
FR-018 is likewise a prohibition, so no prerequisite replaces it).

Seven rows carry `conflicting` rather than `full gap`, on four mechanisms, each a
reachable execution producing an outcome the requirement forbids: the
head-checks gate treats an inherited failing check as the pull request's own
blocker (`RQA-FR-014`, `RQA-FR-036`); the human-resume path writes an
approval-eligible decision from the authorization alone, without re-running the
gates that failed and with no required basis (`RQA-FR-011`, `RQA-FR-037`);
`budget.reserve` returns a permissive decision when a configured bound has been
reached, both for the per-model axis it never queries and at exact equality on
the two axes it does (`RQA-FR-022`, `RQA-FR-039`); and a review whose obligations
are satisfied terminates in an advisory COMMENT or in `human_required` without
submitting either verdict whenever the relevant authority is not `live`, which
`RQA-NFR-026` makes the default (`RQA-FR-028`, degree set by the maintainer's
2026-09-06 ruling on this row's population).

No row carries an open escalation. `FR035-TRACKER-STATE` was settled by the
maintainer on 2026-09-08 from his own tracker query, which `RQA-FR-035` records
and which confirms that row; `FR028-ADVISORY-POPULATION` was closed by that ruling.

## Register

| id | gap degree | root cause | evidence | depends on | revision | notes |
| --- | --- | --- | --- | --- | --- | --- |
| RQA-FR-001 | partial gap | not built | U-VERDICT-01, U-VERDICT-02, scripts/panel.py:406-416, scripts/verdict.py:165-197, schemas/reviewer-verdict.json:4-5, references/contracts.md:85-123 | - | 9267b6308 | Met: every slot-filling verdict is checked against the published schema (`panel.py:406-416` calling `validate_verdict`). Unmet: `validate_verdict` enforces only the schema's `required` list — not the `severity` enum, the `location` pattern, `minLength` or `additionalProperties` — so a verdict the published definition rejects still fills a slot; and no published artefact defines review scope, one of AC01's six concepts. Search re-run for that last negative: `grep -rniE "review scope" SKILL.md OPERATORS.md references/ schemas/ onboarding/ config.example.json` → no output, exit 1. `U-DOCS-22` was struck from this cell on the maintainer's 2026-09-06 ruling that documentation-to-code naming drift does not bear on this requirement; the degree is unaffected, because it rested on the verdict-validation gate and the schema-enforcement shortfall, both still cited. |
| RQA-FR-002 | fit | - | U-VERDICT-04, U-VERDICT-07, U-VERDICT-11, U-VERDICT-12, U-DISPATCH-24, U-AUTHORITY-03, scripts/planner.py:162-181, scripts/planner.py:194-247, scripts/panel.py:498-514, scripts/evidence.py:21-23, scripts/panel.py:537-540, scripts/findings.py:43-61, schemas/reviewer-verdict.json:16-21, scripts/dispatcher.py:798-802, scripts/config.py:255-273, scripts/panel.py:566-574, scripts/panel.py:726-751, scripts/approval_evaluate.py:268-288, scripts/dispatcher.py:1418-1421 | - | 9267b6308 | Checked concept by concept against AC01's six, since agreement on only some does not satisfy the criterion, and every citation re-opened in round 2. Review scope: `plan_review` takes only PR facts as keyword arguments and selects or omits each activity with a recorded reason (planner.py:162-181, :194-247 — the round-1 citation of :129-137 was `classify_changes`, a helper, and is withdrawn), and `_plan_for_job` writes that plan to the ledger as the `review_plan` entry (panel.py:498-514). Required evidence: three canonical artefact names fixed as the contract every writer and reader uses (evidence.py:21-23), with the panel refusing to run without `evidence.txt` (panel.py:537-540). Findings: one schema shape (schemas/reviewer-verdict.json:16-21) and one severity-plus-location fingerprint matching across differently-worded reports (findings.py:43-61). Blocking conditions: repository policy, the same inputs FR-003's row cites — `findings.blocking_severities` (dispatcher.py:798-802) and `risk.bands` (config.py:255-273) — identical for two reviews of the same PR. Review completion: `run_panel`'s completeness predicate (panel.py:726-751), against one schema constant for every runner (panel.py:566-574). Final disposition: computed by `approval_evaluate.evaluate` and applied by the dispatcher's own transitions (approval_evaluate.py:268-288, dispatcher.py:1418-1421), never by harness output. `modes.py:136-152` is withdrawn: it resolves which execution mode aggregates signals and supports none of the six. The best-effort ledger write is a recording-reliability defect recorded on RQA-FR-012, not a divergence in meaning between two harnesses, which is what this row tests. |
| RQA-FR-003 | fit | - | U-AUTHORITY-03, U-AUTHORITY-04, scripts/dispatcher.py:798-802, scripts/config.py:255-273, scripts/config.py:278-291, scripts/authority.py:88-121 | - | 9267b6308 | The blocking outcome is computed from per-repository configuration — `findings.blocking_severities`, `risk.bands`, `risk.protected_triggers`, and the per-repo `authority[repo][activity]` override — so the same diff under two configurations reaches two outcomes and the difference is attributable to the configuration. |
| RQA-FR-008 | full gap | not built | U-VERDICT-02, U-VERDICT-04, schemas/reviewer-verdict.json:16-21, scripts/verdict.py:31, scripts/findings.py:43-51 | - | 9267b6308 | A finding carries exactly severity, title, location, evidence and primary_source; the schema's `additionalProperties: false` forbids a category being carried at all. Two searches re-run, with their raw stdout pasted verbatim in "Raw search output" after this table. `grep -rniE "mechanical" scripts/ schemas/` → one hit, `scripts/planner.py:125`, a comment reading "mechanically narrower", not a classification. `grep -rniE "categor" scripts/ schemas/` → nine hits, every one inside the error-disposition registry in a single file and none of them a finding taxonomy: scripts/errors.py:199, scripts/errors.py:202, scripts/errors.py:207, scripts/errors.py:221, scripts/errors.py:234, scripts/errors.py:240, scripts/errors.py:244, scripts/errors.py:245, scripts/errors.py:246. So the mechanical-versus-substantive distinction this row requires exists nowhere in `scripts/` or `schemas/`; RQA-FR-017 and RQA-FR-025 rest on this same cited result. |
| RQA-FR-009 | fit | - | U-AUTHORITY-04, U-DOCS-33, scripts/dispatcher.py:798-802, scripts/dispatcher.py:911-915, scripts/findings.py:157-163, scripts/action_gate.py:63-83 | - | 9267b6308 | Reviewer severity is one declared input: the blocking set comes from the repository's own `findings.blocking_severities`, and blocking additionally requires corroboration, a live `request_changes` authority and the deterministic gate. Severity alone never decides. |
| RQA-FR-005 | full gap | not built | scripts/queue.py:116-118, scripts/common.py:471-478, scripts/dispatcher.py:2140-2164, scripts/panel.py:626-631 | - | 9267b6308 | No materiality comparison exists at this revision. A job is keyed on the head SHA, so a push that changes nothing material yields a new `(repo, number, head, lane)` key, a fresh job and a full panel run. Search re-run, raw stdout pasted verbatim in "Raw search output" after this table: `grep -rni -e material -e reuse -e regenerat -e invalidat scripts/` → 21 matches in 11 files, none of them a materiality or reuse comparison, and every one named here — scripts/dispatcher.py:1071, scripts/notify.py:63, scripts/modes.py:167, scripts/assurance.py:15, scripts/assurance.py:32, scripts/assurance.py:110, scripts/common.py:553, scripts/approval.py:8, scripts/approval_evaluate.py:63, scripts/panel.py:79, scripts/panel.py:561, scripts/logging_otel.py:150, scripts/model_registry.py:85, scripts/model_registry.py:102, scripts/model_registry.py:103, scripts/model_registry.py:104, scripts/model_registry.py:116, scripts/model_registry.py:142, scripts/model_registry.py:145, scripts/verdict.py:28, scripts/verdict.py:37 — being the `MATERIAL_DISAGREEMENT` signal and prose about it, "credential material" and "route material", an idempotent-enqueue docstring, a 304 body reuse, a local-variable comment and one policy-hash docstring about a config change invalidating a persisted decision. RQA-FR-006, RQA-FR-007 and RQA-FR-020 rest on this same cited result. Evidence correction carried forward: U-RESILIENCE-13 and U-DOCS-25 tag `job_id` stability with this ID, but that mechanism prevents re-dispatching an unchanged revision — RQA-BR-007's subject — and says nothing about an immaterial push. |
| RQA-FR-006 | full gap | not built | scripts/planner.py:129-137, scripts/planner.py:194-247, scripts/panel.py:626-631, scripts/queue.py:159-169 | - | 9267b6308 | Obligations are re-planned from scratch for each head, every panel attempt deletes the prior slot files, and the older job is superseded. Nothing computes which obligations a given file change invalidates — established by the materiality/reuse search quoted in full on RQA-FR-005's row, whose only `invalidat` hit is a docstring about a policy hash. The planner's changed-path fan-out scopes activities within one review; it is not cross-revision invalidation. |
| RQA-FR-007 | full gap | not built | scripts/ledger.py:70-83, scripts/ledger.py:121-163, scripts/planner.py:194-247, scripts/panel.py:626-631 | - | 9267b6308 | The ledger records the activities selected and omitted for one revision, never a reused-versus-regenerated partition across revisions; the eight declared ledger kinds carry no such entry, and the materiality/reuse search quoted on RQA-FR-005's row returns no reuse decision anywhere in `scripts/`. The RQA-FR-006 edge was dropped in round 1 re-review: a truthful degenerate record — reused = none, regenerated = all — satisfies this row's fit criterion with no invalidation computation in place, so the prerequisite is not forced. |
| RQA-FR-014 | conflicting | built contrary | U-VERDICT-06, U-AUTHORITY-11, scripts/dispatcher.py:296-297, scripts/checks.py:115-123, scripts/checks.py:49-51, scripts/github_query.py:454 | - | 9267b6308 | `checks_ok = all_passing(head checks)` feeds the `checks_complete_ok` approval gate, so a failing check is treated as attributable to the pull request whatever the base does. Only the base ref *name* is ever read. Search re-run and quoted as it returned: `grep -rni -e merge.base -e mergebase -e inherit -e attributab scripts/` → five hits, every one an unrelated comment — budget.py:60 ("rather than inheriting"), runners.py:19 and :76 ("inherits credit", "inherited from the caller's cwd"), errors.py:24 and panel.py:397 (a failure "attributable to the PROVIDER"). No base check state is read anywhere, and the REST surface (github_rest.py:60-121) exposes no merge-base or base-ref checks method. Closing this requires changing that evaluation, not adding to it. RQA-FR-015 and RQA-FR-036 rest on this same cited result. |
| RQA-FR-015 | full gap | not built | scripts/dispatcher.py:296-297, scripts/ledger.py:121-163, scripts/github_query.py:454 | - | 9267b6308 | No inherited-versus-attributable classification is computed — the merge-base search quoted on RQA-FR-014's row returns only unrelated comments — so none is stated in the record, and the ledger's declared kinds carry no entry for one. The RQA-FR-014 edge was dropped in round 1 re-review: FR-014's own fit criterion tests the classification "independent of whether that classification is yet persisted in or exposed from the review record", so a classification computed for the record alone would close this row while FR-014 stayed open. |
| RQA-FR-036 | conflicting | built contrary | U-VERDICT-06, U-VERDICT-16, scripts/checks.py:115-123, scripts/dispatcher.py:296-297, scripts/risk.py:223-250 | - | 9267b6308 | An inherited failing check does contribute to a blocking disposition today: `all_passing` fails closed on any failing check and `checks_complete_ok` is one of the 22 conjunctive gates, so approval is unreachable while it fails. Requires removing that contribution, not adding a mechanism. The RQA-FR-014 edge was dropped on re-review: excluding the failure from the gate is the same execution change FR-014's own criterion names, so the two are mutually entailing and neither precedes the other. |
| RQA-FR-010 | full gap | not built | U-DISPATCH-24, U-VERDICT-16, scripts/planner.py:194-247, scripts/risk.py:204-262, schemas/reviewer-verdict.json:4-5 | - | 9267b6308 | No obligation carries a state from the seven-value set: planner activities carry a selection or omission reason, approval gates are booleans, and the verdict's six-value `signal` plus its `missing_evidence` list are per verdict, not per obligation. Search re-run and quoted as it returned: `grep -rni -e contradictory -e not_verified -e evidence_state scripts/ schemas/` → five hits, all about *contradictory verdict fields* in the schema check (panel.py:16,348,417; verdict.py:5,195); `not_verified` and `evidence_state` return nothing on their own. Evidence correction: U-DOCS-09, U-DOCS-48 and U-DOCS-49 tag this ID onto panel completeness and signal parsing, which bear on RQA-FR-011/RQA-FR-037 and RQA-FR-001 instead. |
| RQA-FR-012 | partial gap | not built | U-RESILIENCE-06, U-RESILIENCE-07, U-DISPATCH-20, U-DISPATCH-25, scripts/ledger.py:121-163, scripts/explain.py:53-81 | - | 9267b6308 | One command reconstructs revision, policy version, routes with harness/model/provider, evidence, findings, assurance, human events, decision basis and disposition from the ledger alone. Two elements fail. The protocol in force is never recorded: `grep -rn "protocol" scripts/` → no output, exit 1, so no entry carries a protocol identity of any kind. And `_ledger_record` swallows every write failure with a bare `except Exception: pass`, so a reconstruction can be silently incomplete. The RQA-FR-001 edge was dropped in round 1 re-review: a protocol identifier can be recorded against the definition that already exists, so FR-001's completeness is not a prerequisite. |
| RQA-FR-013 | partial gap | not built | U-AUTHORITY-06, U-AUTHORITY-07, scripts/human_cli.py:216-220, scripts/approval.py:122-146, scripts/approval.py:233-271, scripts/approval_evaluate.py:352-358, scripts/common.py:268-281 | - | 9267b6308 | The approving human is named: `--actor` is `required=True` and `decide` records it on the row. The basis is not: `--reason` defaults to the empty string and `enqueue`/`decide` store it unvalidated. And the authoritative `approval_decisions` record carries neither — its DDL declares exactly `id, job_id, repo, number, head_sha, policy_hash, status, mode, risk_score, created_at, expires_at` (common.py:268-281), with no actor or basis column for `persist_human_approval` to write. |
| RQA-FR-011 | conflicting | built contrary | U-AUTHORITY-07, U-VERDICT-16, scripts/human_cli.py:178-197, scripts/human_cli.py:220, scripts/approval_evaluate.py:352-358, scripts/approval.py:122-146 | - | 9267b6308 | The automatic path is fail-closed — 22-gate conjunction, panel completeness predicate. The human-resume path is not: `persist_human_approval` writes a decision row already marked `eligible` from the authorization alone, without re-running the gates that failed, and the authorizing reason may be empty. That is exactly the named approval with no substantiated basis the fit criterion says does not count an obligation satisfied, and it reaches `completed_auto_approved`. Closing it requires constraining that path. Both edges were dropped on re-review: singular-splits.md's CL-032 entry states FR-010 and this row can hold independently, and this row also closes by refusing the bypass outright, which needs no basis record from RQA-FR-013. |
| RQA-FR-016 | full gap | not built | U-RESILIENCE-07, U-RESILIENCE-16, U-QUEUE-02, scripts/dispatcher.py:2125-2137, scripts/explain.py:57-66, scripts/states.py:78-118 | - | 9267b6308 | Narrowed on re-review, and downgraded from partial gap: no reachable command returns a per-pull-request current disposition. `runtime_status` takes no PR argument at all — it groups the whole state directory by status — and `explain.py pr <number>` reconstructs a past outcome from ledger history, exiting 1 with an error naming the repo and number when no entry exists yet. Nothing maps the 29 job statuses onto AC08's six values. Searches re-run per value, each as `grep -rn "<value>" scripts/`: `being reviewed`, `awaiting remediation`, `unable to progress` and the literal `review-complete` each → no output, exit 1. `blocked` → nine hits, all incidental and none a disposition value: scripts/dispatcher.py:672, scripts/dispatcher.py:1389, scripts/shadow.py:414, scripts/shadow.py:420, scripts/shadow.py:429, scripts/shadow.py:435, scripts/shadow.py:634, scripts/shadow.py:635, scripts/shadow.py:638 — two log-prose strings and, in the shadow risk sweep, the `unblocked_bad` local and a `blocked` boolean field (raw stdout in "Raw search output" after this table). `awaiting human` → human_cli.py:89 (an error string) and approval.py:275 (a docstring), both about approval. `grep -rn "review.completed" scripts/` → dispatcher.py:1176, panel.py:786, a log metric attribute key and a coincidentally similar but distinct string, not an occurrence of the AC08 value. No value is a returned or mapped disposition, so no obligation of this row is met. The per-PR state itself is maintained and kept fresh by supersession, but nothing exposes it as a disposition. |
| RQA-FR-028 | conflicting | built contrary | U-DISPATCH-18, U-DISPATCH-17, U-AUTHORITY-01, U-AUTHORITY-08, U-DISPATCH-16, scripts/dispatcher.py:1513-1523, scripts/dispatcher.py:1471-1481, scripts/dispatcher.py:941-950, scripts/advisory.py:154-156, scripts/advisory.py:63-69, scripts/github_mutate.py:99-113, scripts/authority.py:44, scripts/authority.py:149-151, scripts/config.py:242-246, scripts/dispatcher.py:631-665, scripts/dispatcher.py:1010-1035 | - | 9267b6308 | Degree set by the maintainer's 2026-09-06 ruling, which closed this row's population question (`FR028-ADVISORY-POPULATION`): an advisory-mode review IS inside the population, nothing in the requirement scopes it to an authority mode, and its fit criterion states that a satisfied review submitting neither verdict fails the check. Evidence re-derived for that degree rather than relabelled — these citations show the reachable execution producing the forbidden outcome, not an absence. A satisfied review whose approval mode is `disabled` takes the `else: # disabled -> advisory only` branch, transitions to `advisory_action`, and terminates `completed_advisory` (dispatcher.py:1513-1523); that terminal transition is unconditional, so the forbidden outcome does not depend on anything the advisory posting does. The comment itself is separately gated by a second authority activity: `post_advisory` resolves `comment` mode and returns `posted: false` unless it is `live` (advisory.py:154-156), so under full defaults no comment is delivered at all and the job still ends `completed_advisory` having submitted neither verdict; when one is delivered its body states it approves nothing and requests no changes (advisory.py:63-69) and its GraphQL event is hard-coded `COMMENT` (github_mutate.py:99-113), structurally not a submission either way. The `shadow` disposition terminates identically (dispatcher.py:1471-1481). On the other verdict, a satisfied review carrying corroborated defects under a non-live `request_changes` authority transitions to `human_required` and returns, again submitting nothing (dispatcher.py:941-950). This is the common case, not an edge: `DEFAULT_MODE` is `"disabled"` and `defaults()` disables every activity (authority.py:44, :149-151), and `approval.mode` defaults to `"disabled"` (config.py:242-246). Both submissions do exist and are reachable under live authority — APPROVE in `_execute_live_approval` (dispatcher.py:631-665) and CHANGES_REQUESTED in `_execute_request_changes`, whose mutation and terminal `changes_requested` transition are at dispatcher.py:1010-1035 (the round-5 finding that :631-665 contains no CHANGES_REQUESTED code is accepted; that citation now carries only the APPROVE claim) — which is why closing this requires changing what the non-live terminal branches do rather than building a submission path. `depends on` re-checked and stays `-`: neither RQA-NFR-026 nor RQA-NFR-017 is a substrate, authority or contract prerequisite — the submission machinery and its per-activity gate both already exist, so this row's gap closes by changing the non-live terminal branches, and its relationship to those two rows is a tension the replacement must reconcile, not a precedence. |
| RQA-FR-029 | full gap | not built | U-AUTHORITY-01, U-AUTHORITY-09, scripts/authority.py:32-34, scripts/github_mutate.py:99-113 | RQA-NFR-017 | 9267b6308 | The system cannot merge at all: `merge` is not one of the six authority activities and the `MUTATIONS` registry carries no merge entry. Search re-run and quoted as it returned: `grep -rni -e '"merge"' -e "'merge'" -e mergepullrequest -e "def merge" -e merge_method -e auto_merge scripts/` → no output, exit 1 — no merge operation, method or configuration key exists on any path. (A bare `grep -rn merge scripts/` does hit, which is why the round-1 blanket claim was withdrawn: `merged` is a terminal lifecycle status and appears in history prose.) Neither direction of the biconditional is exercisable because no merge-after-review configuration exists to condition on. The RQA-NFR-008 edge was dropped on re-review: implementing the biconditional creates that switch, so the two are coupled rather than ordered; the RQA-NFR-017 edge is **authority** — merging before a separately-authorised merge activity exists ships the action without its check. |
| RQA-FR-037 | conflicting | built contrary | U-VERDICT-12, U-DOCS-54, U-DOCS-56, scripts/human_cli.py:178-197, scripts/human_cli.py:220, scripts/approval_evaluate.py:352-358 | - | 9267b6308 | AC14's side of the same contradiction as RQA-FR-011. The panel and gate paths never manufacture success — completeness predicate, 22-gate conjunction, shadow mode persisting no decision row — but a human authorization carrying an empty basis converts a gate-failed job into `completed_auto_approved` and a submitted APPROVED. The RQA-FR-013 edge was dropped on re-review: this row also closes by refusing the bypass outright, which requires no basis record. |
| RQA-FR-017 | full gap | built then orphaned | U-DISPATCH-26, U-DOCS-13, scripts/worktree.py:102, scripts/worktree.py:195, scripts/dispatcher.py:2162, scripts/runners.py:120 | RQA-FR-008 | 9267b6308 | `worktree.py` implements create/commit/push/clean completely and nothing under `scripts/` reaches it (methodology §2.4's worked example). Search re-run and quoted as it returned: `grep -rn "worktree" scripts/` → hits in exactly two files, `scripts/worktree.py` itself and `scripts/runners.py:120`, a comment reading "keeps the call usable from a worktree or bare path" — no import and no call. No finding is classified mechanical in the first place either (see the `mechanical`/`categor` searches quoted on RQA-FR-008's row), so such a finding is resolved only through a human or a full re-review cycle. Second cause present: `not built`, for the mechanical classification. |
| RQA-FR-018 | full gap | built then orphaned | U-DISPATCH-26, U-DOCS-13, U-DOCS-53, scripts/worktree.py:102, scripts/dispatcher.py:2162 | - | 9267b6308 | No remediation runs — the `worktree` search quoted on RQA-FR-017's row shows the only occurrences outside the module are one comment — so nothing preserves unrelated valid review work across one; the guarantee is not vacuously met, because the mechanism that would resolve a mechanical finding exists and is orphaned. The RQA-FR-017 edge was dropped in round 2: this row requires only non-invalidation, while FR-017 can additionally fail on an unnecessary intervention unconnected to any authority, evidence or judgement gap, so a mechanism preserving every unrelated artefact while still generating one unnecessary human request closes this row with FR-017 open — the separating world singular-splits.md's CL-036 entry states as "a system could satisfy either alone". Being a prohibition, it needs no population substrate either, so no prerequisite replaces the edge. |
| RQA-FR-025 | partial gap | not built | U-AUTHORITY-12, scripts/notify.py:180-196, scripts/notify.py:194-196, schemas/reviewer-verdict.json:16-21 | - | 9267b6308 | The human queue is durable and pull-based and the default transport is `none`, which queues only, so nothing demands attention by default. But no condition is ever classified routine, mechanical or non-urgent — the `mechanical` and `categor` searches quoted on RQA-FR-008's row return one comment and an error-disposition registry — and `deliver()` carries no urgency or routing parameter: `grep -rni -e urgen -e immediate -e priorit scripts/notify.py scripts/approval.py` → no output, exit 1. So with a `command` transport configured every escalation fires the same immediate delivery whatever raised it. The RQA-FR-008 edge was dropped on re-review: this is a prohibition, and it also closes by issuing no immediate request at all, which needs no finding category. |
| RQA-FR-026 | partial gap | not built | U-DISPATCH-14, U-DISPATCH-15, U-DISPATCH-16, scripts/dispatcher.py:1408-1417, scripts/assurance.py:100-134, scripts/assurance.py:168-184 | - | 9267b6308 | Re-evidenced on re-review; the earlier JobBlockingError-forwarding and empty-enqueue-argument examples did not hold up and are withdrawn. Most escalations do name a concrete cause: the evidence-gather failure, the uncorroborated finding, `authority_not_live`, the failed gates with risk score and band. The terminal assurance escalation does not: any non-SUCCESS, non-REQUEST_CHANGES decision transitions to `human_required` with the bare decision label `"HUMAN"` as its reason, and `classify` returns that same label for a reserved-for-human signal, for material disagreement and for exhausted capability alike — so the record loses which of AC13's five causes produced it. |
| RQA-FR-027 | partial gap | not built | U-AUTHORITY-07, U-DISPATCH-07, scripts/human_cli.py:88-89, scripts/human_cli.py:114-144, scripts/states.py:110 | - | 9267b6308 | Supplying an approval decision resumes a `human_approval_pending` job through `approval_revalidation` with no re-review. Nothing else resumes. Search re-run, raw stdout pasted verbatim in "Raw search output" after this table: `grep -rn "approval_revalidation" scripts/` → 20 matches, every one named here — scripts/dispatcher.py:88, scripts/dispatcher.py:583, scripts/dispatcher.py:1463, scripts/dispatcher.py:1876, scripts/queue.py:33, scripts/budget.py:73, scripts/human_cli.py:123, scripts/human_cli.py:126, scripts/human_cli.py:133, scripts/approval.py:245, scripts/states.py:7, scripts/states.py:10, scripts/states.py:11, scripts/states.py:13, scripts/states.py:52, scripts/states.py:91, scripts/states.py:94, scripts/states.py:95, scripts/states.py:100, scripts/states.py:110. Exactly two of them write the status — dispatcher.py:1463, the automatic live-approval path entered from approval evaluation, and human_cli.py:126, resume, which refuses any status other than `human_approval_pending` at :88-89. The other eighteen are the transition table and its docstring arrows (states.py:7, :10, :11, :13, :52, :91, :94, :95, :100, :110), status-list membership (queue.py:33, budget.py:73, dispatcher.py:88, :1876), two docstrings (dispatcher.py:583, approval.py:245) and, in `human_cli.py`, the `can_transition` guard at :123 and the status echoed into the returned dict at :133 — the round-5 finding that the earlier three-way classification did not cover those last two, or the full ten `states.py` hits, is accepted and corrected here. So no command carries a `human_required` job forward, even though the table legalises `human_required -> approval_revalidation`. |
| RQA-FR-019 | partial gap | not built | U-POLICY-08, U-POLICY-09, U-DISPATCH-24, U-RESILIENCE-03, scripts/strategies.py:63-90, scripts/strategies.py:137-181, scripts/modes.py:155-179, scripts/planner.py:188-200, config.example.json:166-172 | - | 9267b6308 | Met: the executed mode never demands more independent participants than the profile the policy states (`for_profile`, modes.py:155-179), a docs-or-tests-only change omits the baseline questions with a recorded reason (planner.py:188-200), and a `MISSING_EVIDENCE` verdict escalates instead of re-running the identical loop. Unmet: nothing compares the reasoning strategy or higher-cost method against the policy's stated assurance — the registry of twelve named strategies is `STRATEGIES`/`STRATEGY_BY_NAME` at strategies.py:63-90 and the selector that walks them from internal signals is `select_strategy` at strategies.py:137-181, neither of which reads the policy's assurance statement. Citation corrected in round 5: modes.py:155-179 and planner.py:188-200 are cited only for the mode-derivation and activity-omission claims above, which is all they support. The example config's own `strategies.active` allowlist is read by no script: `grep -rn "\"strategies\"" scripts/` → two hits, ledger.py:146 and :178, both the explain report's own output key, not a read of `config["strategies"]`. |
| RQA-FR-020 | partial gap | not built | U-QUEUE-01, U-RESILIENCE-12, U-AUTHORITY-09, scripts/common.py:525-546, scripts/panel.py:626-631 | - | 9267b6308 | Reuse is complete for three result classes: an existing job for the same `(repo, number, head, lane)` is not recreated, a recorded mutation id returns the prior response instead of re-sending, and a 304'd REST body is reused from cache. No reviewer result is ever reused — every panel attempt deletes the prior slot files, and the materiality/reuse search quoted on RQA-FR-005's row returns no cross-revision result store anywhere in `scripts/`. |
| RQA-FR-021 | partial gap | not built | U-DISPATCH-13, U-RESILIENCE-01, U-RESILIENCE-12, scripts/dispatcher.py:1323-1329, scripts/budget.py:217-220, scripts/budget.py:223-231, scripts/budget.py:16-19 | - | 9267b6308 | Met: rate-limit consumption is recorded from the response headers the environment actually exposes. Unmet: runners report no token count — the module's own docstring says so at budget.py:16-19 — so the reservation is written into `cost_ledger` as what the attempt cost, with no field marking it an estimate. The insert writes exactly `recorded_at, job_id, repo, number, model, provider_family, kind, tokens, latency_ms` (budget.py:223-231), so the `kind` column separates a reservation row from a spend row, and nothing separates an estimated spend from a measured one. |
| RQA-FR-022 | conflicting | built contrary | U-DISPATCH-12, U-RESILIENCE-01, scripts/budget.py:396-401, scripts/budget.py:408, scripts/budget.py:57, scripts/budget.py:117-118, scripts/budget.py:133-134, scripts/budget.py:184, config.example.json:182 | - | 9267b6308 | Downgraded from fit on re-review, then judged against the primary test: does a reachable execution produce an outcome this row forbids? It does, twice. `per_model_daily_tokens` is defaulted at 20,000,000, resolved by `limits()` and validated by `validate_budget()`, and advertised in the example config, but `reserve()`'s `checks` tuple covers only `per_pr_tokens` and `per_repo_daily_tokens`, and the accessor that would read the third axis is never called — `grep -rn "spent_for_model" scripts/` → one hit, `scripts/budget.py:184`, its own definition. So a run whose per-model daily spend has reached that configured bound is allowed to proceed and ends in none of AC11's three outcomes. Separately, the enforced axes compare `already + tokens > cap`, so an attempt landing exactly at a configured cap is also permitted; the module's own docstring states that design ("a budget can be reached but not exceeded") against a requirement whose trigger is the bound being *reached*. Both are permissive decisions returned in cases the requirement forbids, and adding the missing projection changes what `reserve()` decides rather than extending it. RQA-FR-039 rests on this same cited result. |
| RQA-FR-023 | fit | - | U-POLICY-10, U-POLICY-13, U-VERDICT-09, U-VERDICT-10, scripts/routing.py:116-186, scripts/panel.py:653-722 | - | 9267b6308 | An unavailable configured reviewer, model or provider is passed over rather than halting the review: `resolve_route` skips an attempted or cooled-down rung and returns the next configured candidate, and the panel's candidate loop falls through to the next configured candidate in the lane, retiring a whole provider family after a provider-scoped failure. |
| RQA-FR-024 | fit | - | U-POLICY-10, U-VERDICT-09, U-VERDICT-10, U-DOCS-27, scripts/routing.py:66-98, scripts/routing.py:151-186, scripts/panel.py:653-722 | - | 9267b6308 | Ladder rungs are derived solely from the configured pools, and when a configured route becomes unavailable at runtime nothing outside configuration is substituted for it: `is_route_available` passes over a cooled-down rung and `resolve_route` returns the next *configured* candidate, exhausting to the `human` rung with no model selected; the panel's candidate loop likewise falls through to the next configured candidate and retires a failed provider family rather than reaching for an unconfigured one. Corrected in round 2: the earlier "an unknown runner raises rather than being routed" clause is withdrawn — `_routes_from_config` silently omits an unrecognised runner at ladder-build time and `runners.adapter_for`'s raise happens later, at execution; both are configuration handling, not the runtime-unavailability path this requirement names. |
| RQA-FR-038 | partial gap | not built | U-QUEUE-11, U-DISPATCH-07, U-DISPATCH-21, U-RESILIENCE-02, U-AUTHORITY-02, scripts/states.py:79-109, scripts/dispatcher.py:1808-1878 | RQA-NFR-024, RQA-NFR-030 | 9267b6308 | `safe_stop` is a legal target from all 14 nonterminal statuses, the stop records its reason, and `recover` releases leases and resumes without replaying a decision — a clear, safe, recoverable stop. The criterion additionally requires the stopped state to be observably holding the standing invariants, and the credential floor and ceiling cannot be observed at all. Search re-run and quoted as it returned: `grep -rni -e x-oauth-scopes -e "granted scope" -e "token scope" -e scopes scripts/` → no output, exit 1; U-AUTHORITY-02 reaches the same finding from the other side, that `github_auth` derives capability from a repository's `permissions` object and never inspects the credential's own granted scope. |
| RQA-FR-039 | conflicting | built contrary | U-DISPATCH-12, U-RESILIENCE-01, scripts/budget.py:396-401, scripts/budget.py:408, scripts/budget.py:57, scripts/budget.py:117-118, scripts/budget.py:184, config.example.json:182 | - | 9267b6308 | Downgraded from fit on re-review, same mechanism as RQA-FR-022 and the same primary test. The two enforced axes do refuse before any spend and downgrade to `human_required` or `degraded_draft`. The configured `per_model_daily_tokens` bound is never projected — the `spent_for_model` search quoted on RQA-FR-022's row returns only its own definition — so a run that has reached it proceeds and can end `completed_auto_approved`, a successful outcome this row forbids; the same holds at exact equality on the two enforced axes, where the comparison is `>` rather than `>=`. One corrective change to `reserve()` closes both rows' assessments. |
| RQA-FR-004 | fit | - | U-POLICY-01, U-QUEUE-10, U-DISPATCH-09, U-DISPATCH-11, U-RESILIENCE-09, scripts/config.py:446-455 | - | 9267b6308 | The repo-local config and its inline policy are read from the live filesystem path on every call, never compiled into an artefact, and hashed into the snapshot a job pins, so an edited policy applies to the next review with no rebuild, reinstall or redeploy while an in-flight job keeps its pin. |
| RQA-FR-030 | full gap | not built | U-DISPATCH-25, scripts/runners.py:138-157, scripts/runners.py:164-171, scripts/panel.py:301-314 | - | 9267b6308 | `adapter_for` admits exactly the three coded adapters and raises `UnknownRunnerError` for anything else, which `_run_reviewer` converts into a job-blocking error. There is no plugin, config-driven or discovery path by which a harness not built in could participate: `grep -rni -e plugin -e entry_point -e entrypoints -e importlib -e __import__ scripts/` → no output, exit 1. Admission therefore always requires a source change. The RQA-FR-001 edge was dropped on re-review: FR-001 establishes the review protocol definition, not the harness interaction contract this row is defined against, so it is not the prerequisite. |
| RQA-FR-031 | fit | - | U-POLICY-01, U-POLICY-06, U-QUEUE-08, U-RESILIENCE-10, U-RESILIENCE-16, scripts/scheduled-tick.sh:44-47, scripts/scheduled-tick.sh:49-66, scripts/scheduled-tick.sh:68 | - | 9267b6308 | Configuration, state, artifacts and credentials are per repo-root on the operator's own machine with no hosted service in the loop; one timer takes several repo roots as arguments and ticks each independently in its own loop, recording the worst status and exiting on it rather than halting on the first failure; the repository slug is arbitrary, so two repositories under different owners are simply two independent local configurations. Line range corrected in round 2: the earlier `:40-42` citation covered only the `RQA_PYTHON`/`RQA_LANES`/`RQA_LIMIT` defaults, not the usage guard, the per-root loop or `exit "$worst"`. |
| RQA-FR-032 | fit | - | U-POLICY-10, U-POLICY-11, U-POLICY-13, scripts/panel.py:656-668, scripts/routing.py:116-186, OPERATORS.md:151-153 | - | 9267b6308 | The candidate — runner, selector, provider family — is chosen from the configured pools before `_attempt_candidate` sends the prompt, and the configured routes can be enumerated ahead of any review through the documented `route_probe.py --json` command. Caveat, not a shortfall against the criterion's nameability test: the executed route is only recorded afterwards, in the ledger entry written once a candidate succeeds. |
| RQA-FR-033 | fit | - | U-POLICY-10, U-VERDICT-02, scripts/routing.py:66-98, scripts/panel.py:566-574, scripts/verdict.py:165-197 | - | 9267b6308 | The protocol is provider-independent: the same schema gate, the same signal and recommendation vocabulary and the same mode aggregation run whatever the pools contain, and removing a provider only removes the rungs `_routes_from_config` derives from configuration. |
| RQA-FR-034 | full gap | not built | U-QUEUE-12, U-VERDICT-02, U-VERDICT-14, U-VERDICT-15, U-VERDICT-17, U-VERDICT-18, scripts/states.py:104, scripts/states.py:129-131 | - | 9267b6308 | Downgraded from partial gap on re-review. The one positive example the earlier row offered does not hold: the legacy `action -> completed` transition is justified only as "preserved for existing callers", the docstring names no caller, and no code under `scripts/` ever transitions a job to the `action` status. Two searches re-run, raw stdout pasted verbatim in "Raw search output" after this table. `grep -rn '"action"' scripts/` → 12 matches in 7 files, none of them a status write: scripts/dispatcher.py:653, scripts/dispatcher.py:846, scripts/dispatcher.py:1027, scripts/queue.py:34, scripts/ledger.py:41, scripts/notify.py:118, scripts/approval.py:59, scripts/approval.py:143, scripts/lease.py:125, scripts/states.py:59, scripts/states.py:89, scripts/states.py:104 — the ledger entry kind and its `ACTION` constant, NONTERMINAL membership, human-request row and packet fields, a CLI argument name, and the transition table itself. `grep -rn '"action"' tests/` → 8 matches: tests/test_errors_states.py:54, tests/test_errors_states.py:64, tests/test_errors_states.py:65, tests/test_errors_states.py:71, tests/test_errors_states.py:72, tests/test_repairs.py:326, tests/test_repairs.py:328, tests/test_notify.py:38. The legacy path is exercised only there — `assert can_transition("adjudication", "action")` and `assert can_transition("action", "completed")` — which methodology §2.3 says confers nothing, so the ground is a bare label, what this row's own fit criterion disqualifies. The tests-scoped search was asserted without being quoted in round 4; the round-5 finding is accepted and it is quoted here. The nearest remaining candidate, `checks.py`'s docstring, explains which defect the shared vocabulary fixed rather than substantiating a ground against the §6 baseline. Several components are retained serving no requirement: `verdict.validate_structure` and `read_verdict`, `risk.BoundedChange`, `write_assessment`/`read_assessment`, `DEFAULT_PROTECTED` and `ProtectedTriggerError`, `states.assert_job_exists`, and the `can_approve`/`action_recommended` fields no branch reads — each established by its cited unit's own caller search, not by this row. |
| RQA-FR-035 | full gap | not built | requirements/requirements-specification.md:1319, requirements/clause-inventory.md:63, gap/manifest.md:52 | - | 9267b6308 | Nothing in the 121 assessed files addresses the issue-tracker state this row requires. Search re-run over the whole skill directory and quoted as it returned: `grep -rl -e "#109" -e "#535" -e "#536" .` → six files, five under `requirements/` (the specification, the normative extract, the quality assessment, the methodology and the clause inventory — the frozen specification's own derivation material) and `gap/register/fr.md`, this row's own text; no assessed file. Settled by observation, not interpretation: on 2026-09-08 the maintainer queried the tracker himself and recorded what it returned — `gh issue view {109,535,536} --repo launchpad-26/buzz --json number,state,stateReason` → `109 OPEN  - enh: agent workflow — PR review agent as a first-pass reviewer`, `535 OPEN  - feature: review agent reviews real PRs`, `536 OPEN  - feature: review agent gating decided and validated`. All three are open and none carries a state reason, so none is closed and none is re-parented: #109 satisfies neither limb of the first condition, #535 and #536 are not reconciled against this scope, and three open review-agent issues cannot be the exactly-one authoritative scope the third condition names. The recorded `full gap` / `not built` is therefore confirmed correct, and the observation is his on that date rather than a claim this tree-scoped analysis re-derived — it is recorded here so the next reader inherits it instead of re-querying. This requirement is satisfiable only by action on the issue tracker: it is #2068's work, not code, so no disposition unit can ever serve it, which is why this row cites no `U-` id and why the absence of one is correct rather than an omission. |

## Raw search output

Verbatim stdout for the searches whose hits the rows above enumerate, pasted
as returned, per the 2026-09-06 ruling: a tree-wide absence or count is
evidenced by the command and its raw output, while a named artefact's
structure is evidenced by a `path:line` into that artefact and needs no
command. Every command was run with `launchpad/skills/review-queue-automation`
as the working directory, at `9267b6308`. Each row states the same count and
names the same hits inline, so the arithmetic is checkable inside the table
and the transcription is checkable against these blocks.

**RQA-FR-008** — 1 matching line(s).

```
$ grep -rniE "mechanical" scripts/ schemas/
scripts/planner.py:125:#: mechanically narrower and does not need the deep code questions.
```

**RQA-FR-008** — 9 matching line(s).

```
$ grep -rniE "categor" scripts/ schemas/
scripts/errors.py:199:# Error category registry: retryability + authority + severity + escalation
scripts/errors.py:202:# the category constrains autonomy:
scripts/errors.py:207:CATEGORY_META: dict[str, dict[str, Any]] = {
scripts/errors.py:221:    # spec categories that map onto dispositions / markers
scripts/errors.py:234:for _k in list(CATEGORY_META):
scripts/errors.py:240:        # these are additional named categories, not dispositions
scripts/errors.py:244:def category_meta(disposition: str) -> dict[str, Any]:
scripts/errors.py:245:    """Return the safety metadata for a disposition/category (fail-safe unknown)."""
scripts/errors.py:246:    return CATEGORY_META.get(disposition, {
```

**RQA-FR-005 (also cited by RQA-FR-006, RQA-FR-007, RQA-FR-020)** — 21 matching line(s).

```
$ grep -rni -e material -e reuse -e regenerat -e invalidat scripts/
scripts/dispatcher.py:1071:    material and must not reach the log.
scripts/notify.py:63:    """Redact a field value that looks like it carries credential material."""
scripts/modes.py:167:    what the disagreement means, and folding it in here would turn a material
scripts/assurance.py:15:or on material disagreement the panel cannot settle, control moves to a human.
scripts/assurance.py:32:    "MATERIAL_DISAGREEMENT",
scripts/assurance.py:110:    if "MATERIAL_DISAGREEMENT" in signals:
scripts/common.py:553:            # response: a 304 reuses the ORIGINAL Link so later pages are not lost.
scripts/approval.py:8:Idempotency: enqueueing the same (repo, number, head, policy, job) reuses the
scripts/approval_evaluate.py:63:    change invalidates a previously persisted decision. Deterministic."""
scripts/panel.py:79:    "MATERIAL_DISAGREEMENT",
scripts/panel.py:561:    # reused for the attempt log below, so it is computed exactly once.
scripts/logging_otel.py:150:        # Skip anything that looks like credential material or evidence envelope/body.
scripts/model_registry.py:85:def runtime_route_material(config: dict[str, Any]) -> dict[str, Any]:
scripts/model_registry.py:102:def route_material_fingerprint(config: dict[str, Any]) -> str:
scripts/model_registry.py:103:    material = runtime_route_material(config)
scripts/model_registry.py:104:    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
scripts/model_registry.py:116:    fingerprint = route_material_fingerprint(config)
scripts/model_registry.py:142:    """Mark the current route material qualified after every configured probe passes."""
scripts/model_registry.py:145:    fingerprint = route_material_fingerprint(config)
scripts/verdict.py:28:    "MATERIAL_DISAGREEMENT",
scripts/verdict.py:37:    (lambda d: d.get("signal") in ("MISSING_EVIDENCE", "INSUFFICIENT_CAPABILITY", "MATERIAL_DISAGREEMENT", "HUMAN_RESERVED") and d.get("recommendation") == "clean", "signal conflicts with clean recommendation"),
```

**RQA-FR-016** — 9 matching line(s).

```
$ grep -rn "blocked" scripts/
scripts/dispatcher.py:672:            summary=f"{repo}#{number} approval blocked at revalidation",
scripts/dispatcher.py:1389:        _log(logger, "error", body="job blocked", phase="assurance",
scripts/shadow.py:414:    unblocked_bad = [
scripts/shadow.py:420:    if not unblocked_bad:
scripts/shadow.py:429:    learned = max(0, min(int(configured_max), min(unblocked_bad) - 1))
scripts/shadow.py:435:                  f"cleared every non-risk gate was {min(unblocked_bad)}; the "
scripts/shadow.py:634:        entries.append({"risk": r["risk_score"], "blocked": bool(non_risk_failed), "outcome": r["outcome"]})
scripts/shadow.py:635:    candidates = sorted({e["risk"] for e in entries if not e["blocked"]} | {0, int(current_max)})
scripts/shadow.py:638:        approvable = [e for e in entries if not e["blocked"] and e["risk"] <= t]
```

**RQA-FR-027** — 20 matching line(s).

```
$ grep -rn "approval_revalidation" scripts/
scripts/dispatcher.py:88:    "approval_revalidation": 6,   # live
scripts/dispatcher.py:583:    The job stays in `approval_revalidation` for the duration of the call, because
scripts/dispatcher.py:1463:        _transition_guarded(state, job_id, "approval_revalidation", logger=logger,
scripts/dispatcher.py:1876:    "approval_evaluation", "approval_revalidation", "approval_action",
scripts/queue.py:33:               "approval_revalidation", "human_approval_pending", "advisory_action",
scripts/budget.py:73:    "approval_evaluation", "approval_revalidation", "approval_action",
scripts/human_cli.py:123:    if not can_transition("human_approval_pending", "approval_revalidation"):
scripts/human_cli.py:126:        "UPDATE jobs SET status='approval_revalidation', reason=?, updated_at=? WHERE id=?",
scripts/human_cli.py:133:        "status": "approval_revalidation",
scripts/approval.py:245:    `approval_revalidation`. `decline`/`request_changes` are terminal: the bound
scripts/states.py:7:    approval_evaluation -> would_auto_approve | approval_revalidation |
scripts/states.py:10:    would_auto_approve -> approval_revalidation
scripts/states.py:11:    approval_revalidation -> approval_action
scripts/states.py:13:    human_approval_pending -> approval_revalidation | completed_human_declined |
scripts/states.py:52:        "approval_revalidation",
scripts/states.py:91:        {"would_auto_approve", "approval_revalidation", "human_approval_pending",
scripts/states.py:94:    "would_auto_approve": frozenset({"approval_revalidation", "superseded", "safe_stop"}),
scripts/states.py:95:    "approval_revalidation": frozenset(
scripts/states.py:100:        {"approval_revalidation", "completed_human_declined", "advisory_action", "degraded", "safe_stop", "superseded"}
scripts/states.py:110:    "human_required": frozenset({"superseded", "approval_revalidation", "advisory_action", "safe_stop"}),
```

**RQA-FR-034** — 12 matching line(s).

```
$ grep -rn '"action"' scripts/
scripts/dispatcher.py:653:    _ledger_record(state, job, head_sha, "action", {
scripts/dispatcher.py:846:    _ledger_record(state, job, head_sha, "action", {
scripts/dispatcher.py:1027:    _ledger_record(state, job, head_sha, "action", {
scripts/queue.py:34:               "action", "retryable", "held")
scripts/ledger.py:41:ACTION = "action"
scripts/notify.py:118:        "action_required": request.get("action"),
scripts/approval.py:59:    "rationale", "action", "decision", "decision_actor", "decided_at",
scripts/approval.py:143:        "action": action,
scripts/lease.py:125:    parser.add_argument("action", choices=["claim", "release", "verify"])
scripts/states.py:59:        "action",          # preserved legacy sink -> completed
scripts/states.py:89:    "adjudication": frozenset({"action", "approval_evaluation", "human_required", "held", "retryable", "superseded", "safe_stop"}),
scripts/states.py:104:    "action": frozenset({"completed", "held", "human_required", "superseded", "approval_evaluation", "safe_stop"}),
```

**RQA-FR-034** — 8 matching line(s).

```
$ grep -rn '"action"' tests/
tests/test_errors_states.py:54:        "human_required", "action", "completed", "superseded",
tests/test_errors_states.py:64:    assert can_transition("adjudication", "action")
tests/test_errors_states.py:65:    assert can_transition("action", "completed")
tests/test_errors_states.py:71:    assert not can_transition("human_required", "action")
tests/test_errors_states.py:72:    assert not can_transition("completed", "action")
tests/test_repairs.py:326:    assert can_transition(None, "action") is False
tests/test_repairs.py:328:    assert can_transition("completed", "action") is False
tests/test_notify.py:38:        "action": "approve",
```
