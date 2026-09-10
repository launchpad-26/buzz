# ADR-D — Terminal outcome of a satisfied review when verdict authority is not granted

**Status:** [issue #2157](https://github.com/launchpad-26/buzz/issues/2157) open · recommendation made · *assumed accepted for #2071, pending maintainer decision*
**Parent:** [#2006](https://github.com/launchpad-26/buzz/issues/2006) · **Raised by:** #2071 architecture · **Decomposition-blocking:** **blocking**
**Parts affected:** P-02, P-11, P-09 · **Requirements:** RQA-FR-028, RQA-NFR-017, RQA-NFR-026, RQA-NFR-007, RQA-FR-016

## Question

RQA-FR-028 says a review whose obligations are satisfied *shall submit* APPROVED or CHANGES_REQUESTED.
RQA-NFR-017 and RQA-NFR-026 say `approve` and `request-changes` are separately authorised and default
to disabled, and RQA-NFR-024's own text names an "advisory-only repository" as a legitimate
configuration. So on a repository where verdict authority is not granted, a satisfied review cannot
submit. What is its terminal outcome? The gap register records the estate's answer — end in an
advisory COMMENT or `human_required` without a verdict — as RQA-FR-028 `conflicting`.

## Why the architecture cannot settle it alone

Both readings are consistent with the frozen text and they differ in observable behaviour for every
repository in the default configuration. Choosing is an interpretation of two requirements in tension,
which #2069's process reserved for the maintainer (ADR-A..C were resolved at source for the same
reason). Non-goal 6 also bounds the answer: it must not decide whether a human's decision counts toward
required approvals.

## Options

| | option | consequence for the parts |
|---|---|---|
| (a) | The review posts its rendering as a COMMENT (if `comment` is granted) and the job ends **review-complete**. FR-028 is read as scoped to the activities the repository granted. | P-02 gains a terminal state reachable without a verdict; RQA-FR-016's *review-complete* then means "RQA has nothing further to do", not "an authoritative verdict exists"; RQA-NFR-007's "whenever progression remains possible" is satisfied vacuously. No contract changes. |
| (b) | The review posts its rendering as a COMMENT (if `comment` is granted) and then raises an escalation with cause *authority requirement*; the job rests at **awaiting human judgement** until a human records a decision through `rqa decide`, which is the authoritative outcome on that repository. | P-02's disposition mapping has no verdict-less success state; P-11 sees one escalation per completed review on such repositories; the record carries "no source-conforming next transition available" as RQA-NFR-007 requires. No contract changes. |
| (c) | Refuse to review at all where neither verdict activity is granted. | Removes advisory-only, which RQA-NFR-024 names as legitimate. Rejected on that ground. |

## Recommendation — (b)

It is the only option under which RQA-FR-037's "never manufacture a successful outcome" and
RQA-FR-016's *review-complete* keep one meaning: an authoritative verdict exists. It is the honest
disposition — on an advisory-only repository the PR *is* waiting on a human — and it satisfies
RQA-FR-025/BR-013 because the escalation is a durable record, never a notification. It does not decide
Non-goal 6: whether the human's decision (or RQA's own APPROVED) counts toward required approvals
remains branch protection's. Cost: repositories that never grant a verdict activity accumulate open
escalations; that is the truthful state of those repositories, and `rqa status` says so.

## Why blocking

By the components.md §9 definition (part boundary, E-NN contract, record owner) nothing moves. But
(a) and (b) give `rqa status`'s *review-complete* two different meanings — "an authoritative verdict
exists" against "RQA has nothing further to do" — and that is a contract with the operator through
E-17, and the flow's §4 state table differs between them. A P-02 lane built to (b) before ratification
may rework. Labelled blocking on that ground; the reviewer of this design argued the same.

## Post-decide mechanics under (b)

A human decision on an *authority requirement* escalation does not re-enter the verdict step — RQA is
still not permitted to act, so re-entering would loop. Instead the human acts on GitHub and records the
outcome (`rqa decide --outcome approved|changes_requested`); P-02 verifies the submitted review is
visible at the same head and transitions the job directly to `approved` or `changes_requested` as the
authoritative human outcome (flow step 12b). Every other cause re-enters judgement (step 12a).
