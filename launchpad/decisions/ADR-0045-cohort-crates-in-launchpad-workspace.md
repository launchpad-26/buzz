---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#1409
decided_in: launchpad-26/buzz#1409
supersedes: none
---

# ADR-0045 — Cohort crates live under `launchpad/crates/` as workspace members

## Decision

Choose Option B. Cohort-authored Rust crates live under `launchpad/crates/`, keeping all
cohort source inside the `launchpad/` boundary, and are registered as members of the
upstream root Cargo workspace via an append-only addition to the root `Cargo.toml`
`members` list. That single-file, append-only divergence is granted as a named §3
exception by this record. Upstream's `crates/` directory is not touched.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

Two open Tasks require a cohort crate to exist and build (#551, #524), and `launchpad/
AGENTS.md` §3's closed exception list requires an ADR for any exception. The root
`Cargo.toml` declares an explicit 31-path `members` list with no glob, so workspace
membership is an edit to an upstream file in every option except C and D. Option B
confines cohort source to `launchpad/` and reduces the divergence to one append-only line
of an upstream file — smaller than a directory-level exception, and reversible by removing
one line.

Rejected: source under upstream `crates/` (A, puts cohort source inside an upstream-owned
directory and needs a wider exception), a separate cohort workspace (C, second lockfile,
second dependency-audit surface, existing workspace-wide CI does not reach it), and a
separate repository (D, cross-repo release step for every change).

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 2; reversibility 1;
security/trust 0; data/state 0; contracts/dependencies 2; operations 1. No hard High-risk
trigger. The one-line `Cargo.toml` divergence re-conflicts on merges, but it is
append-only and single-file — the bounded form of the §3 boundary this ADR exists to
permit.

## Consequences

- Both planned crates get a home inside `launchpad/` and build through the existing
  workspace and CI.
- The root `Cargo.toml` becomes a standing one-line divergence, recorded in the
  divergence register; upstream syncs touching the members list are visible conflicts, not
  silent drift.
- Future cohort crates follow the same path without a new ADR per crate.

## Security implications

No security, trust, or authority consequence: the options differ in build topology and
upstream merge cost, not in what anyone can reach or read. The one-line members-list
divergence is the mechanism whose risk is bounded and visible, unlike a second workspace
CI would silently not cover.

## Supersedes

Conditionally amends #13:decision-2 (the two `.github/` exceptions) by adding this third,
named exception; the underlying closed-list rule is untouched.

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #1409.