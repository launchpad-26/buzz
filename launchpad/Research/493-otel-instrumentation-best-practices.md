# OpenTelemetry instrumentation best practice for Buzz

**Title:** OpenTelemetry instrumentation best practice and Buzz applicability map

**Summary:** Current OpenTelemetry best practice is trace-first, not trace-only: use spans for causal operations, correlated logs for lifecycle and witnessed errors, bounded metrics for aggregate behavior, Resources for producer identity, W3C Trace Context for controllable boundaries, links for fan-out and batch causality, and bounded fail-open export. Stable HTTP, service, PostgreSQL, core signal, and propagation contracts can be treated as durable inputs. Browser, messaging, CLI, app/session, subprocess-carrier, GenAI-agent, and MCP guidance is still Development or Release Candidate and must be pinned and reviewed rather than promoted silently.

**Tags:** `observability` `opentelemetry` `tracing` `logs` `metrics` `semantic-conventions` `context-propagation` `buzz`

**Evidence cutoff:** 2026-08-22

**Governing repository revision:** `26920e5c30d8a07a3d59c306d4e2b9056750e762`

**Answers:** [launchpad-26/buzz#493](https://github.com/launchpad-26/buzz/issues/493) under [PRD #289](https://github.com/launchpad-26/buzz/issues/289)

---

## Bottom line

For Buzz, "OpenTelemetry best practice" means one vendor-neutral evidence model, not one mandatory SDK topology and not "emit every signal everywhere." Traces carry causal flow; logs preserve lifecycle, untraced activity, and safe error evidence; metrics describe aggregate rates, latency, errors, saturation, drops, and exporter health; Resources identify the emitting runtime; exemplars connect useful aggregate measurements to representative sampled traces. This is the trace-first model accepted by [ADR-0023](../decisions/ADR-0023-use-opentelemetry-conventions.md) and [ADR-0024](../decisions/ADR-0024-w3c-trace-context-correlation.md), not a trace-only model.

The most durable OpenTelemetry inputs at the cutoff are the stable core APIs and SDK contracts, the stable log data model, stable Resource model, stable service identity, stable HTTP spans, stable PostgreSQL client spans, stable metric cardinality and exemplar behavior, and the OpenTelemetry requirement to use W3C Trace Context Level 2 in its W3C propagator. Other official guidance is useful but not equally binding: messaging, browser, CLI, app/session, Redis, object-store, SDK self-observability, GenAI-agent, and MCP conventions remain Development; process and RPC conventions and environment-variable propagation are Release Candidate.

Buzz should therefore apply stable conventions directly where they fit, pin and review unstable conventions where they are the best available model, and create no Buzz-specific convention until implementation proves a concrete representational gap. The only evidenced gaps at this stage are named later; this research does not design their wire formats or choose exporters, collectors, stores, dashboards, or a platform.

## Scope and method

This is standards research and an applicability map. It does not inventory current Buzz instrumentation; that is [issue #462](https://github.com/launchpad-26/buzz/issues/462). Runtime names below are coverage boundaries supplied by PRD #289 and issue #493, not a claim that every executable, route, method, or worker has already been enumerated.

Mobile is excluded by the accepted PRD scope. This artifact makes no mobile recommendation even where an official convention groups mobile, web, and desktop applications together.

The primary baseline is:

- OpenTelemetry Specification **1.60.0**, tag `v1.60.0`, commit `29ae8c7710d2ea52e21a5ff81fb1cd657bcd3306`.
- OpenTelemetry Semantic Conventions **1.44.0**, tag `v1.44.0`, commit `e10a930844c6951757a43b849d364f7d056ac32b`.
- OpenTelemetry GenAI Semantic Conventions at cutoff commit `55a32cddb97d99cec08d5ee081e74206a0636041`, committed 2026-08-21. This separate official repository has no stable version used here, so every GenAI and MCP claim is treated as Development guidance retrieved 2026-08-22.
- W3C Trace Context Level 2 Candidate Recommendation (18 April 2023), plus the OpenTelemetry 1.60.0 requirement that its W3C propagator implement Level 2.
- Official OpenTelemetry browser and JavaScript documentation retrieved 2026-08-22 where the versioned specifications do not define browser SDK maturity or delivery constraints.

Tagged GitHub sources are used for normative claims so the cited text cannot drift after the evidence cutoff. Mutable official documentation is cited only with an explicit retrieval date.

## Governing constraints preserved

- **[ADR-0023](../decisions/ADR-0023-use-opentelemetry-conventions.md):** use OpenTelemetry APIs, SDKs, protocols, and semantic conventions as the canonical observability model; do not create a parallel Buzz telemetry schema.
- **[ADR-0024](../decisions/ADR-0024-w3c-trace-context-correlation.md):** use W3C Trace Context across every technically controllable boundary, correlate logs with trace/span IDs, and use exemplars for trace-to-metric navigation. A context break must be explicit and bounded.
- **[ADR-0025](../decisions/ADR-0025-controlled-free-text-telemetry.md):** classify, filter, bound, and mark truncation before the product export boundary. Prohibited content remains prohibited in every profile; a convention's existence is not permission to collect its field.
- **[ADR-0026](../decisions/ADR-0026-fail-open-telemetry-export.md):** observability is fail-open and bounded, signal loss is made visible, security audit durability stays separate, and configuration is presented through an off state plus preset profiles rather than independent per-signal switches.

These are accepted constraints, not decisions reopened by the maturity findings below. This research neither selects the profile contents nor changes the mobile exclusion.

## How claims are classified

**Normative OTel requirement** means an RFC 2119/8174 requirement in the versioned OpenTelemetry specification. It normally constrains an OTel API, SDK, exporter, or conforming instrumentation. It becomes a Buzz requirement only when Buzz adopts or implements that surface.

**Stable convention** means the cited semantic-convention group or field is Stable in Semantic Conventions 1.44.0. Stable instrumentations must not emit unstable parts by default, while stable groups cannot regress to a lower maturity level. [Semantic Conventions 1.44.0, group stability][semconv-groups]

**Experimental guidance** is the issue's umbrella term for official material whose current OTel maturity is Development, Alpha, Beta, or Release Candidate. OpenTelemetry renamed "Experimental" to "Development"; Development signals may change, be incomplete, or be removed, and long-term dependencies should not be taken on them. [OpenTelemetry 1.60.0, versioning and stability][otel-stability]

**Local recommendation** is this research's application of the evidence and accepted ADRs to Buzz. It is not an OpenTelemetry requirement and does not finalize the desired state, implementation, profile, or platform.

**Deferred or uncertain** marks a question owned by current-state, desired-state, profile, or implementation work. It is not permission to invent an answer in this task.

## Source-backed signal model

### Traces and spans

**Normative OTel requirements.** A span represents one operation, has at most one parent, may contain attributes, timestamped events, links, and status, and must be ended after creation. Span names should identify a low-cardinality class of operation rather than an individual instance. Attributes and links relevant to head sampling should be supplied at span creation, because later additions may not affect the sampling decision. [OpenTelemetry 1.60.0, Tracing API §§ Span, Span Creation, Links][otel-trace-api]

**Stable guidance.** Use the applicable domain convention before defining a local shape. HTTP client and server spans are Stable and require low-cardinality method/target naming; instrumentation must not default to a raw URI path as the target. PostgreSQL client spans are Stable and use stable database operation, namespace, response, server, and error attributes, while query parameters remain Development and opt-in. [Semantic Conventions 1.44.0, HTTP spans][semconv-http] [Semantic Conventions 1.44.0, PostgreSQL][semconv-postgresql]

**Local recommendation.** Create spans for diagnosically significant operations with duration or cross-boundary work, not every function. One logical operation should not be double-instrumented at adjacent abstraction layers. Prefer stable protocol conventions and generic OTel span primitives over speculative `buzz.*` attributes. Exact span boundaries and names belong to issues #477-#480 after #462 and the current-state assessments.

### Logs and standalone events

**Stable OTel model.** An OTel LogRecord can carry event and observed timestamps, trace ID, span ID, trace flags, severity, body, Resource, instrumentation scope, attributes, and event name. A non-empty event name makes the record an OTel Event. If a span context is active, the Logs SDK must populate trace-context fields from that context. [OpenTelemetry 1.60.0, Logs Data Model][otel-logs-model] [OpenTelemetry 1.60.0, Logs SDK § ReadableLogRecord][otel-logs-sdk]

**Normative OTel behavior.** Trace-based log filtering defaults to false; when false, log records must not be dropped merely because their trace is unsampled. This makes logs an independent signal rather than a trace attachment. [OpenTelemetry 1.60.0, Logs SDK § LoggerConfig][otel-logs-sdk]

**Local recommendation.** Use structured log events for startup and shutdown, connection and session lifecycle, state transitions, background activity without an active span, product-visible exporter degradation, and the exact safe error evidence that must outlive a transient UI. When a span is active, correlate with `trace_id` and `span_id`; do not duplicate an exception at every layer. Logs remain subject to ADR-0025's field classification, filtering, size bounds, truncation marker, and absolute prohibited-content list.

### Metrics

**Stable OTel model.** Synchronous instruments record measurements inline and can associate them with Context. OTel's "asynchronous instruments" are callback-based metric instruments; the term is unrelated to asynchronous application execution, and their measurements cannot be associated with Context. Counters represent non-negative additive change, histograms represent distributions, UpDownCounters represent additive change in either direction, and gauges represent current non-additive values. [OpenTelemetry 1.60.0, Metrics API §§ Synchronous and Asynchronous instruments, Counter, Histogram, Gauge, UpDownCounter][otel-metrics-api]

**Normative OTel behavior.** Metric SDKs should support a hard aggregation-cardinality limit; overflow is aggregated into the `otel.metric.overflow=true` series and measurements must not be double-counted or dropped because of cardinality overflow. Metric callbacks should not run indefinitely, and SDK implementations should apply a callback timeout. [OpenTelemetry 1.60.0, Metrics SDK §§ Observations inside asynchronous callbacks, Cardinality limits][otel-metrics-sdk]

**Local recommendation.** Product metrics should cover aggregate operation counts, latency distributions, errors, current load or saturation, queue pressure, dropped telemetry, and exporter health. Keep metric attributes bounded and exclude event IDs, trace IDs, session IDs, pubkeys, channel IDs, repository paths, prompts, error messages, and other unbounded values. Put trace correlation in exemplars, not metric attributes.

### Resources and instrumentation scope

**Normative and stable OTel behavior.** A Resource is an immutable representation of the entity producing telemetry. The Stable service entity requires `service.name`; Stable `service.version` is recommended. A Stable service instance uses `service.instance.id`, which must be unique within its service namespace/name and should be treated as potentially confidential operational identity. [OpenTelemetry 1.60.0, Resource SDK][otel-resource-sdk] [Semantic Conventions 1.44.0, service Resources][semconv-service]

**Experimental guidance.** Process Resources are Release Candidate within an overall Development document. Browser Resources, the app entity (`app.build_id`, `app.installation.id`), and session conventions are Development. The app convention prohibits using hardware identifiers as `app.installation.id`. [Semantic Conventions 1.44.0, process Resources][semconv-process] [Semantic Conventions 1.44.0, browser Resources][semconv-browser] [Semantic Conventions 1.44.0, app entity][semconv-app] [Semantic Conventions 1.44.0, sessions][semconv-session]

**Local recommendation.** Every emitting Buzz runtime needs stable logical service identity and build/version context. Runtime-instance, installation, device, client, and session identity must be scoped to the narrowest useful signal and reviewed for consent, privacy, persistence, and cardinality. Do not decide the exact resource names or whether Development app/session fields are enabled until desired-state work can compare the runtimes.

## Correlation and context

### W3C Trace Context

**Normative OTel requirement.** OTel propagators inject and extract cross-cutting context through a carrier. Extraction of malformed values must not throw or overwrite an existing valid Context. OTel instrumentation libraries should call configured propagators on remote calls. The OTel W3C propagator must parse and validate `traceparent` and `tracestate` according to W3C Trace Context Level 2 and propagate valid values. [OpenTelemetry 1.60.0, Propagators API][otel-propagators]

**Standards maturity.** W3C Trace Context Level 2 is a Candidate Recommendation, not a W3C Recommendation at the cutoff. Its privacy rules prohibit personally identifiable or sensitive information in `traceparent` or `tracestate`, and its security guidance warns that blindly honoring an externally supplied sampled flag can create cost and denial-of-service risk. [W3C Trace Context Level 2, 18 April 2023][w3c-trace-context-2]

**Local recommendation fixed by ADR-0024.** Each user-initiated or scheduled operation starts or continues one trace, and W3C Trace Context propagates across every technically controllable Buzz boundary. Incoming context is correlation data only: it is not authentication, authorization, trust, tenant identity, or proof that work belongs to a user. At an external trust boundary Buzz may validate, limit, ignore sampling pressure, or deliberately restart context, but the behavior must be documented and must not encode identity into new trace IDs.

### In-process asynchronous work

**Normative OTel model.** Context is immutable and carries execution-scoped values between logically associated execution units. Attach returns a token that restores the prior Context on detach. [OpenTelemetry 1.60.0, Context API][otel-context]

**Local recommendation.** Capture the relevant Context when work is scheduled, make it current only for that work, and restore the previous Context afterwards. Use a child span for one causal continuation. Use a link when work is delayed, batched, fan-out/fan-in, has multiple causal inputs, or already has a different valid ambient parent. A timer or worker with no causal predecessor starts a new trace. Long-lived workers should not keep one unbounded lifetime span; lifecycle belongs in logs and bounded metrics, while each unit of work gets its own operation span.

### Messaging, fan-out, and Nostr events

**Experimental guidance.** Messaging semantic conventions 1.44.0 are Development. They recommend attaching a creation context to each message, do not specify the carrier, and use span links as the default producer/consumer correlation because batches and fan-out cannot fit a single-parent tree. Receive/process spans must not be created for prefetched messages until the message is actually forwarded to application code. [Semantic Conventions 1.44.0, messaging spans][semconv-messaging]

**Local recommendation.** Treat the messaging model as the best current analogy for Nostr event production, relay processing, delivery, and subscription fan-out, not as proof that Nostr is an OTel `messaging.system`. Use links for one-to-many delivery, batches, replay, and work with multiple inputs. Do not mint a `messaging.system=nostr` value or a Buzz-specific event schema in this research.

**Deferred or uncertain.** Semantic Conventions 1.44.0 contain no general WebSocket or Nostr convention; a repository search found only technology-specific WebSocket mentions under .NET SignalR/Kestrel material. Nostr event tags are signed and persisted product data, while PRD #289 explicitly says correlation must not require a backend-specific identifier in permanent Nostr events. Desired-state work must therefore distinguish ephemeral envelopes, connection context, per-message context, links, and an explicitly bounded context break without selecting a wire change here.

### Span events, links, and exceptions

**Normative OTel model.** Span events are timestamped named annotations with attributes. Links relate a span to another SpanContext in the same or another trace; links available at span creation should be supplied then so a sampler can consider them. Recording an exception creates an `exception` span event but does not itself set span status. [OpenTelemetry 1.60.0, Tracing API §§ Add Events, Link, Record Exception][otel-trace-api]

**Stable and experimental error guidance.** The Stable exception convention says an unhandled exception that causes the operation to fail should be recorded as an `exception` event and uses the stable exception attribute set. The cross-signal "Recording errors" guidance is Development: successful operations leave status unset; failed operations should set `Error` and a predictable, low-cardinality `error.type`; handled/retried errors should not mark the enclosing successful operation as failed. [Semantic Conventions 1.44.0, exceptions][semconv-exceptions] [Semantic Conventions 1.44.0, recording errors][semconv-errors]

**Local recommendation.** Use span events for meaningful point-in-time occurrences within an operation, not for every debug statement. Record an error once at the layer that owns its outcome, preserve a stable machine-readable `error.type` or domain status, and add controlled free text only where ADR-0025 permits it. A retry attempt may have its own failed span while the enclosing logical operation succeeds; the parent operation must describe its own final outcome.

### Span status

**Normative OTel requirement.** Span status defaults to `Unset`. Status description is valid only with `Error`. Instrumentation generally should not set `Ok`; it should leave status `Unset` unless semantic conventions classify the operation as an error. [OpenTelemetry 1.60.0, Tracing API § Set Status][otel-trace-api]

**Stable protocol guidance.** HTTP server 4xx responses remain unset by default because they represent a client-side error, while HTTP 5xx responses should be `Error`; HTTP client interpretation differs. The convention also distinguishes caller cancellation from an error. [Semantic Conventions 1.44.0, HTTP spans § Status][semconv-http]

**Local recommendation.** Define success and failure per operation and protocol, not by log severity or the mere presence of an error-looking message. Keep status description bounded and safe; use `error.type` and protocol status fields for classification rather than copying arbitrary exception text.

### Baggage

**Normative OTel model.** Baggage is a stable, application-defined set of key/value pairs that may propagate across arbitrary boundaries. The API must provide a way to clear all baggage before sending to an untrusted process. [OpenTelemetry 1.60.0, Baggage API][otel-baggage-api]

**Official security guidance.** Baggage is not automatically a span, log, or metric attribute; instrumentation must copy it deliberately. It has no built-in integrity guarantee and can be exposed to unintended downstream services. [OpenTelemetry baggage documentation, retrieved 2026-08-22][otel-baggage-docs]

**Local recommendation.** Do not use baggage for pubkeys, member identity, auth state, tokens, prompts, file paths, repository content, raw event data, or another universal Buzz join. Default to no Buzz baggage. If a later concrete use survives threat modelling, allowlist the key and destination and clear it at trust boundaries. Trace Context alone carries causal identity.

### Sampling

**Normative OTel model.** Trace sampling controls whether spans record and/or export. `IsRecording` governs whether span data is retained by processors; the propagated sampled flag communicates the recording decision to descendants. Samplers can consider only data available at span creation. [OpenTelemetry 1.60.0, Tracing SDK § Sampling][otel-trace-sdk]

**Local recommendation.** Keep parent-aware decisions consistent across Buzz-controlled runtimes, but do not trust an unauthenticated upstream sampled flag as authority to spend unbounded resources. Put stable low-cardinality sampling-relevant fields and causal links on the span at creation. Because failures are often known only at span end, head sampling alone cannot guarantee retention of every failed operation; correlated logs and aggregate metrics remain necessary.

**Deferred.** This research selects no algorithm, rate, tail-sampling component, per-runtime override, or profile. Profile contents remain owned by #492 after current-state evidence, and the shared desired-state contract belongs to #477. The Logs SDK's default of no trace-based filtering should be preserved unless a later explicit policy provides equivalent durable error evidence.

### Exemplars

**Stable OTel behavior.** Exemplars are sampled measurements that add specific context to an aggregate metric. A synchronous measurement can carry the active trace and span IDs; SDKs must provide exemplar sampling hooks, should enable exemplar sampling by default, and should default the eligibility filter to trace-based sampling. [OpenTelemetry 1.60.0, Metrics SDK § Exemplar][otel-metrics-sdk]

**Local recommendation.** Use exemplars where a latency, error, saturation, or drop distribution benefits from a direct jump to a representative trace. Do not place trace IDs in metric attributes. An asynchronous metric instrument cannot associate its callback measurement with Context, so it should not be assumed to provide trace-linked exemplars.

## Client and process guidance

### Browser clients

**Experimental guidance.** The official JavaScript documentation says traces and metrics are Stable and logs are Development in the JS implementation, but client instrumentation for browsers is experimental and mostly unspecified. Browser Resource conventions are also Development. [OpenTelemetry JavaScript status, retrieved 2026-08-22][otel-js-status] [OpenTelemetry browser guide, retrieved 2026-08-22][otel-js-browser]

**Official delivery constraints.** Browser OTLP export cannot use gRPC; HTTP/protobuf or HTTP/JSON is required. CSP and CORS can block export, and a public web application may force its receiver surface to be publicly reachable. [OpenTelemetry JavaScript exporters, retrieved 2026-08-22][otel-js-exporters]

**Local recommendation.** Instrument browser work deliberately rather than assuming server auto-instrumentation covers it. Fetch can use W3C headers when browser policy permits. The browser WebSocket API cannot set arbitrary upgrade headers, so that boundary needs another explicit, safe carrier or a documented break. Export route, authentication, receiver exposure, and transport deployment belong to buzz-infrastructure#113; Buzz owns what the browser emits, its safety controls, and its disabled/failure behavior.

### Desktop native and frontend clients

**Experimental guidance.** OTel provides a Development app entity for mobile, web, and desktop applications, Development session conventions, Development browser entities for browser-hosted code, and Release Candidate process identity. It does not provide a Stable desktop-application convention in 1.44.0. [Semantic Conventions 1.44.0, app entity][semconv-app] [Semantic Conventions 1.44.0, sessions][semconv-session] [Semantic Conventions 1.44.0, process Resources][semconv-process]

**Local recommendation.** Treat desktop native Rust and frontend webview code as distinct instrumentation scopes and potentially distinct SDK/resource producers even where they share an OS process. Cross-runtime causal flow over Tauri commands, events, and channels needs explicit injection/extraction rather than an assumption that language-local Context crosses the bridge. Build, installation, instance, client, and session fields need consent and stability review before adoption; exact identities are deferred.

### Subprocesses and command-line programs

**Experimental guidance.** The environment-variable carrier specification is Release Candidate. Its normative carrier rules keep propagation format-agnostic; its non-normative spawning guidance recommends copying the parent environment, injecting into the copy, and extracting at child startup. It warns that environment variables are inappropriate for sensitive information. [OpenTelemetry 1.60.0, environment-variable carriers][otel-env-carriers]

**Experimental guidance.** CLI semantic conventions are Development and apply to short-lived programs, with execution/caller spans and exit-code-based error treatment. Process command arguments should not be collected by default unless sanitized. [Semantic Conventions 1.44.0, CLI spans][semconv-cli]

**Local recommendation.** Use an explicit per-invocation carrier for each child. An environment copy is the best current official startup mechanism when no protocol field exists, but a long-lived ACP, agent, MCP, or backend subprocess needs request-level propagation in its own protocol rather than one startup context reused forever. Never export the raw environment. Command arguments, cwd, stdout, stderr, prompts, tool input, and tool output remain controlled or prohibited content under ADR-0025.

### Agents, model calls, and MCP

**Experimental guidance at an exact cutoff commit.** Official OpenTelemetry GenAI agent, model, tool, and MCP conventions are all Development at commit `55a32cddb97d99cec08d5ee081e74206a0636041`. The MCP convention recommends MCP-specific spans over generic RPC spans, uses `params._meta` for configured propagators on individual requests/notifications, and treats transport context as independent from MCP request context. Tool arguments and results are opt-in and explicitly marked potentially sensitive. [OpenTelemetry GenAI agent spans, cutoff commit][genai-agent-spans] [OpenTelemetry GenAI spans, cutoff commit][genai-spans] [OpenTelemetry MCP conventions, cutoff commit][genai-mcp]

**Local recommendation.** Treat these as the leading official vocabulary for Buzz agent invocations, model calls, tool execution, and MCP client/server operations, but pin the adopted revision and do not promise stable field names. Avoid duplicate spans where agent/tool and MCP instrumentation describe the same execution. ADR-0025 is stricter than "opt-in": prompts, responses, tool arguments/results, and subprocess output may cross the product export boundary only through classified, filtered, bounded fields, and prohibited content never may.

## Buzz boundary applicability map

The map below identifies the standards fit and correlation shape. "Product" means Buzz-controlled code or configuration at the product export boundary. "Infrastructure" means launchpad-26/buzz-infrastructure#113 after that boundary.

### Relay request and realtime boundaries

**Relay HTTP ingress, generic bridge endpoints, webhooks, health, media, and Git smart HTTP.** Apply Stable HTTP server conventions to the HTTP request itself, use W3C headers directly, and preserve protocol/domain outcomes as structured attributes or events without raw route cardinality. Product owns extraction, span lifetime, safe fields, and downstream injection. Infrastructure owns collection and presentation. Whether every health probe should trace is a desired-state signal-depth question, not decided here. [Semantic Conventions 1.44.0, HTTP spans][semconv-http]

**Relay HTTP clients and peer/dependency HTTP calls.** Apply Stable HTTP client conventions and inject configured W3C context. Separate the logical call from individual retries where the applicable convention requires it. Product owns client-side outcome, timeout, retry, and correlation; the called service's internals remain outside PRD #289.

**WebSocket upgrade and connection lifecycle.** The upgrade is HTTP and can carry direct W3C headers when the client API exposes them. The upgraded connection and frames lack a general OTel WebSocket convention. Use generic spans/events and stable network attributes only where applicable; do not declare a local stable schema. A long-lived connection should use lifecycle logs and metrics plus bounded operation spans rather than one unbounded active span. Browser handshake propagation remains a bounded uncertainty because arbitrary headers are unavailable.

**Nostr EVENT, REQ, COUNT, subscriptions, fan-out, replay, and huddle messages.** The Development messaging model supplies the causal analogy: creation context, producer/consumer work, and links for fan-out/batches. It does not supply a Nostr carrier or stable Nostr attribute set. Product desired-state work must decide which ephemeral message families can carry context and where permanent signed events or incompatible peers require a documented break. Pubkeys, account identity, and timestamps may aid diagnosis but do not replace W3C causality under ADR-0024.

### Relay asynchronous and dependency boundaries

**Background tasks, workflows, timers, queues, and spawned work.** Capture Context at scheduling; create a bounded per-work-item span; use links for delayed, batched, replayed, or multi-source work; start a new trace for independent periodic work. Lifecycle and liveness use logs and metrics. Product owns propagation into work and truthful drop/failure signals. Infrastructure owns retention, alerting, and worker dashboards.

**PostgreSQL adapter.** Stable PostgreSQL client spans apply directly. Product owns logical operation, duration, outcome, pool wait/timeout where representable, safe query summary/text, and caller correlation. PostgreSQL server telemetry is infrastructure-owned and out of scope. ADR-0025 may require stricter query-text handling than the semantic convention permits. [Semantic Conventions 1.44.0, PostgreSQL][semconv-postgresql]

**Redis adapter and pub/sub.** Redis-specific conventions are Development even though the shared database span convention is Stable; Redis pub/sub may also resemble Development messaging conventions. Product desired-state work must choose the applicable official model per operation without double-counting. Redis server health and exporter configuration are infrastructure-owned. [Semantic Conventions 1.44.0, Redis][semconv-redis]

**Object storage, peer relays, RPC, model providers, and other adapters.** Use Stable HTTP when it describes the wire call; apply domain conventions only at their published maturity. Object-store conventions are Development, RPC is Release Candidate, and GenAI is Development. Product owns Buzz's side of duration, result, timeout, retries, safe target identity, and context; external internals and platform monitoring remain outside this PRD. [Semantic Conventions 1.44.0, object stores][semconv-object-store] [Semantic Conventions 1.44.0, RPC][semconv-rpc] [OpenTelemetry GenAI spans, cutoff commit][genai-spans]

### Desktop and web boundaries

**Desktop native runtime.** Use stable service/resource identity, native operation spans, structured logs, bounded metrics, and direct W3C propagation on controllable network requests. Product owns local exporter status and consent-aware client fields. Packaged-client transport, endpoint credentials, collection, and retention are infrastructure-owned.

**Desktop frontend and webviews.** Use browser/JavaScript guidance knowingly as experimental, correlate render, interaction, request, and user-visible error evidence, and pass explicit Context across Tauri IPC. Frontend logs remain independent of trace sampling. Do not assume console output is an export or that frontend Context crosses into Rust automatically.

**Browser web client.** Fetch supports direct W3C propagation subject to browser policy; WebSocket upgrade headers do not. Browser instrumentation and Resources are Development, and export is limited to browser-compatible HTTP with CSP/CORS constraints. Product owns safe signal generation and failure behavior; infrastructure owns any receiving route, authentication, rate limiting, TLS, storage, and access.

### Agent, MCP, and first-party tool boundaries

**ACP harness.** Continue the initiating trace into each ACP operation through an explicit protocol carrier. Use a startup carrier only for process creation, not for all later requests. Represent async notifications or multi-source work with links where a single parent would be false. The exact ACP carrier is deferred because no Stable ACP semantic convention was found.

**Buzz agent and managed-agent runtime.** Give each invocation or scheduled run a bounded root/continued operation, preserve Context through model and tool calls, and use Development GenAI conventions only with a pinned revision. Logs cover lifecycle and untraced failures; metrics cover aggregate invocation latency, errors, tool counts, saturation, and drops. Content fields remain controlled by ADR-0025.

**Developer MCP client/server and tools.** The official Development MCP convention is directly relevant, including independent MCP-versus-transport context and request-level propagation. Avoid duplicate tool spans when another layer already owns the operation. Product desired-state work must decide whether to adopt the current `params._meta` guidance and how to version it; this research does not change the protocol.

**Managed subprocesses and repository operations.** Use a separate child environment or protocol carrier per invocation, span the bounded execution, capture exit status and safe error classification, and restore the parent's Context. Raw argv, environment, paths, stdout, and stderr are not safe by default. Process-internal telemetry belongs to that child when Buzz controls it; Buzz's caller span still owns the observed child outcome.

**First-party CLI, admin, Git helpers, pairing CLI/relay, backend provider, and other shipped helpers.** Short-lived commands can use the Development CLI model; network calls propagate W3C directly where the protocol allows; subprocess calls use an explicit carrier. Long-lived pair relays and backend providers are services/workers rather than CLI executions. Exact executable coverage and distribution status belong to #462/#476, not this map.

## Exporter failure and telemetry self-observation

**Normative OTel requirements.** OTel implementations must not throw unhandled runtime exceptions or cause the application to fail because an exporter cannot reach its destination. Export calls must have a reasonable upper time bound. Built-in batch span and log processors have bounded queues and drop new telemetry once `maxQueueSize` is reached; a failed final export drops the batch. OTLP exporters must retry transient failures with exponential backoff and jitter. [OpenTelemetry 1.60.0, error handling][otel-error-handling] [OpenTelemetry 1.60.0, Tracing SDK §§ Batching processor, Span Exporter][otel-trace-sdk] [OpenTelemetry 1.60.0, Logs SDK §§ Batching processor, LogRecordExporter][otel-logs-sdk] [OpenTelemetry 1.60.0, OTLP exporter § Retry][otel-otlp-exporter]

**Experimental guidance.** SDK self-observability is Development. The current Development SDK metric conventions define queue size/capacity, processor results, inflight records, exporter outcomes, and export duration for traces, logs, and metric data points. [OpenTelemetry 1.60.0, self-observability][otel-self-observability] [Semantic Conventions 1.44.0, OTel SDK metrics][semconv-sdk-metrics]

**Local recommendation fixed by ADR-0026.** Buzz product work always continues when export is disabled, unavailable, backpressured, misconfigured, or failing. Buffers and retry state are bounded; excess telemetry is dropped safely and counted. Exporter health, queue pressure, and signal loss need a local observation path that does not depend exclusively on the failing exporter. No failure path may spill telemetry into an unclassified file or unrestricted stdout. Security audit records retain their separate durability contract.

**Deferred.** Exact buffer sizes, retry budgets, shutdown flush behavior, local diagnostic surfaces, on/off profile defaults, and signal depth vary by runtime and SDK and belong to #477-#480 and #492. Infrastructure #113 owns receiver availability and observability-platform monitoring; product code still owns fail-open behavior up to its export boundary.

## Cross-cutting safety and cardinality rules

- **Local recommendation:** Treat all propagated context as untrusted input. Validate format and bounds, never use it for authorization, and do not let an incoming sampled flag force unbounded work. [OpenTelemetry 1.60.0, Propagators API][otel-propagators] [W3C Trace Context Level 2, Security Considerations][w3c-trace-context-2]
- **Local recommendation:** Use low-cardinality operation names and `error.type`; place event, channel, session, trace, tool-call, and request identifiers on spans or controlled logs only when diagnostically necessary, never as metric attributes.
- **Local recommendation:** Apply ADR-0025 before the product export boundary. OTel's existence of an attribute is not a safety approval. Private keys, auth tokens, raw environment variables, and binary attachments remain prohibited under every profile.
- **Local recommendation:** Treat URLs, query text, user-agent strings, command arguments, paths, prompts, responses, tool arguments/results, exception messages, and stack traces as potentially sensitive or unbounded. Prefer templates, summaries, types, codes, counts, and explicit classified content fields.
- **Normative/Stable basis:** Attribute, event, and link limits are SDK concerns; metric cardinality overflow has defined Stable behavior. Product schemas should nevertheless avoid generating unbounded values rather than relying on truncation or overflow after the fact. [OpenTelemetry 1.60.0, Tracing SDK § Span Limits][otel-trace-sdk] [OpenTelemetry 1.60.0, Metrics SDK § Cardinality limits][otel-metrics-sdk]

## Product and infrastructure ownership

### Buzz product ownership

- Signal selection, operation boundaries, span lifecycle, safe structured logs, product metrics, Resources, and semantic-convention versioning.
- W3C extraction/injection and explicit carriers across controllable HTTP, IPC, protocol, messaging, worker, and subprocess boundaries.
- Error classification and safe preservation of witnessed product errors.
- Product-side filtering, truncation, content classification, cardinality control, consent controls, and prohibited-content enforcement.
- Explicit telemetry on/off behavior, bounded queues and retry state, dropped-signal accounting, and a non-exclusive local view of exporter degradation.
- A documented vendor-neutral export contract and truthful behavior when export is absent or broken.

### buzz-infrastructure#113 ownership

- Receiver and collector selection, deployment, availability, and self-monitoring.
- Telemetry transport outside the product exporter, endpoint exposure, TLS, credentials, and platform access control.
- Storage, retention, deletion enforcement after export, querying, presentation, dashboards, alerts, and alert-to-issue automation.
- Host, container, PostgreSQL server, Redis server, object-storage server, ingress, DNS, firewall, and platform monitoring.

### Contract boundary

Product and infrastructure must agree on supported vendor-neutral signal/transport contracts, limits, authentication handoff, and failure semantics. That agreement does not move content classification or fail-open behavior out of the product, and it does not move collector/storage design into this issue.

## Evidenced gaps, uncertainties, and downstream owners

1. **No general WebSocket or Nostr convention in Semantic Conventions 1.44.0.** This is a concrete standards gap, not evidence that Buzz needs a new schema. Owner: #477/#478/#479 for desired-state treatment; a new extension or ADR only if implementation later proves the existing general primitives inadequate.
2. **Messaging guidance is Development and deliberately leaves the carrier unspecified.** It supplies link and trace-shape guidance but not a Nostr wire answer. Owner: #481 for end-to-end correlation after runtime desired states.
3. **Browser instrumentation is experimental and mostly unspecified.** Fetch, WebSocket, CSP/CORS, public receiver exposure, and exporter maturity differ from server runtimes. Owner: #479 for product requirements; infrastructure #113 for delivery architecture.
4. **Desktop app, browser, and session identity conventions are Development; process and environment-carrier conventions are Release Candidate.** Exact client/installation/session identity and subprocess propagation remain version-sensitive and privacy-sensitive. Owner: #477/#479/#480.
5. **GenAI-agent and MCP conventions are Development at a cutoff commit, not a stable version.** They are highly relevant and include sensitive opt-in content fields, but require pinning and migration review. Owner: #480.
6. **SDK self-observability names are Development.** ADR-0026 requires exporter failure and signal loss to be visible even if a runtime SDK lacks or changes those metrics. Owner: #477 and runtime desired-state issues.
7. **Sampling policy is intentionally unresolved.** Head sampling cannot select on failures discovered at span end; external sampled flags are untrusted; profiles are not yet decided. Owner: #492 for the profile decision and #477 for the shared contract after current-state evidence.
8. **Current SDK capability is unknown per runtime.** A specification requirement does not prove the Rust, JavaScript/browser, or other selected SDK version implements it. Owner: #462 and #463-#476 current-state assessments.

No new consequential decision outside the existing issue plan was discovered. The uncertainties above are already owned by current-state, profile, desired-state, or infrastructure work; this task neither resolves them nor creates an ADR.

## Inputs to later PRD #289 stages

- #477 can turn the stable core, safety, correlation, sampling, resource, and fail-open findings into the shared desired-state contract.
- #478 can apply Stable HTTP/PostgreSQL guidance and explicitly version messaging, Redis, object-store, WebSocket, Nostr, worker, and adapter treatment.
- #479 can define desktop/web evidence while preserving browser and client maturity constraints and the native/frontend/IPC boundary.
- #480 can pin Development agent, GenAI, MCP, CLI, and subprocess guidance and apply ADR-0025 before any content export.
- #481 can define direct W3C propagation, explicit carriers, links, and bounded context breaks end to end without storing backend-specific identifiers in permanent Nostr events.
- #486/#487 can sequence implementation only after the current-state and gap-analysis chain exists.

This artifact is evidence input only. It does not implement instrumentation, define final profiles, select an observability platform, or replace #462's component inventory.

## Sources

All sources below are primary OpenTelemetry or W3C sources. Versioned links are pinned; mutable documentation records the retrieval date in the label above.

[otel-stability]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/versioning-and-stability.md

[otel-trace-api]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/trace/api.md

[otel-trace-sdk]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/trace/sdk.md

[otel-logs-model]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/logs/data-model.md

[otel-logs-sdk]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/logs/sdk.md

[otel-metrics-api]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/metrics/api.md

[otel-metrics-sdk]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/metrics/sdk.md

[otel-resource-sdk]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/resource/sdk.md

[otel-context]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/context/README.md

[otel-propagators]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/context/api-propagators.md

[otel-env-carriers]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/context/env-carriers.md

[otel-baggage-api]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/baggage/api.md

[otel-error-handling]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/error-handling.md

[otel-self-observability]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/self-observability.md

[otel-otlp-exporter]: https://github.com/open-telemetry/opentelemetry-specification/blob/v1.60.0/specification/protocol/exporter.md

[semconv-groups]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/general/semantic-convention-groups.md

[semconv-service]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/resource/service.md

[semconv-process]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/resource/process.md

[semconv-browser]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/resource/browser.md

[semconv-app]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/registry/entities/app.md

[semconv-session]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/general/session.md

[semconv-http]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/http/http-spans.md

[semconv-errors]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/general/recording-errors.md

[semconv-exceptions]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/exceptions/exceptions-spans.md

[semconv-messaging]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/messaging/messaging-spans.md

[semconv-postgresql]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/db/postgresql.md

[semconv-redis]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/db/redis.md

[semconv-object-store]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/object-stores/README.md

[semconv-rpc]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/rpc/rpc-spans.md

[semconv-cli]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/cli/cli-spans.md

[semconv-sdk-metrics]: https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/otel/sdk-metrics.md

[genai-agent-spans]: https://github.com/open-telemetry/semantic-conventions-genai/blob/55a32cddb97d99cec08d5ee081e74206a0636041/docs/gen-ai/gen-ai-agent-spans.md

[genai-spans]: https://github.com/open-telemetry/semantic-conventions-genai/blob/55a32cddb97d99cec08d5ee081e74206a0636041/docs/gen-ai/gen-ai-spans.md

[genai-mcp]: https://github.com/open-telemetry/semantic-conventions-genai/blob/55a32cddb97d99cec08d5ee081e74206a0636041/docs/gen-ai/mcp.md

[w3c-trace-context-2]: https://www.w3.org/TR/2023/CR-trace-context-2-20230418/

[otel-baggage-docs]: https://opentelemetry.io/docs/concepts/signals/baggage/

[otel-js-status]: https://opentelemetry.io/docs/languages/js/

[otel-js-browser]: https://opentelemetry.io/docs/languages/js/getting-started/browser/

[otel-js-exporters]: https://opentelemetry.io/docs/languages/js/exporters/
