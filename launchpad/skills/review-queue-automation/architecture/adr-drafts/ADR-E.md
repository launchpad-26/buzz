# ADR-E — Meeting the credential floor and ceiling when the only credential is the operator's `gh auth token`

**Status:** decided 2026-09-11 — recommendation (a) accepted; recorded as [ADR-0062](../../../../decisions/ADR-0062-rqa-credential-floor-and-ceiling.md), which closes [issue #2158](https://github.com/launchpad-26/buzz/issues/2158). This draft is retained as the architecture's rationale, not as an open question.
**Parent:** [#2006](https://github.com/launchpad-26/buzz/issues/2006) · **Raised by:** #2071 architecture · **Decomposition-blocking:** **blocking**
**Parts affected:** P-08, P-09, P-01 · **Requirements:** RQA-NFR-024, RQA-NFR-030, RQA-NFR-025, RQA-FR-038

## Question

The maintainer has constrained the design during #2071: **the GitHub credential is `gh auth token`;
personal access tokens are out of scope.** RQA-NFR-024 requires the credential to carry, per managed
repository, pull-request write and contents read plus exactly the extra write scope its configured
activities need; RQA-NFR-030 requires it to carry no permission beyond that on a managed repository and
none at all on an unmanaged one. The gap register records the estate's use of `gh auth token` as
RQA-NFR-030 `conflicting` (`built contrary`), because the operator's GitHub CLI credential is
user-wide. Under the constraint, how are the floor and the ceiling met?

## Why the architecture cannot settle it alone

The constraint and the requirement's ceiling half cannot both be fully satisfied by RQA: the breadth of
`gh auth token` is decided by how the operator authenticated `gh`, outside RQA. Whether the residual is
acceptable — and whether RQA-NFR-030's row should be re-read as a provisioning obligation on the
operator — is the maintainer's to decide, not the architecture's.

## Options

| | option | consequence for the parts |
|---|---|---|
| (a) | **Enforce the exercised authority, attest the rest.** P-08 grants an activity only when the pinned snapshot grants it *and* a per-job capability probe (E-16) proves the `gh auth token` can perform it on that repository. P-09 never addresses a repository outside the configured set. RQA-NFR-024's floor is checked (probe fails → no grant → escalation *authority requirement*). RQA-NFR-030's ceiling is met for what RQA *does*; what the token *could* do elsewhere is recorded as attested-not-proven in the `attestation` entry P-08 contributes for the job, and the onboarding output tells the operator to scope `gh auth login` as narrowly as GitHub permits. | P-08: `capabilities` record per job; E-22 is `gh auth token`; E-16 probes per repository. P-01's admission gate refuses a repository whose probe fails outright. No per-repository credential store exists. |
| (b) | **Treat RQA-NFR-030 as unmeetable under the constraint** and record it as a standing non-conformance in the register with no design response. | Same parts as (a) minus the probe; less evidence in the record. Rejected: the probe is cheap and it is what makes the floor checkable rather than assumed. |
| (c) | **Ask GitHub for the token's own scope metadata** and refuse to run when it exceeds the managed set. | Depends on GitHub exposing per-repository permission enumeration for the CLI's OAuth credential, which was not verifiable while drafting; if it exists it strengthens (a), it does not replace it. |

## Maintainer ruling, 2026-09-08 — residual accepted for this version

The constraint exists because Launchpad-26 organisation policy would require org-admin approval for a
personal access token or a GitHub App, which the maintainer has decided not to pursue for this version.
Consequence, in his words: if that means unauthorised repositories are reachable by the token, so be it;
it will be addressed outside this project. RQA-NFR-030's ceiling half is therefore an **accepted
residual** for this version, not an open question, and the architecture proceeds on (a).

## Recommendation — (a), with (c) folded in if the metadata proves available

It is the most RQA can do under the constraint, it makes the floor a proof rather than a hope, and it
states the residual honestly instead of hiding it. Every write still goes through one gate and one
adapter. If the maintainer later relaxes the constraint, two credential reads change, not one: P-08's
E-22 read and P-09's own private per-call `transport._credential()` resolution, which is deliberately
independent of E-22 (`P-09-github-adapter.md` §4); `probe()` is the one declared exception.

## Why blocking

E-22's shape (one operator credential, not one per repository), the `capabilities` record, and the
absence of any credential store are contracts P-08, P-09 and P-01 lanes build to. Had the maintainer
chosen differently — a credential per repository, or none of the probing — those lanes would have been
cut to a different shape. It is recommended and assumed, but it is the one ADR whose alternative moves
a contract, so it is listed as blocking.
