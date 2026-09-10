---
status: Accepted
date: 2026-09-11
issue: launchpad-26/buzz#2157
decided_in: agent session — no addressable comment exists; see Provenance
supersedes: none
---

# ADR-0061 — A satisfied review without verdict authority escalates; it never completes

## Decision

Where a review-queue-automation (RQA) job's obligations are satisfied but the repository has granted
neither `approve` nor `request_changes`, the job **posts its rendering as a comment (when `comment` is
granted) and then raises an escalation with cause *authority requirement***. It rests at the FR-016
disposition **awaiting human judgement** until a human records an outcome through `rqa decide`. That
human decision is the authoritative outcome on such a repository.

This is option **(b)** of
[`ADR-D`](../skills/review-queue-automation/architecture/adr-drafts/ADR-D.md), the architecture's
recommendation.

Consequently:

- **`review-complete` keeps exactly one meaning: an authoritative verdict exists.** No terminal
  success state is reachable without one.
- **A human decision on an *authority requirement* escalation does not re-enter the verdict step.**
  RQA is still not permitted to act, so re-entry would loop. The human acts on GitHub; P-02 verifies
  the submitted review is visible at the same head and transitions the job directly to `approved` or
  `changes_requested` (flow step 12b). Every other escalation cause re-enters judgement (step 12a).
- **Advisory-only remains a legitimate configuration.** Option (c) — refusing to review at all — is
  rejected, because RQA-NFR-024's own text names an advisory-only repository as legitimate.

This decision does **not** decide Non-goal 6: whether a human's decision, or RQA's own APPROVED,
counts toward a repository's required approvals remains branch protection's business. RQA never
configures it.

## Context

RQA-FR-028 says a review whose obligations are satisfied *shall submit* APPROVED or
CHANGES_REQUESTED. RQA-NFR-017 and RQA-NFR-026 make `approve` and `request_changes` separately
authorised and disabled by default. Both readings of the resulting tension are consistent with the
frozen requirements specification, and they differ in observable behaviour for **every repository in
the default configuration** — so this was an interpretation of two requirements in tension, which
#2069's process reserved for the maintainer. The gap register records the pre-existing estate's
answer (an advisory comment, or `human_required` without a verdict) as RQA-FR-028 `conflicting`.

The #2071 architecture proceeded on this recommendation as an assumption, annotated `[ADR-D assumed]`
at each affected site. Those annotations now stand ratified.

Affected parts: **P-02** (lifecycle), **P-11** (escalation), **P-09** (GitHub adapter).
Requirements: RQA-FR-028, RQA-NFR-017, RQA-NFR-026, RQA-NFR-007, RQA-FR-016.

## Consequences

- **Good.** RQA-FR-037's "never manufacture a successful outcome" and RQA-FR-016's *review-complete*
  keep one meaning each. The disposition is honest: on an advisory-only repository the pull request
  genuinely is waiting on a human. RQA-FR-025/BR-013 are satisfied because the escalation is a
  durable record rather than a notification.
- **Bad, stated plainly.** A repository that never grants a verdict activity **accumulates one open
  escalation per completed review**. That is the truthful state of such a repository and `rqa status`
  reports it, but operators of advisory-only repositories will see a growing queue that only human
  action clears.
- **Decomposition.** #2072's P-02 lane can now be cut. `rqa status`'s *review-complete* is a contract
  with the operator through E-17, and the two options gave it different meanings; that is why this
  ADR was decomposition-blocking even though no part boundary, `E-NN` signature or record owner
  changes between the options.

## Provenance

**This outcome was written by an AI agent exercising `launchpad/AGENTS.md` §5 delegated authority on
behalf of @tucktuck101**, who ruled on all four RQA architecture ADRs (#2157, #2158, #2159, #2160) in
one instruction, verbatim:

> urgh just go with the recomendations, record the adr files we need and submit a pr for them as a batch.

**Deviation from `launchpad/decisions/README.md`, recorded here rather than below the conclusion it
qualifies:** that README requires the deciding human's instruction to be quoted verbatim *and the
comment where they said it to be linked*. **No such comment exists.** The instruction was given only
in an agent session, which §5 rule 2 states is not a record — "not addressable, not durable, and not
readable by whoever audits this later". Offered the choice between posting the instruction as a
comment first and proceeding without one, @tucktuck101 selected "I proceed now, quoting this session
verbatim", with the deviation disclosed in every record and in the pull request. An auditor therefore
cannot reach the original instruction; this quotation is its only surviving form, and the quote's
fidelity — including its typing errors, left intact — is the only control on it.

The argument for the decision is on [#2157](https://github.com/launchpad-26/buzz/issues/2157) and in
[`ADR-D`](../skills/review-queue-automation/architecture/adr-drafts/ADR-D.md), which is retained as
the architecture's own rationale draft.
