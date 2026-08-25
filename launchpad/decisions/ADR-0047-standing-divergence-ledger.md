---
status: Accepted
date: 2026-08-26
issue: launchpad-26/buzz#294
decided_in: launchpad-26/buzz#294
supersedes: none
---

# ADR-0047 — Standing positions for fork divergences are recorded in a durable ledger

## Decision

The fork maintains a versioned divergence ledger for every upstream-owned file it
modifies or deletes. The ledger is the authoritative record of the fork's standing
position during vendor drops.

Each row MUST state the path, classification, position, enforcement mechanism,
rationale or `unrecorded`, security relevance, and a termination condition where
applicable.

Default positions are:

- Cohort-owned material: fork wins.
- Upstream product code and build tooling: upstream wins.
- Generated lockfiles: regenerate; do not preserve either side mechanically.

Exceptions override these defaults:

- The five deployment-provenance files accepted in ADR-0005 retain their fork
  position.
- The pinned binaries accepted in ADR-0017 use newest wins.
- The nine product-code rows decided in #339 retain their recorded positions:
  permanent, converging, or permanent-by-construction as applicable.

Permitted enforcement mechanisms are transforming merge driver, per-path merge
assignment, post-merge assertion, recorded `rerere` replay, and explicit
escalation. Every security-relevant automatic-fork-win row MUST require review on
every vendor drop.

`rerere.autoUpdate` MUST remain disabled for vendor-drop merges.

A converging row MUST include a deterministic upstream-status check and MUST be
removed once upstream has incorporated the equivalent change.

This outcome was selected by @tucktuck101 in the 2026-08-26 ADR-clearing session.

## Context

The fork adopts upstream through vendor-drop merges while retaining selected,
recorded divergences. ADR-0021 makes the recorded decline the durable mechanism;
ADR-0022 limits drop review to the intersection of upstream-touched files and
ledger rows. A fork-modified upstream file without a ledger row can therefore
avoid adjudication entirely.

A binary fork/upstream flag is insufficient. ADR-0017 requires newest wins for
its pinned binaries, while some divergences apply only to a portion of a file.
The ledger must record both the intended position and a mechanism capable of
enforcing it.

## Consequences

- Every new modification or deletion of an upstream-owned file receives a
  recorded position before it can become an unreviewed divergence.
- The vendor-drop process can compute its contested surface from the ledger.
- Defaults reduce ambiguity for future rows; explicit exceptions preserve
  accepted cohort positions.
- Security-relevant automatic preservation remains visible on every drop rather
  than masking upstream security fixes.
- Converging divergences do not become permanent by inertia.

## Security implications

Automatic fork wins can retain an outdated dependency, hook binary, deployment
image configuration, or other security-sensitive content despite a later upstream
fix. The ledger therefore marks security relevance explicitly and requires
per-drop review for every security-relevant automatic-fork-win row.

Disabling `rerere.autoUpdate` prevents a replayed resolution from being staged
silently. Recorded `rerere` remains a labour-saving replay mechanism, not an
unreviewed authority to update the merge result.

## Supersedes

none — this operationalizes ADR-0021 and ADR-0022 without changing either
accepted decision.

## Provenance

Decision made by @tucktuck101 in the 2026-08-26 ADR-clearing session. The full
alternatives, evidence, and prior inputs remain in #294.