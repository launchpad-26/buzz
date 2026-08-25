---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#298
decided_in: launchpad-26/buzz#298
supersedes: none
---

# ADR-0038 — A small named group of humans may advance `main` to a chosen vendor point

## Decision

Choose Option A. Add a small, named group of humans to the push restriction on
`launchpad-26/main`, limited to the people who may take a vendor drop. The operation
remains fast-forward-only; `allow_force_pushes` and `allow_deletions` stay false, and
no automation receives any credential. Every advance records the chosen point and the
rationale for it.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

`main` is a vendor branch — upstream pinned at a chosen point — and today push is
restricted to a single named human who is not the owner of the work. The branch sat
eleven days behind `launchpad`'s own merge-base, so `git diff main launchpad` mixed
upstream's work into the cohort's divergence. The ask is narrow: occasional, deliberate,
attributable fast-forwards by hand, not standing write access for automation.

ADR-0015 set the pattern: no standing credential for automation, irreversible steps
proposed rather than taken, every action attributable. A fast-forward is publicly visible,
so attributability matters more than reversibility.

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 2; reversibility 2;
security/trust 1; data/state 0; contracts/dependencies 0; operations 1. No hard
High-risk trigger. Wideness is bounded to a short named list, fast-forward only, with
force-push and deletion prohibited; the residual concern is ordinary (more accounts
whose compromise matters).

## Consequences

- The vendor branch can be corrected to at least `launchpad`'s merge-base, making it a
  truthful baseline.
- Availability improves: one person's absence no longer stalls the curation loop.
- The list must stay short and named; growing it by default is the risk to watch.

## Security implications

The original framing asked for standing push access for a scheduled process; this grants
occasional, attributable, human fast-forwards to a chosen point — a supply-chain trust
choice (who picks the point ~4,300 files of upstream code is pinned to), not a credential
grant. No credential exists to steal.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #298.