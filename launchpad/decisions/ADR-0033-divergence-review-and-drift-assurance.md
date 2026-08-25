---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#301
decided_in: launchpad-26/buzz#301
supersedes: none
---

# ADR-0033 — Divergence requires human review and deterministic drift detection

## Decision

The upstream boundary receives two complementary assurances:

1. `CODEOWNERS` requests human review when an ordinary pull request touches the
   upstream-owned boundary.
2. A deterministic scheduled or post-merge check compares the divergence register's
   paths with the computed contested set and fails loudly when either set has an
   unmatched path.

The drift check validates membership and required structure, not whether a prose
justification is correct. Vendor-drop pull requests must not create a blind spot: the
set comparison runs independently of any ordinary-PR exemption.

This outcome was selected automatically under @tucktuck101's explicit approval for
the 2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

ADR-0021 makes the divergence register the durable record of a declined upstream
change, while ADR-0022 limits per-drop adjudication to the registered contested
surface. A missing row is therefore a lost decision. Research in #369 established
that a small `CODEOWNERS` rule accurately requests review on the boundary at modest
frequency, but human review cannot prove the register remains complete. Conversely,
a mechanical set check can prove completeness but not informed review. Both properties
are required and neither substitutes for the other.

## Risk classification

**Clear Medium (4/12), high confidence.** Blast radius 1; reversibility 1;
security/trust 0; data/state 0; contracts/dependencies 1; operations 1. No hard
High-risk trigger applies and no critical dimension scores 2. The controls affect one
repository workflow, are reversible, and do not alter identity, credentials,
production state, or a trust boundary.

## Consequences

- Boundary changes receive a visible human review request.
- Register drift is detected even where a drop workflow bypasses ordinary path checks.
- The deterministic check remains explainable and stable because it compares sets
  rather than asking a model to judge prose.
- Contributors touching the boundary incur an additional review request.
- Two controls must be maintained, because they answer different questions.
- A genuinely inaccurate but structurally complete reason can still pass; review owns
  judgement.
- Task #537 does not implement either assurance. Separate implementation work is
  required under the daily vendor-drop feature.

## Security implications

The controls reduce the chance that an undocumented divergence silently suppresses an
upstream security fix. They add no credential and make no model verdict authoritative.
Security relevance still requires human judgement in the register/drop process.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full options are in #301 and the measured enforcement evidence is
in #369.
