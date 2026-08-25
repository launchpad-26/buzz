---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#299
decided_in: launchpad-26/buzz#299
supersedes: none
---

# ADR-0039 — A GitHub App installation token authors the vendor-drop PR

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human — *"You may not decide an ADR
outcome"* — and #299's *Decision outcome* is still blank. When a human states the
outcome in #299, this record's `status` becomes `Accepted`. Everything below is a
drafted proposal, not a settled rule.

The proposed option: Option A. The vendor-drop pull request is authored by a GitHub App
installation token: PRs opened with an app token trigger `pull_request` workflows, so CI
runs with no change to `ci.yml`. The identity is the app's, not a person's, which is
what makes the audit trail true.

**Authorship only — an app token cannot approve.** This is the load-bearing limit and it
is worth stating rather than leaving to inference.
[ADR-0019](./ADR-0019-review-checks-gate-only-when-deterministic.md) records that
*"GitHub treats required approving reviews and required status checks as two independent
gates, and a check can never satisfy the review count"*, and rejects *"A GitHub App
submitting a literal `APPROVE` review"* as a mechanism. Opening a pull request produces
no approval, so nothing here lets an automated identity clear its own work, and nothing
here routes around ADR-0038 — that record governs push to `main`; this one governs who
authors a pull request into `launchpad`. The app's permissions must be scoped to match:
no approving-review capability, and no push to `main`.

## Context

A PR opened by the Actions `GITHUB_TOKEN` triggers no `pull_request` workflow runs, and
`ci.yml` triggers on `push: [main, release]` plus `pull_request:` — so a drop PR opened
by the obvious implementation would arrive with zero checks. The app-token option is the
standard answer: CI fires, the identity is attributable to the app, and the token is
scoped to declared permissions, revocable independently of any person.

**On precedent — corrected.** #299's own drivers and security section attribute the
scoped/revocable/audit-log properties to `launchpad/decisions/ADR-0015`. ADR-0015 does
not contain them: its subject is handbook page authoring mode, and its only mention of
tokens is a list of things a handbook page must not expose — *"no live hostnames, keys,
tokens, `.env` bodies, or member rosters"*. That citation should not be relied on, here
or in #299.

The record that does set this pattern is
[ADR-0008](./ADR-0008-security-audit-privilege.md). It rejects a long-lived person-held
PAT because *"a PAT held by a person outlives that person and is a standing liability on
a public repo"*, and where a credential is genuinely needed it pre-specifies exactly
this shape: someone with org-owner rights *"creates a GitHub App scoped to
`administration: read` only"*, *"Installs it on `launchpad-26/buzz` specifically, not
org-wide"*, and *"Stores its App ID and private key as an Actions secret or Environment
— never a tracked file"*, with *"its scope, owner and expiry recorded where the next
person can find them"*. Option A here is the same pattern at a different scope — least
permission needed to open a pull request, nothing wider.

Rejected: editing `ci.yml`'s triggers (B, deepens divergence in an already-conflicting
upstream file), `workflow_dispatch` (C, not associated with the PR), a PAT (D, gives
automation a person's identity and makes the audit trail lie), and accepting unchecked
drop PRs (E).

**The fifth option, raised in #299's premise correction and weighed here.** Because a
drop is now initiated by a human rather than a cron, #299 notes that *"the human who
takes the drop opens the PR from their own machine — a fifth option not listed below,
which costs nothing to set up and gives up the unattended path in #273's second success
criterion. That option should be weighed alongside the others."* It is the cheapest
option available and it is not rejected on cost or on safety — a human-opened PR
triggers `pull_request` workflows and is attributable to a real person, which are the
two properties this decision needs. It is not proposed here for one reason only: it
forecloses the unattended path PRD #273 asks for, so choosing it is a scope decision
about #273 rather than an identity decision, and it should be taken as such. If a human
settling #299 prefers it, the correct consequence is that #273's unattended criterion is
amended or dropped in the same breath — not that this record is quietly satisfied by a
person doing the work by hand.

## Consequences

- Drop PRs arrive with CI checks rather than zero checks.
- An admin must create and install the app and store its credentials — the same class of
  privilege question as writing to `main`.
- The PRD's *"`just ci` gates every sync PR"* criterion becomes **partly** achievable:
  this settles whether the checks *run*, not whether they *gate*. ADR-0019 records that
  *"Zero required status checks are configured"*, that `adr-boundary` *"runs and passes
  on every pull request but is not required, so it blocks nothing"*, and that
  *"Enforcement is deferred until the CI/CD pipeline is live."* Gating therefore depends
  on the required status checks work — #153 and #146 remain open by that decision, not
  by obstruction — and until it lands a drop PR shows checks a reviewer can read but
  nothing the platform enforces.

## Security implications

The sync PR carries untrusted upstream content; whether CI executes that content is
exactly what this decision turns on — running CI on the drop PR means building
cohort-untrusted code on the cohort's runners, which is the correct, reviewed posture
versus merging it unchecked. The app token is scoped, revocable, and shows as the app in
the audit log, unlike a PAT.

A credential is introduced where ADR-0038 introduces none, and that asymmetry is
deliberate rather than an oversight: authorship needs an identity, a fast-forward of
`main` does not. Following ADR-0008, the app must be installed on this repository
specifically rather than org-wide, its private key held as an Actions secret or
Environment and never as a tracked file, and its scope, owner and expiry written down
where the next person will find them.

## Supersedes

none

## Provenance

Drafted by an agent from #299's options; the decision itself is pending a human, as
stated at the top of *Decision*. Full alternatives, the measured `ci.yml` triggers, and
the 2026-08-22 premise correction that raised the fifth option remain in #299.

Verified while drafting: ADR-0015 does not contain the token properties #299 attributes
to it; ADR-0008 pre-specifies the scoped-GitHub-App pattern quoted above; ADR-0019
records that zero required status checks are configured and that a check can never
satisfy the review count. All three were read in full on `launchpad`.

Not verified independently in this document: whether a GitHub App exists or has been
requested, and the current state of required status checks beyond what ADR-0019 recorded
on 2026-08-21.
