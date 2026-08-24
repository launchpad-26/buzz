---
status: Accepted
date: 2026-08-22
issue: launchpad-26/buzz#489
decided_in: launchpad-26/buzz#489
supersedes: none
---

# ADR-0024 — Use W3C Trace Context for cross-runtime correlation

## Decision

W3C Trace Context is Buzz's primary correlation mechanism. Each user-initiated or scheduled operation starts or continues one trace, and Buzz propagates that context across every technically controllable boundary.

Traces carry causal flow. Logs remain a separate OpenTelemetry signal and include `trace_id` and `span_id` when an active span exists. Metrics remain a separate signal and use exemplars where they materially help move from an aggregate symptom to a representative trace.

Unavoidable propagation breaks are documented explicitly. Buzz does not replace trace propagation with account pubkeys, member identity, or another universal identity join.

## Context

The motivating failure in PRD #289 crosses a client, relay admission, room state, successful peers, dependency operations, and client presentation. Similar paths cross desktop parent and frontend processes, ACP and agent subprocesses, MCP tools, Git helpers, background workers, and external-service adapters. Independently generated component identifiers cannot reliably reconstruct those operations.

Account or device identity would provide a durable join, but it would not express causal order and would create unnecessary tracking and disclosure risk. W3C Trace Context is the OpenTelemetry-compatible mechanism designed for causal propagation across process and network boundaries.

## Consequences

**Good.** One operation can be followed across Buzz-controlled runtimes and asynchronous work without relying on timestamps or a participant's memory.

**Good.** Logs and metrics remain useful for startup, crashes, background health, rates, saturation, and operations without an active trace while still linking to traces when possible.

**Bad.** Nostr events, subprocess protocols, persisted work, and delayed jobs do not all carry W3C headers naturally. Implementations must define safe propagation carriers or record a bounded context break.

**Bad.** Trace context alone does not identify the affected member, build, environment, or session. Those remain scoped OpenTelemetry resource and span attributes, not substitutes for causal context.

## Security implications

Trace identifiers can join activity across systems and become sensitive operational metadata. They must not encode user identity or secrets, and access and retention must follow the telemetry data they correlate. Propagation must accept only valid bounded context and must not treat externally supplied trace context as authorization or trust evidence.
