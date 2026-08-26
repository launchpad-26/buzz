# Current observability overview

> Current-state documentation tracked by
> [issue #457](https://github.com/launchpad-26/buzz/issues/457).

## Purpose and scope

This overview gives operators, contributors, and agents a single, time-constrained account
of what can be observed in Buzz today. It explains which signals the product currently
emits or exposes, what context survives after a fault, how activity can be correlated
across component boundaries, and which diagnostic questions the available evidence can
and cannot answer. The [coverage inventory](coverage.md) is the canonical stage-1
completeness record; the component deep dives remain the source for current evidence.

The scope is the current product-observability boundary of the Buzz relay, the desktop
client—including its native Tauri process and frontend—and the browser web client. It
covers instrumentation, emitted signals, health and diagnostic surfaces, error context,
correlation identifiers, persistence, export boundaries, and verified sensitive-data
risks. The [coverage inventory](coverage.md) is the canonical component assignment and
assessment-progress record; it does not claim that pending component assessments are
complete. Mobile observability is excluded by
[PRD #289](https://github.com/launchpad-26/buzz/issues/289).

This is a vendor-neutral description of current behavior, not a target architecture. It
distinguishes signals emitted by Buzz from the external collection, storage, and
operational systems that may consume them. Future instrumentation, platform design, and
policy decisions are outside this document. Where the completed research does not
establish an answer, the gap remains explicit.

## System and component boundaries

This documentation groups current observability by three in-scope product runtime
containers:

- The [relay](relay.md) is the shared server boundary. It accepts client connections,
  authenticates and routes activity, runs features such as huddles, and exposes
  process-side telemetry and health surfaces.
- The [desktop client](desktop.md) spans two local runtimes: the native Tauri process and
  the frontend running inside its webview. A failure visible to one desktop user may
  originate in either runtime, at their boundary, or in an interaction with the relay.
- The [web client](web.md) runs in the browser. Its observable state is constrained by
  the browser runtime and by the transport boundary between the browser and relay.

This is a runtime-container grouping, not a claim that Buzz has only three internal
components. The relay contains protocol ingress, authentication, event handling,
subscriptions, huddles, workflows, Git, media, persistence adapters, and operational
surfaces; desktop and web likewise contain multiple feature and transport components.
Buzz also depends on PostgreSQL, Redis, object storage, peer services, and agent
subprocesses. Their internal observability is outside these product-runtime deep dives.
Mobile is part of the wider product but explicitly outside PRD #289.

The three documented runtimes do not currently form a single observability system. Each
determines what it emits, which context is available, and whether output can leave or
survive the process. External collection, storage, querying, dashboards, and operational
deployment begin after the product export boundaries and are not treated as product
instrumentation.

Boundaries matter diagnostically. A signal present in one component does not establish
that the corresponding client or server activity can be found in another, and output
that is emitted but neither retained nor exported is unavailable for later investigation.
The following sections describe those handoffs at overview level; the linked component
documents contain the detailed evidence.

## High-level instrumentation approach

Buzz does not currently use one instrumentation model across its in-scope runtime
containers:

- The [relay](relay.md#instrumentation-mechanisms) writes structured JSON logs, creates
  explicit HTTP, WebSocket-operation, and datastore spans, exposes Prometheus metrics,
  and serves health and status endpoints. Its optional OpenTelemetry path exports spans
  and in-span events, not logs or metrics.
- The [desktop client](desktop.md#instrumentation-mechanisms) uses free-text native
  stdout/stderr, frontend console calls, transient user-facing errors, and live Tauri
  state. Managed-agent subprocesses have a separate file-log path. The desktop installs
  no active tracing subscriber, span exporter, metrics recorder, or frontend telemetry
  SDK.
- The [web client](web.md#instrumentation-mechanisms) has one application-authored
  console error plus path-specific promise, query, toast, and inline-error handling. It
  has no shared logger, global error capture, spans, metrics, or telemetry exporter.

These mechanisms were built for different local purposes. Signal presence in one
runtime does not imply equivalent coverage, retention, or correlation in another.

## Signal types

| Signal | Relay | Desktop | Web |
|---|---|---|---|
| Logs | Structured JSON on stdout; in-span events can also enter exported traces. | Free-text native stdout/stderr, frontend console records, and retained managed-agent child logs. | One raw console-error path; no shared logging layer. |
| Errors | Structured events and span status on instrumented paths; free-text messages and errors also exist. | Native errors, transient toasts, root render recovery, and live feature state; most are not retained. | Selected query, invite, and repository errors reach UI or console; no global runtime-error capture. |
| Traces | Optional OTLP/gRPC span export; 51 span names were observed at the default filter in the completed exercise. | No active spans or trace exporter. | No spans or trace exporter. |
| Metrics | Prometheus counters, gauges, and histograms on a dedicated listener. | No verified client-process metrics surface. | No client metrics, Web Vitals, or performance telemetry. |
| Health and diagnostics | Liveness, dependency-aware readiness, service status, mesh status, and aggregate metrics. | Relay/huddle/agent live state and managed-agent records; no client-wide health contract. | Tab-local loading/error state and browser DevTools; no client health contract. |

The table records verified presence and absence, not complete feature coverage.
Successful huddles, many relay error paths, representative client failures, production
builds, and deployed collection were not comprehensively exercised.

## Cross-component correlation

Correlation is strongest inside an instrumented relay operation. Relay JSON lines can
carry `trace_id` and `span_id`, while `conn_id`, subscription ID, event ID, channel ID,
pubkey, and timestamps support domain joins. WebSocket operations on one connection
share `conn_id` but are separate root traces.

Desktop and web clients also carry domain identifiers in product traffic and live state:
signed event IDs and pubkeys, subscription IDs, relay and channel identifiers, and
timestamps. Desktop huddle state adds parent and ephemeral channel IDs, participant
pubkeys, and a thread event ID. These values can support a manual comparison over a
small incident window.

There is no distributed trace across the components. Neither client sends W3C trace
context and the relay does not extract it. Relay-generated connection and trace IDs are
not returned to the clients. Context also breaks inside the relay when upgraded or
spawned work has no active span; huddle join events therefore remain uncorrelated stdout
records despite carrying useful domain context on many paths.

## Current monitoring and diagnostic capability

The relay provides the only persistent-query-capable product signals, and only when an
external system captures them. Its health surfaces can distinguish process response from
dependency readiness; spans can follow selected authentication, HTTP, WebSocket, and
datastore operations; and metrics can show aggregate rates and latency. Relay stdout can
explain several huddle admission failures by member, channel, and reason if that stream
was retained.

Desktop diagnostics are mostly live and local. Connection and huddle state can identify
the current phase of a failure, and managed-agent status plus retained child logs can
support after-the-fact investigation. Packaged macOS native stdout/stderr was observed
going to `/dev/null`; frontend console records and dismissed errors have no application
record.

Web diagnosis is limited to the open tab. Visible errors, the one console path, and
DevTools network inspection can help reproduce selected repository, invite, or Nostr
failures. They cannot provide historical, aggregate, cross-user, or client-to-relay
diagnosis.

Consequently, a human or agent can investigate selected relay-side behavior and retained
managed-agent failures today. The current product cannot reliably retrieve a frontend
error after dismissal, compare participating clients after the event, or reconstruct one
end-to-end operation across client and relay.

## Vendor-neutral export boundaries

The current product exposes separate export boundaries:

- Relay logs leave through stdout; spans can leave through optional OTLP/gRPC export;
  metrics are scraped from a dedicated Prometheus endpoint; health and status are
  synchronous HTTP responses.
- Desktop native output can reach an invoking terminal but was discarded in the measured
  packaged macOS launch. Frontend records remain in the live webview inspector.
  Managed-agent child output and selected agent state can persist in app-data files.
  The desktop has no product telemetry exporter.
- Web signals remain in browser memory, rendered UI, console, and DevTools. Its HTTP and
  WebSocket traffic is product traffic, not telemetry, and no telemetry ingest request
  exists.

These boundaries describe how a signal can leave its product runtime. Collection,
durable storage, querying, access control, retention, and deployment begin outside them.
The checked-in fork configuration does not establish that relay stdout, spans, or
metrics are collected in a deployed environment.

## Privacy and security

The current diagnostic surfaces already contain data that would require deliberate
handling if collected:

- Relay fields include full pubkeys, client socket addresses, community hostnames,
  correlating event/channel/session identifiers, infrastructure paths, and unbounded
  error, message, and subprocess-stderr text.
- Desktop native and frontend diagnostics can include pubkeys, domain identifiers,
  filesystem paths, arbitrary error objects, and unbounded managed-agent child output.
  The existing encrypted-key egress guard covers declared relay product paths, not an
  undeclared telemetry path or raw `nsec`.
- Web product and diagnostic surfaces contain routes, invite and repository identifiers,
  Nostr events and signatures, public keys, filters, content, signed HTTP authorization,
  and raw third-party error objects. A credential embedded in browser code would be
  visible to that runtime.

The absence of a client telemetry pipeline limits off-machine disclosure today but does
not make local consoles, discarded output, or retained files safe by construction.
This document records the verified exposure surfaces; it defines no filtering, access,
or retention policy.

## Known gaps

- **Verified limitation — no unified system:** relay, desktop, and web signals use
  separate mechanisms, destinations, and lifetimes.
- **Verified limitation — client history:** packaged desktop native output and both
  clients' frontend errors generally cannot be recovered after the relevant process,
  tab, inspector, or toast is gone.
- **Verified limitation — client telemetry:** desktop and web create no spans or
  client-process metrics and have no telemetry exporter.
- **Verified limitation — correlation:** there is no propagated trace identity across
  client and relay. Domain identifiers permit only manual, path-dependent joins.
- **Verified limitation — relay coverage:** huddle join events have no active span;
  several exits lack member attribution or fall below the default filter. Other spawned
  work can have the same export gap.
- **Verified limitation — collection is not retention:** relay output can cross product
  boundaries, but the repository does not establish that deployed storage preserves it.
- **Unknown — installed clients:** the completed inventory did not establish which build
  every participating member runs, and this fork had no packaged desktop distribution
  path at the evidence cutoff.
- **Unknown — participating platforms:** only one macOS x86_64 machine was recorded;
  packaged Linux and Windows behavior was not tested.
- **Unknown — deployed configuration:** live relay filters, resource attributes,
  collector state, proxy/browser policy, and persistence were not inspected.
- **Unknown — unexercised behavior:** representative concurrency, many relay and client
  failure paths, production browser behavior, and complete sensitive free-text contents
  remain outside the completed evidence.

## Component deep dives

- [Canonical coverage inventory](coverage.md)
- [Relay](relay.md)
- [Desktop](desktop.md)
- [Web](web.md)

## Verification metadata

- Repository revision:
  [`678008ea49e790ada52e84d54b47f47dd77c6b38`](https://github.com/launchpad-26/buzz/tree/678008ea49e790ada52e84d54b47f47dd77c6b38)
- Evidence cutoff date: 2026-08-22
- Verification methods: controlled relay and collector exercises; trace-payload and
  wire-volume inspection; reproducible huddle admission runs; packaged macOS descriptor
  and file inspection; a bounded browser error exercise; pinned source and dependency
  inspection; and synthesis of the component deep dives. No deployed relay, complete
  participating-machine inventory, or new overview-specific experiment was used.
- Evidence sources: [relay](relay.md#evidence-and-verification-metadata),
  [desktop](desktop.md#evidence-and-verification-metadata), and
  [web](web.md#evidence-and-verification-metadata) deep dives, with their linked completed
  research and revision-pinned implementation evidence.
