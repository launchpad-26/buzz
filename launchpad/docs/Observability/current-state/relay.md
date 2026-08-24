# Relay observability — current state

> Current-state documentation tracked by
> [issue #458](https://github.com/launchpad-26/buzz/issues/458).

## Component scope and runtime

This page covers the `buzz-relay` server process: from process startup and configuration
through the work it performs for connected clients. That runtime accepts WebSocket and
HTTP traffic, authenticates and routes client activity, executes relay-side feature work
such as huddles, and runs background tasks. The scope includes diagnostic and monitoring
signals produced by that work, including signals emitted from asynchronous tasks owned by
the relay process.

The responsibility boundary ends where work leaves the relay process. Client-side
behavior belongs to the [desktop](desktop.md) and [web](web.md) deep dives. PostgreSQL,
Redis, object storage, peer relays, and any external telemetry system are separate
runtimes: this page covers what the relay records about its interactions with them, but
not their internal observability. Collection, storage, querying, dashboards, and
deployment are likewise outside the relay runtime unless they affect whether a
relay-produced signal crosses its export boundary.

This boundary is about runtime ownership rather than source-directory ownership.
Supporting Buzz crates execute inside the relay process, so signals they emit while
serving relay work are in scope. Conversely, a signal concerning relay activity is not
treated as relay telemetry when it exists only in a client or an external service.

## Instrumentation mechanisms

The relay uses four independent mechanisms. They do not form one pipeline:

1. `tracing` events and spans feed a JSON formatting layer that writes structured logs
   to standard output. `RUST_LOG` controls this layer and defaults to
   `buzz_relay=info`.
2. The same tracing registry can attach an OpenTelemetry layer. It exports spans and
   in-span events over OTLP/gRPC only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set;
   otherwise initialization is a no-op. `BUZZ_OTEL_FILTER`, separately from
   `RUST_LOG`, controls this layer and defaults to
   `buzz_relay=info,buzz_datastore=info`.
3. The `metrics` facade records counters, gauges, and histograms. A Prometheus exporter
   exposes them as text on a dedicated HTTP listener, configured by
   `BUZZ_METRICS_PORT` and defaulting to port `9102`.
4. Application and probe routers expose synchronous health and status responses.

Instrumentation is mixed. HTTP middleware creates `http.request` spans, the main
WebSocket path creates explicit per-operation `ws.auth`, `ws.event`, `ws.req`, and
`ws.count` spans, and datastore methods use generated client spans. Other paths emit
structured events without creating or inheriting a span. This distinction determines
whether an event can become part of an exported trace.

## Emitted signals

### Logs

The standard-output surface is newline-delimited JSON with timestamp, level, target, and
message. Events inside a span also carry the current span fields; when OTLP is enabled,
correlated lines include `trace_id` and `span_id`. Bare events still reach standard
output, but have no trace identifiers.

### Traces

At the default OTLP filter, a live exercise observed **51 distinct span names**. Of
1,015 captured spans, 989 were datastore spans; four background pollers accounted for
84% of the sample. Relay operation spans carry fields such as `conn_id`, `sub_id`,
`event_id`, event `kind`, and HTTP method. Structured log events emitted inside those
spans become span events, which is where fields including `pubkey`, `channel_id`,
channel `name`, route, status, and result counts appeared.

The observed resource contained only `service.name=buzz-relay`. The runtime exercise did
not establish a complete span-name inventory for every relay feature or failure path.
It did establish that OTLP carries traces only: no log records or metric points were
received through this exporter.

At zero connected clients, [the measured default-filter rate](https://github.com/launchpad-26/buzz/issues/312)
was approximately **1.71 spans and 598 uncompressed wire bytes per second**, or
**51.66 MB per day**. Three background Postgres polling calls produced 87.6% of the
idle spans. The measurement used a local debug relay with one community; it did not
exercise a huddle, representative cohort concurrency, or the deployed relay.

### Metrics

The metrics listener exposes Prometheus counters, gauges, and histograms. Framework
metrics include HTTP request counts and latency by bounded status, caller, and matched
route labels; health, metrics, and unmatched paths are excluded from that middleware.
Buzz-specific metrics are recorded at their feature call sites. This page does not claim
that every metric family or feature path was exercised by the completed research.

### Health and status signals

The relay exposes simple health and liveness responses, dependency-aware readiness,
service status, and mesh status. These are request/response state surfaces rather than
stored telemetry.

## Export boundaries

Standard-output JSON leaves the process through its stdout stream whenever the relay
runs; persistence depends on whatever launches and captures that stream. There is no
product-side OTLP log exporter.

Traces leave through the optional OTLP/gRPC span exporter. A controlled run at revision
`678008ea49e790ada52e84d54b47f47dd77c6b38` set
`OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4317` and delivered 152 spans in 41
batches with no export errors. Leaving the variable unset disables this path.
`BUZZ_OTEL_FILTER` controls which targets and levels enter it.

Metrics leave through `GET /metrics` on the dedicated metrics listener. Health and
status data leave through HTTP responses on the application router or the separate
health listener. These are independent boundaries: enabling trace export does not
export logs or metrics, and scraping metrics does not retain logs or traces.

The fork's Compose configuration sets the health and metrics ports but does not set an
OTLP endpoint or filter. The completed research did not verify a deployed relay
environment, TLS export, a release build, or external persistence of any surface.

## Health and monitorability

The application router exposes `/health`, `/_liveness`, and `/_readiness`.
`/health` and `/_liveness` return `200 ok` without dependency checks.
`/_readiness` returns ready only when the relay is not shutting down and PostgreSQL,
Redis, and the community-deletion serving catalog pass checks within two seconds; its
failure response names which check failed.

A separate health-only listener exposes `/_liveness`, `/_readiness`, `/_status`, and
`/_mesh` without the application router's metrics, tracing, authentication, or CORS
middleware. `/_status` reports service name, package version, and process uptime.
`/_mesh` distinguishes mesh disabled from enabled status. The current Compose
healthcheck uses the dedicated `/_readiness` endpoint.

These surfaces can answer whether the process responds, whether its checked dependencies
permit serving, how long this process instance has run, and whether mesh is enabled.
They do not establish that a user workflow succeeds, that background workers are
healthy, that clients can connect from their networks, or that emitted telemetry is
being retained. Dedicated health probes themselves produce no trace or HTTP request
metric through the application middleware.

## Diagnostic use cases

Current relay telemetry can support several bounded investigations:

- A NIP-42 authentication or Nostr request can be followed through an operation span
  into its datastore child spans. Authentication success records the connection,
  event, and member pubkey.
- HTTP bridge activity can expose method plus in-span events for route, status, result
  count, accepted event kind, and event identifiers.
- A datastore failure can set an OTLP error status without exporting SQL, bind
  parameters, the database URL, or the error text in the datastore span.
- The reproducible huddle membership fault produces a relay stdout event containing
  `channel_id`, the rejected member's `pubkey`, and the denial reason, while successful
  joins produce comparable member and peer-index context.
- Metrics can establish aggregate request rates, latency, and feature-specific
  operational counts where the relevant call sites emit them.

The huddle example also shows the limit. Its join events are useful in stdout, but the
audio connection runs without an active span, so those events are not exported through
OTLP and have no trace identifiers. Some rejection exits lack a member identifier, and
four are below the default filter. A later investigation therefore depends on stdout
having been retained and on the exercised exit carrying sufficient context.

## Correlation and context

Within an exported relay operation, `trace_id` and `span_id` connect JSON log lines to
their OTLP span. `conn_id` links authentication, request, count, and event operations
belonging to the same WebSocket connection, although those operations are separate root
traces rather than children of one connection trace. `sub_id`, `event_id`, `kind`,
`channel_id`, `pubkey`, and timestamps provide progressively more domain-specific joins.

No W3C trace-context propagator is configured. HTTP and WebSocket-upgrade headers reach
relay handlers, but the relay does not extract a caller's `traceparent`; Nostr WebSocket
messages have no header surface. Consequently, current client and relay traces are not
joined by propagated trace identity. For the huddle case, stdout events can often be
compared by pubkey, channel, and time, but this is a data join rather than distributed
trace propagation.

Context also breaks inside the relay. An HTTP upgrade span ends with the upgrade
response, and work in a bare spawned task does not inherit it. The main Nostr WebSocket
path restores visibility by creating per-operation spans; the huddle path does not.
Events outside any span remain uncorrelated stdout records.

## Sensitive-data handling

The current surfaces contain identifying and potentially sensitive values. A source
classification of 130 relay field keys found:

- 15 keys that can directly identify a person or endpoint, including full Nostr
  pubkeys, client socket addresses, and community hostnames;
- 34 pseudonymous identifiers—including connection, event, channel, community, session,
  and repository identifiers—that become identifying when joined with relay data;
- four infrastructure-address or filesystem-path fields;
- ten unbounded or mixed free-text fields, plus the formatter's `message`, whose contents
  cannot be proven safe from their key or type.

The most open-ended surfaces are interpolated log messages, `error`, and up to 64 KiB of
raw Git subprocess `stderr`. User-controlled channel names, event `d` tags, ref names,
and some reason fields are also free text. The completed source review found no field
that carries a database connection string, authentication token, private key, or
environment dump by construction; arbitrary error and subprocess text remain paths by
which such data could appear.

Existing datastore-span instrumentation deliberately omits SQL, bind parameters, DSNs,
and error contents. Metric label values are mostly closed sets, but the `community`
label is a hostname. No redaction, collection, access, or retention policy is defined
here.

## Known gaps

- **Verified limitation — huddle trace gap:** join-path events are written to stdout but
  do not reach OTLP because the upgraded connection runs without an active span.
- **Verified limitation — incomplete huddle attribution:** 8 of 17 failure exits carry
  the joiner's pubkey; the pre-auth failure and several other exits cannot identify the
  affected member. Four exits are below the default OTLP filter.
- **Verified limitation — operation roots:** WebSocket authentication, request, count,
  and event spans share `conn_id` but use separate trace IDs. There is no connection
  root span.
- **Verified limitation — no distributed context:** the relay extracts no incoming
  trace context from HTTP or WebSocket-upgrade headers.
- **Verified limitation — split signals:** OTLP exports spans only, metrics use a
  Prometheus listener, and logs use stdout. No product mechanism retains all three.
- **Verified limitation — health coverage:** probe success does not exercise a user
  workflow or demonstrate that telemetry export and retention work.
- **Verified limitation — default-filter noise:** idle background polling dominates the
  measured trace volume.
- **Unknown — deployed configuration:** the completed research did not establish the
  deployed relay's filters, resource attributes, release-build behavior, TLS exporter
  behavior, or whether any stdout and metrics surfaces are currently collected.
- **Unknown — unexercised paths:** successful huddles, many relay features, error and
  rejection paths, mesh operation, representative concurrency, and exporter behavior
  under load were outside the recorded runtime exercises.
- **Unknown — free-text contents:** source establishes that error, message, and
  subprocess-output fields are unbounded, but no production values were inspected.

## Evidence and verification metadata

- Repository revision:
  [`678008ea49e790ada52e84d54b47f47dd77c6b38`](https://github.com/launchpad-26/buzz/tree/678008ea49e790ada52e84d54b47f47dd77c6b38)
- Evidence cutoff date: 2026-08-22
- Verification methods: controlled local relay and OTLP-collector runs; collector span
  counters and raw payload inspection; wire-byte measurement; reproducible huddle
  admission exercises; source and dependency inspection. No deployed relay was
  inspected.
- Research evidence: [OTLP delivery #309](https://github.com/launchpad-26/buzz/issues/309),
  [runtime span inventory #310](https://github.com/launchpad-26/buzz/issues/310),
  [field classification #311](https://github.com/launchpad-26/buzz/issues/311),
  [volume measurement #312](https://github.com/launchpad-26/buzz/issues/312),
  [huddle reproduction #313](https://github.com/launchpad-26/buzz/issues/313),
  [huddle attribution #314](../../../Research/314-huddle-join-attribution.md), and
  [trace propagation #323](../../../Research/323-trace-context-propagation.md).
- Pinned implementation evidence:
  [`telemetry.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/telemetry.rs),
  [`metrics.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/metrics.rs),
  [`router.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/router.rs),
  [`connection.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/connection.rs), and
  [`audio/handler.rs`](https://github.com/launchpad-26/buzz/blob/678008ea49e790ada52e84d54b47f47dd77c6b38/crates/buzz-relay/src/audio/handler.rs).

Back to the [overview](overview.md). See also [desktop](desktop.md) and [web](web.md).
