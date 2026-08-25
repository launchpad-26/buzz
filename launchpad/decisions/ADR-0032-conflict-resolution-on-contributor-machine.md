---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#297
decided_in: launchpad-26/buzz#297
supersedes: none
---

# ADR-0032 — Escalated vendor conflicts are resolved on a contributor machine

## Decision

Escalated upstream merge conflicts are resolved on a contributor machine through a
documented `just` entry point that recreates the merge and leaves the conflicted tree
for a human. The workflow supplies a deterministic escalation bundle; it does not
attempt an interactive resolution inside GitHub Actions.

A provisioned environment is deferred. It may be reconsidered if repeated use shows
that contributor-machine variance, attestability, or shared-resolution state causes a
real operational problem; no environment is built speculatively.

This outcome was selected automatically under @tucktuck101's explicit approval for
the 2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

ADR-0021 chooses merge-based vendor adoption and ADR-0022 scopes adjudication to the
contested surface. Novel conflicts still require a human resolution, but GitHub
Actions has no interactive session and no dedicated development environment exists.
The current repository toolchain already runs on contributor machines, making a local
resume command the smallest usable path.

## Risk classification

**Low (3/12), high confidence.** Blast radius 1; reversibility 0; security/trust 0;
data/state 0; contracts/dependencies 1; operations 1. No hard High-risk trigger
applies. The decision locates a bounded human workflow, creates no credential or
privilege, changes no production system, and is cheap to replace later.

## Consequences

- A conflict can be handled with infrastructure that exists now.
- A human is present by construction for every novel semantic resolution.
- The exact toolchain and command can be documented and tested once rather than
  reconstructed per drop.
- Local execution is not centrally attested and can vary by contributor machine.
- Resolution reuse remains governed separately; this record does not choose a shared
  `rr-cache` or grant an agent authority to resolve a novel conflict.
- Existing Task #537 owns updating PRD #273 and its vendor-drop workflow. The concrete
  resume command belongs in that implementation decomposition; no new task is raised
  by this decision record.

## Security implications

No trust boundary or privilege changes. The contributor uses their existing repository
access, and the workflow does not add a hosted credential or execute an untrusted
resolution unattended. Upstream content remains untrusted input to the review process.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives and evidence remain in #297.
