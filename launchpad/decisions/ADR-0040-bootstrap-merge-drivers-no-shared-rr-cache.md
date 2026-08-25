---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#300
decided_in: launchpad-26/buzz#300
supersedes: none
---

# ADR-0040 — Bootstrap merge drivers via `just`; do not ship a shared `rr-cache`

## Decision

Choose a hybrid of Options A and C. Custom merge drivers and `rerere` are bootstrapped via
a `just` recipe wired into `just setup`, so every clone that runs setup gets them. The
`rr-cache` is **not** shared: each clone keeps a private cache, and the PRD criterion "a
conflict resolved once is not resolved again" is stated honestly as meaning "the same
person does not resolve the same conflict twice." A bootstrap-detection check confirms a
clone has run setup so the drivers are actually active.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

`rerere` state lives in `.git/rr-cache/` (per-clone, never committed) and custom merge
drivers are defined in git config, not `.gitattributes` — `merge=ours` is inert until
every clone runs `git config merge.ours.driver true`. A `.gitattributes` shipped without
the bootstrap looks like it works and silently does not.

Rejected: sharing `rr-cache` via an orphan branch (A) or `actions/cache` (B) — the branch
is the most machinery of any option and requires the sync token to write somewhere beyond
the sync; Actions cache is evictable and best-effort. Rejected a git-hook/`includeIf`
bootstrap (D) as deliberate subversion of git's design. Rejected relying on built-in
`union` (E) as wrong for nearly every file in the candidate set.

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 1; reversibility 1;
security/trust 1; data/state 0; contracts/dependencies 1; operations 1. The bootstrap
installs an execution hook locally, but it is explicit and readable, and no credential or
production state changes. No hard High-risk trigger.

## Consequences

- Drivers actually run for any clone that has run setup; a check flags clones that have
  not.
- Criterion 4 is recorded as per-machine, not per-repository — an honest narrowing the
  PRD cannot claim unqualified.
- Two people may still resolve the same conflict independently; nothing reports that it
  happened, which is the accepted cost of not sharing.

## Security implications

A merge driver is an arbitrary shell command git executes during a merge — which is why
git forbids shipping one in the repo. The bootstrap asks contributors to run an explicit,
readable command that installs an execution hook; `true` as the `ours` driver is trivially
safe, and the `rr-cache'` — not shared here — contains source fragments that are not a
disclosure concern on a public fork.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #300.