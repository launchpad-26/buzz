# PRD #2006 — normative extract (authoring input for the RQA requirements specification)

**Status of this file:** verbatim extract, not authored text. Every line below the
rule is copied unmodified from the body of
[launchpad-26/buzz#2006](https://github.com/launchpad-26/buzz/issues/2006).

**Revision pin.** Extracted from the issue body as returned by
`gh api repos/launchpad-26/buzz/issues/2006 --jq .body` with:

- `updated_at`: `2026-09-01T06:34:12Z`
- SHA-256 of the full issue body at extraction: `12bb2a6d5ca0f55446332e9f4300faa1a392b835f6457f49c303ea5f1ef596dd`

If #2006 is amended, its `updated_at` and body hash change and this extract is
detectably stale rather than silently so.

**Extraction rule.** The sections `## Problem` (problem statement, P1–P12, C1–C9
and the project requirement), `## Success criteria` (AC01–AC17 and both closing
criteria), `## Non-goals` and `## Security implications` are included in full and
unmodified. The sections `## Evidence` and `## Impacted components` are excluded,
because they describe the current implementation and this extract is the input to
a specification that must be authored without reference to it
([#2069](https://github.com/launchpad-26/buzz/issues/2069)). The HTML alias
comment and the scope-supersession note are likewise excluded as context imposing
no obligation; the supersession itself is restated by #2006's final closing
criterion, which is included.

---

## Problem

Launchpad Buzz does not have a consistent, auditable, efficient, and trustworthy
pull-request review process.

Reviews are performed using different reviewer-defined protocols, different
blocking thresholds, and inconsistent levels of evidence. Review records do not
consistently capture structured provenance showing who or what performed the
review or which process was followed. The same unchanged revision is frequently
reviewed multiple times, while mechanical or creation-time defects can consume
the same blocking mechanism as substantive correctness, security, architectural,
or evidence failures.

As a result, GitHub review state does not reliably communicate whether a pull
request has received sufficient review, what was actually examined, which
findings materially block the change, or why an approval should be trusted.
Humans must interpret and reconcile accumulated reviews, checks, findings,
exceptions, and approvals before deciding whether a pull request can progress.
That consumes scarce human attention and interrupts other development work.

The process also consumes finite model and token capacity. Duplicate review,
unnecessary re-review, overlapping reviewer effort, and inefficient review
strategies can consume enough capacity that contributors cannot continue
implementation work.

The operational consequence is duplicated work, resource exhaustion, human
interruption, and a growing review queue. The more important consequence is
reduced assurance: substantial review activity does not consistently demonstrate
that the important risks, claims, and evidence associated with a pull request
were actually examined.

**The twelve problems this PRD exists to solve:**

| ID | Problem |
|---|---|
| P1 | **No shared review protocol.** Reviewers use independently designed processes, so a review has no consistent definition across the repository. |
| P2 | **Review provenance is not recorded.** Records do not establish who or what reviewed, which protocol was followed, or how the judgement was produced. |
| P3 | **Blocking semantics are inconsistent.** Reviewers apply materially different thresholds for `CHANGES_REQUESTED`, so GitHub review state has no consistent meaning. |
| P4 | **Mechanical and substantive findings share one blocking mechanism.** Procedural issues and correctness/security/architectural/evidence failures are all expressed as `CHANGES_REQUESTED`. |
| P5 | **Cheaply remediable findings create unnecessary review cycles.** An agent can identify a deterministic defect and supply the exact remedy, yet the fix still needs another contributor and another review cycle. |
| P6 | **Review work is duplicated across unchanged revisions.** |
| P7 | **Review output has poor signal-to-noise for assurance.** Activity focuses on labels, metadata and formatting without establishing whether higher-value claims, risks or cited evidence were verified. |
| P8 | **Automated review and check signals require manual interpretation.** Humans must decide whether a failure is attributable to the PR, inherited from base, procedural, incomplete automation, unrelated infrastructure, or a genuine blocker. |
| P9 | **Progression depends heavily on manual owner intervention.** |
| P10 | **Human approvals do not consistently preserve review evidence.** Approval satisfies merge mechanics without preserving assurance evidence. |
| P11 | **PR review consumes scarce model capacity inefficiently.** Capacity is shared with implementation work. |
| P12 | **PR review consumes scarce human attention and causes unnecessary interruption.** Routine, mechanical or non-urgent PR issues impose context-switching costs where no human judgement is required. |

**The nine design constraints the solution must hold** (they bound the design;
they do not prescribe an implementation):

| ID | Constraint |
|---|---|
| C1 | **Tooling independence.** Must operate across uncontrolled contributor environments; cannot depend on a particular harness, agent, model or provider. Contributors may use a thin skill/plugin/hook conforming to a common interaction contract. |
| C2 | **Open interoperability.** Integration boundaries use open, portable, implementation-neutral contracts and formats where practical. |
| C3 | **Multi-repository and cross-organisation operation.** Public and private repositories, different owners, different organisations. |
| C4 | **Repository-specific policy and configuration.** Updating configuration must not require rebuilding or redeploying RQA. |
| C5 | **Local-first operation.** No central hosting, tenancy or SaaS functionality required; one contributor can run the complete workflow locally. |
| C6 | **End-to-end GitHub review responsibility.** Must manage the lifecycle through authoritative `APPROVED` or `CHANGES_REQUESTED`. Whether RQA also merges is configurable per repository. |
| C7 | **Configured resilience.** Alternative models/providers only when explicitly configured. Failure must not leave an ambiguous, corrupted or partially authoritative outcome. |
| C8 | **GitHub scope.** GitHub only; generic cross-SCM support is not required. |
| C9 | **External model use is permitted.** Code, diffs, metadata and evidence may be sent to explicitly configured external providers; users choose review paths appropriate to sensitivity. |

**Project requirement:** RQA must have an open-source, freely usable
implementation path. Optional external providers need not themselves be free or
open source.
## Success criteria

Each line is one acceptance criterion from the requirements baseline, stated as
an observable check. A criterion is satisfied only when its **complete**
behaviour is demonstrated — passing one clause of a multi-part criterion does
not satisfy the criterion.

- [ ] AC01 — Every RQA-managed review produces a verdict that validates against one published protocol definition covering review scope, required evidence, findings, blocking conditions, review completion and final disposition; two reviews of the same PR by different harnesses, models or providers carry the same concept semantics.
- [ ] AC02 — Two repositories configured with different review policies produce demonstrably different blocking outcomes on the same diff, and a policy change takes effect on the next review with no rebuild, reinstall or redeploy.
- [ ] AC03 — A push that changes nothing material re-runs zero reviewer calls; a push touching file X re-runs only the review obligations invalidated by that change; the reused and regenerated sets are both recorded and inspectable.
- [ ] AC04 — Every finding carries a category distinguishing mechanical, procedural and creation-time findings from correctness, security, architectural and evidence findings, and whether it blocks is decided by repository policy, not by the reviewer's severity choice alone.
- [ ] AC05 — Every required review obligation carries an explicit evidence state from {verified, not verified, unavailable, contradictory, failed, incomplete, unknown}, and no successful disposition can be produced while any required obligation is unsatisfied.
- [ ] AC06 — For any authoritative review outcome, a single command reconstructs the exact PR revision, protocol and policy in force, reviewer identity and type, harness, model, provider, evidence examined, findings produced, decision basis and disposition; a human approval used to satisfy assurance names the approving human and the basis of that approval.
- [ ] AC07 — For a PR whose only failing check also fails on its merge base, RQA classifies that failure as inherited rather than attributable, does not treat it as a blocker, and states the classification.
- [ ] AC08 — For any managed PR, one command returns its current disposition from {being reviewed, blocked, awaiting remediation, awaiting human judgement, review-complete, unable to progress} and the reason, without a human reconciling historical reviews, comments or checks.
- [ ] AC09 — A finding classified as mechanical and permitted by policy is resolved without unnecessarily creating human intervention or a complete re-review cycle, and resolving it does not invalidate unrelated review work that remains valid. Per the baseline, this does not require RQA to modify code directly.
- [ ] AC10 — For a given policy, RQA performs no reviewer pass, independent pass, repeated analysis, reasoning strategy or higher-cost method that is not required by that policy's stated assurance, and valid existing results are reused rather than regenerated.
- [ ] AC11 — Resource consumption is recorded from what the execution environment actually exposes and is distinguishable from an estimate; a configured bound, when reached, produces a configured fallback, an explicitly incomplete review, or an escalation — never a successful outcome.
- [ ] AC12 — With a configured reviewer, model or provider made unavailable, RQA continues through an explicitly configured fallback; with no fallback configured it invents none and stops in a clear, safe, recoverable non-success state.
- [ ] AC13 — Routine, mechanical and non-urgent conditions raise no immediate human request; a required escalation names the specific unresolved decision, conflicting judgement, evidence gap, required information or authority requirement; and supplying that input resumes the lifecycle without restarting the review.
- [ ] AC14 — RQA submits `APPROVED` or `CHANGES_REQUESTED` when the obligations are satisfied and cannot manufacture a successful outcome when they are not; one repository can be configured to merge after review and another configured not to, with both behaving accordingly.
- [ ] AC15 — A harness not built into RQA participates in a review by satisfying the published interaction contract alone, with no change to RQA's own source.
- [ ] AC16 — One operator running locally reviews PRs across at least two independently configured repositories under different GitHub owners or organisations, with no centrally hosted service.
- [ ] AC17 — The active external provider path is identifiable before evidence is sent, and removing that provider from configuration leaves RQA's review protocol and semantics unchanged.
- [ ] Every architectural component retained in the delivered design is justified against this baseline under the §6 rule: it materially serves a criterion, no materially simpler approach suffices, or a constraint requires it.
- [ ] #109 is closed or explicitly re-parented, and its features #535 and #536 are reconciled against this scope, so exactly one authoritative review-agent scope is open.
## Non-goals

- Non-GitHub source control. GitLab, Bitbucket and generic cross-SCM support are out of scope (C8).
- Centrally hosted, multi-user, multi-tenant or SaaS operation. RQA is local-first for this scope (C5).
- Mandating any specific model, provider or coding harness. Naming a default is permitted; depending on one is not (C1, C9).
- Prescribing implementation mechanisms — a particular database, message queue, telemetry backend, GitHub App, language, deployment architecture or agent harness. Those are design choices to be justified against this baseline, not requirements of it (§6).
- Making an external provider mandatory. RQA's protocol and semantics must survive removing any one provider (AC17).
- Deciding the human-approval count. Whether RQA's approval substitutes for a human approval is a policy and governance question owned by the repository, not by this PRD.
- Re-litigating #109's phase model. The phases are superseded by the acceptance criteria above; no phase-1/2/3 gating work is carried forward as-is.
- Retrofitting provenance onto the 1,064 historical reviews. The evidence is used to establish the problem, not to be corrected.
## Security implications

- **PR content is untrusted data, never instructions.** A PR author controls the diff, body and comments that RQA reads. A crafted PR attempting to induce a clean review or a fabricated evidence state is itself a blocking finding. This applies at every authority level, including advisory-only.
- **Authority is per-activity and fail-closed.** Review, comment, approve, request-changes, remediate and merge are separately configured and default to disabled; a malformed or unreadable policy must never widen authority.
- **Remediation authority is the largest new exposure.** AC09 asks RQA to modify and push a branch. That authority must be separately gated, bounded to categories policy names as mechanical, isolated from the repository working tree, and never able to force-push, merge, bypass protection, or touch a protected branch.
- **Provenance must be forgeable-proof.** AC06 records reviewer identity, harness, model and provider. If that record can be written by the reviewed content or by an unauthenticated model response, the audit trail is worse than none.
- **External providers receive repository content** (C9). The active provider path must be identifiable before evidence is sent, so an operator can decide whether a given repository or change may be sent at all. Private repositories under AC16 make this a per-repository decision, not a global one.
- **Credentials stay narrow.** A GitHub token scoped to the target repositories with pull-requests write and contents read; no deploy keys, no relay or VPS credentials, no access to a contributor's machine.
- **Reaching a resource bound must never produce a successful review** (AC11). A false green under exhaustion is the highest-severity failure mode in this system.
