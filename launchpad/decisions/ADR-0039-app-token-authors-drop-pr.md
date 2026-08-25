---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#299
decided_in: launchpad-26/buzz#299
supersedes: none
---

# ADR-0039 — A GitHub App installation token authors the vendor-drop PR

## Decision

Choose Option A. The vendor-drop pull request is authored by a GitHub App installation
token: PRs opened with an app token trigger `pull_request` workflows, so CI runs with
no change to `ci.yml`. The identity is the app's, not a person's, satisfying
attributability and ADR-0015's requirements.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

A PR opened by the Actions `GITHUB_TOKEN` triggers no `pull_request` workflow runs, and
`ci.yml` triggers on `push: [main, release]` plus `pull_request:` — so a drop PR opened
by the obvious implementation would arrive with zero checks. The app-token option is the
standard answer: CI fires, the identity is attributable to the app, and the token is
scoped to declared permissions, revocable independently of any person.

Rejected: editing `ci.yml`'s triggers (B, deepens divergence in an already-conflicting
upstream file), `workflow_dispatch` (C, not associated with the PR), a PAT (D, gives
automation a person's identity and makes the audit trail lie), and accepting unchecked
drop PRs (E).

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 2; reversibility 1;
security/trust 2; data/state 0; contracts/dependencies 1; operations 1. A credential is
introduced, but it is app-scoped, revocable, and attributable — the least-privilege
option that still makes CI run on the drop PR. No hard High-risk trigger.

## Consequences

- Drop PRs arrive with CI checks rather than zero checks.
- An admin must create and install the app and store its credentials — the same class of
  privilege question as writing to `main`.
- The PRD's "just ci gates every sync PR" criterion becomes achievable.

## Security implications

The sync PR carries untrusted upstream content; whether CI executes that content is
exactly what this decision turns on — running CI on the drop PR means building
cohort-untrusted code on the cohort's runners, which is the correct, reviewed posture
versus merging it unchecked. The app token is scoped, revocable, and shows as the app in
the audit log, unlike a PAT.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #299.