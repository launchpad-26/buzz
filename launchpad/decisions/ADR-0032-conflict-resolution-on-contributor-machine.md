---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#297
decided_in: launchpad-26/buzz#297
supersedes: none
---

# ADR-0032 — Escalated vendor conflicts are resolved on a contributor machine

## Decision

Option D — escalated upstream merge conflicts are resolved on a contributor machine
through a documented `just` entry point that recreates the merge and leaves the
conflicted tree for a human. The workflow supplies a deterministic escalation bundle; it
does not attempt an interactive resolution inside GitHub Actions.

A provisioned environment is deferred. It is reconsidered when either of these is
observed, whichever comes first:

- the same escalated conflict is resolved independently on two different contributor
  machines, or
- one resolution is rejected in review because it could not be reproduced on another
  machine.

Feature #525 owns watching for both. No environment is built speculatively.

## Context

ADR-0021 chooses merge-based vendor adoption and ADR-0022 scopes adjudication to the
contested surface. Novel conflicts still require a human resolution, but GitHub
Actions has no interactive session and no dedicated development environment exists.
The current repository toolchain already runs on contributor machines, making a local
resume command the smallest usable path.

## Consequences

- A conflict can be handled with infrastructure that exists now.
- A human is present by construction for every novel semantic resolution.
- The exact toolchain and command can be documented and tested once rather than
  reconstructed per drop.
- Local execution is not centrally attested and can vary by contributor machine.
- **Resolution reuse is not solved here, and if #300 decides against a shared
  `rr-cache` it is not solved anywhere.** In that case the same conflict can be
  resolved from scratch by a second person on a second machine with nothing reporting
  that it happened — which is the PRD success criterion #297 identified as at risk.
  The reconsideration triggers above exist to make that observable rather than silent.
- This record does not grant an agent authority to resolve a novel conflict.
- Task #1426 owns the reproducible escalation bundle and local `just` resume entry
  point under Feature #525. It was raised because #541 owns the scheduled merge but
  does not cover this conflict-resolution UX.

## Security implications

**This is the half of #273 that runs untrusted upstream content on a contributor's own
workstation.** `cargo build` and `pnpm install` both execute code from the tree, so a
hostile upstream commit reaches a contributor's machine before anyone has read it. That
exposure is a property of resolving locally and it is accepted here only as far as this
record's scope reaches: `buzz-infrastructure` #103 owns the workstation-exposure
question and this record does not settle it. Anyone implementing #1426 must treat #103
as an open dependency rather than assume the boundary is clear.

The contributor uses their existing repository access, and the workflow adds no hosted
credential and executes no untrusted resolution unattended. Upstream content remains
untrusted input to the review process.

## Supersedes

none

## Provenance

Drafted by an agent from #297's options. Jeffrey (@tucktuck101) made the decision on
2026-08-31 after reviewing options A–D with their positive and negative consequences and
the agent's recommendation of Option D (contributor machine now, provisioned environment
deferred behind two named reconsideration triggers); he replied verbatim: **"just A"**,
immediately corrected to **"sorry meand D."** — Option D is the decision. Full
alternatives and evidence remain in #297.
