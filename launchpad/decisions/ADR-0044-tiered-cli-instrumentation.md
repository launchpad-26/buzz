---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#492
decided_in: launchpad-26/buzz#492
supersedes: none
---

# ADR-0044 — Tiered instrumentation for first-party CLI operations

## Decision

**Not settled, and explicitly blocked. Do not treat this record as decided.** This record
is `Proposed`, not `Accepted`, and it is blocked on evidence that does not exist yet.

Two independent reasons, both of which must clear first:

1. **A human instructed that this outcome stay blank.** @tucktuck101 on #492, 2026-08-22:
   *"**Decision status: blocked on evidence.** Instrumentation depth will be controlled by
   preset telemetry profiles, but the profile set, default, and signal contents are not yet
   decidable. #462 and #474-#476 must first establish current runtime capabilities, cost,
   safety boundaries, and distribution constraints. **Keep the Decision outcome blank; do
   not invent profiles** in desired-state or implementation work before this evidence
   exists."* #492's *Decision outcome* is still blank.
2. **An accepted ADR says the same.** `ADR-0026-fail-open-telemetry-export.md` (Accepted,
   2026-08-22): *"The exact profiles, defaults, and signal depth are not decided here;
   issue #492 remains blocked on the current-state assessments needed to establish viable
   profiles."* Those assessments are open: #474, #475 and #476 — the last being the CLI
   current-state assessment this record most needs — are all still open.

What follows is therefore a **draft shape for the eventual decision**, recorded so the
reasoning is not lost, and not a rule anyone should implement. It becomes `Accepted` only
after #474–#476 close and a human states the outcome in #492.

### What this record deliberately does NOT contain

An earlier revision of this record kept a "draft shape" that named two profiles, defined
their signal contents, and set numeric graduation thresholds. That was the prohibited act,
not a way around it: #492 says *"do not invent profiles"*, and a record cannot both invent
a profile set and claim it is not choosing one. Those inventions are withdrawn rather than
relocated, and nothing replaces them here.

What survives is only the shape of the question, which #474-#476 must answer before anyone
can answer it:

- Depth is configured by **preset profiles**, not per-signal toggles. That is not this
  record's choice — `ADR-0026-fail-open-telemetry-export.md` already decided it: *"When
  enabled, configuration uses preset profiles rather than individual or granular
  signal-level toggles."* Whatever #492 eventually decides is expressed in that vocabulary.
- Correlation uses **W3C Trace Context**, per `ADR-0024-w3c-trace-context-correlation.md`,
  which makes it *"Buzz's primary correlation mechanism"* and forbids substituting another
  universal identity join. Not open for this record to revisit either.
- Content handling follows `ADR-0025-controlled-free-text-telemetry.md`, which permits free
  text as a *"required diagnostic capability"* under its named controls (field
  classification, secret and credential filtering before the export boundary, size limits
  with a visible truncation marker, restricted and audited access, defined retention,
  contributor consent) and absolutely prohibits *"[p]rivate keys, authentication tokens,
  raw environment variables, and binary attachments"*. An earlier revision of this record
  said "no raw user content is exported", which reads as forbidding the evidence ADR-0025
  requires; that is withdrawn.
- The existing machine-readable CLI output contract is preserved and never weakened. It is
  itself an agent contract.

**The open questions, left open:** which profiles exist, which is the default, what each
one's signal contents are, and what promotes a tool from one to another. #462 and #474-#476
must establish current runtime capabilities, cost, safety boundaries and distribution
constraints first. Anyone tempted to fill these in before that evidence lands should read
the comment on #492 again.

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

What this record cannot do is choose the profile set, its default, or its signal contents.
That is exactly what #492 is blocked on, and the sketch above deliberately stops short of
naming a default.

## Consequences

- Nothing is implementable from this record while it is `Proposed`. That is intended.
- Once unblocked: the decision will express depth as profiles, correlate with W3C Trace
  Context, and handle content under ADR-0025's controls. Everything past that is
  undetermined by design.
- The machine-readable CLI contract, which is itself an agent contract, stays stable.
- Expressing depth as profiles keeps one vocabulary with ADR-0026 instead of two.

## Security implications

CLI arguments, stdin/stdout, repository paths, keys, auth challenges, and subprocess
output may be sensitive. Content handling defers wholly to ADR-0025's control set rather
than restating a stricter-sounding rule that would conflict with it. Because this record is
blocked, no exposure changes on its account; the assessments in #474–#476 include the
safety boundaries that must inform the eventual profile set.

## Supersedes

none

## Provenance

Drafted by an agent from #492's options. The decision is pending both a human and the
evidence in #474–#476, as stated at the top of *Decision*; an earlier version of this
record asserted an outcome despite the standing instruction on #492 not to, and that is
withdrawn. Full alternatives remain in #492.
