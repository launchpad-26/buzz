---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#307
decided_in: launchpad-26/buzz#307
supersedes: none
---

# ADR-0043 — Prefer fork-owned overrides; in-place edits require a recorded justification

## Decision

Choose Option A. The default for a standing disagreement with upstream is a fork-owned file
that overrides, wraps, or delegates to upstream's — never a copy. An in-place edit to an
upstream file is allowed only with a recorded justification in the PR body explaining why
an override was not possible, and that justification lands in the divergence register as
the file's recorded reason. The distinction between *override* (delegates to upstream,
keeps receiving upstream's changes) and *copy* (diverges silently) is explicit: copies are
prohibited.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

Of 48 diverged upstream files, 27 are edits to upstream's files — the entire conflict
surface — and 20 of those have no recorded reason. ADR-0005 already chose a wrapper for
`deploy/compose/run.sh` and rejected forking `docker.yml` into a copy, recording that "a
conflict that Git shows you is better than a divergence that nothing does." This
generalises that precedent with the justification gate. It applies to work not yet done;
the 27 existing edits are not worth retrofitting.

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 2; reversibility 1;
security/trust 1; data/state 0; contracts/dependencies 1; operations 1. No hard High-risk
trigger. This reduces future conflict volume; the security property is that upstream's
fixes keep arriving on files the fork does not own.

## Consequences

- The form of divergence has a governing rule; the 20 silent edits stop being the pattern.
- The justification requirement lands in the register at the moment of divergence — the
  exact gap the register exists to fill.
- Rust/TSX often have no override mechanism, so the rule will frequently resolve to "edit
  in place, justification: no alternative" — honest, and it leaves the register complete.

## Security implications

An in-place edit means every upstream fix to that file arrives as a visible conflict —
delayable but visible. A durable decline on a wholly fork-owned file means upstream's fixes
to the *upstream* file keep flowing untouched — the safer posture. A copying wrapper
silently stops receiving upstream fixes with nothing reporting the gap: strictly worse than
a conflict and explicitly rejected by this record.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #307.