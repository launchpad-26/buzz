---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#305
decided_in: launchpad-26/buzz#305
supersedes: none
---

# ADR-0041 — Pin `main` to relay/desktop upstream tags with a standing prompt

## Decision

Choose Option A. The vendor branch `launchpad-26/main` is advanced only to named upstream
release tags — `relay-v*` or `desktop-v*` — ignoring the mobile RC stream, and each pin is
recorded as the resolved commit SHA alongside the tag name. A standing automated report
prompts the drop decision; a human takes the drop deliberately. The immediate action is to
move `main` to at least `launchpad`'s merge-base so it is a truthful baseline.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

`main` sits exactly on `mobile-v0.9.0-rc.1` (2026-08-06), 0 ahead / 228 behind, while
`launchpad`'s merge-base with upstream is 2026-08-17 — eleven days later — so `git diff main
launchpad` mixes upstream's own work into the cohort's divergence. Upstream's tag stream is
dominated by mobile RCs the fork does not ship. Tags are the natural pin because upstream
publishes and tests them; recording the SHA defends against tag mutability.

Rejected: per arbitrary commit (C, no coherence guarantee), time-boxed HEAD (D, the mirror
behaviour curation rejects), and demand-driven-only (E, what produced the unnoticed
gap — valid as an additional trigger, not as the sole rule).

## Risk classification

**Clear Medium (5/12), high confidence.** Blast radius 1; reversibility 2;
security/trust 1; data/state 0; contracts/dependencies 1; operations 1. No hard High-risk
trigger. A deliberately held vendor branch delays upstream fixes by policy; the standing
prompt is the compensating control that keeps that delay visible and bounded.

## Consequences

- `main` becomes a baseline someone can rely on; the first action fixes the current
  inconsistency.
- The gap becomes a stated policy choice with an owner rather than an unnoticed default.
- A tag filter can be wrong the first time upstream tags something important under a name
  it does not match; recording the SHA bounds the risk.

## Security implications

The pin determines how long an upstream security fix waits before it is visible to the
cohort. The standing prompt is wired to the upstream-intelligence work so fixes that should
jump the queue are surfaced; pinning to a published, tested tag is a stronger provenance
position than an arbitrary mid-series commit.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #305.