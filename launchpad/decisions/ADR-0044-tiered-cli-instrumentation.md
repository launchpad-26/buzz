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

### Draft shape

Instrumentation depth is expressed as **preset profiles**, which is the mechanism ADR-0026
already fixed: *"When enabled, configuration uses preset profiles rather than individual or
granular signal-level toggles."* Earlier drafts of this record spoke only of "tiers" and
never mentioned profiles, which left an implementer with two governing nouns and no
mapping. There is one noun: a profile. A "tier" in the sketch below is a profile, and the
profile set itself is what #474–#476 must inform.

- **Baseline profile.** Every first-party CLI emits structured command outcomes, correlated
  using **W3C Trace Context** (`traceparent`), which `ADR-0024-w3c-trace-context-correlation.md`
  makes *"Buzz's primary correlation mechanism"* and which forbids substituting another
  universal identity join. Earlier drafts said "propagated correlation IDs", which did not
  name the mandated mechanism.
- **Traced profile.** Spans and metrics are added where lifecycle or latency evidence needs
  them.

Graduation from baseline to traced requires at least one of the following, each stated so
it can be decided rather than argued:

- the command supervises a subprocess whose expected wall-clock exceeds **30 seconds**
  (earlier drafts said "long-lived", which set no threshold);
- the command holds or presents a credential, or performs a relay administrative
  operation; or
- an operator has filed a diagnosis request naming the command and the missing signal, and
  no existing baseline outcome answers it. This replaces "end-to-end diagnosis with no
  other signal", which was unfalsifiable — another signal can always be claimed to exist.

**Content rules, aligned with ADR-0025 rather than against it.** The existing
machine-readable CLI output contract is preserved and never weakened. Telemetry content
follows `ADR-0025-controlled-free-text-telemetry.md`, which permits free text as a
*"required diagnostic capability"* subject to its named controls: explicit field
classification, secret and credential filtering before the export boundary, size limits
with a visible truncation marker, restricted and audited access, defined retention, and
contributor consent. What is prohibited under every profile is what ADR-0025 prohibits —
*"[p]rivate keys, authentication tokens, raw environment variables, and binary
attachments"* — plus any unclassified or unfiltered field. An earlier draft of this record
said "no raw user content is exported", which reads as forbidding the evidence ADR-0025
requires; that wording is withdrawn.

**Scrubbing is a profile requirement, not a deferred obligation.** Span data on the
administrative surface is exported only after credential filtering, per ADR-0025. An
earlier draft deferred this onto graduation criteria that did not contain it.

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
- Once unblocked: complete outcomes and correlation joins for every command; spans only
  where they earn their cost.
- Decidable graduation criteria stop teams under-instrumenting high-risk administrative or
  subprocess operations, and stop the criteria being arguable in review.
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
