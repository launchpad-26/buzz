# RQA requirements specification

## Provenance and pin

This specification is derived solely from
[`prd-2006-normative-extract.md`](prd-2006-normative-extract.md), the verbatim extract of
[launchpad-26/buzz#2006](https://github.com/launchpad-26/buzz/issues/2006)'s Problem, Success criteria, Non-goals
and Security implications sections. It was authored without reading any other file under this skill's directory,
any GitHub issue, or any implementation of RQA.

- **Pinned to #2006 as of:** `updated_at` `2026-09-01T06:34:12Z`, body SHA-256
  `12bb2a6d5ca0f55446332e9f4300faa1a392b835f6457f49c303ea5f1ef596dd`, extract committed at `7c41608be`. If #2006 is
  amended, this pin goes stale and is detectable rather than silent.
- **Frozen for [#2069](https://github.com/launchpad-26/buzz/issues/2069) at commit** `be77edee5` — the
  panel-approved wording baseline `validate.py` compares against. This restructured presentation of the
  same content was committed at `02272b10c`.
- **Published here** because [#2067](https://github.com/launchpad-26/buzz/issues/2067) is the feature that
  produced it; where policy documents belong repo-wide is an open question owned by
  [#2064](https://github.com/launchpad-26/buzz/issues/2064), not by this document.
- **Open questions this specification surfaces but does not settle** are drafted under
  [`adr-drafts/`](adr-drafts/) and referenced from the affected requirements below by token (`ADR-A`, `ADR-B`,
  `ADR-C`); none has been filed as a GitHub issue yet — see [`adr-drafts/README.md`](adr-drafts/README.md).

---

## What this is

**Review Queue Automation (RQA)** reviews pull requests automatically: it checks a PR against a repository's
own rules, decides whether the PR passes, and can act on the result (comment, approve, request changes, fix a
small class of issues itself, or hand a decision to a person). It is meant to replace ad-hoc, inconsistent human
review with something repeatable, auditable, and no more expensive than it needs to be.

**This document is RQA's requirements specification** — the list of things RQA must be true of, written as
individually identified, checkable statements. It does not say how RQA is built. It says what any build of RQA
has to satisfy, and how a reader can tell whether a given build satisfies it.

Every requirement below carries one `shall` obligation, a plain-English gloss of that obligation, the exact
source text it comes from, and a fit criterion — the specific, checkable thing that decides whether the
obligation is met. **The gloss is not itself a requirement.** Only the `shall` statement and the fit criterion
are binding; the gloss exists to help a reader who is new to RQA understand the statement faster.

> **Non-normative material is marked.** Only a requirement's `shall` statement and its fit criterion are binding. Every *In plain terms* gloss, every section introduction, and every `See also` note exists to help a reader, and is not itself a requirement.

---

## Reading order

- **New to RQA?** Read this page top to bottom once: the purpose above, then the eleven sections below in order.
  Each section opens with one sentence naming the question it answers.
- **Looking for one requirement?** Every requirement has a unique ID, prefixed `RQA-BR-`, `RQA-FR-`, or
  `RQA-NFR-` plus a number — for example `RQA-FR-005`. Search this file for that exact ID; each appears in
  exactly one place, as a heading.
- **Reviewing everything a repository, or a feature, touches?** Use the class indexes just below to see every
  business, functional, or non-functional requirement at a glance, grouped by ID rather than by topic.
- **Want the reasoning behind how this document was built** — the 29148 methodology, the EARS patterns, the
  source-clause inventory, how one acceptance criterion sometimes became several requirements, the quality
  assessment, or the open questions raised as ADRs — see [Cold reference material](#cold-reference-material) at
  the end of this document.

---

## Requirements by class

**Business requirements (14):**

| ID | ID | ID | ID | ID | ID |
|---|---|---|---|---|---|
| [RQA-BR-001](#rqa-br-001) | [RQA-BR-002](#rqa-br-002) | [RQA-BR-003](#rqa-br-003) | [RQA-BR-004](#rqa-br-004) | [RQA-BR-005](#rqa-br-005) | [RQA-BR-006](#rqa-br-006) |
| [RQA-BR-007](#rqa-br-007) | [RQA-BR-008](#rqa-br-008) | [RQA-BR-009](#rqa-br-009) | [RQA-BR-010](#rqa-br-010) | [RQA-BR-011](#rqa-br-011) | [RQA-BR-012](#rqa-br-012) |
| [RQA-BR-013](#rqa-br-013) | [RQA-BR-014](#rqa-br-014) |  |  |  |  |

**Functional requirements (39):**

| ID | ID | ID | ID | ID | ID |
|---|---|---|---|---|---|
| [RQA-FR-001](#rqa-fr-001) | [RQA-FR-002](#rqa-fr-002) | [RQA-FR-003](#rqa-fr-003) | [RQA-FR-004](#rqa-fr-004) | [RQA-FR-005](#rqa-fr-005) | [RQA-FR-006](#rqa-fr-006) |
| [RQA-FR-007](#rqa-fr-007) | [RQA-FR-008](#rqa-fr-008) | [RQA-FR-009](#rqa-fr-009) | [RQA-FR-010](#rqa-fr-010) | [RQA-FR-011](#rqa-fr-011) | [RQA-FR-012](#rqa-fr-012) |
| [RQA-FR-013](#rqa-fr-013) | [RQA-FR-014](#rqa-fr-014) | [RQA-FR-015](#rqa-fr-015) | [RQA-FR-016](#rqa-fr-016) | [RQA-FR-017](#rqa-fr-017) | [RQA-FR-018](#rqa-fr-018) |
| [RQA-FR-019](#rqa-fr-019) | [RQA-FR-020](#rqa-fr-020) | [RQA-FR-021](#rqa-fr-021) | [RQA-FR-022](#rqa-fr-022) | [RQA-FR-023](#rqa-fr-023) | [RQA-FR-024](#rqa-fr-024) |
| [RQA-FR-025](#rqa-fr-025) | [RQA-FR-026](#rqa-fr-026) | [RQA-FR-027](#rqa-fr-027) | [RQA-FR-028](#rqa-fr-028) | [RQA-FR-029](#rqa-fr-029) | [RQA-FR-030](#rqa-fr-030) |
| [RQA-FR-031](#rqa-fr-031) | [RQA-FR-032](#rqa-fr-032) | [RQA-FR-033](#rqa-fr-033) | [RQA-FR-034](#rqa-fr-034) | [RQA-FR-035](#rqa-fr-035) | [RQA-FR-036](#rqa-fr-036) |
| [RQA-FR-037](#rqa-fr-037) | [RQA-FR-038](#rqa-fr-038) | [RQA-FR-039](#rqa-fr-039) |  |  |  |

**Non-functional requirements (30):**

| ID | ID | ID | ID | ID |
|---|---|---|---|---|
| [RQA-NFR-001](#rqa-nfr-001) | [RQA-NFR-002](#rqa-nfr-002) | [RQA-NFR-003](#rqa-nfr-003) | [RQA-NFR-004](#rqa-nfr-004) | [RQA-NFR-005](#rqa-nfr-005) |
| [RQA-NFR-006](#rqa-nfr-006) | [RQA-NFR-007](#rqa-nfr-007) | [RQA-NFR-008](#rqa-nfr-008) | [RQA-NFR-009](#rqa-nfr-009) | [RQA-NFR-010](#rqa-nfr-010) |
| [RQA-NFR-011](#rqa-nfr-011) | [RQA-NFR-012](#rqa-nfr-012) | [RQA-NFR-013](#rqa-nfr-013) | [RQA-NFR-014](#rqa-nfr-014) | [RQA-NFR-015](#rqa-nfr-015) |
| [RQA-NFR-016](#rqa-nfr-016) | [RQA-NFR-017](#rqa-nfr-017) | [RQA-NFR-018](#rqa-nfr-018) | [RQA-NFR-019](#rqa-nfr-019) | [RQA-NFR-020](#rqa-nfr-020) |
| [RQA-NFR-021](#rqa-nfr-021) | [RQA-NFR-022](#rqa-nfr-022) | [RQA-NFR-023](#rqa-nfr-023) | [RQA-NFR-024](#rqa-nfr-024) | [RQA-NFR-025](#rqa-nfr-025) |
| [RQA-NFR-026](#rqa-nfr-026) | [RQA-NFR-027](#rqa-nfr-027) | [RQA-NFR-028](#rqa-nfr-028) | [RQA-NFR-029](#rqa-nfr-029) | [RQA-NFR-030](#rqa-nfr-030) |

---

## Requirements by topic

1. [Protocol and assurance](#protocol-and-assurance)
2. [Policy, findings and blocking](#policy-findings-and-blocking)
3. [Revision reuse and check attribution](#revision-reuse-and-check-attribution)
4. [Evidence and provenance](#evidence-and-provenance)
5. [Lifecycle, disposition and merge](#lifecycle-disposition-and-merge)
6. [Remediation and escalation](#remediation-and-escalation)
7. [Capacity and resilience](#capacity-and-resilience)
8. [Harness interoperability and operation](#harness-interoperability-and-operation)
9. [External provider sensitivity](#external-provider-sensitivity)
10. [Authority, credentials and untrusted content](#authority-credentials-and-untrusted-content)
11. [Scope and design baseline](#scope-and-design-baseline)

---

## Protocol and assurance

What a review is, and what makes one trustworthy: one shared definition, applied the same way regardless of who or what performs it.

### RQA-BR-001

The review process for a pull request shall be consistent, auditable, efficient, and trustworthy.

*In plain terms: Reviews should work the same way every time, leave a trail, avoid wasted effort, and be believable.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-001** (Problem, paragraph 1, [extract](prd-2006-normative-extract.md#problem)): “Launchpad Buzz does not have a consistent, auditable, efficient, and trustworthy pull-request review process.”

**Fit criterion:** Each of the four qualities is validated by the source-derived obligations already in this set, not by an independent packaging or cardinality test of its own: consistency by RQA-BR-002's cross-reviewer definitional agreement; auditability by RQA-FR-012's full outcome reconstruction and RQA-NFR-022/RQA-NFR-028's tamper-evident provenance; efficiency by RQA-FR-019/RQA-FR-020's bound against policy-required work and RQA-FR-021's actual-versus-estimate distinction; trustworthiness by RQA-FR-011's disposition gate and RQA-FR-013's approval-basis naming. This row is satisfied exactly when those cited rows are; no separate 'one audit trail per PR' packaging constraint or bare bound-exists proxy is imposed here.

### RQA-BR-002

A pull-request review shall have one consistent definition across the repository, independent of which reviewer performed it.

*In plain terms: Two people should describe what a pull-request review is supposed to check the same way, regardless of who reviewed it.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-006** (P1, [extract](prd-2006-normative-extract.md#problem)): “No shared review protocol. Reviewers use independently designed processes, so a review has no consistent definition across the repository.”

**Fit criterion:** Given the same class of change reviewed under this repository's protocol, two reviewers independently describe the same review scope, required evidence, findings taxonomy, blocking conditions, review-completion condition, and final-disposition semantics — all six of AC01/CL-028's protocol concepts, not a subset of them; agreement on only some (e.g. scope and evidence but not blocking conditions or disposition semantics) does not satisfy this check.

### RQA-FR-001

Every managed review shall produce a verdict that validates against one published protocol definition covering review scope, required evidence, findings, blocking conditions, review completion and final disposition.

*In plain terms: There should be one written definition of what a review checks, what evidence it needs, and how it ends, and every completed review should match it.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: [#2064](https://github.com/launchpad-26/buzz/issues/2064) (repo-wide policy/contract document placement)

**Source:**
- **CL-028** (AC01, [extract](prd-2006-normative-extract.md#success-criteria)): “Every RQA-managed review produces a verdict that validates against one published protocol definition covering review scope, required evidence, findings, blocking conditions, review completion and final disposition; two reviews of the same PR by different harnesses, models or providers carry the same concept semantics.”

**Fit criterion:** A verdict from any managed review can be checked against a single published protocol definition and either validates or fails validation against it; there is exactly one such definition in force for the review, however it is packaged (a single document, a schema plus prose, or any other representation).

### RQA-FR-002

Two reviews of the same pull request performed by different harnesses, models or providers shall carry the same concept semantics.

*In plain terms: If two different AI systems review the same PR, they should mean the same thing by their verdicts, even though the systems are different.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-028** (AC01, [extract](prd-2006-normative-extract.md#success-criteria)): “Every RQA-managed review produces a verdict that validates against one published protocol definition covering review scope, required evidence, findings, blocking conditions, review completion and final disposition; two reviews of the same PR by different harnesses, models or providers carry the same concept semantics.”

**Fit criterion:** Given two review records for the same PR produced through different harnesses, models or providers, each of the protocol concepts AC01 names — review scope, required evidence, findings, blocking conditions, review completion, and final disposition — means the same thing in both records; agreement on only some of these concepts does not satisfy this check.

**See also:** [RQA-FR-030](#rqa-fr-030) (harness/model/provider interoperability, Harness interoperability and operation)

---

## Policy, findings and blocking

How a repository's own policy decides what counts as a finding and what blocks a merge — and why two repositories can legitimately disagree.

### RQA-BR-004

The threshold at which a finding blocks a pull request shall be consistent rather than left to each reviewer's individual judgement.

*In plain terms: The line between "this blocks the merge" and "this doesn't" should be a repository rule, not a personal call.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-008** (P3, [extract](prd-2006-normative-extract.md#problem)): “Blocking semantics are inconsistent. Reviewers apply materially different thresholds for CHANGES_REQUESTED, so GitHub review state has no consistent meaning.”

**Fit criterion:** Two reviewers applying the same policy to equivalent findings reach the same blocking decision.

### RQA-BR-005

Mechanical, procedural, or creation-time findings shall not be indistinguishable in the record from substantive correctness, security, architectural or evidence findings merely because both block.

*In plain terms: A trivial typo and a real security bug both blocking the PR shouldn't look the same in the record — the record should say which kind each finding is.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-009** (P4, [extract](prd-2006-normative-extract.md#problem)): “Mechanical and substantive findings share one blocking mechanism. Procedural issues and correctness/security/architectural/evidence failures are all expressed as CHANGES_REQUESTED.”
- **CL-002** (Problem, paragraph 2, [extract](prd-2006-normative-extract.md#problem)): “Reviews are performed using different reviewer-defined protocols, different blocking thresholds, and inconsistent levels of evidence. Review records do not consistently capture structured provenance showing who or what performed the review or which process was followed. The same unchanged revision is frequently reviewed multiple times, while mechanical or creation-time defects can consume the same blocking mechanism as substantive correctness, security, architectural, or evidence failures.”

**Fit criterion:** Given a mechanical, procedural, or creation-time finding and a substantive finding that both contribute to the same blocking outcome on a PR, a reader can still tell them apart in the record by category and decision basis; two policy-blocking findings sharing the one authoritative outcome C6/AC14 require does not, by itself, fail this check — what fails it is a record in which the two categories of finding cannot be told apart at all.

### RQA-FR-003

Two repositories configured with different review policies shall be able to produce demonstrably different blocking outcomes on the same diff.

*In plain terms: Two repositories with different review rules are allowed to reach different pass/fail verdicts on an identical change.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-029** (AC02, [extract](prd-2006-normative-extract.md#success-criteria)): “Two repositories configured with different review policies produce demonstrably different blocking outcomes on the same diff, and a policy change takes effect on the next review with no rebuild, reinstall or redeploy.”

**Fit criterion:** The same diff submitted under two differently configured repository policies produces two blocking outcomes, and the difference is attributable to the policy configuration.

**See also:** [RQA-FR-004](#rqa-fr-004) (same source criterion (AC02))

### RQA-FR-008

Every finding shall carry a category distinguishing mechanical, procedural and creation-time findings from correctness, security, architectural and evidence findings.

*In plain terms: Every finding should be labelled as either a mechanical/procedural issue or a substantive one (correctness, security, architecture, evidence).*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-031** (AC04, [extract](prd-2006-normative-extract.md#success-criteria)): “Every finding carries a category distinguishing mechanical, procedural and creation-time findings from correctness, security, architectural and evidence findings, and whether it blocks is decided by repository policy, not by the reviewer's severity choice alone.”

**Fit criterion:** Every finding in a review record carries at least one category that makes the mechanical-vs-substantive distinction observable, drawn from one of the two named groups — mechanical/procedural/creation-time, or correctness/security/architectural/evidence — and no finding is uncategorised. A finding may additionally carry further categories outside those two groups (for example, an orthogonal 'performance' tag) without failing this check, and a finding legitimately carrying two categories from the two named groups also satisfies it, provided the distinguishing category is present and observable; this check does not close the category taxonomy to only the two named groups.

### RQA-FR-009

Whether a finding blocks a pull request shall be decided by repository policy, not by the reviewer's severity choice alone.

*In plain terms: Whether a finding blocks the PR is decided by the repository's policy, not by how severe an individual reviewer feels it is.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-031** (AC04, [extract](prd-2006-normative-extract.md#success-criteria)): “Every finding carries a category distinguishing mechanical, procedural and creation-time findings from correctness, security, architectural and evidence findings, and whether it blocks is decided by repository policy, not by the reviewer's severity choice alone.”

**Fit criterion:** Given a finding's category, repository policy, and any other input the policy itself declares relevant — which may include reviewer severity as one named input alongside others — the blocking decision is reproducible from those inputs; this check fails only where reviewer severity, independent of repository policy and its other declared inputs, alone determines the blocking decision. A policy that declares severity as one input among several does not fail this check merely for including it.

---

## Revision reuse and check attribution

How the review avoids redoing work on an unchanged revision, and how it decides whether a failing check belongs to the pull request or to its base branch.

### RQA-BR-007

Review work shall not be duplicated across a revision that has not changed.

*In plain terms: If nothing changed, the review shouldn't redo work it already did.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-011** (P6, [extract](prd-2006-normative-extract.md#problem)): “Review work is duplicated across unchanged revisions.”

**Fit criterion:** Requesting review twice on an identical revision does not repeat the same reviewer work twice.

### RQA-BR-009

A failing automated review or check signal shall carry an attribution — to the pull request, the base, a procedural cause, incomplete automation, unrelated infrastructure, or a genuine blocker — without requiring a human to decide which.

*In plain terms: When an automated check fails, the record should say why it's being treated as a failure of this PR (versus the base branch, a flaky test, or something unrelated) — without a human having to work that out.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-013** (P8, [extract](prd-2006-normative-extract.md#problem)): “Automated review and check signals require manual interpretation. Humans must decide whether a failure is attributable to the PR, inherited from base, procedural, incomplete automation, unrelated infrastructure, or a genuine blocker.”

**Fit criterion:** Given a failing automated review signal or a failing check, a reader finds its attribution in the record rather than having to investigate and decide it themselves; a system that attributes only check failures and leaves automated-review-signal failures uninterpreted fails this check.

### RQA-FR-005

A push that changes nothing material shall re-run zero reviewer calls.

*In plain terms: If a push doesn't change anything that matters to the review, no reviewer call should run again for it.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-030** (AC03, [extract](prd-2006-normative-extract.md#success-criteria)): “A push that changes nothing material re-runs zero reviewer calls; a push touching file X re-runs only the review obligations invalidated by that change; the reused and regenerated sets are both recorded and inspectable.”

**Fit criterion:** A push whose diff is immaterial to every review obligation is followed by reliable, independently checkable evidence that zero reviewer invocations occurred — a boundary trace, an audited invocation log, or an equivalent independently corroborated observation; a bare recorded counter reading zero, with no independent corroboration, is insufficient on its own to satisfy this check.

### RQA-FR-006

A push that touches file X shall re-run only the review obligations that push invalidates.

*In plain terms: If a push only touches one file, only the checks that file could affect should re-run — not the whole review.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-030** (AC03, [extract](prd-2006-normative-extract.md#success-criteria)): “A push that changes nothing material re-runs zero reviewer calls; a push touching file X re-runs only the review obligations invalidated by that change; the reused and regenerated sets are both recorded and inspectable.”

**Fit criterion:** For a push touching a known file, the set of obligations re-run is exactly the set invalidated by that file's change — no more, no less; where that invalidated set is every obligation (for example, a root policy-file change that legitimately invalidates all of them), re-running all of them satisfies this check, since the criterion tests set equality with what the push actually invalidates, not a bound below the total.

### RQA-FR-007

The set of review obligations reused from a prior revision and the set regenerated for the current revision shall each be recorded and inspectable.

*In plain terms: The review should keep a visible record of which checks it reused from before and which ones it redid.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-030** (AC03, [extract](prd-2006-normative-extract.md#success-criteria)): “A push that changes nothing material re-runs zero reviewer calls; a push touching file X re-runs only the review obligations invalidated by that change; the reused and regenerated sets are both recorded and inspectable.”

**Fit criterion:** For any review, a reader can retrieve both the reused-obligation set and the regenerated-obligation set and see which obligation is in which.

### RQA-FR-014

When a pull request's only failing check also fails on its merge base, the review shall classify that failure as inherited rather than attributable.

*In plain terms: If a PR's only failing check also fails on the branch it's built from, that failure is the base branch's problem, not the PR's.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-034** (AC07, [extract](prd-2006-normative-extract.md#success-criteria)): “For a PR whose only failing check also fails on its merge base, RQA classifies that failure as inherited rather than attributable, does not treat it as a blocker, and states the classification.”

**Fit criterion:** Given a pull request whose only failing check also fails on its merge base, the review's decision behaviour and decision basis treat that failure as inherited rather than attributable — for example, excluding it from the blocking-condition evaluation — independent of whether that classification is yet persisted in or exposed from the review record, which RQA-FR-015 tests separately; the check does not apply to a PR with more than one failing check.

### RQA-FR-015

When a pull request's only failing check also fails on its merge base, the review shall state the inherited-versus-attributable classification of that failure in the record.

*In plain terms: The review record should explicitly say whether a failing check belongs to the PR or was inherited from its base.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-034** (AC07, [extract](prd-2006-normative-extract.md#success-criteria)): “For a PR whose only failing check also fails on its merge base, RQA classifies that failure as inherited rather than attributable, does not treat it as a blocker, and states the classification.”

**Fit criterion:** For a pull request whose only failing check also fails on its merge base, the inherited classification of that failure is retrievable from the review record; the check does not extend to a classification of a check failure outside AC07's own condition.

### RQA-FR-036

When a pull request's only failing check also fails on its merge base, the review shall not treat that failure as a blocker.

*In plain terms: A failing check that's inherited from the base branch shouldn't be treated as something that blocks this PR.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-034** (AC07, [extract](prd-2006-normative-extract.md#success-criteria)): “For a PR whose only failing check also fails on its merge base, RQA classifies that failure as inherited rather than attributable, does not treat it as a blocker, and states the classification.”

**Fit criterion:** Given a pull request whose only failing check also fails on its merge base, that failure does not contribute to a blocking disposition, even though every other required obligation is still checked normally.

---

## Evidence and provenance

What a review has to prove it actually checked, and what a completed review record has to be able to show about itself afterwards.

### RQA-BR-003

A review record shall establish who or what performed the review, which protocol was followed, and how the judgement was produced.

*In plain terms: A finished review record should say who or what did it, what rules it followed, and how it reached its verdict.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-007** (P2, [extract](prd-2006-normative-extract.md#problem)): “Review provenance is not recorded. Records do not establish who or what reviewed, which protocol was followed, or how the judgement was produced.”

**Fit criterion:** Given any review record, a reader can name its performer, its protocol, and the basis of its judgement without asking the performer.

### RQA-BR-008

Review output shall establish whether the higher-value claims, risks and cited evidence in a pull request were verified, not only its labels, metadata or formatting.

*In plain terms: A review's output should show whether the PR's actual claims and evidence were checked — not just that some checkboxes were ticked.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-012** (P7, [extract](prd-2006-normative-extract.md#problem)): “Review output has poor signal-to-noise for assurance. Activity focuses on labels, metadata and formatting without establishing whether higher-value claims, risks or cited evidence were verified.”

**Fit criterion:** A reader of a review record can state which claims, risks or cited evidence were verified and which were not, distinct from cosmetic observations.

### RQA-BR-011

A human approval used to satisfy assurance shall preserve the evidence behind that approval, not merely satisfy merge mechanics.

*In plain terms: When a human's sign-off is used as proof of assurance, the evidence behind that sign-off should be kept, not thrown away once the merge button works.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-015** (P10, [extract](prd-2006-normative-extract.md#problem)): “Human approvals do not consistently preserve review evidence. Approval satisfies merge mechanics without preserving assurance evidence.”

**Fit criterion:** A human approval used to satisfy assurance carries retrievable evidence of what was examined, not only the fact of approval; an approval recorded only to satisfy merge mechanics, and never cited as assurance evidence, is outside this check's population and its absence of retrievable examination evidence does not fail it — the same assurance-use predicate RQA-FR-013's fit criterion applies.

### RQA-BR-014

Review activity on a pull request shall demonstrate that the important risks, claims and evidence associated with it were actually examined.

*In plain terms: A review should be able to show that the PR's important risks, claims and evidence were actually looked at, not skipped over.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-005** (Problem, paragraph 5, [extract](prd-2006-normative-extract.md#problem)): “The operational consequence is duplicated work, resource exhaustion, human interruption, and a growing review queue. The more important consequence is reduced assurance: substantial review activity does not consistently demonstrate that the important risks, claims, and evidence associated with a pull request were actually examined.”

**Fit criterion:** For a completed review, a reader can confirm from the record — not from trust in the activity's volume — that the important risks, claims and evidence were examined.

### RQA-FR-010

Every required review obligation shall carry an explicit evidence state from {verified, not verified, unavailable, contradictory, failed, incomplete, unknown}.

*In plain terms: Every obligation a review has to check should carry a clear status — verified, failed, unknown, and so on — not be left implicit.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-032** (AC05, [extract](prd-2006-normative-extract.md#success-criteria)): “Every required review obligation carries an explicit evidence state from {verified, not verified, unavailable, contradictory, failed, incomplete, unknown}, and no successful disposition can be produced while any required obligation is unsatisfied.”

**Fit criterion:** Every required obligation in a review record carries exactly one evidence state from the seven-value set, and no required obligation is left without one.

**See also:** [RQA-FR-011](#rqa-fr-011) (same source criterion (AC05))

### RQA-FR-012

For any authoritative review outcome, a single command shall reconstruct the exact PR revision, the protocol and policy in force, reviewer identity and type, harness, model, provider, evidence examined, findings produced, decision basis and disposition.

*In plain terms: For any official outcome, one command should be able to pull up exactly what was reviewed, under what rules, by whom or what, and why it ended that way.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-033** (AC06, [extract](prd-2006-normative-extract.md#success-criteria)): “For any authoritative review outcome, a single command reconstructs the exact PR revision, protocol and policy in force, reviewer identity and type, harness, model, provider, evidence examined, findings produced, decision basis and disposition; a human approval used to satisfy assurance names the approving human and the basis of that approval.”

**Fit criterion:** Running one command against an authoritative outcome returns each of the elements AC06 names — PR revision, protocol in force, policy in force, reviewer identity, reviewer type, harness, model, provider, evidence examined, findings produced, decision basis, and disposition — with none requiring a second lookup.

### RQA-FR-013

A human approval used to satisfy assurance shall name the approving human and the basis of that approval.

*In plain terms: When a human's approval is used to satisfy a requirement, the record should name that person and say what their approval was actually based on.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-033** (AC06, [extract](prd-2006-normative-extract.md#success-criteria)): “For any authoritative review outcome, a single command reconstructs the exact PR revision, protocol and policy in force, reviewer identity and type, harness, model, provider, evidence examined, findings produced, decision basis and disposition; a human approval used to satisfy assurance names the approving human and the basis of that approval.”

**Fit criterion:** Every recorded human approval used to satisfy assurance names a specific human and states the basis for that approval; an approval recorded only to satisfy merge mechanics, and never cited as assurance evidence, is outside this check's population and its absence of a named basis does not fail it.

### RQA-NFR-022

A provenance record shall never be writable by the reviewed content or by an unauthenticated model response.

*In plain terms: The record of who reviewed what, and how, must never be something the PR's own content or an unverified AI response could write into.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: [`ADR-C`](adr-drafts/ADR-C-external-harness-provenance-authentication.md)

**Source:**
- **CL-058** (Security implications, bullet 4, [extract](prd-2006-normative-extract.md#security-implications)): “Provenance must be forgeable-proof. AC06 records reviewer identity, harness, model and provider. If that record can be written by the reviewed content or by an unauthenticated model response, the audit trail is worse than none.”

**Fit criterion:** Attempting to set any element of the authoritative provenance record RQA-FR-012 reconstructs — PR revision, protocol in force, policy in force, reviewer identity, reviewer type, harness, model, provider, evidence examined, findings produced, decision basis, and disposition — from PR content or from an unauthenticated model response is rejected rather than accepted into the record; a check that exercises only the reviewer-identity/harness/model/provider fields and leaves the other eight elements untested does not satisfy this row.

### RQA-NFR-028

A provenance record shall be protected against forgery or alteration by any actor lacking authority to write it.

*In plain terms: The official review record has to be protected so nobody without the right authority can quietly forge or edit it.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: [`ADR-C`](adr-drafts/ADR-C-external-harness-provenance-authentication.md)

**Source:**
- **CL-058** (Security implications, bullet 4, [extract](prd-2006-normative-extract.md#security-implications)): “Provenance must be forgeable-proof. AC06 records reviewer identity, harness, model and provider. If that record can be written by the reviewed content or by an unauthenticated model response, the audit trail is worse than none.”

**Fit criterion:** For any authoritative outcome, no element of the provenance record RQA-FR-012 reconstructs — PR revision, protocol in force, policy in force, reviewer identity, reviewer type, harness, model, provider, evidence examined, findings produced, decision basis, and disposition — can be created or altered by an actor lacking authority to write it and then be **accepted as authentic and authoritative without detection**; tamper-evidence satisfies this check — for example, a signed or otherwise integrity-checked record whose unauthorised alteration produces a detectably invalid result that the system refuses to treat as authoritative. This row does not require the underlying storage bytes to be physically unalterable; it requires that an unauthorised alteration, if made, cannot pass as authentic. RQA-NFR-022 tests the two source-named writers against this same acceptance boundary, this row tests every other unauthorised actor against it.

---

## Lifecycle, disposition and merge

How a pull request's status is tracked end to end, how a review reaches its final verdict, and when merging after that verdict is allowed.

### RQA-FR-011

No successful disposition shall be produced while any required review obligation is unsatisfied.

*In plain terms: A review can't hand out a passing result while something it's required to check is still unresolved.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-032** (AC05, [extract](prd-2006-normative-extract.md#success-criteria)): “Every required review obligation carries an explicit evidence state from {verified, not verified, unavailable, contradictory, failed, incomplete, unknown}, and no successful disposition can be produced while any required obligation is unsatisfied.”

**Fit criterion:** A review in which some required obligation is neither in the 'verified' evidence state nor demonstrably satisfied through a recorded, named human approval under RQA-FR-013 that substantiates that specific obligation's content never yields a successful disposition; a named approval with no substantiated basis for the specific obligation it is claimed to satisfy does not, by itself, count that obligation as satisfied, and AC05's own evidence-state vocabulary is not bypassed by naming an approver alone.

**See also:** [RQA-FR-010](#rqa-fr-010) (same source criterion (AC05)), [RQA-FR-037](#rqa-fr-037) (dual-source restatement of the same proposition, AC14)

### RQA-FR-016

For any managed pull request, one command shall return its current disposition from {being reviewed, blocked, awaiting remediation, awaiting human judgement, review-complete, unable to progress} and the reason, without a human reconciling historical reviews, comments or checks.

*In plain terms: One command should tell you a PR's current status — in review, blocked, waiting on a fix, waiting on a person, done, or stuck — and why, without a human digging through history.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-035** (AC08, [extract](prd-2006-normative-extract.md#success-criteria)): “For any managed PR, one command returns its current disposition from {being reviewed, blocked, awaiting remediation, awaiting human judgement, review-complete, unable to progress} and the reason, without a human reconciling historical reviews, comments or checks.”

**Fit criterion:** Driving a managed PR through its observable lifecycle transitions and, after each transition, querying the one command shows a result and reason equal to the PR's independently established current state at that point — not merely one of the six legal values with a plausible-sounding reason regardless of the PR's actual state; a command that returns a stale or generic answer after a transition has occurred fails this check even if the value it returns is individually legal.

**See also:** [RQA-NFR-007](#rqa-nfr-007) (shares source criterion AC08)

### RQA-FR-028

When the review's obligations are satisfied, the review shall submit APPROVED or CHANGES_REQUESTED.

*In plain terms: Once every obligation is met, the review submits an official APPROVED or CHANGES_REQUESTED verdict.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-041** (AC14, [extract](prd-2006-normative-extract.md#success-criteria)): “RQA submits APPROVED or CHANGES_REQUESTED when the obligations are satisfied and cannot manufacture a successful outcome when they are not; one repository can be configured to merge after review and another configured not to, with both behaving accordingly.”

**Fit criterion:** Every review whose required obligations are all satisfied results in a submitted APPROVED or CHANGES_REQUESTED outcome; a satisfied review that submits neither fails this check.

### RQA-FR-029

The system shall merge after a successful review if and only if the repository is configured to merge after review.

*In plain terms: The system only auto-merges after a passing review if that repository has turned auto-merge-after-review on.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-041** (AC14, [extract](prd-2006-normative-extract.md#success-criteria)): “RQA submits APPROVED or CHANGES_REQUESTED when the obligations are satisfied and cannot manufacture a successful outcome when they are not; one repository can be configured to merge after review and another configured not to, with both behaving accordingly.”

**Fit criterion:** One repository configured to merge-after-review merges following a successful disposition; a second repository configured not to does not, on an otherwise identical successful disposition — both directions of the biconditional are exercised, not merely the enabled case.

### RQA-FR-037

The review shall never manufacture a successful outcome when its required obligations are not satisfied.

*In plain terms: The review must never claim success while something it's required to satisfy is actually unsatisfied — no matter what pressure there is to close it out.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-041** (AC14, [extract](prd-2006-normative-extract.md#success-criteria)): “RQA submits APPROVED or CHANGES_REQUESTED when the obligations are satisfied and cannot manufacture a successful outcome when they are not; one repository can be configured to merge after review and another configured not to, with both behaving accordingly.”

**Fit criterion:** A review whose required obligations are unsatisfied never results in a submitted APPROVED outcome, an internally recorded review-complete or other successful disposition (including the 'review-complete' value RQA-FR-016 names), or any other representation the protocol treats as a successful outcome, regardless of any other pressure to close it out; a check that exercises only the submitted APPROVED path and ignores an internally-recorded success signal does not satisfy this row.

**See also:** [RQA-FR-011](#rqa-fr-011) (dual-source restatement of the same proposition, AC05)

### RQA-NFR-007

The system shall manage every step of a pull request's review lifecycle, carrying it through to an authoritative APPROVED or CHANGES_REQUESTED outcome whenever progression remains possible.

*In plain terms: The system should carry a PR through every stage of review on its own, all the way to an official APPROVED or CHANGES_REQUESTED, whenever that's actually possible.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-023** (C6, [extract](prd-2006-normative-extract.md#problem)): “End-to-end GitHub review responsibility. Must manage the lifecycle through authoritative APPROVED or CHANGES_REQUESTED. Whether RQA also merges is configurable per repository.”
- **CL-035** (AC08, [extract](prd-2006-normative-extract.md#success-criteria)): “For any managed PR, one command returns its current disposition from {being reviewed, blocked, awaiting remediation, awaiting human judgement, review-complete, unable to progress} and the reason, without a human reconciling historical reviews, comments or checks.”
- **CL-039** (AC12, [extract](prd-2006-normative-extract.md#success-criteria)): “With a configured reviewer, model or provider made unavailable, RQA continues through an explicitly configured fallback; with no fallback configured it invents none and stops in a clear, safe, recoverable non-success state.”

**Fit criterion:** Every managed PR reaches an authoritative APPROVED or CHANGES_REQUESTED outcome, or the record carries evidence that no source-conforming next transition was available at the point the PR entered RQA-FR-038's safe non-success stop or RQA-FR-016's 'unable to progress' disposition; a PR labelled with either non-success alternative while an available reviewer, a valid policy, and no unresolved decision existed fails this check even though the label itself is a legal value. A recorded human approval (RQA-FR-013) or the input a raised escalation names being supplied and resuming the lifecycle (RQA-FR-026, RQA-FR-027) does not itself fail this check, because the system still initiates, tracks and incorporates that input.

**See also:** [RQA-FR-016](#rqa-fr-016) (shares source criterion AC08), [RQA-FR-023](#rqa-fr-023) (shares source criterion AC12, Capacity and resilience), [RQA-FR-024](#rqa-fr-024) (shares source criterion AC12, Capacity and resilience), [RQA-FR-038](#rqa-fr-038) (shares source criterion AC12, Capacity and resilience)

### RQA-NFR-008

Whether the system also merges after an authoritative outcome shall be configurable per repository.

*In plain terms: Whether the system also merges the PR after approving it is a per-repository on/off switch.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-023** (C6, [extract](prd-2006-normative-extract.md#problem)): “End-to-end GitHub review responsibility. Must manage the lifecycle through authoritative APPROVED or CHANGES_REQUESTED. Whether RQA also merges is configurable per repository.”

**Fit criterion:** Two repositories can independently be set to merge-after-review or not, and each behaves as configured.

---

## Remediation and escalation

When the system may fix something itself, when it must instead ask a human, and the limits on both.

### RQA-BR-006

A cheaply remediable, deterministic finding accompanied by its exact remedy shall not require a further contributor and a further review cycle to resolve.

*In plain terms: If a finding is simple, certain, and comes with its own fix, nobody should have to open a new review cycle just to apply that fix.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-010** (P5, [extract](prd-2006-normative-extract.md#problem)): “Cheaply remediable findings create unnecessary review cycles. An agent can identify a deterministic defect and supply the exact remedy, yet the fix still needs another contributor and another review cycle.”

**Fit criterion:** A deterministic defect with a supplied remedy is resolved without requiring **both** a second contributor turn **and** a second full review cycle together; a resolution needing one of the two alone — for example, one lightweight contributor acknowledgement with no further review cycle — satisfies this check. This tests only ¬(A∧B), the weaker of the two source-admitted readings (see this row's Unambiguous caveat), per round 7's correction of a prior criterion that operationalised the stronger ¬A∧¬B reading #2006's own text does not force; what fails this check is the combination occurring together, not either element occurring alone.

### RQA-BR-010

Progression of a pull request through review shall not depend on manual owner intervention beyond what genuinely requires human judgement.

*In plain terms: A PR should be able to move forward on its own unless it genuinely needs a person's judgement — an owner shouldn't be a bottleneck for things a machine can safely decide.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-014** (P9, [extract](prd-2006-normative-extract.md#problem)): “Progression depends heavily on manual owner intervention.”
- **CL-017** (P12, [extract](prd-2006-normative-extract.md#problem)): “PR review consumes scarce human attention and causes unnecessary interruption. Routine, mechanical or non-urgent PR issues impose context-switching costs where no human judgement is required.”
- **CL-040** (AC13, [extract](prd-2006-normative-extract.md#success-criteria)): “Routine, mechanical and non-urgent conditions raise no immediate human request; a required escalation names the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement; and supplying that input resumes the lifecycle without restarting the review.”

**Fit criterion:** A pull request whose findings require no human judgement is driven through every applicable lifecycle transition RQA-FR-016 names, and none of those transitions depends on owner action; a system that automates the first transition and then requires an owner to act on a later one, even where that later transition itself requires no judgement, fails this check.

### RQA-BR-013

Routine, mechanical or non-urgent pull-request conditions shall not interrupt a human where no human judgement is required.

*In plain terms: Small, routine, non-urgent issues shouldn't page a human if a human's judgement genuinely isn't needed to resolve them.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-017** (P12, [extract](prd-2006-normative-extract.md#problem)): “PR review consumes scarce human attention and causes unnecessary interruption. Routine, mechanical or non-urgent PR issues impose context-switching costs where no human judgement is required.”

**Fit criterion:** No condition genuinely requiring no human judgement ever raises a notification demanding a human's immediate attention. A condition that does require human judgement may still raise a specific, non-immediate required escalation (RQA-FR-026's own population) without failing this check — what this row prohibits is an immediate-attention interruption for a condition that did not need one, not every notification whatsoever; whether or when a condition is subsequently resolved or progressed remains a lifecycle-row concern (e.g. RQA-FR-016, RQA-FR-017), not this row's own test.

### RQA-FR-017

A finding classified as mechanical and permitted by policy shall be resolved without unnecessarily creating human intervention or a complete re-review cycle.

*In plain terms: If policy says a finding is safe and mechanical to fix, fixing it shouldn't drag in a human or force a full re-review.*

`State-driven` · `Must` · `DECIDED` · ADR: [`ADR-A`](adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md)

**Source:**
- **CL-036** (AC09, [extract](prd-2006-normative-extract.md#success-criteria)): “A finding classified as mechanical and permitted by policy is resolved without unnecessarily creating human intervention or a complete re-review cycle, and resolving it does not invalidate unrelated review work that remains valid. Per the baseline, this does not require RQA to modify code directly.”

**Fit criterion:** A mechanical, policy-permitted finding is resolved, and every human-intervention request or full re-review cycle generated in the course of resolving it is one a source-derived authority, evidence, or judgement gap genuinely makes necessary — necessity determined by repository policy where policy speaks to it; an intervention generated for any other reason while resolving the finding (for example, an unnecessary re-confirmation request unconnected to an authority, evidence, or judgement gap) fails this check even if it is not the request that formally closes the finding.

### RQA-FR-018

Resolving a finding classified as mechanical and permitted by policy shall not invalidate unrelated review work that remains valid.

*In plain terms: Fixing one mechanical finding shouldn't throw away other review work that's still valid.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: [`ADR-A`](adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md)

**Source:**
- **CL-036** (AC09, [extract](prd-2006-normative-extract.md#success-criteria)): “A finding classified as mechanical and permitted by policy is resolved without unnecessarily creating human intervention or a complete re-review cycle, and resolving it does not invalidate unrelated review work that remains valid. Per the baseline, this does not require RQA to modify code directly.”

**Fit criterion:** After a mechanical finding is resolved, every unrelated obligation that was previously satisfied remains valid and satisfied. Whether that unrelated obligation is also, redundantly, re-run is RQA-FR-020's own test (reuse of a valid result), not this row's — an unrelated obligation that is redundantly re-run but remains satisfied and valid does not fail this check; what fails it is a previously valid obligation becoming invalid or unsatisfied as a side effect of the remediation.

### RQA-FR-025

A routine, mechanical or non-urgent condition shall not raise an immediate human request.

*In plain terms: A routine, minor, non-urgent issue shouldn't immediately ping a human.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-040** (AC13, [extract](prd-2006-normative-extract.md#success-criteria)): “Routine, mechanical and non-urgent conditions raise no immediate human request; a required escalation names the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement; and supplying that input resumes the lifecycle without restarting the review.”

**Fit criterion:** No review event classified routine, mechanical or non-urgent generates a human-facing request that demands immediate attention.

### RQA-FR-026

A required escalation shall name the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement that produced it.

*In plain terms: When the review does have to escalate to a human, it must say exactly what decision, disagreement, missing evidence, missing information, or authority it's stuck on.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-040** (AC13, [extract](prd-2006-normative-extract.md#success-criteria)): “Routine, mechanical and non-urgent conditions raise no immediate human request; a required escalation names the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement; and supplying that input resumes the lifecycle without restarting the review.”

**Fit criterion:** Every escalation record names one of the five listed causes concretely, not as a generic 'needs attention' notice.

### RQA-FR-027

Supplying the input a raised escalation names shall resume the lifecycle without restarting the review.

*In plain terms: Once someone answers what an escalation asked for, the review picks back up from there — it doesn't start over.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-040** (AC13, [extract](prd-2006-normative-extract.md#success-criteria)): “Routine, mechanical and non-urgent conditions raise no immediate human request; a required escalation names the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement; and supplying that input resumes the lifecycle without restarting the review.”

**Fit criterion:** After the requested input is supplied for an open escalation, the review continues from its prior state rather than beginning again from the start.

### RQA-NFR-019

Remediation authority shall be bounded to only the finding categories a repository's policy names as mechanical.

*In plain terms: The system can only auto-fix the specific categories of issue that a repository's policy has explicitly labelled safe to auto-fix.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: [`ADR-A`](adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md)

**Source:**
- **CL-057** (Security implications, bullet 3, [extract](prd-2006-normative-extract.md#security-implications)): “Remediation authority is the largest new exposure. AC09 asks RQA to modify and push a branch. That authority must be separately gated, bounded to categories policy names as mechanical, isolated from the repository working tree, and never able to force-push, merge, bypass protection, or touch a protected branch.”

**Fit criterion:** Attempting a remediation action against a finding outside the categories the repository's policy names as mechanical is denied before it takes effect — the authority to perform it does not exist for that category; a run whose history merely happens not to have attempted one, with the broader authority still present, does not satisfy this check.

### RQA-NFR-020

Remediation shall be isolated from the repository's working tree.

*In plain terms: Auto-fixing has to happen somewhere separate from the repository's real working copy — it can't touch it directly.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: [`ADR-A`](adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md)

**Source:**
- **CL-057** (Security implications, bullet 3, [extract](prd-2006-normative-extract.md#security-implications)): “Remediation authority is the largest new exposure. AC09 asks RQA to modify and push a branch. That authority must be separately gated, bounded to categories policy names as mechanical, isolated from the repository working tree, and never able to force-push, merge, bypass protection, or touch a protected branch.”

**Fit criterion:** Attempting a remediation action against the repository's working tree — the boundary CL-057 itself names — is denied before it takes effect; the check does not require establishing whether a contributor was concurrently or 'actively' using that tree, because CL-057 names the working tree itself as the isolation boundary, not contributor activity within it.

### RQA-NFR-021

Remediation shall never force-push, merge, bypass branch protection, or touch a protected branch.

*In plain terms: Auto-fixing must never force-push, merge on its own, bypass branch protection, or touch a protected branch.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: [`ADR-A`](adr-drafts/ADR-A-ac09-remediation-code-modification-contradiction.md)

**Source:**
- **CL-057** (Security implications, bullet 3, [extract](prd-2006-normative-extract.md#security-implications)): “Remediation authority is the largest new exposure. AC09 asks RQA to modify and push a branch. That authority must be separately gated, bounded to categories policy names as mechanical, isolated from the repository working tree, and never able to force-push, merge, bypass protection, or touch a protected branch.”

**Fit criterion:** Attempting a force-push, a merge, a branch-protection bypass, or a write to a protected branch under remediation authority is denied before it takes effect; remediation authority is never able to perform any of the four, regardless of what a particular run's history shows — a run whose history is clean only because none was attempted, while the capability to perform one still exists, does not satisfy this check.

---

## Capacity and resilience

Using shared AI capacity no more than a policy requires, and behaving safely when a resource limit, reviewer, model or provider is unavailable.

### RQA-BR-012

Review activity shall use scarce model capacity efficiently, given that capacity is shared with implementation work.

*In plain terms: Reviews compete with real engineering work for the same AI capacity, so a review shouldn't burn more of it than the situation calls for.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-016** (P11, [extract](prd-2006-normative-extract.md#problem)): “PR review consumes scarce model capacity inefficiently. Capacity is shared with implementation work.”

**Fit criterion:** Comparing recorded model/token consumption for a review against what that review's policy states as required assurance shows no material excess; a system that merely records consumption without this comparison being able to show non-excess does not satisfy the check.

### RQA-FR-019

For a given policy, no reviewer pass, independent pass, repeated analysis, reasoning strategy or higher-cost method not required by that policy's stated assurance shall be performed.

*In plain terms: A policy shouldn't trigger more review passes, checks, or expensive analysis than it actually asks for.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-037** (AC10, [extract](prd-2006-normative-extract.md#success-criteria)): “For a given policy, RQA performs no reviewer pass, independent pass, repeated analysis, reasoning strategy or higher-cost method that is not required by that policy's stated assurance, and valid existing results are reused rather than regenerated.”

**Fit criterion:** Comparing every effort type CL-037 names — reviewer pass, independent pass, repeated analysis, reasoning strategy, and higher-cost method — that a review actually performed against its policy's stated assurance requirement shows none beyond what the policy requires; a pass that uses an unrequired repeated analysis, reasoning strategy, or higher-cost method fails this check even where the raw pass count matches policy.

### RQA-FR-020

A valid existing result shall be reused rather than regenerated.

*In plain terms: If a valid result already exists, it should be reused instead of computed again.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-037** (AC10, [extract](prd-2006-normative-extract.md#success-criteria)): “For a given policy, RQA performs no reviewer pass, independent pass, repeated analysis, reasoning strategy or higher-cost method that is not required by that policy's stated assurance, and valid existing results are reused rather than regenerated.”

**Fit criterion:** Where a prior result remains valid for the current revision, the review record shows it reused rather than a new equivalent result generated.

### RQA-FR-021

Resource consumption shall be recorded from what the execution environment actually exposes and be distinguishable from an estimate.

*In plain terms: How much compute/resources a review used should come from real measurements, not be confused with a guess.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-038** (AC11, [extract](prd-2006-normative-extract.md#success-criteria)): “Resource consumption is recorded from what the execution environment actually exposes and is distinguishable from an estimate; a configured bound, when reached, produces a configured fallback, an explicitly incomplete review, or an escalation — never a successful outcome.”

**Fit criterion:** Where the execution environment exposes an actual resource-consumption reading, that actual figure — not an estimate substituted in its place — is what the record relies on; a run that has an exposed actual reading available and records only an estimate instead fails this check. Where the environment ever produces only an estimate (no actual reading exposed), an observer can distinguish that record's estimated reading from an actual one by its own inspectable provenance. This check does not require a system whose environment always exposes actuals to manufacture an estimate-only scenario for testing — the estimate-distinguishability test applies only where an estimate is genuinely in use.

### RQA-FR-022

When a configured resource bound is reached, the review shall produce a configured fallback, an explicitly incomplete review, or an escalation.

*In plain terms: If a review hits a configured resource limit, it should end in one of three ways: fall back to what's configured, finish as an explicitly incomplete review, or escalate — nothing else.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-038** (AC11, [extract](prd-2006-normative-extract.md#success-criteria)): “Resource consumption is recorded from what the execution environment actually exposes and is distinguishable from an estimate; a configured bound, when reached, produces a configured fallback, an explicitly incomplete review, or an escalation — never a successful outcome.”

**Fit criterion:** Every review run in which a configured bound was reached ends in one of the three named outcomes; where the outcome is a fallback, it is the fallback already in force in configuration before the bound was reached, not one invented ad hoc — a run that substitutes an unconfigured alternative and calls it 'a fallback' fails this check even though a fallback-shaped outcome occurred.

### RQA-FR-023

Where a fallback is explicitly configured, the review shall continue through that fallback when a configured reviewer, model or provider becomes unavailable.

*In plain terms: If a fallback is set up in advance, the review keeps going through it when a reviewer, model or provider goes down.*

`Optional-feature` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-039** (AC12, [extract](prd-2006-normative-extract.md#success-criteria)): “With a configured reviewer, model or provider made unavailable, RQA continues through an explicitly configured fallback; with no fallback configured it invents none and stops in a clear, safe, recoverable non-success state.”

**Fit criterion:** Given a configured fallback and an unavailable configured reviewer, model or provider, the review proceeds via the fallback rather than halting.

**See also:** [RQA-NFR-007](#rqa-nfr-007) (shares source criterion AC12)

### RQA-FR-024

While no fallback is configured for a reviewer, model or provider, the review shall invent no fallback when that reviewer, model or provider becomes unavailable.

*In plain terms: If no fallback is set up, the review must not invent one on the spot when a reviewer, model or provider goes down.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-039** (AC12, [extract](prd-2006-normative-extract.md#success-criteria)): “With a configured reviewer, model or provider made unavailable, RQA continues through an explicitly configured fallback; with no fallback configured it invents none and stops in a clear, safe, recoverable non-success state.”

**Fit criterion:** With no fallback configured and a configured reviewer, model or provider unavailable, the review never substitutes an unconfigured alternative in its place.

**See also:** [RQA-NFR-007](#rqa-nfr-007) (shares source criterion AC12)

### RQA-FR-038

While no fallback is configured for a reviewer, model or provider, the review shall stop in a clear, safe, recoverable non-success state when that reviewer, model or provider becomes unavailable.

*In plain terms: If no fallback is configured and a reviewer, model or provider goes down, the review has to stop cleanly and safely, in a state that can be picked back up later.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-039** (AC12, [extract](prd-2006-normative-extract.md#success-criteria)): “With a configured reviewer, model or provider made unavailable, RQA continues through an explicitly configured fallback; with no fallback configured it invents none and stops in a clear, safe, recoverable non-success state.”

**Fit criterion:** With no fallback configured and a configured reviewer, model or provider unavailable, the review halts in a state independently observable to hold every standing security invariant this specification states — RQA-NFR-010 (no ambiguous/corrupted/partial outcome), RQA-NFR-018 (no widened authority), RQA-NFR-019…021 (remediation bounds), RQA-NFR-022/RQA-NFR-028 (forgeable-proof provenance), and RQA-NFR-024/RQA-NFR-030 (credential floor and ceiling) — and from which a subsequent run can resume. This set is bounded to the standing invariants that describe a state a stopped run can be *left in*; it deliberately excludes RQA-NFR-015/016 (untrusted-content handling and blocking-finding behaviour, which describe ongoing review conduct, not a resting state), RQA-NFR-017/026 (per-activity authorisation configuration, a standing system setting independent of any one run's stop), and RQA-NFR-023/027/029 (external-send decisions, which govern whether content is sent during a run, not the state left behind once it stops) — each excluded for the stated reason, not silently. `Safe` is not fully closed-form: CL-039 does not itself enumerate what safety consists of beyond 'clear, safe, recoverable', so this check tests the most complete, explicitly-bounded set of source-derived standing invariants available, which requirements-quality-assessment.md records as an open-texture limitation rather than an exhaustive definition of 'safe'.

**See also:** [RQA-NFR-007](#rqa-nfr-007) (shares source criterion AC12)

### RQA-FR-039

When a configured resource bound is reached, the review shall never produce a successful outcome.

*In plain terms: Hitting a configured resource limit should never, by itself, produce a passing review.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-038** (AC11, [extract](prd-2006-normative-extract.md#success-criteria)): “Resource consumption is recorded from what the execution environment actually exposes and is distinguishable from an estimate; a configured bound, when reached, produces a configured fallback, an explicitly incomplete review, or an escalation — never a successful outcome.”

**Fit criterion:** No review run in which a configured bound was reached ends in a successful disposition, independent of which of RQA-FR-022's three outcomes it produced instead.

### RQA-NFR-009

An alternative model or provider shall be used only when explicitly configured.

*In plain terms: The system only switches to a backup model or provider when that's been explicitly turned on — never automatically.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-024** (C7, [extract](prd-2006-normative-extract.md#problem)): “Configured resilience. Alternative models/providers only when explicitly configured. Failure must not leave an ambiguous, corrupted or partially authoritative outcome.”

**Fit criterion:** With no alternative model or provider configured, none is substituted; one only activates once configuration names it.

### RQA-NFR-010

A failure during review shall never leave an ambiguous, corrupted or partially authoritative outcome.

*In plain terms: If something goes wrong mid-review, the result should never come out half-finished, corrupted, or ambiguous about whether it counts as official.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-024** (C7, [extract](prd-2006-normative-extract.md#problem)): “Configured resilience. Alternative models/providers only when explicitly configured. Failure must not leave an ambiguous, corrupted or partially authoritative outcome.”

**Fit criterion:** Every failure during a review run is independently checked against three distinct invariants — the outcome is not ambiguous, not corrupted, and not partially authoritative — and passes only if all three hold; a clearly labelled but corrupted non-authoritative record fails this check even though it is unambiguous.

---

## Harness interoperability and operation

Running across different AI tooling, repositories and organisations, and operating from one person's own machine.

### RQA-FR-004

A change to a repository's review policy shall take effect on that repository's next review with no rebuild, reinstall or redeploy.

*In plain terms: Changing a repository's review rules should work on the very next review — no reinstall, no redeploy.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-029** (AC02, [extract](prd-2006-normative-extract.md#success-criteria)): “Two repositories configured with different review policies produce demonstrably different blocking outcomes on the same diff, and a policy change takes effect on the next review with no rebuild, reinstall or redeploy.”

**Fit criterion:** After a policy configuration change, the very next review on that repository reflects the new policy without any build, install or deployment step having been performed in between.

**See also:** [RQA-FR-003](#rqa-fr-003) (same source criterion (AC02)), [RQA-NFR-005](#rqa-nfr-005) (near-duplicate obligation, C4)

### RQA-FR-030

A harness not built into the system shall be able to participate in a review by satisfying the published interaction contract alone, with no change to the system's own source.

*In plain terms: An AI harness that isn't built into the system should still be able to take part in a review, purely by speaking the published interface — with no code changes to the system itself.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: [`ADR-C`](adr-drafts/ADR-C-external-harness-provenance-authentication.md)

**Source:**
- **CL-042** (AC15, [extract](prd-2006-normative-extract.md#success-criteria)): “A harness not built into RQA participates in a review by satisfying the published interaction contract alone, with no change to RQA's own source.”

**Fit criterion:** A harness never previously integrated participates in a review using only the published interaction contract, with one fixed, unmodified revision of the system's own source held constant throughout both admission and execution of that review — inspectable as identical at every point during the review, not merely equal again at the end; a transient patch applied to admit the harness and reverted afterward fails this check even though the source is identical before and after.

### RQA-FR-031

One operator running locally shall be able to review pull requests across at least two independently configured repositories under different GitHub owners or organisations, with no centrally hosted service.

*In plain terms: One person, running this locally, should be able to review PRs across at least two separately configured repositories under different GitHub owners, with no shared hosted service involved.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-043** (AC16, [extract](prd-2006-normative-extract.md#success-criteria)): “One operator running locally reviews PRs across at least two independently configured repositories under different GitHub owners or organisations, with no centrally hosted service.”

**Fit criterion:** One operator, running locally with no centrally hosted service, completes a review on each of two repositories under two different GitHub owners or organisations; this check does not require both reviews to run from the same physical machine — one operator reviewing one repository from a local desktop and the other from a local laptop, with no central service involved in either, still satisfies it, since CL-043 requires one operator running locally, not one physical machine.

### RQA-NFR-001

The system shall operate across uncontrolled contributor environments without depending on a particular harness, agent, model or provider.

*In plain terms: The system should work no matter what tooling a contributor happens to use — it shouldn't be locked to one harness, agent, model or provider.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-018** (C1, [extract](prd-2006-normative-extract.md#problem)): “Tooling independence. Must operate across uncontrolled contributor environments; cannot depend on a particular harness, agent, model or provider. Contributors may use a thin skill/plugin/hook conforming to a common interaction contract.”

**Fit criterion:** The system's conformance to the published interaction contract is demonstrated through materially independent implementations, including at least one environment not previously used in that demonstration, and inspection shows the system's core review logic carries no hard-coded dependency requiring one particular harness, agent, model or provider to be present; a per-provider adapter implementing a common interface is not itself evidence of forbidden dependence — only a core logic path that fails or behaves differently without one specific harness/agent/model/provider is. A system hard-coded to exactly two known combinations does not satisfy this check merely by running under both of them.

### RQA-NFR-002

Where a contributor chooses to use a thin skill, plugin or hook conforming to the published interaction contract for a non-built-in environment, the system shall accommodate that environment's participation through the contract.

*In plain terms: If a contributor's environment isn't built in but follows the published interface, the system should let it take part anyway.*

`Optional-feature` · `Could` · `DECIDED` · ADR: [#2064](https://github.com/launchpad-26/buzz/issues/2064) (repo-wide policy/contract document placement)

**Source:**
- **CL-018** (C1, [extract](prd-2006-normative-extract.md#problem)): “Tooling independence. Must operate across uncontrolled contributor environments; cannot depend on a particular harness, agent, model or provider. Contributors may use a thin skill/plugin/hook conforming to a common interaction contract.”

**Fit criterion:** A contributor's environment integrates via a thin skill, plugin or hook that conforms to the published interaction contract, and the system accommodates that environment's participation through the contract; this check does not require the system to separately implement acceptance of each of the three named mechanism forms — a system that lets the environment speak the contract directly, without a dedicated skill/plugin/hook acceptance path, still satisfies this check provided a contributor's conforming use of one is accommodated when it occurs.

### RQA-NFR-003

Where practical, an integration boundary shall use open, portable, implementation-neutral contracts and formats.

*In plain terms: Wherever it's practical, the interfaces between components should use open, portable formats rather than anything proprietary.*

`State-driven` · `Must` · `DECIDED` · ADR: [#2064](https://github.com/launchpad-26/buzz/issues/2064) (repo-wide policy/contract document placement)

**Source:**
- **CL-019** (C2, [extract](prd-2006-normative-extract.md#problem)): “Open interoperability. Integration boundaries use open, portable, implementation-neutral contracts and formats where practical.”

**Fit criterion:** For the contract an integration boundary uses, and separately for the format it uses, all three qualities — open, portable, and implementation-neutral — hold conjunctively, or an independent evaluator can verify a specific, evidenced reason why holding all three was impractical for that artifact; an artifact meeting only one or two of the three qualities, with no evidenced impracticality reason covering the others, fails this check. The evaluator's verification does not require the implementation itself to carry a prescribed record of that reason — the reason must be evidenced and checkable, not necessarily stored by the system under test.

### RQA-NFR-004

The system shall operate across multiple repositories and multiple organisations, including both public and private repositories under different owners.

*In plain terms: The system should be able to work across many repositories and organisations at once, whether they're public or private.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-020** (C3, [extract](prd-2006-normative-extract.md#problem)): “Multi-repository and cross-organisation operation. Public and private repositories, different owners, different organisations.”

**Fit criterion:** The system completes a review on a repository under one organisation and a second repository under a genuinely different organisation — not merely a second owner account within the same organisation — with one covering a public repository and the other a private one. Both organisations are necessarily GitHub organisations, since C8/RQA-NFR-011 scope the whole specification to GitHub; this fit criterion does not itself re-derive that scoping from CL-020, which is platform-neutral, and names no platform.

### RQA-NFR-005

Updating a repository's policy or configuration shall not require rebuilding or redeploying the system.

*In plain terms: Changing a repository's settings shouldn't require rebuilding or redeploying anything.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-021** (C4, [extract](prd-2006-normative-extract.md#problem)): “Repository-specific policy and configuration. Updating configuration must not require rebuilding or redeploying RQA.”

**Fit criterion:** A policy or configuration change is applied and takes effect without any build or deployment step being run.

**See also:** [RQA-FR-004](#rqa-fr-004) (near-duplicate obligation, AC02)

### RQA-NFR-006

One contributor shall be able to run the complete review workflow locally, with no central hosting, tenancy or SaaS functionality required.

*In plain terms: A single person should be able to run the whole review workflow on their own machine — no shared server, no multi-tenant hosting required.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-022** (C5, [extract](prd-2006-normative-extract.md#problem)): “Local-first operation. No central hosting, tenancy or SaaS functionality required; one contributor can run the complete workflow locally.”

**Fit criterion:** A single contributor completes an end-to-end review from their own machine with no centrally hosted RQA service in the loop; GitHub itself, as the platform under review, is necessarily reached over the network and is not what this check tests.

---

## External provider sensitivity

Sending code or evidence to an external AI provider only when explicitly allowed, and only as far as that permission goes.

### RQA-FR-032

The active external provider path shall be identifiable before evidence is sent to it.

*In plain terms: Before any evidence is sent out, it should be clear which external AI provider is actually being used.*

`Optional-feature` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-044** (AC17, [extract](prd-2006-normative-extract.md#success-criteria)): “The active external provider path is identifiable before evidence is sent, and removing that provider from configuration leaves RQA's review protocol and semantics unchanged.”

**Fit criterion:** Before any evidence leaves the system for an external provider, the specific provider path it will use can be named.

### RQA-FR-033

Removing the active external provider from configuration shall leave the review protocol and semantics unchanged.

*In plain terms: If the external AI provider is removed from configuration, the review's rules and meaning stay exactly the same.*

`Event-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-044** (AC17, [extract](prd-2006-normative-extract.md#success-criteria)): “The active external provider path is identifiable before evidence is sent, and removing that provider from configuration leaves RQA's review protocol and semantics unchanged.”

**Fit criterion:** With the external provider removed from configuration, the same published protocol definition still validates reviews and the same concept semantics still hold.

### RQA-NFR-012

Where an external provider is explicitly configured, the system shall permit code, diffs, metadata and evidence to be sent to it.

*In plain terms: If an operator has turned on an external AI provider, the system is allowed to send it code, diffs, metadata and evidence.*

`Optional-feature` · `Could` · `DECIDED` · ADR: —

**Source:**
- **CL-026** (C9, [extract](prd-2006-normative-extract.md#problem)): “External model use is permitted. Code, diffs, metadata and evidence may be sent to explicitly configured external providers; users choose review paths appropriate to sensitivity.”

**Fit criterion:** With an external provider configured, each of code, diffs, metadata and evidence — every type the statement names — can individually be sent to it; the statement names an inclusive list of permitted content types, not any single alternative among them, so a system that can send only one of the four types does not satisfy this check.

### RQA-NFR-013

An operator shall be able to choose a review path appropriate to a repository's sensitivity.

*In plain terms: An operator should be able to pick a review approach that matches how sensitive a given repository is.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-026** (C9, [extract](prd-2006-normative-extract.md#problem)): “External model use is permitted. Code, diffs, metadata and evidence may be sent to explicitly configured external providers; users choose review paths appropriate to sensitivity.”

**Fit criterion:** An operator can select, per repository, a review path that avoids sending that repository's content to an external provider, distinct from one that permits it.

### RQA-NFR-023

The decision to permit sending a given repository's content to an external provider shall be made per repository, not globally.

*In plain terms: Whether a given repository's content is allowed to go to an external AI provider is decided one repository at a time — never as one global switch.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-059** (Security implications, bullet 5, [extract](prd-2006-normative-extract.md#security-implications)): “External providers receive repository content (C9). The active provider path must be identifiable before evidence is sent, so an operator can decide whether a given repository or change may be sent at all. Private repositories under AC16 make this a per-repository decision, not a global one.”

**Fit criterion:** Configuring one repository to permit external-provider sends and a second to forbid it produces different sending behaviour on each, from one shared installation.

### RQA-NFR-027

Where no external provider is explicitly configured, no code, diff, metadata or evidence shall be sent to any external provider.

*In plain terms: If no external AI provider has been turned on, nothing — no code, diff, metadata or evidence — leaves the system for one.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-024** (C7, [extract](prd-2006-normative-extract.md#problem)): “Configured resilience. Alternative models/providers only when explicitly configured. Failure must not leave an ambiguous, corrupted or partially authoritative outcome.”
- **CL-026** (C9, [extract](prd-2006-normative-extract.md#problem)): “External model use is permitted. Code, diffs, metadata and evidence may be sent to explicitly configured external providers; users choose review paths appropriate to sensitivity.”

**Fit criterion:** With no external provider configured, no code, diff, metadata or evidence leaves the system for one.

### RQA-NFR-029

An operator shall be able to deny sending an individual change's content to an external provider even where its repository otherwise permits external-provider sends.

*In plain terms: An operator can block one specific sensitive change from being sent to an external provider, even if that repository normally allows it.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-059** (Security implications, bullet 5, [extract](prd-2006-normative-extract.md#security-implications)): “External providers receive repository content (C9). The active provider path must be identifiable before evidence is sent, so an operator can decide whether a given repository or change may be sent at all. Private repositories under AC16 make this a per-repository decision, not a global one.”

**Fit criterion:** A repository configured to permit external-provider sends in general still allows one specific, individually flagged change to be withheld from every external provider; a system offering only a repository-wide toggle, with no way to withhold one sensitive change, fails this check.

---

## Authority, credentials and untrusted content

What permissions the system is allowed to hold, how those permissions turn on, and how it treats a pull request's own content as untrusted.

### RQA-NFR-015

Pull-request content shall be treated as untrusted data, never as instructions, at every authority level including advisory-only.

*In plain terms: Nothing in a pull request — its diff, description, or comments — should ever be treated as an instruction to the reviewer. It's just data to inspect, always.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-055** (Security implications, bullet 1, [extract](prd-2006-normative-extract.md#security-implications)): “PR content is untrusted data, never instructions. A PR author controls the diff, body and comments that RQA reads. A crafted PR attempting to induce a clean review or a fabricated evidence state is itself a blocking finding. This applies at every authority level, including advisory-only.”

**Fit criterion:** Adversarial injection content placed in a PR's diff, body or comments produces no change in review behaviour or evidence state attributable to **following that content as an instruction** — the review neither approves, alters a finding, nor changes an evidence state because the content told it to — at each configured authority level including advisory-only. This check explicitly allows, and RQA-NFR-016 separately requires, the defensive response to the same content: classifying it and recording a blocking finding is not itself a change made because the content instructed it, and does not fail this check; a system that silently ignores the attempted injection with no defensive response fails RQA-NFR-016, not this row.

### RQA-NFR-016

A pull request crafted to induce a clean review or a fabricated evidence state shall itself be recorded as a blocking finding, at every authority level including advisory-only.

*In plain terms: If a PR is crafted to trick the review into passing or to fake its own evidence, that attempt itself should be recorded as a blocking finding.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-055** (Security implications, bullet 1, [extract](prd-2006-normative-extract.md#security-implications)): “PR content is untrusted data, never instructions. A PR author controls the diff, body and comments that RQA reads. A crafted PR attempting to induce a clean review or a fabricated evidence state is itself a blocking finding. This applies at every authority level, including advisory-only.”

**Fit criterion:** Given a PR containing content designed to manufacture a clean review or false evidence state, the review record contains a blocking finding describing that attempt, whether the system is running advisory-only or at any other configured authority level.

### RQA-NFR-017

Each of review, comment, approve, request-changes, remediate and merge shall be separately authorised.

*In plain terms: Reviewing, commenting, approving, requesting changes, auto-fixing, and merging are each switched on or off separately — turning one on doesn't turn on the others.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-056** (Security implications, bullet 2, [extract](prd-2006-normative-extract.md#security-implications)): “Authority is per-activity and fail-closed. Review, comment, approve, request-changes, remediate and merge are separately configured and default to disabled; a malformed or unreadable policy must never widen authority.”

**Fit criterion:** Each of the six named activities has its own authorisation setting, independent of the other five.

### RQA-NFR-018

A malformed or unreadable policy shall never widen authority beyond what was already granted.

*In plain terms: If a policy file is broken or unreadable, that failure should never accidentally grant more permission than the system already had.*

`State-driven` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-056** (Security implications, bullet 2, [extract](prd-2006-normative-extract.md#security-implications)): “Authority is per-activity and fail-closed. Review, comment, approve, request-changes, remediate and merge are separately configured and default to disabled; a malformed or unreadable policy must never widen authority.”

**Fit criterion:** Deliberately corrupting or truncating the policy input never results in an activity gaining authorisation it did not already have, regardless of what form that policy input takes — a tracked file, a database record, an API response, or any other representation; the check also exercises a policy input that is unreadable for a reason other than malformation — permission denied, unavailable, or timed out — and confirms the same non-widening result holds there too, not only for the malformed-input path.

### RQA-NFR-024

The credential the system holds shall carry pull-request write and repository-content read on the repositories where the system is configured to submit authoritative review outcomes.

*In plain terms: On any repository where the system is set up to give an official verdict, its access token needs at least write-to-PRs and read-the-code permissions.*

`Optional-feature` · `Must` · `DECIDED` · ADR: [`ADR-B`](adr-drafts/ADR-B-credential-scope-vs-merge-capability.md)

**Source:**
- **CL-060** (Security implications, bullet 6, [extract](prd-2006-normative-extract.md#security-implications)): “Credentials stay narrow. A GitHub token scoped to the target repositories with pull-requests write and contents read; no deploy keys, no relay or VPS credentials, no access to a contributor's machine.”
- **CL-056** (Security implications, bullet 2, [extract](prd-2006-normative-extract.md#security-implications)): “Authority is per-activity and fail-closed. Review, comment, approve, request-changes, remediate and merge are separately configured and default to disabled; a malformed or unreadable policy must never widen authority.”

**Fit criterion:** For a repository configured to submit authoritative review outcomes, inspecting the credential's granted scopes shows both pull-request write and repository-content read present on it; a credential missing either named permission on such a repository fails this check. This row states only the floor for that configuration; what a credential may hold on a repository configured for narrower activity, or beyond these two permissions anywhere, is RQA-NFR-030's own check, not this one's.

### RQA-NFR-025

The system shall hold no deploy-key, relay or VPS credential, and no credential granting access to a contributor's machine.

*In plain terms: The system should never hold a deploy key, a relay credential, a VPS credential, or anything that could reach a contributor's own machine.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-060** (Security implications, bullet 6, [extract](prd-2006-normative-extract.md#security-implications)): “Credentials stay narrow. A GitHub token scoped to the target repositories with pull-requests write and contents read; no deploy keys, no relay or VPS credentials, no access to a contributor's machine.”

**Fit criterion:** An inventory of credentials the system holds contains no deploy key, no relay or VPS credential, and nothing granting access to a contributor's own machine.

### RQA-NFR-026

Each of review, comment, approve, request-changes, remediate and merge shall default to disabled.

*In plain terms: Reviewing, commenting, approving, requesting changes, auto-fixing, and merging all start out turned off until someone deliberately turns them on.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-056** (Security implications, bullet 2, [extract](prd-2006-normative-extract.md#security-implications)): “Authority is per-activity and fail-closed. Review, comment, approve, request-changes, remediate and merge are separately configured and default to disabled; a malformed or unreadable policy must never widen authority.”

**Fit criterion:** An unconfigured deployment has every one of the six named activities off, with no activity defaulting to enabled.

### RQA-NFR-030

The credential the system holds shall have no permission broader than pull-request write and repository-content read, no permission on any repository outside those it manages, and no permission on a repository beyond what the activities configured for that repository require.

*In plain terms: The system's access token should never hold more than the minimum permissions needed — nothing extra, nowhere it doesn't manage, and nothing beyond what a given repository's setup actually requires.*

`Unwanted-behaviour` · `Must` · `DECIDED` · ADR: [`ADR-B`](adr-drafts/ADR-B-credential-scope-vs-merge-capability.md)

**Source:**
- **CL-060** (Security implications, bullet 6, [extract](prd-2006-normative-extract.md#security-implications)): “Credentials stay narrow. A GitHub token scoped to the target repositories with pull-requests write and contents read; no deploy keys, no relay or VPS credentials, no access to a contributor's machine.”
- **CL-056** (Security implications, bullet 2, [extract](prd-2006-normative-extract.md#security-implications)): “Authority is per-activity and fail-closed. Review, comment, approve, request-changes, remediate and merge are separately configured and default to disabled; a malformed or unreadable policy must never widen authority.”

**Fit criterion:** Inspecting the credential's granted scopes shows, on every repository: nothing beyond pull-request write and repository-content read; no permission at all on a repository outside the managed set; and, on a repository configured for narrower activity than submitting authoritative review outcomes (for example, advisory-only), no more permission than that narrower activity requires — a credential carrying pull-request write on a repository configured only for advisory, non-authoritative activity fails this check by holding more than that configuration needs, even though it holds no more than the two named permission types in the abstract. All three are ceiling tests on the same credential; a credential failing any one of them fails this check.

---

## Scope and design baseline

What repository host this covers, and the baseline every kept piece of the design has to justify itself against.

### RQA-FR-034

Every architectural component retained in the delivered design shall be justified as materially serving a criterion, as having no materially simpler sufficient approach, or as required by a constraint.

*In plain terms: Every piece of the design that's kept has to earn its place — it either clearly helps meet a requirement, has no simpler substitute, or is required by a constraint.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-045** (Closing criterion 1, [extract](prd-2006-normative-extract.md#success-criteria)): “Every architectural component retained in the delivered design is justified against this baseline under the §6 rule: it materially serves a criterion, no materially simpler approach suffices, or a constraint requires it.”

**Fit criterion:** For every retained architectural component, a recorded justification substantiates — with a specific, checkable claim, not a bare label — at least one of the three named grounds: the specific criterion it materially serves, the specific materially-simpler alternative that was considered and rejected and why, or the specific constraint requiring it; a recorded claim that names a ground with no supporting specific content does not satisfy this check. This row does not prescribe who authors or evaluates the justification — CL-045/the §6 rule names neither — only that the substantiation itself is specific and checkable.

### RQA-FR-035

Exactly one authoritative review-agent scope shall remain open, achieved by closing or explicitly re-parenting #109 and reconciling its features #535 and #536 against this scope.

*In plain terms: There should be exactly one place that owns "what does the review agent do" — old overlapping issues get closed or folded in so there's no ambiguity about scope.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-046** (Closing criterion 2, [extract](prd-2006-normative-extract.md#success-criteria)): “#109 is closed or explicitly re-parented, and its features #535 and #536 are reconciled against this scope, so exactly one authoritative review-agent scope is open.”

**Fit criterion:** At any point after delivery, each of three conditions is checked on its own terms, not interchangeably: #109 is confirmed to be either closed or explicitly re-parented (not merely 'reconciled'); #535 and #536 are each confirmed reconciled against this scope; and exactly one open issue can be pointed to as the authoritative review-agent scope.

### RQA-NFR-011

The system shall support review of GitHub-hosted repositories.

*In plain terms: The system needs to work with repositories hosted on GitHub.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-025** (C8, [extract](prd-2006-normative-extract.md#problem)): “GitHub scope. GitHub only; generic cross-SCM support is not required.”

**Fit criterion:** The system's review-lifecycle requirements are demonstrated against a GitHub-hosted repository; a system that supports GitHub review as this specification requires satisfies this row regardless of whether it also supports a second source-control platform, since C8/Non-goal 1 release cross-SCM support as out of scope rather than prohibiting it.

### RQA-NFR-014

The system shall have an open-source, freely usable implementation path, and an optional external provider used alongside it need not itself be free or open source.

*In plain terms: There has to be a way to run this using only free, open-source software — any paid external AI provider is optional, not required.*

`Ubiquitous` · `Must` · `DECIDED` · ADR: —

**Source:**
- **CL-027** (Project requirement, [extract](prd-2006-normative-extract.md#problem)): “RQA must have an open-source, freely usable implementation path. Optional external providers need not themselves be free or open source.”

**Fit criterion:** A user can assemble and run a complete implementation using only free, open-source components, and choosing to add a non-free external provider on top does not remove that path.


---

## Cold reference material

The material below explains *how* this specification was built and checked. None of it changes any requirement's
obligation; it exists so the derivation can be audited.

- [**Methodology**](methodology.md) — how this document is structured relative to ISO/IEC/IEEE 29148:2018, the
  EARS patterns used, and the vocabulary, status and priority conventions it follows.
- [**Source-clause inventory**](clause-inventory.md) — every clause of the extract (`CL-001`–`CL-065`), and
  what became of each one.
- [**Singular-split record**](singular-splits.md) — where one acceptance criterion produced more than one
  requirement, and why.
- [**Set-level assessment**](set-assessment.md) — the specification judged as a whole, including the
  ISO/IEC 25010:2023 sweep of the non-functional class.
- [**Traceability**](traceability.md) — the rule that binds a multi-part acceptance criterion to all of its
  requirements, and the two checks that confirm every clause and every requirement are correctly linked.
- [**Revision history**](revision-history.md) — what changed across this specification's review rounds, briefly.
- [**Quality assessment**](requirements-quality-assessment.md) — every requirement judged against the nine
  ISO/IEC/IEEE 29148:2018 individual requirement characteristics.
- [**ADR drafts**](adr-drafts/) — the open questions this specification surfaces but does not settle.
- [**Normative extract**](prd-2006-normative-extract.md) — the source text everything above derives from.
