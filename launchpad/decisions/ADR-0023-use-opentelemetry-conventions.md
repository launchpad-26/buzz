---
status: Accepted
date: 2026-08-22
issue: launchpad-26/buzz#488
decided_in: launchpad-26/buzz#488
supersedes: none
---

# ADR-0023 — Use OpenTelemetry conventions for all Buzz instrumentation

## Decision

Buzz product instrumentation uses OpenTelemetry conventions for traces, logs, metrics, resources, errors, and context propagation.

Buzz will not define a parallel product-specific telemetry schema in advance. When implementation encounters a concrete concept that OpenTelemetry does not represent adequately, that gap will be addressed then with the smallest necessary extension or follow-up decision. Hypothetical gaps do not justify a second convention.

This is a semantic and interoperability decision, not a requirement that every runtime emit every OpenTelemetry signal. Signal requirements and instrumentation depth remain owned by the desired-state work under PRD #289.

## Context

PRD #289 covers relay, desktop, web, ACP, agent, MCP, and first-party tool runtimes. A shared convention is required if their evidence is to compose into one diagnosable operation. Defining Buzz-specific conventions before current-state and desired-state assessment would duplicate an established standard, create translation work, and commit the project to maintaining two semantic models.

OpenTelemetry already provides the common data model and conventions needed for service identity, spans, logs, metrics, errors, resources, and W3C Trace Context. The project should use those capabilities directly and evaluate exceptions only against observed needs.

## Consequences

**Good.** Instrumentation has one standard vocabulary and remains compatible with vendor-neutral OpenTelemetry tooling.

**Good.** Implementers do not spend current-state or strategy work designing speculative Buzz-specific attributes.

**Bad.** OpenTelemetry conventions will not describe every future Buzz product concept perfectly. A real gap may require a narrowly scoped extension or later ADR.

**Bad.** Convention changes upstream may require compatibility or migration work. Instrumentation reviews must distinguish stable conventions from experimental ones.

## Security implications

Using a standard schema does not make emitted values safe. Every field still requires classification, bounded cardinality, and the free-text controls decided separately in ADR-0025. OpenTelemetry exporters remain an exfiltration boundary; credentials, keys, and prohibited content must not be emitted merely because a standard attribute exists.
