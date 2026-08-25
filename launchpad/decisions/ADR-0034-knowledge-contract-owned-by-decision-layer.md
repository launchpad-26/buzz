---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#589
decided_in: launchpad-26/buzz#589
supersedes: none
---

# ADR-0034 — The knowledge contract is owned by the decision layer

## Decision

Choose Option D. The normative `knowledge.*` interface contract is a shared,
implementation-neutral specification owned by `launchpad/decisions/`, and both the
Python project-intelligence pipeline and the shipped Rust crate maintain executable
conformance tests against it. Neither implementation owns the contract or serves as
the other's unchecked source of truth.

Changes to the normative interface are made through a superseding decision record;
accepted ADR files are not edited in place as a living specification. Mechanical test
fixtures may derive from the accepted contract, but they must identify the ADR version
they assert.

This outcome was selected automatically under @tucktuck101's explicit approval for
the 2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

`launchpad/project-intelligence/CONTRACT.md` currently sits beside the Python
implementation. Once a Rust crate ships the same public surface, leaving the contract
there makes one implementer the apparent owner and leaves Rust conformance unchecked.
Moving it into the crate reverses the asymmetry. The decision layer is the existing
home for binding cross-component rationale and provides a neutral authority.

## Risk classification

**Clear Medium (4/12), high confidence.** Blast radius 1; reversibility 1;
security/trust 0; data/state 0; contracts/dependencies 1; operations 1. No hard
High-risk trigger applies and no critical dimension scores 2. This is an internal,
same-repository contract-location choice with a planned migration and no credential,
production-data, public-protocol, or trust-boundary change.

## Consequences

- Python and Rust are peers against one neutral normative contract.
- Drift becomes observable on both sides rather than only in the pipeline.
- Interface changes incur a new ADR version, which preserves history but is heavier
  than editing a living document.
- Two conformance suites must be maintained and kept aligned with the named decision
  version.
- Task #553 owns defining the contract and Task #552 owns packaging the corpus into the
  crate. Their implementation must apply this location and two-sided conformance rule;
  no additional task is required.

## Security implications

No exposure or trust boundary changes. The contract continues to govern provenance
behavior, but this record changes only where that internal specification is authoritative
and how implementations demonstrate conformance.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #589.
