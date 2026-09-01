---
id: operations-observability-traces
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "crates/buzz-relay/src/telemetry.rs's module doc comment states the wiring as an ASCII diagram: the tracing crate feeds an always-on fmt::layer().json() to stdout plus an OpenTelemetryLayer attached only when an OTLP endpoint env var is set, and states plainly that when OTEL_EXPORTER_OTLP_ENDPOINT is unset the module is a no-op — no OTLP connection is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:1-18"
  - statement: "try_init_tracer in telemetry.rs reads std::env::var(\"OTEL_EXPORTER_OTLP_ENDPOINT\"); if that call errors (the variable is unset), it returns TracerInit::Disabled immediately, before building any exporter or provider."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:238-247"
  - statement: "When the endpoint variable is set, try_init_tracer builds an opentelemetry_otlp::SpanExporter via .with_tonic().build() (a gRPC exporter); classify_exporter_result then either constructs an SdkTracerProvider with .with_resource(resource).with_batch_exporter(exporter), registers it globally via opentelemetry::global::set_tracer_provider, and returns TracerInit::Enabled(provider) on Ok, or returns TracerInit::ExporterBuildFailed(e.to_string()) on Err without installing any provider."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:238-268"
  - statement: "main() in crates/buzz-relay/src/main.rs builds one shared Resource via telemetry::service_resource(), calls telemetry::try_init_tracer(resource.clone()) before installing the tracing subscriber, derives otel_enabled as matches!(&tracer_init, telemetry::TracerInit::Enabled(_)), and only when true attaches a tracing_opentelemetry layer; it installs a tracing_subscriber::registry() carrying the always-on JSON fmt layer (filtered by a RUST_LOG-driven EnvFilter), the optional OTEL layer (filtered by otel_env_filter(BUZZ_OTEL_FILTER)), and a TraceContextLookup layer forced to LevelFilter::OFF; an ExporterBuildFailed outcome is logged via tracing::warn! only after the subscriber has finished installing, so the process does not crash on a bad OTLP endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:96-148"
  - statement: "telemetry.rs's TraceContextLookup/TraceContextJson formatter injects trace_id and span_id fields into a stdout JSON log line only when its enabled flag is true, and main() constructs that formatter as trace_context_lookup.json_formatter(otel_enabled) — so trace_id/span_id correlation fields are present on JSON log lines only when the OTLP exporter actually initialized (otel_enabled == true), never merely because a span exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:52-59"
      - "crates/buzz-relay/src/telemetry.rs:117-175"
      - "crates/buzz-relay/src/main.rs:130-136"
  - statement: ".env.example documents RUST_LOG, BUZZ_OTEL_FILTER and OTEL_EXPORTER_OTLP_ENDPOINT together under a \"Logging / Tracing\" heading; both BUZZ_OTEL_FILTER and OTEL_EXPORTER_OTLP_ENDPOINT are commented out by default, with an inline comment on the endpoint variable reading \"optional — leave unset to disable\"."
    entry_class: FACT
    evidence:
      - ".env.example:174-183"
  - statement: "The workspace root Cargo.toml pins tracing-opentelemetry 0.33, opentelemetry 0.32 (feature trace), opentelemetry_sdk 0.32 (features trace, rt-tokio) and opentelemetry-otlp 0.32 with default-features = false and features grpc-tonic, tls-ring — so the only exporter transport compiled into the workspace is gRPC via tonic; no HTTP/protobuf OTLP exporter is available."
    entry_class: FACT
    evidence:
      - "Cargo.toml:88-91"
  - statement: "Grepping every crate's Cargo.toml for the string opentelemetry finds matches in exactly two files, crates/buzz-datastore-tracing/Cargo.toml and crates/buzz-relay/Cargo.toml; only crates/buzz-relay/src/telemetry.rs and crates/buzz-relay/src/main.rs call try_init_tracer or otherwise register a global tracer provider, so buzz-relay is the only binary in this workspace that can export a trace via OTLP — buzz-datastore-tracing's dependency backs its own #[instrument]-generating proc macro (a separate, operator-invisible concern), not a second exporter."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/Cargo.toml:21-25"
      - "crates/buzz-relay/Cargo.toml:44-47"
  - statement: "telemetry.rs's module doc comment lists OTEL_TRACES_SAMPLER (default parentbased_always_on) and OTEL_TRACES_SAMPLER_ARG as \"standard OTEL env vars honoured,\" but neither name appears anywhere else in crates/buzz-relay/src/telemetry.rs, and the SdkTracerProvider::builder() call in classify_exporter_result is never chained with .with_sampler(...) — so nothing in this crate reads either variable or configures a sampler explicitly; whatever default opentelemetry_sdk applies on its own is what actually governs sampling, which this node does not independently re-derive (the opentelemetry layers node already recorded that as a lower-confidence INFERENCE, and this node treats sampling as effectively unconfigurable from this workspace's own code rather than re-verifying the SDK's internal default)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:20-24"
      - "crates/buzz-relay/src/telemetry.rs:253-268"
  - statement: "Searching every .rs file under crates/ and desktop/src-tauri for traceparent, tracestate, TraceContextPropagator, inject_context, extract_context and Propagator returns zero matches, so no W3C trace-context header extraction or injection exists anywhere in this workspace; the WebSocket-to-HTTP and HTTP-to-WebSocket boundaries this repository exposes carry no propagated trace context across process or transport boundaries today."
    entry_class: FACT
    evidence:
      - "grep_workspace(pattern='traceparent|tracestate|TraceContextPropagator|inject_context|extract_context|Propagator', scope='crates/**/*.rs;desktop/src-tauri/**/*.rs') -> zero matches"
  - statement: "crates/buzz-relay/src/connection.rs's WebSocket message dispatcher creates a named tracing::info_span! per client-message type (ws.auth, ws.event, ...) and calls .instrument(span) on the future before tokio::spawn-ing it, with the ws.event span declaring conn_id, event_id and kind fields (the latter two as tracing::field::Empty, recorded later); crates/buzz-relay/src/handlers/event.rs's handle_event carries #[tracing::instrument(skip_all, fields(event_id, kind))] and records both fields via tracing::Span::current().record(...) once parsed from the incoming message — so a single WebSocket EVENT message's two nested spans both carry the same event_id/kind identifiers, independent of whether OTEL export is enabled."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:560-594"
      - "crates/buzz-relay/src/handlers/event.rs:607-617"
  - statement: "crates/buzz-relay/src/router.rs installs a tower_http::trace::TraceLayer via http_trace_layer(), whose make_http_span builds one tracing::info_span!(\"http.request\", otel.kind = \"server\", http.request.method = ...) span per incoming HTTP request — a middleware-driven span-creation mechanism distinct from the WebSocket dispatcher's manual info_span!, but subject to the same OTEL-export gating: the span exists either way, but only feeds an exported trace when otel_enabled is true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:200-220"
  - statement: "CONTRIBUTING.md's \"Logging and Tracing\" section states the workspace-wide convention directly: use the tracing crate for all instrumentation, and prefer structured fields (tracing::info!(channel_id = %id, event_kind = kind, \"Event ingested\")) over string-interpolated messages."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md:291-302"
  - statement: "No occurrence of otel, opentelemetry, jaeger, collector or traceparent (case-insensitive) appears in this repository's docker-compose.yml, docker-compose.harness.yml, deploy/compose/*, or deploy/local/quickstart-ha-values.yaml, and the only \"collector\" hits anywhere under launchpad/deploy/ are in runbooks/hardening-spec.md's log-shipping table (\"buzz_log_target: local journal only | remote collector\"), which names a log collector, not an OTLP trace collector — so no OTLP collector, Jaeger instance, or equivalent tracing backend is configured anywhere in this repository's own deployment material."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "docker-compose.harness.yml"
      - "deploy/compose/compose.yml"
      - "deploy/local/quickstart-ha-values.yaml"
      - "launchpad/deploy/runbooks/hardening-spec.md:89"
  - statement: "AGENTS.md's ecosystem table names squareup/block-coder-tf-stacks as the Terraform + ArgoCD repository that deploys the relay to the staging Kubernetes cluster, and that repository is not present in this workspace, so whether it configures an OTLP collector for the staging deployment could not be checked from within this repository."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "The dispatch brief for this batch identifies the logs (#1211), metrics (#1212), alerts (#1209) and dashboards (#1210) tasks as sibling operations/observability reference nodes being authored in parallel in this same batch, and directs this node to name the boundary with them in prose without declaring relationships to their unmerged node ids."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1213 task dispatch brief (corpus-batch-author, Feature #618 batch run)"
  - statement: "layers-observability-tracing, layers-observability-opentelemetry and layers-observability-datastore-tracing are merged nodes on origin/launchpad at the recorded revision, covering respectively the tracing-crate span-creation shapes, the OTEL SDK/exporter wiring mechanics, and the buzz-datastore-tracing proc-macro's instrumentation policy — all three read directly in this worktree to confirm they exist and to avoid re-narrating their content rather than trusting the batch's existing-node-ids listing alone."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/layers/observability/tracing.md"
      - "launchpad/docs/corpus/layers/observability/opentelemetry.md"
      - "launchpad/docs/corpus/layers/observability/datastore-tracing.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to carry a reference description, structured entries, an optional Commands table, an explicit boundary statement against its concept/how-to neighbors, relationships limited to nodes that already resolve on the merge target, and a scope-and-omissions section separating ownership exclusions from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: layers-observability-tracing
  - type: references
    target: layers-observability-opentelemetry
  - type: references
    target: layers-observability-datastore-tracing
---

# Distributed tracing: operations reference

This node catalogues the configuration knobs, verification commands, and
operational facts an **operator** needs to turn distributed trace export on
or off, confirm it is working, and know what does and does not exist for it
in this repository's own deployment material. It is the config/verification
companion to three already-merged `layers/observability` nodes that describe
the same subject from a developer/implementation angle:
`layers-observability-tracing` (how spans get created in application code),
`layers-observability-opentelemetry` (how the OTEL SDK/exporter is wired
internally), and `layers-observability-datastore-tracing` (the
`buzz-datastore-tracing` proc-macro's instrumentation policy). This node does
not restate their internals; see *Boundary* below for exactly where the line
sits, and *Scope and omissions* for the corollary — everything the exporter
mechanism itself, as opposed to its operator-facing configuration and
verification, is those nodes' territory.

## Trace-related environment variables

Ordered as `.env.example` declares them, under its "Logging / Tracing"
heading. All are read by `crates/buzz-relay/src/telemetry.rs` and
`crates/buzz-relay/src/main.rs`; none of them is read by any other binary in
this workspace, because `buzz-relay` is the only crate that registers an OTEL
tracer provider (confirmed by grepping every crate's `Cargo.toml` for
`opentelemetry`, which matches only `buzz-relay` and `buzz-datastore-tracing`
— the latter backs a proc macro, not a second exporter).

| Variable | Description | Example |
|---|---|---|
| `RUST_LOG` | Standard `tracing-subscriber` `EnvFilter` string. Governs only the always-on JSON stdout log layer. Deliberately independent from `BUZZ_OTEL_FILTER` below, so changing log verbosity can never remove a parent span from an exported trace. | `buzz_relay=debug,buzz_datastore=info,buzz_db=debug,buzz_auth=debug,buzz_pubsub=debug,tower_http=debug` |
| `BUZZ_OTEL_FILTER` | `EnvFilter` string applied only to the OTEL export layer. Optional; falls back to `buzz_relay=info,buzz_datastore=info` when unset. Has no effect unless `OTEL_EXPORTER_OTLP_ENDPOINT` is also set — with no endpoint there is no OTEL layer for this filter to apply to. | `buzz_relay=info,buzz_datastore=info` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | The single switch that turns trace export on or off. Unset (the shipped default) means `try_init_tracer` returns `Disabled` immediately: no exporter is built, no OTLP connection is attempted, and the JSON stdout logs continue exactly as if this variable did not exist. Set means a gRPC OTLP `SpanExporter` is built against this endpoint. | `http://localhost:4317` |
| `OTEL_SERVICE_NAME` | Read explicitly by `service_resource()`; used only when set and non-empty. Falls back to the hard-coded literal `buzz-relay`. Overridden by `service.name` set via `OTEL_RESOURCE_ATTRIBUTES` below, which is applied last. | `buzz-relay-staging` |
| `OTEL_RESOURCE_ATTRIBUTES` | Standard OTEL resource-attribute string, read by the SDK's `EnvResourceDetector` and overlaid last onto the `Resource` — so a `service.name` set here wins over `OTEL_SERVICE_NAME`. Not documented in `.env.example`; its existence and priority come from reading `telemetry.rs`'s own doc comment and `service_resource()`'s implementation directly. | `service.name=buzz-relay-staging,deployment.environment=staging` |
| `OTEL_TRACES_SAMPLER` / `OTEL_TRACES_SAMPLER_ARG` | Named in `telemetry.rs`'s own module doc comment as "standard OTEL env vars honoured," but no code in this crate reads either name, and the tracer-provider builder is never chained with `.with_sampler(...)`. Setting either variable has no code path in this workspace that reads it. Whatever default `opentelemetry_sdk` applies on its own governs sampling; this node does not re-derive that default and does not claim these variables are inert at the SDK layer, only that `buzz-relay`'s own code does not consult them. | not read by this crate's own code |

## Commands

<!-- Commands an operator can run to verify or exercise this repository's own trace-related code, not a general OTEL/OTLP tutorial. -->

| Command | Description | Argument | Example |
|---|---|---|---|
| `cargo test -p buzz-relay telemetry::` | Runs `telemetry.rs`'s own unit tests, which pin the `service_resource()` priority order and the `TracerInit::Disabled`/`ExporterBuildFailed` outcomes deterministically, without needing a live OTLP endpoint or network access. | none | `cargo test -p buzz-relay telemetry::tests::test_try_init_tracer_disabled_when_endpoint_unset` |
| `grep -c 'OTEL_EXPORTER_OTLP_ENDPOINT' .env` | Confirms whether a running deployment's own `.env` file actually sets the endpoint variable, since the shipped `.env.example` ships it commented out by default. | path to the environment file in use | `grep OTEL_EXPORTER_OTLP_ENDPOINT .env` |
| `RUST_LOG=buzz_relay=info OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 cargo run -p buzz-relay` | Starts the relay with trace export enabled against a locally reachable OTLP receiver (an operator-supplied collector; this repository ships none — see *What this repository does not provide* below). A startup `tracing::warn!` naming an exporter-build failure, rather than a crash, is the signal that the endpoint could not be reached or parsed. | `OTEL_EXPORTER_OTLP_ENDPOINT` value | `http://localhost:4317` |
| `jq 'select(.trace_id != null)'` over a JSON stdout log stream | Filters the relay's JSON logs down to lines that carry trace/span correlation fields — present only when export is enabled (see *Boundary* and *What operators have without export* below), never merely because a span exists. | a JSON-log stream | piped from the relay's stdout |

## Boundary

This node does not describe:

- How a span is created in application code, which `#[instrument]` call-site
  shapes exist, or how span context survives a `tokio::spawn` boundary — that
  is `layers-observability-tracing`'s territory.
- The OTEL SDK/exporter internals this node's environment-variable table
  reflects — the `TracerInit` state machine, the `Resource`/service-name
  derivation logic, and how the three tracing-subscriber layers are composed
  in `main()` — that is `layers-observability-opentelemetry`'s territory.
  This node states the operator-facing surface of that mechanism (the
  variables, their effect, and how to verify them), not its internals.
- `buzz-datastore-tracing`'s instrumentation policy — which fields the
  `#[datastore_span]` macro permits, its slow-operation sampling threshold, or
  its metrics side effect — that is `layers-observability-datastore-tracing`'s
  territory. This node names it only because its default target,
  `buzz_datastore`, appears in `BUZZ_OTEL_FILTER`'s own fallback value.
- How to accomplish a task step by step (standing up a collector, rotating an
  OTLP endpoint credential) — no such procedure exists in this repository to
  document, and inventing one here would be exactly the fabricated
  operational content this corpus's authoring rules forbid. See *What this
  repository does not provide* below for what is actually absent, stated as
  an absence rather than as an unwritten how-to.
- Request correlation via structured logging in general, or per-surface log
  conventions — a neighbouring operations/observability concern being
  documented separately in this same batch; see *Scope and omissions*.

## What this repository does not provide

**No collector is configured anywhere in this repository's own deployment
material.** Grepping `docker-compose.yml`, `docker-compose.harness.yml`,
`deploy/compose/*`, and `deploy/local/quickstart-ha-values.yaml` for `otel`,
`opentelemetry`, `jaeger`, `collector`, and `traceparent` (case-insensitive)
returns zero matches. The only "collector" hits anywhere under
`launchpad/deploy/` name a **log** collector in a hardening runbook's
log-shipping table, not an OTLP trace collector. An operator who sets
`OTEL_EXPORTER_OTLP_ENDPOINT` is pointing at infrastructure they must stand up
themselves; this repository ships no compose service, Helm value, or script
that does it for them.

**No cross-process trace-context propagation exists.** Searching every `.rs`
file under `crates/` and `desktop/src-tauri` for W3C `traceparent`/
`tracestate` headers or any `opentelemetry::propagation` `Propagator`,
`inject_context`, or `extract_context` call returns zero matches. A span
created for one WebSocket message or HTTP request does not extend into a
downstream HTTP call this relay makes, and no incoming `traceparent` header is
read to attach an inbound request to an upstream caller's trace. "Trace
context propagation" in this codebase means only in-process span nesting
across `.await` points and — where the source carries an explicit comment
saying so — across one `tokio::spawn` boundary via `.instrument(span)`
captured beforehand.

**Sampling is effectively unconfigurable from this workspace's own code.**
`OTEL_TRACES_SAMPLER`/`OTEL_TRACES_SAMPLER_ARG` are named in
`telemetry.rs`'s own doc comment as honoured, but nothing in `buzz-relay`
reads either variable, and no `.with_sampler(...)` call appears anywhere in
the exporter setup. Enabling export therefore exports at whatever
`opentelemetry_sdk`'s own unconfigured default is — the module comment claims
`parentbased_always_on` — with no operator-facing knob in this repository to
change it.

## What operators have without export

With `OTEL_EXPORTER_OTLP_ENDPOINT` unset — the shipped default — there is no
exported trace, and there is also no `trace_id`/`span_id` correlation field in
the JSON stdout logs: that injection is gated on `otel_enabled`, which is
`false` whenever the exporter never initialized. What an operator has instead
is the structured-field convention `CONTRIBUTING.md` states directly: spans
and events carry explicit named fields (`event_id`, `kind`, `conn_id`, and
others recorded via `tracing::Span::current().record(...)` or passed inline to
`tracing::info!`), independent of whether OTEL export is on. Grepping or
filtering a JSON log stream by one of those field values — `event_id` to
follow one event's ingestion, `conn_id` to follow one WebSocket connection —
is the correlation mechanism available without a collector. It requires
knowing which field name to filter on and is not automatic the way a
`trace_id` join would be; this node states that limitation rather than
implying the two are equivalent.

## Relationships

- references: `layers-observability-tracing` — the span-creation and
  in-process propagation mechanics whose operator-facing configuration
  surface this node catalogues.
- references: `layers-observability-opentelemetry` — the OTEL SDK/exporter
  internals this node's environment-variable table is the operator-facing
  reflection of.
- references: `layers-observability-datastore-tracing` — the
  `buzz-datastore-tracing` policy macro whose default target
  (`buzz_datastore`) appears in `BUZZ_OTEL_FILTER`'s own fallback value.

## Scope and omissions

**This node covers** the environment variables that control `buzz-relay`'s
OTLP trace export, verification commands that do not require a live
collector, what this repository's own deployment material does and does not
configure for a trace-export destination, the absence of cross-process
trace-context propagation, the practical unconfigurability of sampling from
this workspace's own code, and the structured-field correlation an operator
has in the (default, and only demonstrated) case where export is off.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `tracing`-crate span-creation shapes and in-process propagation mechanics | `layers-observability-tracing` |
| OTEL SDK/exporter internals (`TracerInit`, `Resource` derivation, layer composition) | `layers-observability-opentelemetry` |
| `buzz-datastore-tracing` proc-macro instrumentation policy | `layers-observability-datastore-tracing` |
| Structured logging conventions and per-surface log correlation, beyond the one convention named above | a sibling operations/observability node being authored in this same batch, not yet merged at the time this node was written |
| Metrics/gauge telemetry as a signal distinct from spans | a sibling operations/observability node being authored in this same batch, not yet merged at the time this node was written |
| Alerting and dashboard configuration built on top of any exported telemetry | sibling operations/observability nodes being authored in this same batch, not yet merged at the time this node was written |
| Standing up or configuring an OTLP collector, Jaeger instance, or equivalent backend | not implemented anywhere in this repository; an operator's own infrastructure decision |
| The staging Kubernetes deployment's actual OTEL/collector configuration, if any | the private `squareup/block-coder-tf-stacks` repository (Terraform + ArgoCD), not present in this workspace and not checked by this node |

**Expected but not verified when this node was written:**

- **Whether any span in a real deployment of this relay has ever actually
  reached an exported OTLP trace** was not established — that depends on an
  operator setting `OTEL_EXPORTER_OTLP_ENDPOINT` and pointing it at a reachable
  collector, neither of which this node found evidence of happening anywhere
  in this repository's own configuration.
- **Whether `squareup/block-coder-tf-stacks` configures a collector for the
  staging cluster** could not be checked — that repository is not part of this
  workspace and this task did not have access to it.
- **Whether `opentelemetry_sdk` performs its own environment-based sampler
  auto-configuration beneath the level `buzz-relay`'s own code reads** was not
  independently re-derived here; this node treats sampling as unconfigurable
  from this workspace's own code, which is a narrower and directly verified
  claim than a claim about the SDK's internal default behavior.
- **Whether any binary other than `buzz-relay` (`buzz-cli`, `buzz-agent`,
  `sprig`, the desktop Tauri backend) creates spans that could ever be
  exported** was not exhaustively re-checked here beyond confirming, via each
  crate's `Cargo.toml`, that none of them depends on `opentelemetry` — so none
  of them can register a tracer provider regardless of environment
  configuration, but their own `tracing`-crate usage (local, unexported spans)
  was not otherwise surveyed as part of this operations-facing task.

## Note on the template used

This node was written using
`launchpad/docs/corpus/templates/reference.md`, which was already merged on
`origin/launchpad` at the recorded revision and directs a reference-shaped
node to carry a reference description, structured entries, an optional
Commands table, an explicit boundary statement against its concept/how-to
neighbors, relationships limited to nodes that already resolve on the merge
target, and a scope-and-omissions section separating what the node excludes
by ownership from what it expected to verify and could not.
