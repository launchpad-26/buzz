---
status: Accepted
date: 2026-08-22
issue: launchpad-26/buzz#491
decided_in: launchpad-26/buzz#491
supersedes: none
---

# ADR-0026 — Fail open when telemetry export is unavailable

## Decision

Buzz product operations continue when telemetry export is disabled, unavailable, backpressured, misconfigured, or failing.

Telemetry buffering is bounded. When the bound is reached, excess telemetry is dropped safely and counted. Exporter health, buffer pressure, and signal loss must be observable without requiring the failing export path itself to report them exclusively.

Security audit records retain their separate durability contract and are not weakened by this decision.

Telemetry has an explicit on/off control. When enabled, configuration uses preset profiles rather than individual or granular signal-level toggles. The exact profiles, defaults, and signal depth are not decided here; issue #492 remains blocked on the current-state assessments needed to establish viable profiles.

## Context

A collector, network path, exporter, or local buffer can fail independently of Buzz. Failing product operations because the diagnostic path is unavailable would turn an observability incident into a product outage. Buffering indefinitely would defer the outage until memory or disk is exhausted and would retain sensitive telemetry without a defensible bound. Silently disabling export would preserve availability while hiding evidence loss.

The product therefore needs an explicit availability contract: continue serving, bound resource use, and make degradation visible. Operators and participating contributors also need a comprehensible configuration surface. Preset profiles provide a reviewable combination of cost, content, and diagnostic depth; per-signal toggles would create untestable configurations and inconsistent evidence.

## Consequences

**Good.** Collector or network failure does not stop messaging, huddles, agents, Git operations, or other Buzz product behavior.

**Good.** Buffer and drop accounting makes evidence loss explicit and bounded.

**Good.** Preset profiles provide a small set of supportable configurations instead of a combinatorial signal matrix.

**Bad.** Fail-open behavior accepts that diagnostic evidence can be lost during an observability outage. An incident may therefore remain partially unexplained.

**Bad.** Exporter health needs an observation path that does not depend solely on the exporter being healthy. Each runtime may have different viable local diagnostics.

**Bad.** Profile definition remains unresolved until current-state assessment completes. Implementations must not invent incompatible profile names or contents in the interim.

## Security implications

Bounded buffering limits denial-of-service and retention exposure. No failure mode may spill telemetry into an unclassified fallback file or unrestricted stdout. Turning export off must be explicit and observable locally, but must not reveal telemetry content. Preset profiles remain subject to ADR-0025: no profile may export private keys, authentication tokens, raw environment variables, or binary attachments.
