---
id: platforms-relay-metrics-server
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "crates/buzz-relay/src/metrics.rs opens with the crate/module doc comment 'Prometheus metrics: recorder setup, upkeep task, and HTTP middleware.' followed by an ASCII diagram reading 'metrics-rs facade (metrics::counter!, histogram!, etc.) -> PrometheusBuilder -> HTTP listener on :9102 -> GET /metrics -> Prometheus text format', with a closing note that 'Framework metrics (http_requests_total, http_request_latency_ms) are recorded by track_metrics middleware on the app router. Buzz-specific metrics are recorded inline at their call sites.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:1-14"
  - statement: "install(port, gauge_idle_timeout_secs) builds a PrometheusBuilder, calls .with_http_listener(([0,0,0,0], port)), sets an idle timeout for gauge-kind metrics via .idle_timeout(MetricKindMask::GAUGE, Some(Duration::from_secs(gauge_idle_timeout_secs))), registers explicit per-metric histogram bucket boundaries (millisecond buckets for http_request_latency_ms; second-scale buckets for buzz_git_hydrate_seconds, buzz_git_upload_pack_stream_seconds, buzz_git_pack_cache_populate_seconds, buzz_git_pack_cache_population_wait_seconds, buzz_git_pack_compaction_seconds and, via a _seconds suffix matcher, any other seconds-scale histogram; byte buckets for buzz_git_hydrate_bytes, buzz_git_upload_pack_stream_bytes, buzz_git_pack_compaction_bytes; pack-count buckets for buzz_git_hydrate_packs, buzz_git_pack_compaction_packs_before/after; and fanout-count buckets for buzz_fanout_recipients), then calls .build(), sets the returned recorder as the global metrics recorder via metrics::set_global_recorder, and tokio::spawn(exporter)s the returned exporter future -- its own doc comment states 'build() returns the recorder + exporter future and internally spawns the upkeep task, so no separate upkeep call is needed' and 'Panics if a recorder is already installed or the port is in use.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:58-147"
  - statement: "The GET /metrics HTTP endpoint is served entirely by the exporter future PrometheusBuilder.build() returns (bound to the port passed into install(), via .with_http_listener), not by any axum route on the relay's own app or health routers -- no /metrics handler function exists anywhere in crates/buzz-relay/src/router.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:66-146"
      - "crates/buzz-relay/src/router.rs"
  - statement: "track_metrics is separate axum middleware with its own doc comment stating it 'Emits: http_requests_total{code, caller, action} -- counter, http_request_latency_ms{code, caller, action} -- histogram' and 'Skips health/metrics paths (/_*, /health) to avoid polluting dashboards'; its body matches any MatchedPath starting with \"/_\" or equal to \"/health\" or \"/metrics\", returning early via next.run(req).await for all three without recording either metric, and separately returns early (also without recording) when no MatchedPath extension is present at all (unmatched/404 traffic), specifically to avoid what its inline comment calls a 'cardinality bomb' from URI-scanning traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:149-207"
  - statement: "For matched, non-excluded paths, track_metrics records both metrics with three labels: code (the exact HTTP status code as a string), caller (from the x-envoy-downstream-service-cluster header, validated to at most 64 ASCII alphanumeric/hyphen/underscore bytes and defaulting to \"unknown\" otherwise, with an inline comment noting the header is mesh-trusted inside CAKE but client-controlled on the public TCP listener, hence the validation), and action (the matched route pattern, e.g. \"/api/channels/{channel_id}\", explicitly not the raw URI, to avoid unbounded cardinality from scanners)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:161-206"
  - statement: "crates/buzz-relay/src/config.rs defines metrics_port: u16 on the relay Config struct, documented as 'TCP port for the Prometheus metrics exporter (GET /metrics)', populated from the BUZZ_METRICS_PORT environment variable with a default of 9102 when unset or unparsable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:197-198"
      - "crates/buzz-relay/src/config.rs:823-826"
  - statement: "crates/buzz-relay/src/main.rs imports the metrics module under the alias relay_metrics (use buzz_relay::metrics as relay_metrics), computes usage_idle_timeout_secs from two small helper functions -- usage_metrics_interval_secs (reads BUZZ_USAGE_METRICS_INTERVAL_SECS, defaults to 300, floors at 5) and usage_metrics_idle_timeout_secs, which delegates to idle_timeout_secs(configured, interval_secs) (reads BUZZ_USAGE_METRICS_IDLE_TIMEOUT_SECS if set, else defaults to 900, then takes the max of that and interval_secs * 3) -- and then calls relay_metrics::install(config.metrics_port, usage_idle_timeout_secs) exactly once, immediately followed by two metrics::gauge! calls (buzz_audit_enabled, buzz_push_enabled) and an info! log reading 'Prometheus metrics exporter started' with port and idle_timeout_secs fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:21"
      - "crates/buzz-relay/src/main.rs:168-177"
      - "crates/buzz-relay/src/main.rs:1479-1500"
  - statement: "serve()'s own doc comment (an ASCII diagram) names four listeners the relay binds, the fourth reading 'Listener 4: TCP 0.0.0.0:9102 (metrics, via PrometheusBuilder -- already bound)' -- confirming the metrics HTTP listener is bound earlier in main() (inside install(), before serve() is ever called), not inside serve() alongside the app/health TCP and UDS listeners it does bind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1256"
  - statement: "crates/buzz-relay/src/router.rs imports track_metrics (use crate::metrics::track_metrics) and layers it onto the router returned by build_router only, via .layer(middleware::from_fn(track_metrics)) immediately followed by an HTTP trace layer and a CORS layer; this is the same router build_health_router's own separately-constructed Router does not share, so the health-only router carries no track_metrics layer (or any other middleware layer) at all -- corroborating the sibling platforms-relay-health-server node's independent finding about the same two-router split."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:25"
      - "crates/buzz-relay/src/router.rs:203-206"
  - statement: "crates/buzz-relay/Cargo.toml declares three workspace-versioned dependencies this module is written against: metrics, metrics-exporter-prometheus, and metrics-util."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:79-81"
  - statement: "No automated test file in crates/buzz-relay/tests/ or crates/buzz-test-client/tests/ exercises install() or track_metrics() directly (searched by grep for 9102, metrics_port, BUZZ_METRICS_PORT, and /metrics across both directories); the only hit outside metrics.rs/config.rs/main.rs is a doc-comment example in crates/buzz-test-client/tests/nip42_host_binding_live.rs:14 showing how to run a second relay binary with BUZZ_METRICS_PORT=9202 to avoid a port collision with a concurrently running first instance -- not a test of metrics recording or exposition behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs:14"
  - statement: "idle_timeout_secs -- one of install()'s two call-site inputs, computed via usage_metrics_idle_timeout_secs -- does have direct unit test coverage: test_idle_timeout_is_at_least_three_usage_intervals asserts idle_timeout_secs(None, 300) == 900 and idle_timeout_secs(Some(10), 1_000) == 3_000."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:2189-2192"
  - statement: "launchpad/docs/corpus/architecture/containers/relay.md (id: architecture-containers-relay) is merged on origin/launchpad and already names the metrics listener at topology level: one evidence entry states the relay binds 'a Prometheus metrics listener (default 0.0.0.0:9102, already bound by PrometheusBuilder before serve() is called)', and a routing table row lists 'Metrics (TCP) | default 0.0.0.0:9102 | Prometheus scrape endpoint, bound independently via PrometheusBuilder'; this node's own content (handler/config/bucket-registration detail) does not duplicate that container-level topology mention."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md:34"
      - "launchpad/docs/corpus/architecture/containers/relay.md:178"
  - statement: "At repository revision 131b02f989684117d9ab1dd426f1673fa638e523, no platforms/** node is merged onto origin/launchpad (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/platforms returns no entries), even though sibling platforms/relay/* nodes (e.g. platforms-relay-health-server, platforms-relay-app-state) exist as committed content on their own unmerged task branches; those sibling branches establish the type: platforms convention this node follows, but are not valid relationships targets because they do not exist on the branch being merged into."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/platforms') -> no entries, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "Issue #1277's Definition of Done requires (among other bullets) that the node 'states responsibility and well-defined interface/boundary', 'names dependencies and collaborators', 'links source implementation and tests', and 'explains only component-level behavior, not the entire containing platform.'"
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1277 definition of done"
  - statement: "Because install()'s docstring states it panics if a recorder is already installed or the port is in use, and it is called exactly once from main() before serve() runs, the metrics server's failure mode is a startup-time panic rather than a runtime error path -- a misconfigured or colliding metrics_port prevents the relay process from starting at all rather than degrading metrics collection silently."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/metrics.rs:58-65"
      - "crates/buzz-relay/src/main.rs:170"
    confidence: 0.75
---

# Relay metrics server

The relay exposes Prometheus-format operational metrics over plain HTTP
through `crates/buzz-relay/src/metrics.rs`: a global recorder and standalone
HTTP exporter installed once at startup, and a separate piece of axum
middleware that records per-request HTTP metrics on the main API router.
This node answers: what `GET /metrics` actually serves and how, what
`install()` configures at startup, what `track_metrics` records and what it
deliberately excludes, and how the metrics HTTP surface relates to the
relay's other listeners.

**A note on `type` and template.** This node lives under `platforms/relay/`
and uses `type: platforms`, matching the unmerged sibling node
`platforms-relay-health-server` (issue #1272) and every other already-drafted
sibling under `platforms/**` at the time of writing. The merged
`templates/component.md` template's own text recommends `type:
implementation` for a single-component node; this node follows the batch's
established `platforms` convention instead, since no accepted decision was
found settling which of the two is the corpus's final answer for this path
shape, and no sibling node is merged onto `origin/launchpad` yet to defer to
as binding precedent (see *Relationships* below).

## Responsibility

The metrics server's job is to make the relay's operational state visible to
Prometheus without touching the relay's authenticated request path: install
a process-wide metrics recorder, expose it over its own HTTP listener in
Prometheus text format, and record the one class of metric the relay itself
is responsible for (framework-level HTTP request counts and latencies) —
everything else (git hydration timings, fan-out counts, feature-flag gauges,
etc.) is recorded inline at each subsystem's own call sites using the
`metrics-rs` facade macros (`metrics::counter!`, `histogram!`, `gauge!`),
which this module's `install()` configures bucket boundaries for but does not
itself emit. The module-level doc comment states this division directly:
"Framework metrics (`http_requests_total`, `http_request_latency_ms`) are
recorded by `track_metrics` middleware on the app router. Buzz-specific
metrics are recorded inline at their call sites."

## Two distinct pieces

1. **`install(port, gauge_idle_timeout_secs)`** (`metrics.rs:58-147`) —
   called exactly once, from `main.rs:170`, before `serve()` runs. It builds
   a `PrometheusBuilder`, binds its own HTTP listener on `port` via
   `.with_http_listener(([0,0,0,0], port))`, sets an idle timeout for
   gauge-kind metrics so gauges the relay stops emitting eventually drop out
   of the exposition rather than persisting forever, registers explicit
   per-metric histogram bucket boundaries (millisecond buckets for
   `http_request_latency_ms`; second-scale buckets for the git
   hydration/streaming/cache/compaction histograms and, via a `_seconds`
   suffix matcher, any other seconds-scale histogram; byte buckets for the
   git byte-count histograms; pack-count buckets for the git pack-count
   histograms; and count buckets for `buzz_fanout_recipients`), then calls
   `.build()`, installs the returned recorder as the process's single global
   recorder via `metrics::set_global_recorder`, and `tokio::spawn`s the
   returned exporter future. `build()`'s own contract (per `install()`'s
   doc comment) already spawns the upkeep task, so no separate call is
   needed. `install()` panics if a recorder is already installed or the port
   is in use — see *Failure mode* below.
2. **`track_metrics(req, next)`** (`metrics.rs:149-207`) — axum middleware,
   layered only onto the router `build_router` returns
   (`router.rs:203-206`, immediately before the HTTP trace layer and CORS
   layer), never onto the separate health-only router `build_health_router`
   constructs. It records `http_requests_total{code, caller, action}`
   (counter) and `http_request_latency_ms{code, caller, action}` (histogram)
   for every request that reaches it, except paths it deliberately skips
   (see *Metrics exclusion* below).

## `GET /metrics`

`GET /metrics` is served entirely by the exporter future `PrometheusBuilder
.build()` returns — bound to `config.metrics_port` inside `install()` via
`.with_http_listener` — not by any axum route on the relay's own app or
health routers. No `/metrics` handler function exists in
`crates/buzz-relay/src/router.rs`; the endpoint is a wholly separate HTTP
server the `metrics-exporter-prometheus` crate manages internally, serving
whatever the global recorder currently holds in Prometheus text exposition
format.

## Metrics exclusion

`track_metrics` matches the request's `MatchedPath` and returns early via
`next.run(req).await` — recording neither metric — for three cases: any path
starting with `/_` (the health-only router's route prefix, even though those
routes are not mounted on this router), the literal path `/health`, and the
literal path `/metrics` itself. It also returns early, unrecorded, when no
`MatchedPath` extension is present at all — unmatched/404 traffic — with an
inline comment stating this avoids a "cardinality bomb" from URI-scanning
traffic. For every other matched path, it records `code` (the exact HTTP
status code as a string), `caller` (from the `x-envoy-downstream-service-
cluster` header, validated to at most 64 ASCII alphanumeric/hyphen/underscore
bytes and defaulting to `"unknown"` — the header is mesh-trusted inside CAKE
but client-controlled on the public TCP listener, hence the validation), and
`action` (the matched route pattern, e.g. `/api/channels/{channel_id}` — not
the raw URI, to avoid unbounded cardinality from scanners).

## Configuration

`metrics_port` on the relay's `Config` struct is documented as "TCP port for
the Prometheus metrics exporter (`GET /metrics`)", read from
`BUZZ_METRICS_PORT` with a default of `9102` when unset or unparsable
(`config.rs:197-198`, `config.rs:823-826`). `install()`'s second argument,
`gauge_idle_timeout_secs`, is computed at the call site in `main.rs` from two
small helpers: `usage_metrics_interval_secs` (reads
`BUZZ_USAGE_METRICS_INTERVAL_SECS`, defaults to `300`, floors at `5`) feeds
`usage_metrics_idle_timeout_secs`, which delegates to `idle_timeout_secs`
(reads `BUZZ_USAGE_METRICS_IDLE_TIMEOUT_SECS` if set, else defaults to `900`,
then takes the max of that and `interval_secs * 3`) — ensuring the gauge
idle timeout always outlives several usage-poller ticks regardless of how
the poll interval is configured.

## Failure mode

`install()`'s own doc comment states it "Panics if a recorder is already
installed or the port is in use," and it is called exactly once from
`main()` before `serve()` runs. A misconfigured or colliding `metrics_port`
therefore prevents the relay process from starting at all, rather than
degrading metrics collection silently at runtime — a startup-time failure
mode, not a runtime one. (INFERENCE, confidence 0.75 — reasoned from the
docstring and single call site, not from an observed crash.)

## Dependencies

**Depends on**: `metrics`, `metrics-exporter-prometheus`, and `metrics-util`
— the three metrics-specific crates declared in
`crates/buzz-relay/Cargo.toml:79-81` — plus `config.metrics_port` (the value
`install()` is called with) and the two `main.rs` helper functions that
compute `gauge_idle_timeout_secs`.

**Depended on by**: `crates/buzz-relay/src/main.rs`, the sole caller of
`install()` (`main.rs:170`, via the `relay_metrics` alias imported at
`main.rs:21`); `crates/buzz-relay/src/router.rs`, which layers
`track_metrics` onto the main API router (`router.rs:25`, `router.rs:203`);
and, at the facade level named in this module's own doc comment but not
enumerated here, every call site elsewhere in the relay that emits a
Buzz-specific metric via `metrics::counter!`/`histogram!`/`gauge!` and relies
on this module's `install()` having already configured the global recorder
and its bucket boundaries.

## Boundary

This node does not describe:
- The health-only router or its four handlers (`/_liveness`, `/_readiness`,
  `/_status`, `/_mesh`) — that is `platforms-relay-health-server`'s subject
  (`#1272`, unmerged at this revision), referenced here only for the shared
  fact that `track_metrics` is layered onto the main router alone.
- The bucket-boundary rationale for any individual Buzz-specific histogram
  (why git hydration uses those particular second-scale buckets, why fanout
  uses those particular count buckets, etc.) — this node documents that
  `install()` is the single place those boundaries are configured, not why
  each subsystem's own boundary set was chosen; that belongs to each
  subsystem's own future component node.
- Prometheus scrape configuration, alerting rules, dashboards, or any
  deployment-side consumption of the `/metrics` endpoint — that is
  deployment/observability topology, owned by `architecture/deployment/*`
  nodes, not this component-level node.
- The full inventory of every `metrics::counter!`/`histogram!`/`gauge!` call
  site across the relay — this node names the module that installs the
  recorder and records framework-level HTTP metrics, not every subsystem
  that subsequently uses the facade.

## Relationships

- references: `architecture-containers-relay`

  This target exists on `origin/launchpad` at the recorded revision and
  already names the metrics listener at topology level ("a Prometheus
  metrics listener (default 0.0.0.0:9102, already bound by PrometheusBuilder
  before serve() is called)"; a routing-table row for "Metrics (TCP)"). This
  node's own content — handler/config/bucket-registration detail — does not
  duplicate that container-level topology mention, so `references` (cites
  target as supporting context, no ownership or currency dependency implied)
  is the correct relationship type rather than `depends-on`.

  No `depends-on` or `part-of` edge is declared toward any `platforms/**`
  sibling (e.g. `platforms-relay-health-server`, whose subject shares the
  same `track_metrics`-exclusion fact this node also states): at the
  recorded revision, `origin/launchpad`'s corpus tree contains no
  `platforms/**` node at all — every sibling exists only on its own unmerged
  task branch. Declaring an edge to any of them would resolve in this
  worktree but is a hard validation error on the branch this node is
  actually merging into, per `AGENTS.md`'s explicit warning about checking
  the merge-base tree rather than the author's own worktree. The first
  moment any `platforms/relay/*` node merges onto `origin/launchpad` is the
  right moment to add a `references` edge toward it for the shared
  metrics-exclusion fact.

## Scope and omissions

**This node covers** the relay's Prometheus metrics HTTP surface:
`install()`'s startup-time recorder/exporter/bucket-boundary configuration,
`GET /metrics`'s own separate HTTP listener, `track_metrics`'s per-request
HTTP metric recording and its path-based exclusions, the `metrics_port`/
`gauge_idle_timeout_secs` configuration inputs, and `install()`'s
startup-panic failure mode.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The health-only router and its four handlers | `platforms-relay-health-server` (unmerged sibling branch, `#1272`, at this revision) |
| Bucket-boundary rationale for individual Buzz-specific histograms (git hydration, fanout, etc.) | Each subsystem's own future component node, not yet written |
| Prometheus scrape/alerting/dashboard configuration and deployment topology | `architecture/deployment/*` nodes |
| The full inventory of Buzz-specific `metrics::counter!`/`histogram!`/`gauge!` call sites | Each emitting subsystem's own future component node |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating/updating/retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**
- No automated test was found exercising `install()` or `track_metrics()`
  directly, in either `crates/buzz-relay/tests/` or
  `crates/buzz-test-client/tests/`. The one reference found
  (`nip42_host_binding_live.rs:14`) is a doc-comment example showing how to
  avoid a `BUZZ_METRICS_PORT` collision between two concurrently run relay
  binaries in a live test, not a test of metrics recording or exposition
  behavior. This absence was checked by a targeted grep of both test
  directories, not by an exhaustive read of every integration test file.
- Whether `type: platforms` or `type: implementation` is the corpus's
  eventual settled convention for this path shape is unresolved by any
  accepted decision found at this revision; see the note under the title.
