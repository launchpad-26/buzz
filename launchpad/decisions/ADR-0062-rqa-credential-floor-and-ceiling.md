---
status: Accepted
date: 2026-09-11
issue: launchpad-26/buzz#2158
decided_in: agent session — no addressable comment exists; see Provenance
supersedes: none
---

# ADR-0062 — RQA proves the authority it exercises and records the credential breadth it cannot narrow

## Decision

The GitHub credential for review-queue-automation (RQA) is the operator's `gh auth token`. Personal
access tokens and GitHub Apps are out of scope for this version. Under that constraint RQA meets
RQA-NFR-024's floor and RQA-NFR-030's ceiling as follows — option **(a)** of
[`ADR-E`](../skills/review-queue-automation/architecture/adr-drafts/ADR-E.md), the architecture's
recommendation, with option (c) folded in **only if** the metadata proves available:

1. **P-08 grants an activity only when both hold**: the pinned policy snapshot grants it, *and* a
   per-job capability probe (E-16) proves the credential can actually perform it on that repository.
   A failed probe yields no grant, and therefore an *authority requirement* escalation
   (see [ADR-0061](ADR-0061-rqa-terminal-outcome-without-verdict-authority.md)) rather than an
   attempt.
2. **P-09 never addresses a repository outside the configured set.**
3. **What the token could do elsewhere is recorded, not hidden.** P-08 contributes an `attestation`
   entry per job carrying proven capabilities and `attested_not_proven`, and the onboarding output
   tells the operator to scope `gh auth login` as narrowly as GitHub permits.
4. **No per-repository credential store exists.** The credential is read per call and never
   persisted.
5. **If GitHub later exposes per-repository permission enumeration for the CLI's OAuth credential**,
   that reading strengthens this design; it does not replace the probe.

**RQA-NFR-030's ceiling half is an accepted residual for this version, not an open question.** RQA
confines what it *exercises*; the breadth of `gh auth token` is decided by how the operator
authenticated `gh`, outside RQA.

## Context

RQA-NFR-024 requires the credential to carry, per managed repository, pull-request write and contents
read plus exactly the extra write scope its configured activities need. RQA-NFR-030 requires it to
carry no permission beyond that on a managed repository, and none at all on an unmanaged one. The gap
register records the pre-existing estate's use of `gh auth token` as RQA-NFR-030 `conflicting`
(`built contrary`), because the operator's GitHub CLI credential is user-wide.

The constraint and the requirement's ceiling half cannot both be fully satisfied by RQA. The reason
the constraint exists is organisational, not technical: a personal access token or a GitHub App would
require Launchpad-26 org-admin approval, which the maintainer decided not to pursue for this version.
The maintainer's position, recorded in the draft on 2026-09-08 and ratified here: if that means
unauthorised repositories are reachable by the token, so be it; it will be addressed outside this
project.

Option (b) — declaring RQA-NFR-030 unmeetable and mounting no design response — is rejected: the
probe is cheap, and it is what makes the *floor* checkable rather than assumed.

Affected parts: **P-08** (authority gate), **P-09** (GitHub adapter), **P-01** (intake).
Requirements: RQA-NFR-024, RQA-NFR-030, RQA-NFR-025, RQA-FR-038.

## Consequences

- **Good.** The floor becomes a proof rather than a hope: no activity runs without a grant *and* a
  demonstrated capability on that exact repository. Every write goes through one gate and one
  adapter. If the constraint is later relaxed, **two** credential reads change, not one: P-08's E-22
  read, and P-09's own private per-call `transport._credential()` resolution, which is independent of
  E-22 by design so that P-08 is never a runtime dependency of the adapter it probes through
  (`P-09-github-adapter.md` §4). `probe()` is the single declared exception, taking its credential as
  an argument from P-08. Migrating only E-22 would move probing to a new credential while every real
  GitHub operation kept the old one.
- **Bad, stated plainly.** **A credential broader than the managed set remains in use, and RQA cannot
  narrow it.** RQA-NFR-030 is therefore not satisfied as written for this version; it is satisfied
  only for what RQA exercises. Any process running as the operator can reach the same token. The
  residual is accepted, recorded in the register, and owned outside this project — it is not closed.
- **Decomposition.** E-22's shape (one operator credential, not one per repository), the
  `capabilities` record, and the deliberate absence of a credential store are contracts the P-08,
  P-09 and P-01 lanes build to. A different ruling would have cut those lanes differently, which is
  why this ADR was decomposition-blocking.

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
cannot reach the original instruction; this quotation is its only surviving form.

The 2026-09-08 maintainer direction on the residual predates this record and is quoted in
[`ADR-E`](../skills/review-queue-automation/architecture/adr-drafts/ADR-E.md); the argument is on
[#2158](https://github.com/launchpad-26/buzz/issues/2158).
