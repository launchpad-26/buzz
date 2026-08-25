---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#492
decided_in: launchpad-26/buzz#492
supersedes: none
---

# ADR-0044 — Tiered instrumentation for first-party CLI operations

## Decision

Choose the tiered contract. Every first-party CLI emits structured command outcomes with
propagated correlation IDs; spans and metrics are added only where lifecycle or latency
evidence needs them. The existing machine-readable CLI output contract is preserved and
never weakened, and no secret value or raw user content is exported. Explicit criteria
govern when a tool graduates from outcomes-only to full tracing (long-lived subprocesses,
credential-holding administrative commands, end-to-end diagnosis with no other signal).

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

Short-lived commands differ from long-running services: uniform distributed tracing
imposes startup, stdout, and credential-handling complexity without useful diagnostic
value on a tool that runs for two seconds and prints JSON. The end-to-end Git,
administration, agent, pairing, and user-command failures must remain diagnosable, which
outcomes-plus-correlation achieves for the common case while the graduation criteria
catch the high-risk administrative and subprocess surface.

Rejected: full tracing from every command (ceremonial telemetry with credential and
startup complexity), and excluding CLIs entirely (loses diagnosis of product and
administrative operations).

## Risk classification

**Clear Low (4/12), high confidence.** Blast radius 1; reversibility 1;
security/trust 1; data/state 0; contracts/dependencies 1; operations 1. No hard High-risk
trigger. The exposure — CLI args, stdin/stdout, repository paths, keys, auth challenges —
is handled by explicit no-export rules rather than by instrumenting less.

## Consequences

- Complete outcomes and correlation joins for every command; spans only where they earn
  their cost.
- Explicit criteria stop teams under-instrumenting high-risk administrative or subprocess
  operations.
- The machine-readable CLI contract, which is itself an agent contract, stays stable.

## Security implications

CLI arguments, stdin/stdout, repository paths, keys, auth challenges, and subprocess
output may be sensitive. The tiered contract preserves the existing machine-readable
output contracts without exporting raw secrets or user content; the graduation criteria
must require scrubbed export for any span data on the administrative surface.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #492.