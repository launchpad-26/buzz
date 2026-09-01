---
id: layers-observability-prometheus
type: layers
status: draft
origin: launchpad
audiences:
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision ed133f4c5dbd546a67d963f11ffa630a4513b228 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "buzz-relay's metrics module states the exposition pipeline directly in its own module doc: the metrics-rs facade (metrics::counter!, histogram!, etc.) feeds a PrometheusBuilder, which runs an HTTP listener on :9102, and GET /metrics on that listener serves Prometheus text format."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:1-15"
  - statement: "install(port, gauge_idle_timeout_secs) builds the recorder and exporter with PrometheusBuilder::new().with_http_listener(([0,0,0,0], port)), sets a gauge idle timeout (MetricKindMask::GAUGE) so gauge series the relay stops emitting are eventually removed from exposition, configures per-metric histogram bucket boundaries (an exact match on http_request_latency_ms, several exact matches on named buzz_git_* histograms, and a Suffix(\"_seconds\") matcher for the rest), installs the built recorder as the process-global metrics recorder via metrics::set_global_recorder, and spawns the returned exporter future onto the Tokio runtime -- build() already spawns its own internal upkeep task, so no separate upkeep call is made."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:59-147"
  - statement: "The Prometheus HTTP listener PrometheusBuilder binds is a separate embedded server from the relay's axum application router -- it is not a route registered on build_router's Router, and main.rs's own listener diagram lists it as a fourth, independently bound listener (\"Listener 4: TCP 0.0.0.0:9102 (metrics, via PrometheusBuilder -- already bound)\") alongside the TCP app router, the optional UDS app listener, and the health-only TCP listener."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1244-1253"
      - "crates/buzz-relay/src/router.rs:1-30"
  - statement: "relay_metrics::install(config.metrics_port, usage_idle_timeout_secs) is called once during relay startup, before the Postgres connection is established, and its port is logged at boot as both a structured config field (metrics_port) and in a dedicated \"Prometheus metrics exporter started\" info log."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:150-176"
  - statement: "config.rs's metrics_port field is documented as \"TCP port for the Prometheus metrics exporter (GET /metrics)\" and is read from the BUZZ_METRICS_PORT environment variable, parsed as an integer, defaulting to 9102 when unset or unparsable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:197-198"
      - "crates/buzz-relay/src/config.rs:823-826"
  - statement: "The exposition mechanism depends on three workspace-pinned crates: metrics = \"0.24\" (the recorder facade buzz-relay code calls, e.g. metrics::counter!/histogram!/gauge!), metrics-exporter-prometheus = \"0.18\" (PrometheusBuilder, the HTTP listener and the Prometheus text-format renderer), and metrics-util = \"0.20\" (MetricKindMask, used for the gauge idle-timeout policy)."
    entry_class: FACT
    evidence:
      - "Cargo.toml:91-93"
  - statement: "track_metrics is Axum middleware layered onto the application router (merged.layer(middleware::from_fn(track_metrics)) in build_router) that records two framework-level series -- http_requests_total and http_request_latency_ms, both labelled by code/caller/action -- via the same global metrics-rs recorder that PrometheusBuilder installed; it explicitly skips /_*, /health and /metrics paths so its own instrumentation traffic does not pollute the series it records."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:149-207"
      - "crates/buzz-relay/src/router.rs:202-205"
  - statement: "The /metrics path skip inside track_metrics is defensive against the app router only -- the actual scraped exposition endpoint lives on the separate metrics-port listener described above, not on any route the app router itself serves, so that skip guards against the hypothetical case of a request reaching the app router with that path rather than describing where scraping actually happens."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/metrics.rs:161-180"
      - "crates/buzz-relay/src/router.rs:1-30"
    confidence: 0.85
  - statement: "The Helm chart's Service template names a metrics port (port: {{ .Values.service.metricsPort }}, targetPort: metrics) alongside app and health, and values.yaml defaults service.metricsPort to 9102 -- the same default as BUZZ_METRICS_PORT -- confirming the chart wires a distinct named port for scraping rather than reusing the app or health ports."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/service.yaml:16-19"
      - "deploy/charts/buzz/values.yaml:239"
  - statement: "A Prometheus Operator ServiceMonitor for the relay is opt-in (serviceMonitor.enabled, default false in values.yaml), and when enabled selects the relay Service by the chart's own selector labels and scrapes the port named metrics at the configured interval (default 30s) and scrapeTimeout (default 10s)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/servicemonitor.yaml:1-30"
      - "deploy/charts/buzz/values.yaml:393-398"
  - statement: "The repository's dev-compose stack ships a standalone Prometheus container (prom/prometheus:latest) wired to the relay via host.docker.internal, and the root prometheus.yml scrape config it mounts targets host.docker.internal:9102 as job buzz-relay with a 5s scrape_interval -- reachable because the relay itself runs on the host, not inside Docker, in this dev topology."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.dev.yml:29-41"
      - "prometheus.yml"
  - statement: "PrometheusBuilder::new().build() and the exporter task it returns are documented by this node's author to panic (via .expect(...)) if a global metrics recorder is already installed or if the configured port is already in use, rather than returning a recoverable error -- this is stated in code comments on install(), and was not separately exercised by running the relay against an occupied port during authoring."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/metrics.rs:59-66"
      - "crates/buzz-relay/src/metrics.rs:142-146"
    confidence: 0.75
---

# Prometheus exposition

## Definition

**Prometheus exposition**, in buzz-relay, is the mechanism that turns metrics
recorded through the `metrics`-rs facade (`metrics::counter!`, `histogram!`,
`gauge!` call sites scattered through the relay's code) into a scrapeable
`GET /metrics` HTTP endpoint in the Prometheus text exposition format. The
relay's own module doc for this states the pipeline directly: the facade feeds a
`PrometheusBuilder`, which runs an HTTP listener bound at startup, and `GET
/metrics` on that listener serves Prometheus text format.

This node is scoped **only** to that exposition mechanism -- the embedded HTTP
listener, the exporter crate, the text format it serves, and how something else
(a Prometheus server, a Kubernetes `ServiceMonitor`) reaches it. It is **not**
about which metrics exist or what each one means: the catalog of Buzz-specific
series (`buzz_git_hydrate_seconds`, `buzz_fanout_recipients`,
`buzz_community_subscriptions`, and the rest) is a separate concern, covered by
the sibling `layers/observability/metrics` document (in progress alongside this
one; no corpus node for it exists yet to link to as a typed `relationships`
edge -- see *Scope and omissions*).

Do not confuse this with:

- **The conceptual metrics catalog** -- what each named series measures and why
  it exists. That belongs to the sibling `metrics` document, not here.
- **The health/readiness probes** -- `buzz-relay` exposes separate liveness and
  readiness endpoints on its own health-only listener (port 8080 by default);
  those are a Kubernetes probe surface, unrelated to Prometheus scraping, and
  are covered by their own sibling documents.
- **The `track_metrics` Axum middleware's own instrumentation** -- that
  middleware *records* two framework-level series (`http_requests_total`,
  `http_request_latency_ms`) using the same global recorder this document
  describes, but it runs on the relay's *application* router, not on the
  metrics-port listener itself.

## How it fits together

```text
┌───────────────────────────────────────────────────────────────┐
│  metrics-rs facade (metrics::counter!/histogram!/gauge!)      │
│  -- call sites throughout buzz-relay code                     │
│         │                                                     │
│         ▼                                                     │
│  Global recorder, installed once at boot by                   │
│  relay_metrics::install(port, gauge_idle_timeout_secs)         │
│         │                                                     │
│         ▼                                                     │
│  PrometheusBuilder-owned HTTP listener                         │
│  (separate from the app router; default 0.0.0.0:9102,          │
│   BUZZ_METRICS_PORT overrides it)                              │
│         │                                                     │
│         ▼                                                     │
│  GET /metrics -> Prometheus text-format body                  │
│         │                                                     │
│         ▼                                                     │
│  Scraper: Helm ServiceMonitor (opt-in, cluster) or a local     │
│  Prometheus container (dev-compose, host.docker.internal)      │
└───────────────────────────────────────────────────────────────┘
```

The listener this diagram shows is genuinely separate from `buzz-relay`'s
application router (the one serving WebSocket upgrades, `/events`, `/query`,
git smart HTTP, and so on). `main.rs`'s own listener-bind documentation names
four listeners the relay binds, and lists this one as already bound by
`PrometheusBuilder` before the app router's `serve()` call even begins --
it is not a route registered on the application `Router`.

## Startup and configuration

`install()` (in `crates/buzz-relay/src/metrics.rs`) is called once, early in
`main()`, before the Postgres connection is established. It:

- Binds the exporter's HTTP listener via
  `PrometheusBuilder::new().with_http_listener(([0, 0, 0, 0], port))`.
- Sets an idle timeout on gauge-kind series (`MetricKindMask::GAUGE`) so a
  gauge the relay has stopped emitting eventually drops out of exposition
  rather than reporting a stale value forever.
- Configures histogram bucket boundaries per metric: an exact match for
  `http_request_latency_ms` (millisecond buckets), several exact matches for
  named `buzz_git_*` histograms (seconds, byte and pack-count buckets suited to
  git hydration/streaming), and a catch-all `Suffix("_seconds")` matcher for
  every other seconds-scale histogram.
- Installs the built recorder as the process's one global `metrics` recorder
  (`metrics::set_global_recorder`) and spawns the exporter future onto Tokio --
  `build()` already spawns its own upkeep task internally, so no separate call
  is needed.

The port is configurable via `BUZZ_METRICS_PORT` (`config.rs`'s `metrics_port`
field), defaulting to `9102` when unset or unparsable -- the same default value
the Helm chart's `service.metricsPort` and the dev-compose scrape target both
assume.

Per this document's own reading of the install code (not separately exercised
by running the relay against an already-occupied port during authoring): a
second call to `install()`, or a call whose port is already bound, is expected
to panic rather than return a recoverable error, since the code path uses
`.expect(...)` on both the recorder-install and the builder-build steps.

## Use cases

- **Operating a relay in Kubernetes.** Enable the chart's `serviceMonitor` value
  so a Prometheus Operator installation scrapes the relay's `metrics`-named
  Service port automatically, without hand-writing scrape config.
- **Local development.** The dev-compose stack's `prometheus` container and the
  root `prometheus.yml` scrape config let a developer run `docker compose`
  alongside a host-run relay and see live series in a local Prometheus/Grafana
  stack without any cluster.
- **Diagnosing whether the exposition endpoint itself is healthy** -- distinct
  from diagnosing whether a *specific metric's value* is correct, which needs
  the metrics catalog sibling document, not this one.

## Scope and omissions

**This document covers** the Prometheus exposition mechanism in `buzz-relay`:
the embedded HTTP listener `PrometheusBuilder` binds, the exporter crate and its
pinned version, the `GET /metrics` text-format endpoint, its port configuration,
and how the Helm chart and the local dev-compose stack scrape it.

**This document does not cover, and these are named gaps rather than silence:**

- **The conceptual metrics catalog** -- what each named series (`buzz_git_*`,
  `buzz_fanout_recipients`, `buzz_community_subscriptions`, and the rest) means
  and why it exists. Owned by the sibling `layers/observability/metrics`
  document.
- **Health/liveness/readiness probes** -- a separate Kubernetes-probe surface on
  the health-only listener, owned by sibling `liveness`/`readiness` documents.
- **Structured logging and tracing** -- separate observability surfaces, owned
  by their own sibling documents.
- **No `relationships` are declared on this node.** The issue's definition of
  done asks for "typed relationships appropriate to the node," but
  `AGENTS.md`'s node-creation rules require a relationship target to exist on
  the branch being merged into (`origin/launchpad`), and at the revision this
  node was authored against, `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` shows no `layers/` node at all -- not even the sibling
  `metrics` document this node would most naturally reference. A `references`
  edge from this node to that sibling (or vice versa) is left for whichever of
  the two merges second, or a deliberate follow-up edit; inventing an edge to
  an id that does not yet exist on the merge target would be a hard validation
  error per `AGENTS.md`.
- **Expected but not independently verified when this node was written:**
  whether `install()` genuinely panics (rather than erroring gracefully) when
  called twice or against an occupied port was reasoned from the `.expect(...)`
  calls in the source, not confirmed by actually triggering either condition
  against a running relay.
