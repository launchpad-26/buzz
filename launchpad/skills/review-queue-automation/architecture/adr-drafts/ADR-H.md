# ADR-H — How a harness RQA ships no adapter for is admitted to run

**Status:** decided 2026-09-11 — recommendation (b) accepted; recorded as [ADR-0065](../../../../decisions/ADR-0065-external-harness-admission.md), which closes [issue #2217](https://github.com/launchpad-26/buzz/issues/2217). This draft is retained as the architecture's rationale, not as an open question.
**Parent:** [#2006](https://github.com/launchpad-26/buzz/issues/2006) · **Raised by:** the PR #2176 review of the #2072 decomposition · **Decomposition-blocking:** **blocking**
**Parts affected:** P-05, P-06, P-03 · **Requirements:** RQA-FR-030, RQA-NFR-001, RQA-NFR-002, RQA-NFR-015

## Question

AC15 requires that "a harness not built into RQA participates in a review by satisfying the published
interaction contract alone, with no change to RQA's own source", and RQA-FR-030's fit criterion is
explicit that a transient patch applied to admit the harness and reverted afterwards fails the check.

The architecture as merged could not meet that. P-05's `route()` admitted a configured route only when
its `(harness, model)` pair was a key of `aliases.py` — a closed table owned by RQA's source — so a
fourth harness required an RQA source edit, which is exactly what AC15 forbids. Something had to give.
**What form may a harness declaration take, and what gates its execution?**

## Why the architecture cannot settle it alone

The answer decides what RQA will spawn. Under (b) the argv comes from a repository's own
`.rqa/config.json`, so the set of executables RQA may run stops being closed and source-owned and
becomes open and operator-owned. That is a risk posture, and Security bullet 3 makes this class of
decision the maintainer's rather than the architecture's — the same reason ADR-G was raised for
remediation.

## Options

| | option | how AC15 is met | consequence |
|---|---|---|---|
| (a) | **Keep the closed registry.** A third-party harness participates by submitting a pull request that adds a built-in adapter. | It is not met. A source change is required by construction, and RQA-FR-030's fit criterion names exactly that as a failure. | The execution surface stays closed, source-owned and conformance-tested at build time. AC15 is recorded as unmeetable and the PRD's success criterion goes unsatisfied. |
| (b) | **Operator-declared argv.** A route may carry `command`, an argv the operator writes into the repository's policy file; `adapter_for` resolves a non-empty `command` to the generic external-command adapter. Admission to *invocation* is gated by running the published clean/adversarial conformance pair against that exact argv before any PR content reaches it (P-06 §3.2 step 2); a failure excludes the route. Implemented in PR #2176. | Met literally: participation turns on configuration and the published contract, with RQA's source held constant. | RQA spawns an executable named by repo-local config. The conformance gate, the minimal environment, the absence of RQA/GitHub credentials and the nonce-envelope data role all still apply, but *which binary* is no longer RQA's decision. A repository whose policy file an attacker can edit can name a different binary. |
| (c) | **Operator-declared argv from a separate operator-owned file**, not the repository's policy — e.g. a machine-level harness registry alongside the credential. | Met, with the declaration held by the operator rather than by the repository under review. | One more file and one more validation path; a per-repository harness choice becomes impossible, which the multi-repository case (AC16) may want. Narrower blast radius than (b): a compromised repository cannot name a binary. |

## Recommendation — (b), with (c) named as the fallback if the residual is judged too wide

(b) is the only option under which AC15 and RQA-FR-030 are met as written, and the conformance gate
means an unverified command never sees PR content. The honest cost is stated above and is not small:
the policy file is in the repository under review, so under (b) the set of binaries RQA may spawn is
controlled by the same people whose code it is reviewing. (c) keeps AC15 met while moving the
declaration out of the reviewed repository, at the cost of per-repository harness choice.

## Why blocking

`Route.command`, P-05 §3.1 step 2's eligibility disjunct, P-06's `adapter_for` dispatch and the
conformance gate at §3.2 step 2 are contracts the P-05, P-06 and P-03 lanes build to. Option (a)
deletes all four and re-opens AC15; option (c) moves the declaration to a different file and changes
P-03's config surface. #2072's supply and harness lanes cannot be cut safely until this is settled.
