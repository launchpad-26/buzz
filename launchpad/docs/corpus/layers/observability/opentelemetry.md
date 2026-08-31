---
id: layers-observability-opentelemetry
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "crates/buzz-relay/src/telemetry.rs's module doc comment describes the wiring as: the `tracing` crate dispatches spans/events to two layers — an always-on `fmt::layer().json()` layer writing to stdout, and an `OpenTelemetryLayer` attached only when an OTLP endpoint env var is set — with the OTEL path flowing through an `SdkTracerProvider` and a batch OTLP exporter to a collector or Datadog Agent; when the endpoint env var is unset the module states it is a no-op and no OTLP connection is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:1-25"
  - statement: "`try_init_tracer` in telemetry.rs checks `std::env::var(\"OTEL_EXPORTER_OTLP_ENDPOINT\")`; if that variable is unset (`.is_err()`), it returns `TracerInit::Disabled` immediately without building any exporter or provider."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:238-247"
  - statement: "When the endpoint variable is set, `try_init_tracer` builds an `opentelemetry_otlp::SpanExporter` via `.with_tonic().build()` and passes the result to `classify_exporter_result`, which on `Ok` constructs an `SdkTracerProvider` with `.with_resource(resource).with_batch_exporter(exporter)`, registers it as the global tracer provider via `opentelemetry::global::set_tracer_provider`, and returns `TracerInit::Enabled(provider)`; on `Err` it returns `TracerInit::ExporterBuildFailed(e.to_string())` without ever installing a provider."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:238-268"
  - statement: "buzz-relay's `main()` builds one shared `Resource` via `telemetry::service_resource()`, calls `telemetry::try_init_tracer(resource.clone())`, derives `otel_enabled` as `matches!(&tracer_init, telemetry::TracerInit::Enabled(_))`, and — only when enabled — constructs `tracing_opentelemetry::layer().with_tracer(provider.tracer(\"buzz-relay\"))` to attach as the OTEL layer; it then installs a `tracing_subscriber::registry()` carrying three layers: the always-on JSON `fmt::layer()` (filtered by a `RUST_LOG`-driven `EnvFilter` via the file-local `log_env_filter` function), the optional OTEL layer (filtered by `telemetry::otel_env_filter(BUZZ_OTEL_FILTER)`), and a `TraceContextLookup` layer forced to `LevelFilter::OFF` (used only to resolve span IDs to OTEL contexts for the JSON formatter, never to emit its own events)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:96-143"
  - statement: "A `TracerInit::ExporterBuildFailed` outcome is logged via `tracing::warn!(error = %e, ...)` only after `tracing_subscriber::registry()...init()` has run in `main()`, because `try_init_tracer` is deliberately documented as never calling `tracing::warn!` internally — the subscriber may not be installed yet at the point the exporter is built, which would silently drop the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:145-148"
      - "crates/buzz-relay/src/telemetry.rs:232-237"
  - statement: "`telemetry::otel_env_filter` builds an `EnvFilter` from the `BUZZ_OTEL_FILTER` environment variable, falling back to `\"buzz_relay=info,buzz_datastore=info\"` when unset; this filter governs only spans/events exported through the OTEL layer and is deliberately independent from the `RUST_LOG`-driven filter on the stdout JSON layer, specifically so that changing stdout log verbosity cannot remove parent spans from an exported trace."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:178-185"
  - statement: "`telemetry::service_resource` derives the OTEL `Resource`'s `service.name` by reading `OTEL_SERVICE_NAME` (using it only if set and non-empty, otherwise falling back to the literal `\"buzz-relay\"`), then builds the `Resource` with that name and overlays `EnvResourceDetector::new()`, which reads `OTEL_RESOURCE_ATTRIBUTES` and is documented to apply last — so a `service.name` set via `OTEL_RESOURCE_ATTRIBUTES` overrides `OTEL_SERVICE_NAME`, per the function's own doc comment explaining this ordering choice explicitly (avoiding `SdkProvidedResourceDetector`, which would read `OTEL_SERVICE_NAME` but always emit a `service.name` key and clobber the fallback)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:187-217"
  - statement: ".env.example documents `BUZZ_OTEL_FILTER` and `OTEL_EXPORTER_OTLP_ENDPOINT` together under a \"Logging / Tracing\" heading, both commented out (OTEL export disabled) by default for local development, with an inline comment on `OTEL_EXPORTER_OTLP_ENDPOINT` stating \"leave unset to disable\"."
    entry_class: FACT
    evidence:
      - ".env.example:174-183"
  - statement: "The workspace root Cargo.toml pins `tracing-opentelemetry = \"0.33\"`, `opentelemetry = \"0.32\"` (feature `trace`), `opentelemetry_sdk = \"0.32\"` (features `trace`, `rt-tokio`), and `opentelemetry-otlp = \"0.32\"` (`default-features = false`, features `trace`, `grpc-tonic`, `tls-ring`) — meaning the OTLP exporter is gRPC-only (via tonic) and TLS is backed by the `ring` crypto provider, not an HTTP/protobuf exporter."
    entry_class: FACT
    evidence:
      - "Cargo.toml:87-90"
  - statement: "Grepping every crate's Cargo.toml in this repository for the string \"opentelemetry\" returns matches in exactly two files: crates/buzz-datastore-tracing/Cargo.toml and crates/buzz-relay/Cargo.toml, so buzz-relay is the only binary in the workspace with the OTEL SDK wiring described in this node; buzz-datastore-tracing's dependency backs a separate proc-macro instrumentation layer (issue #1136's territory), not the exporter/subscriber wiring this node covers."
    entry_class: FACT
    evidence:
      - "grep(pattern='opentelemetry', glob='crates/*/Cargo.toml') -> crates/buzz-datastore-tracing/Cargo.toml, crates/buzz-relay/Cargo.toml"
  - statement: "crates/buzz-relay/src/telemetry.rs's own module doc comment (lines 20-24) lists `OTEL_TRACES_SAMPLER` (default `parentbased_always_on`) and `OTEL_TRACES_SAMPLER_ARG` as \"standard OTEL env vars honoured\", but neither name appears anywhere else in crates/buzz-relay/src/*.rs (grepped directly), and the `SdkTracerProvider::builder()` call in `classify_exporter_result` is never chained with `.with_sampler(...)` — so no code in this crate reads either variable or configures a sampler explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:20-24"
      - "crates/buzz-relay/src/telemetry.rs:253-268"
  - statement: "The pinned `opentelemetry_sdk` version resolved for buzz-relay's dependency tree is 0.32.1 (per Cargo.lock); reading that version's `trace/provider.rs` source (via docs.rs) found no reference to `OTEL_TRACES_SAMPLER` or `OTEL_TRACES_SAMPLER_ARG`, and the crate's own noop/default tracer-provider construction in that file uses `Sampler::ParentBased(Box::new(Sampler::AlwaysOn))` — matching the \"parentbased_always_on\" default the telemetry.rs comment names — but only that one file was inspected, not the whole crate, so whether some other module in `opentelemetry_sdk` performs its own env-based sampler auto-configuration was not ruled out."
    entry_class: INFERENCE
    confidence: 0.6
    evidence:
      - "https://docs.rs/opentelemetry_sdk/0.32.1/src/opentelemetry_sdk/trace/provider.rs.html"
  - statement: "telemetry.rs's own `#[cfg(test)] mod tests` block carries unit tests for the claims above: `test_service_resource_default_when_env_unset`, `test_service_resource_honors_otel_service_name` and `test_service_resource_empty_string_falls_back_to_default` pin `service_resource`'s three-tier priority order, and `test_try_init_tracer_disabled_when_endpoint_unset` plus `test_classify_exporter_result_maps_err_to_exporter_build_failed` pin the `TracerInit::Disabled` and `TracerInit::ExporterBuildFailed` outcomes deterministically, without depending on live OTLP network behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:496-540"
      - "crates/buzz-relay/src/telemetry.rs:542-579"
  - statement: "Issue #1141's parent PRD is #611, and the batch-run brief that dispatched this task names #1145 (tracing), #1136 (datastore-tracing), #1140 (metrics) and #1142 (prometheus) as sibling tasks whose trace-span, datastore-policy, and metrics content this node must not duplicate."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1141 task dispatch brief (corpus-batch-author, Feature #611 batch run)"
---

# OpenTelemetry

## Definition

**OpenTelemetry (OTEL)** in Buzz is the optional exporter mechanism that carries
`buzz-relay`'s tracing spans out of the process via OTLP gRPC, layered underneath the
always-on JSON stdout logging described by the general logging node (issue #1139,
`layers-observability-logging`). This node documents the mechanism itself — how the
OTEL layer is initialized, what exporter it configures, how its independent filter and
sampling behave, and what environment variables actually control it — not the semantic
content of any particular trace span, which is the `tracing`/`#[instrument]` layer's
own territory.

`crates/buzz-relay/src/telemetry.rs` and the OTEL-related block in
`crates/buzz-relay/src/main.rs` (`main()`, lines ~96-144) are the entirety of this
mechanism's code. `buzz-relay` is the only crate in the workspace with this wiring: a
grep of every crate's `Cargo.toml` for the string `opentelemetry` matches only
`crates/buzz-datastore-tracing` and `crates/buzz-relay` — the former is a separate
proc-macro instrumentation layer (datastore-tracing policy macros, issue #1136's
territory), not the SDK exporter/subscriber wiring this node covers.

## How it is initialized

`main()` builds one shared `Resource` (see *Resource and service name* below) and calls
`telemetry::try_init_tracer(resource.clone())` before installing any tracing
subscriber. `try_init_tracer` is gated entirely on one environment variable,
`OTEL_EXPORTER_OTLP_ENDPOINT`:

- **Unset** → returns `TracerInit::Disabled` immediately. No exporter is built, no OTLP
  connection is attempted, and the OTEL layer is simply absent from the subscriber that
  gets installed next.
- **Set** → builds an `opentelemetry_otlp::SpanExporter` via `.with_tonic().build()`
  (a gRPC exporter, per the crate's pinned features — see *What exporter is
  configured* below) and
  passes the result through `classify_exporter_result`:
  - `Ok(exporter)` → constructs an `SdkTracerProvider` with
    `.with_resource(resource).with_batch_exporter(exporter)`, registers it globally via
    `opentelemetry::global::set_tracer_provider`, and returns
    `TracerInit::Enabled(provider)`.
  - `Err(e)` → returns `TracerInit::ExporterBuildFailed(e.to_string())`. No provider is
    installed in this case.

Back in `main()`, `otel_enabled` is derived as
`matches!(&tracer_init, telemetry::TracerInit::Enabled(_))`. Only when true does it
construct the actual `tracing_opentelemetry` layer —
`tracing_opentelemetry::layer().with_tracer(provider.tracer("buzz-relay"))` — for
attachment to the subscriber. The subscriber itself is a `tracing_subscriber::registry()`
carrying three layers together:

1. The **always-on JSON stdout layer** (`fmt::layer().json()`), filtered by a
   `RUST_LOG`-driven `EnvFilter` (the file-local `log_env_filter` function in
   `main.rs`, falling back to `"buzz_relay=info"`). This layer runs whether or not OTEL
   is enabled.
2. The **optional OTEL layer**, present only when `otel_enabled`, filtered by
   `telemetry::otel_env_filter` (see *Filtering* below).
3. A **`TraceContextLookup` layer**, forced to `LevelFilter::OFF` so it never emits
   events of its own — its only job is resolving a `tracing` span ID to its
   OpenTelemetry span context so the JSON formatter can inject `trace_id`/`span_id`
   fields into stdout log lines when a valid OTEL span is active. That log/trace
   correlation is documented in depth by the logging node (issue #1139); this node
   states only that the lookup layer's presence is part of the OTEL wiring, not what
   it does with the result.

If `try_init_tracer` returned `ExporterBuildFailed`, `main()` logs it via
`tracing::warn!(error = %e, ...)` — but only *after* the subscriber has finished
installing. `try_init_tracer` deliberately never logs internally, because at the point
it runs no subscriber may exist yet, and a `tracing::warn!` call with no subscriber
installed is silently dropped.

## What exporter is configured

The only exporter this mechanism builds is `opentelemetry_otlp::SpanExporter` via
`.with_tonic()` — a gRPC OTLP exporter, matching the workspace's pinned
`opentelemetry-otlp` feature set (`grpc-tonic`, `tls-ring`, `default-features = false`
— no HTTP/protobuf exporter is compiled in). Exported spans are batch-exported
(`.with_batch_exporter(exporter)`), not sent one at a time. The destination is whatever
`OTEL_EXPORTER_OTLP_ENDPOINT` points at — a collector or Datadog Agent, per the module's
own architecture comment — and nothing in `deploy/` or the repository's
`docker-compose*.yml` files configures such a collector; standing one up is an
operator/deployment concern outside this repository's own config.

## Verification

`telemetry.rs` carries its own `#[cfg(test)] mod tests` covering the claims above
deterministically, without depending on a live OTLP network connection:
`test_service_resource_default_when_env_unset`,
`test_service_resource_honors_otel_service_name` and
`test_service_resource_empty_string_falls_back_to_default` pin the three-tier
service-name priority order from *Resource and service name*; and
`test_try_init_tracer_disabled_when_endpoint_unset` plus
`test_classify_exporter_result_maps_err_to_exporter_build_failed` pin the
`TracerInit::Disabled` and `TracerInit::ExporterBuildFailed` outcomes described in
*How it is initialized*.

## Resource and service name

`telemetry::service_resource()` builds the `Resource` attached to the tracer provider.
Its priority order, per the function's own doc comment:

1. `service.name` set via `OTEL_RESOURCE_ATTRIBUTES` — applied last by
   `EnvResourceDetector`, so it wins over everything else.
2. `OTEL_SERVICE_NAME`, read explicitly — used only when set and non-empty.
3. The hard-coded fallback `"buzz-relay"`.

The function deliberately does not use `SdkProvidedResourceDetector` (which also reads
`OTEL_SERVICE_NAME`) because that detector always emits a `service.name` key —
falling back to `unknown_service:<exe>` when unset — which would clobber the
`buzz-relay` default outright.

## Filtering — independent from `RUST_LOG`

`telemetry::otel_env_filter` builds the `EnvFilter` used for the OTEL layer from
`BUZZ_OTEL_FILTER`, falling back to `"buzz_relay=info,buzz_datastore=info"` when unset.
This is a **separate** filter from the `RUST_LOG`-driven one on the stdout JSON layer,
by design: turning stdout log verbosity up or down must not remove parent spans from
an exported trace. `.env.example` documents both variables together under a
"Logging / Tracing" heading, with `BUZZ_OTEL_FILTER` and `OTEL_EXPORTER_OTLP_ENDPOINT`
both commented out (disabled) by default for local development.

## Sampling — a documented claim this node could not confirm in code

`telemetry.rs`'s own module doc comment lists `OTEL_TRACES_SAMPLER` (default
`parentbased_always_on`) and `OTEL_TRACES_SAMPLER_ARG` among the "standard OTEL env
vars honoured." Reading the rest of the file line by line, and grepping every `.rs`
file in the crate for both names, found no other reference to either variable, and the
`SdkTracerProvider::builder()` call in `classify_exporter_result` is never chained with
`.with_sampler(...)`. **No code in `buzz-relay` reads `OTEL_TRACES_SAMPLER` or
`OTEL_TRACES_SAMPLER_ARG`, and no sampler is configured explicitly.**

The default sampler this leaves in place does appear to match the comment's claimed
default: the pinned `opentelemetry_sdk` version (0.32.1, per `Cargo.lock`) constructs
its noop/default tracer provider with
`Sampler::ParentBased(Box::new(Sampler::AlwaysOn))`, per that version's
`trace/provider.rs` source. But this node only inspected that one source file, not the
whole crate, so whether some other part of `opentelemetry_sdk` performs its own
env-based sampler auto-configuration elsewhere was not ruled out — recorded as an
`INFERENCE` with `confidence: 0.6` in the evidence ledger, not a `FACT`. Read the
module comment as aspirational/imprecise rather than as a guarantee that setting either
variable changes sampling behavior; this node did not find code that would honor a
change to either one.

## Use cases

A reader reaches for this node when they need to know: whether distributed tracing
export is on or off for a given `buzz-relay` deployment (check
`OTEL_EXPORTER_OTLP_ENDPOINT`), what happens when the OTLP exporter fails to build
(`ExporterBuildFailed`, logged as a `warn!` after startup — the process does not
crash), how to point exported spans at a different collector or service name, why
`BUZZ_OTEL_FILTER` exists as a separate knob from `RUST_LOG`, and — importantly —
whether `OTEL_TRACES_SAMPLER`/`OTEL_TRACES_SAMPLER_ARG` are worth setting for this
codebase today (per the *Sampling* section above, setting them has no code path to
take effect in `buzz-relay` as currently written).

## Boundaries and non-goals

This node does **not** cover:

- **Trace span semantics and instrumentation** — which spans exist, what
  `#[instrument]` attributes are used where, and what a span's fields mean. That is
  issue #1145's (tracing) territory; this node describes only the exporter/subscriber
  mechanism that carries spans out, not their content.
- **Datastore tracing policy macros** (`buzz-datastore-tracing`) — a separate
  proc-macro crate layered on top of the tracing setup described here, with its own
  `buzz_datastore` tracing target visible in the `BUZZ_OTEL_FILTER` default cited
  above. Its policy mechanics are issue #1136's (datastore-tracing) territory.
- **Metrics and Prometheus** — `buzz-relay`'s Prometheus metrics exporter
  (`relay_metrics::install`, started separately in `main()`) is unrelated code to the
  OTEL tracing wiring in this node; that content belongs to issues #1140 (metrics) and
  #1142 (prometheus).
- **The log/trace correlation mechanism itself** (`TraceContextJson`, the
  `trace_id`/`span_id` injection into JSON log lines) — this node names the
  `TraceContextLookup` layer as part of the wiring installed in `main()`, but the
  correlation behavior it enables is documented by the logging node (issue #1139).
- **Standing up a collector or Datadog Agent to receive the OTLP export** — an
  operator/deployment concern; nothing in this repository's `deploy/` or
  `docker-compose*.yml` files configures one.

## Scope and omissions

**This document covers** how `buzz-relay`'s OTEL SDK layer is initialized, what
exporter it builds, how its resource/service name and independent filter are derived,
what happens on an exporter build failure, and what this node could and could not
confirm about `OTEL_TRACES_SAMPLER`/`OTEL_TRACES_SAMPLER_ARG`, at the recorded
revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Trace span semantics, `#[instrument]` usage, span field meaning | #1145 (tracing) |
| Datastore tracing policy-macro mechanics (`buzz-datastore-tracing`) | #1136 (datastore-tracing) |
| Metrics/Prometheus exporter content | #1140 (metrics), #1142 (prometheus) |
| Log/trace correlation (`TraceContextJson`, injected `trace_id`/`span_id` fields) | logging node, issue #1139 |

**Expected but not verified when this node was written:**

- **Whether any part of `opentelemetry_sdk` beyond `trace/provider.rs` performs its
  own environment-based sampler auto-configuration**, which would mean
  `OTEL_TRACES_SAMPLER`/`OTEL_TRACES_SAMPLER_ARG` are honored indirectly by the SDK
  even though `buzz-relay`'s own code never reads them. Recorded as an `INFERENCE`
  with `confidence: 0.6` in the evidence ledger, not settled.
- **Whether `buzz-datastore-tracing`'s policy macros interact with, or depend on, the
  OTEL provider this node describes being globally registered** was not traced — that
  crate's own mechanics are issue #1136's territory and were not opened beyond its
  `Cargo.toml` dependency line and top-level crate description.

**No `relationships` in this node's front matter.** No `layers` node is merged on
`origin/launchpad` at the recorded revision to target (the sibling `logging` node,
issue #1139, exists only in an unmerged local worktree at the time this node was
written), so declaring any relationship would target an id the corpus checker cannot
resolve at merge time. This is a snapshot of one moment, not a permanent absence — the
first node this one could validly point at is the moment to revisit it.
