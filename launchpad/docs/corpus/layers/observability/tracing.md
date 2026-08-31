---
id: layers-observability-tracing
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
  - statement: "The workspace declares tracing = \"0.1\", tracing-subscriber = { version = \"0.3\", features = [\"env-filter\", \"json\"] } and tracing-opentelemetry = { version = \"0.33\" } as shared workspace dependencies, and CONTRIBUTING.md's \"Logging and Tracing\" section states the repository-wide rule directly: use the `tracing` crate for all instrumentation, and prefer structured fields (`channel_id = %id`) over string-interpolated messages."
    entry_class: FACT
    evidence:
      - "Cargo.toml:85-87"
      - "CONTRIBUTING.md:290-302"
  - statement: "`tracing::instrument` is used exactly once as a bare attribute macro in the workspace's own source (searched every .rs file under crates/ and desktop/src-tauri for `#[instrument`): a doc-comment ASCII diagram in crates/buzz-relay/src/telemetry.rs labels it as one of the two sources feeding the tracing pipeline, alongside `#[instrument]` applied via handler-function attributes described separately below."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:1-11"
  - statement: "crates/buzz-relay/src/handlers/event.rs's handle_event and crates/buzz-relay/src/handlers/auth.rs's handle_auth are both annotated `#[tracing::instrument(skip_all, fields(event_id, kind))]` and `#[tracing::instrument(skip_all, fields(event_id, conn_id))]` respectively — declaring named fields with no assigned value up front, then calling `tracing::Span::current().record(\"event_id\", ...)` (and `.record(\"kind\", ...)` / `.record(\"conn_id\", ...)`) later in the function body once those values become known, rather than passing them at span-creation time."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:607-616"
      - "crates/buzz-relay/src/handlers/auth.rs:42"
      - "crates/buzz-relay/src/handlers/auth.rs:70-72"
  - statement: "crates/buzz-relay/src/connection.rs's WebSocket message dispatcher manually creates one `tracing::info_span!` per client-message type (`ws.auth`, `ws.event`, `ws.req`, `ws.count`) and calls `.instrument(span)` on the future before `tokio::spawn`-ing it, with an inline comment stating the reason directly: the span must be captured before the spawn because a bare `tokio::spawn` drops tracing context, and auth (handled synchronously in the same task) needs no such capture because no span context is lost there."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:560-566"
      - "crates/buzz-relay/src/connection.rs:578-593"
  - statement: "The `ws.event` span in crates/buzz-relay/src/connection.rs is created with `event_id = tracing::field::Empty` and `kind = tracing::field::Empty` fields before the values are known, and the spawned `handle_event` future's own `#[instrument]` span records those same field names inside it — so a single WebSocket EVENT message produces two nested spans (`ws.event`, then `handle_event`) that both carry `event_id`/`kind`, populated at different points via the declare-then-record pattern."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:582-587"
      - "crates/buzz-relay/src/handlers/event.rs:607-616"
  - statement: "crates/buzz-relay/src/router.rs installs a `tower_http::trace::TraceLayer` (via `http_trace_layer()`/`TraceLayer::new_for_http().make_span_with(make_http_span)`) that creates one `tracing::info_span!(\"http.request\", ...)` span per incoming HTTP request, carrying `otel.kind = \"server\"` and `http.request.method` fields — a second, HTTP-specific span-creation mechanism distinct from both the WebSocket connection.rs pattern and the `#[instrument]`-attribute pattern."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:209-220"
  - statement: "crates/buzz-agent/src/agent.rs wraps a single `tokio::select!` branch's LLM call future with `.instrument(tracing::info_span!(\"llm\", session_id = %self.session_id))`, an inline `.instrument()` call on an anonymous span rather than a named span variable or a function-level `#[instrument]` attribute — a third distinct call-site shape for creating a span in this workspace."
    entry_class: FACT
    evidence:
      - "crates/buzz-agent/src/agent.rs:409-410"
  - statement: "The proc-macro crate buzz-datastore-tracing's `datastore_span` attribute macro (crates/buzz-datastore-tracing/src/lib.rs) generates and injects a `#[::tracing::instrument(target = \"buzz_datastore\", name = ..., skip_all, fields(otel.kind = \"client\", db.system.name = \"postgresql\", otel.status_code = ::tracing::field::Empty, ...))]` attribute onto the function it is applied to — reusing the same general `#[instrument]` mechanism this node describes, rather than a separate span-creation API; the macro's own policy specifics (postgresql-only enforcement, which fields are permitted, the slow-operation sampling and metrics-histogram side effects) are issue #1136's (datastore-tracing) territory, not this node's."
    entry_class: FACT
    evidence:
      - "crates/buzz-datastore-tracing/src/lib.rs:76-112"
  - statement: "No W3C `traceparent`/`tracestate` header extraction or injection, and no `opentelemetry::propagation` Propagator usage, appears anywhere in the workspace (grepped every .rs file under crates/ and desktop/src-tauri for `traceparent`, `TraceContextPropagator`, `inject_context`, `extract_context` and `Propagator`; zero matches), so trace context propagation in this codebase means in-process span nesting across async/await and `tokio::spawn` boundaries via `tracing::Span::current()`/`.instrument()`, not cross-process trace-context header propagation between services."
    entry_class: FACT
    evidence:
      - "grep_workspace(\"traceparent|TraceContextPropagator|inject_context|extract_context|Propagator\") -> zero matches across crates/ and desktop/src-tauri"
  - statement: "`.env.example` documents `RUST_LOG` and the optional `BUZZ_OTEL_FILTER`/`OTEL_EXPORTER_OTLP_ENDPOINT` variables together under a \"Logging / Tracing\" heading, with an inline comment stating `BUZZ_OTEL_FILTER` is deliberately independent from `RUST_LOG` so log verbosity changes cannot break trace parentage."
    entry_class: FACT
    evidence:
      - ".env.example:174-183"
  - statement: "crates/buzz-relay/src/telemetry.rs's own module-level doc comment states, as an ASCII diagram, that the `tracing` crate (spans and events from `#[instrument]` and its macros) feeds two layers: an always-on `fmt::layer().json()` to stdout, and an `OpenTelemetryLayer` that is only attached when `OTEL_EXPORTER_OTLP_ENDPOINT` is set, which in turn feeds an `SdkTracerProvider` and OTLP batch exporter; the mechanics of that exporter wiring, the `SdkTracerProvider` setup, and the `OTEL_SERVICE_NAME`/`OTEL_RESOURCE_ATTRIBUTES`/`OTEL_TRACES_SAMPLER` env vars it honours are issue #1141's (opentelemetry) territory, not this node's — this node cites the diagram only to show where spans, as a concept, feed into that separate exporter mechanism."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:1-25"
  - statement: "Neither #1136 (datastore-tracing) nor #1141 (opentelemetry) has a corpus node committed in its own sibling worktree or merged to origin/launchpad as of this node's recorded revision (checked: `git log --oneline` in both `__worktrees/task-1136-datastore-tracing` and `__worktrees/task-1141-opentelemetry` shows no commit past the shared base), so no `relationships` edge to either exists yet; `#1139` (logging) and `#1138` (observability-liveness) have drafts committed in their own sibling worktrees but neither is merged to `origin/launchpad` either, so they are likewise not valid relationship targets at this revision."
    entry_class: FACT
    evidence:
      - "git_log_oneline(\"__worktrees/task-1136-datastore-tracing\", \"__worktrees/task-1141-opentelemetry\") -> no commit past shared base ed133f4c5 in either worktree"
      - "git_ls_tree(\"origin/launchpad\", \"launchpad/docs/corpus\") -> no layers/ subtree present"
  - statement: "Issue #1145's task dispatch brief names #1141 (opentelemetry) as the sibling covering the SDK/exporter-wiring mechanism and #1136 (datastore-tracing) as the sibling covering the buzz-datastore-tracing crate specifically, directing this node to be the general/cross-cutting overview of `tracing` crate usage — spans, `#[instrument]`, and trace context propagation — distinct from both."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1145 task dispatch brief (corpus-batch-author, Feature #611 batch run)"
---

# Tracing

## Definition

**Tracing**, in Buzz, is the practice of building nested, contextual units of work — Rust
[`tracing`](https://docs.rs/tracing) crate **spans** — around code paths so that both a
human reading structured logs and an OpenTelemetry backend can see which operations
happened inside which others, and with what field values attached. This node is the
**general/cross-cutting overview**: the ways spans get created in this codebase, how a span's
context follows work across `.await` points and `tokio::spawn` boundaries, and the declared
convention behind it all. It does not cover the OpenTelemetry SDK/exporter machinery that
turns spans into exported traces (that is issue #1141's territory) or the
`buzz-datastore-tracing` proc-macro crate's own policy mechanics (that is issue #1136's
territory) — see *Boundaries and non-goals* below.

`CONTRIBUTING.md`'s "Logging and Tracing" section states the workspace convention directly:
use `tracing` for all instrumentation, and prefer structured fields
(`tracing::info!(channel_id = %id, event_kind = kind, "Event ingested")`) over
string-interpolated messages. Spans are the mechanism by which those structured events get
grouped and nested, rather than emitted as flat, disconnected lines.

## How spans get created — four shapes, all in this workspace today

**1. Function-level `#[instrument]` attribute, values recorded later.** `handle_event`
(`crates/buzz-relay/src/handlers/event.rs`) and `handle_auth`
(`crates/buzz-relay/src/handlers/auth.rs`) are both annotated
`#[tracing::instrument(skip_all, fields(event_id, kind))]`-shaped attributes: the field names
are declared up front with no value, and the function body later calls
`tracing::Span::current().record("event_id", ...)` once the value becomes available. This
"declare then record" shape exists because the span has to be opened before the event ID or
kind is parsed out of the incoming message — recording lets the span still carry those fields
once they're known, rather than requiring them at creation time.

**2. Manual `tracing::info_span!` + `.instrument()`, captured before a spawn.**
`crates/buzz-relay/src/connection.rs`'s WebSocket dispatcher creates one named span per
message type — `ws.auth`, `ws.event`, `ws.req`, `ws.count` — with `tracing::info_span!(...)`,
then calls `.instrument(span)` on the future *before* handing it to `tokio::spawn`. An inline
comment in the source states the reason plainly: a bare `tokio::spawn` drops tracing context,
so the span must be captured beforehand for it to propagate into the spawned task. Auth is
handled synchronously in the same task, so no such capture is needed there — the comment notes
that explicitly too. Because the spawned `ws.event` future then calls `handle_event`, which
carries its own `#[instrument]` span (shape 1 above) with the same `event_id`/`kind` field
names, a single incoming EVENT message ends up producing two nested spans — `ws.event`, then
`handle_event` — populated by two different mechanisms at two different points.

**3. `tower_http::trace::TraceLayer`, one span per HTTP request.**
`crates/buzz-relay/src/router.rs` installs `TraceLayer::new_for_http().make_span_with(...)`,
where `make_http_span` builds a `tracing::info_span!("http.request", otel.kind = "server",
http.request.method = %request.method())` span per incoming HTTP request. This is a
middleware-driven mechanism distinct from both shapes above — the span is created outside
application handler code, by the HTTP framework layer itself.

**4. Inline `.instrument()` on an anonymous span, wrapping one future.**
`crates/buzz-agent/src/agent.rs` wraps a single `tokio::select!` branch — the LLM completion
call — with `.instrument(tracing::info_span!("llm", session_id = %self.session_id))` directly
at the call site, with no named span variable and no function-level attribute. This is the
narrowest-scoped shape: one future, one inline span, no reuse elsewhere in the function.

**A fifth call site reuses shape 1 through code generation.** The `buzz-datastore-tracing`
proc-macro crate's `datastore_span` attribute macro
(`crates/buzz-datastore-tracing/src/lib.rs`) generates and injects a
`#[::tracing::instrument(target = "buzz_datastore", name = ..., skip_all, fields(otel.kind =
"client", db.system.name = "postgresql", otel.status_code = ::tracing::field::Empty, ...))]`
attribute onto whatever async function it decorates — the same general `#[instrument]`
mechanism as shape 1, produced by a macro instead of written by hand. This node stops there:
the macro's `postgresql`-only enforcement, which fields it allows, and its slow-operation
sampling/metrics side effects are issue #1136's territory, not described further here.

## Trace context propagation, in this codebase, means in-process span nesting

Searching every `.rs` file under `crates/` and `desktop/src-tauri` turns up zero references to
W3C `traceparent`/`tracestate` headers, or to any `opentelemetry::propagation` `Propagator`,
`inject_context`, or `extract_context` call. **There is no cross-process trace-context header
propagation implemented in this workspace today.** What "propagation" means here is narrower
and entirely in-process: a span's context following execution across `.await` points within
one task (the ordinary behavior `tracing`'s `Span::current()` and `#[instrument]` give for
free), and — the one place it takes deliberate extra code — a span surviving a `tokio::spawn`
boundary onto a new task, which requires the explicit `.instrument(span)`-before-`spawn`
pattern documented in shape 2 above. A reader expecting distributed cross-service trace
propagation (e.g. an incoming request's `traceparent` header flowing through to an outbound
call) will not find it implemented here; see *Scope and omissions*.

## Use cases

A reader reaches for this node when they need to understand, before diving into #1141's
OTEL-exporter specifics or #1136's datastore-tracing-policy specifics: what a span is in this
codebase's own terms, which of the four call-site shapes above a given piece of code is using
and why, why some spans declare empty fields and record them later, why a manual
`tracing::info_span!` has to be captured and `.instrument()`-ed before `tokio::spawn` rather
than created inside the spawned future, and — importantly — that this workspace has no
cross-process trace-context propagation today, so a `traceparent` header is not something to
look for.

## Boundaries and non-goals

This node does **not** cover:

- **OpenTelemetry SDK/exporter wiring** — how spans become OTLP-exported traces, the
  `SdkTracerProvider`/OTLP batch exporter setup, `OTEL_SERVICE_NAME`/`OTEL_RESOURCE_ATTRIBUTES`/
  `OTEL_TRACES_SAMPLER` env vars, and the `OpenTelemetryLayer`'s attach/detach behavior around
  `OTEL_EXPORTER_OTLP_ENDPOINT`. This node cites `telemetry.rs`'s module diagram only to show
  where spans, as a concept, feed into that separate mechanism. That mechanism itself is issue
  #1141's (opentelemetry) territory.
- **`buzz-datastore-tracing`'s policy mechanics** — the `postgresql`-only system restriction,
  which fields the macro permits versus rejects, `otel.status_code` recording on error, the
  slow-operation sampling threshold, and the `buzz_db_operation_duration_seconds` metrics
  histogram side effect. This node states only that the macro reuses the general
  `#[instrument]` mechanism described above. The policy details are issue #1136's
  (datastore-tracing) territory.
- **The JSON stdout log format and `trace_id`/`span_id` correlation fields** (`TraceContextJson`
  in `crates/buzz-relay/src/telemetry.rs`), `RUST_LOG`/subscriber initialization per binary, and
  per-surface logging conventions (relay, push-gateway, desktop frontend, mobile) — that is the
  general logging umbrella, drafted separately (see *Scope and omissions* below for why no
  `relationships` edge names it).
- **Cross-process trace-context propagation** — not implemented in this workspace as of the
  recorded revision (see above). This node records that absence; it does not describe a
  propagation mechanism that does not exist.
- **Metrics** (Prometheus/Datadog gauges and histograms) as a telemetry signal distinct from
  spans — a related but separate observability concern this node does not describe.

## Scope and omissions

**This document covers** the general/cross-cutting shape of `tracing`-crate span usage in this
workspace — the four call-site patterns for creating a span, the declare-then-record field
convention, how span context does and does not survive a `tokio::spawn` boundary, and the
absence of any cross-process trace-context propagation — at the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| OpenTelemetry SDK/exporter wiring, env vars, sampler config | #1141 (opentelemetry) |
| `buzz-datastore-tracing` policy-macro mechanics | #1136 (datastore-tracing) |
| General logging conventions and per-surface subscriber setup | #1139 (logging) |
| Structured-field schema/catalogue for log events | #1144 (structured-logging) |
| Metrics/gauge telemetry | Not investigated for this node |

Neither #1141, #1136, #1139, #1144 nor #1138 (observability-liveness) has a corpus node merged
on `origin/launchpad` at this node's recorded revision — #1139 and #1138 have drafts committed
in their own sibling worktrees, and #1141/#1136 have none committed at all — so no
`relationships` edge to any of them exists yet, per `AGENTS.md`'s rule that a relationship may
only target a node that already resolves on the branch being merged into.

**Expected but not verified when this node was written:**

- **Whether any span in this workspace ever actually reaches an exported OTLP trace in
  practice** (versus only ever appearing in local JSON stdout logs) was not established here —
  that depends on `OTEL_EXPORTER_OTLP_ENDPOINT` being set at runtime, and on #1141's exporter
  wiring behaving as its own module doc comment describes; this node read that doc comment but
  did not trace the exporter code path itself.
- **Whether desktop's Rust (Tauri) backend or mobile (Flutter) use `tracing` spans at all** was
  not established. `desktop/src-tauri`'s `managed_agents` module calls bare `tracing::warn!`/
  `info!` (no span, no `#[instrument]` found there), and mobile is a separate Dart codebase with
  no `tracing`-crate dependency — neither surface's own span usage, if any, was traced further
  since neither showed up in this node's searches for `#[instrument]`, `info_span!`, or
  `.instrument(`.
- **Whether `buzz-cli` or other binaries beyond those inspected here create spans** was not
  exhaustively checked; this node's grep for `#[instrument`, `span!`, and `.instrument(` covered
  every `.rs` file under `crates/` and `desktop/src-tauri`, but the resulting call sites were
  read selectively for the shapes described above rather than every single match being narrated
  individually.
