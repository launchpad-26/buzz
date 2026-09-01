---
id: layers-observability-metrics
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
  - statement: "The Rust workspace pins metrics = \"0.24\" (the metrics-rs facade, metrics::counter!/gauge!/histogram!), metrics-exporter-prometheus = \"0.18\" (the Prometheus exporter/recorder), and metrics-util = \"0.20\" (MetricKindMask and related helpers) at the workspace level, so every crate that emits metrics shares one dependency version."
    entry_class: FACT
    evidence:
      - "Cargo.toml:91-93"
  - statement: "buzz-relay's metrics.rs installs the global metrics-rs recorder and a Prometheus HTTP exporter via PrometheusBuilder::new().with_http_listener(([0,0,0,0], port)), where port comes from Config::metrics_port; metrics::set_global_recorder panics if called more than once per process, so install() may run exactly once."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:59-147"
  - statement: "Config::from_env reads metrics_port from the BUZZ_METRICS_PORT environment variable, parsing it and defaulting to 9102 when unset or unparsable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:823-826"
  - statement: "buzz-relay's metrics.rs configures distinct histogram bucket boundaries per metric name or suffix via PrometheusBuilder::set_buckets_for_metric: millisecond buckets for http_request_latency_ms, second-scale buckets for git hydration/pack-cache/compaction operations and for any metric name ending in \"_seconds\" (the general internal-processing default), byte buckets for git hydration/streaming/compaction sizes, pack-count buckets for git pack operations, and a dedicated bucket set for buzz_fanout_recipients, rather than one bucket layout shared by every histogram."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:27-141"
  - statement: "buzz-relay's install() configures idle_timeout only for MetricKindMask::GAUGE, using a caller-supplied gauge_idle_timeout_secs, so the Prometheus exporter drops gauge series that stop being emitted after that timeout while counters and histograms are not subject to the same idle eviction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:66-73"
  - statement: "buzz-relay's track_metrics Axum middleware records http_requests_total (a counter) and http_request_latency_ms (a histogram), labeled by code (exact HTTP status), caller (from the Istio x-envoy-downstream-service-cluster header, validated to at most 64 ASCII alphanumeric/hyphen/underscore bytes and defaulting to \"unknown\" otherwise), and action (the matched Axum route pattern, e.g. /api/channels/{channel_id}); health/metrics paths (/_*, /health, /metrics) and requests with no matched route are skipped specifically to avoid unbounded cardinality from 404 scanner traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs:149-207"
  - statement: "buzz-relay's main() calls relay_metrics::install(config.metrics_port, usage_idle_timeout_secs) once at startup, immediately followed by setting buzz_audit_enabled and buzz_push_enabled gauges from the loaded config, before any other subsystem (database, Redis, WebSocket listener) is initialized."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:168-177"
  - statement: "buzz-relay's EmissionScope enum (BUZZ_USAGE_METRICS_PER_COMMUNITY, values \"all\"/\"off\", defaulting to \"all\" including on an unrecognized value) gates whether per-community usage gauge series (~25 label combinations per community, per the source comment) are emitted at all; the comment states this exists because Datadog's cost is proportional to unique time-series count, and that fleet-wide buzz_total_* gauges always emit regardless of this setting."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:39-92"
  - statement: "Across buzz-relay's handler and subsystem modules, metrics fall into three shapes distinguished by name suffix and call pattern: counters ending in _total that only ever call .increment(n) (e.g. buzz_events_received_total, buzz_auth_failures_total, buzz_git_hydrations_total, buzz_ws_backpressure_disconnects_total), gauges that call .set(...), .increment(...), or .decrement(...) to track a current level (e.g. buzz_ws_connections_active, buzz_db_pool_size, buzz_community_storage_bytes), and histograms that call .record(...) to capture a distribution (e.g. buzz_event_processing_seconds, buzz_git_hydrate_seconds, buzz_fanout_recipients, buzz_ws_send_batch_size)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/storage_sweep.rs"
      - "crates/buzz-relay/src/api/git/hydrate.rs:135-147"
  - statement: "crates/buzz-push-gateway/src/metrics.rs installs a second, independent metrics-rs/Prometheus setup for that binary: its install() calls PrometheusBuilder::new()...install_recorder() with no with_http_listener call at all, and its module doc states metrics are rendered from the private health router (port 8081) rather than a public port, unlike buzz-relay's public :9102 listener."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/metrics.rs:1-40"
  - statement: "buzz-push-gateway's metrics.rs module doc states every label value it emits is a compile-time &'static str drawn from a closed set (DeliveryOutcome variants, fixed error codes, handler stages) and explicitly that no endpoint, device token, relay pubkey, request id, or other request-scoped identifier is ever used as a label, so cardinality is structurally bounded regardless of traffic volume."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/metrics.rs:12-17"
  - statement: "crates/buzz-db/src/runtime/observability.rs states in its module doc that label values come only from the closed enums defined in that module (PoolRole, LockType, Outcome) and that callers must never derive labels from tenant data, events, SQL text, or query identifiers; crates/buzz-db/src/store/usage.rs's module doc states its returned structs are plain data mapped by the relay's usage poller to Prometheus gauge labels via metrics::gauge!(...).set(...)."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/observability.rs:1-4"
      - "crates/buzz-db/src/store/usage.rs:1-13"
  - statement: "ARCHITECTURE.md documents a local docker-compose Prometheus service (prom/prometheus) bound to port 9090 whose stated purpose is \"Metrics collection\" — a separate scrape-side component from the relay's own :9102 metrics-exposition port that it presumably scrapes."
    entry_class: FACT
    evidence:
      - "ARCHITECTURE.md:780"
  - statement: "Neither #1138 (observability-liveness) nor #1139 (logging) nor #1142 (prometheus) has a merged corpus node on origin/launchpad at this node's recorded revision (checked via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, which shows no layers/ path at all), so no relationships edge to any of them exists yet."
    entry_class: FACT
    evidence:
      - "commit ed133f4c5dbd546a67d963f11ffa630a4513b228"
  - statement: "Whether the local docker-compose Prometheus server (ARCHITECTURE.md:780) is actually configured to scrape the relay's :9102 endpoint, versus documented as intended but not wired up, was not traced into a docker-compose.yml scrape_configs block for this node."
    entry_class: INFERENCE
    evidence:
      - "ARCHITECTURE.md:780"
      - "crates/buzz-relay/src/config.rs:823-826"
    confidence: 0.6
  - statement: "Issue #1140's parent PRD is #611, and the issue names #1142 (prometheus) as the sibling task owning exposition-format/scrape-endpoint mechanics that this general metrics node must not duplicate, per the batch-run brief that dispatched this task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1140 task dispatch brief (corpus-batch-author, Feature #611 batch run)"
---

# Metrics

## Definition

**Metrics**, in Buzz, are numeric measurements of running-system behavior emitted through
the Rust [`metrics`](https://docs.rs/metrics) facade (`metrics::counter!`, `gauge!`,
`histogram!`) and exposed in Prometheus exposition format for scraping. The workspace pins
one version of the facade (`metrics = "0.24"`) and its Prometheus exporter
(`metrics-exporter-prometheus = "0.18"`) so every crate that emits metrics shares the same
underlying machinery, even though — as described below — not every binary wires that
machinery up the same way.

Three kinds of metric appear throughout the codebase, distinguished by call pattern and
naming convention:

- **Counters** — monotonically increasing totals, named with a `_total` suffix
  (`buzz_events_received_total`, `buzz_auth_failures_total`), incremented with
  `.increment(n)`. They answer "how many of this happened."
- **Gauges** — a current level that can go up or down, set or adjusted with `.set(...)`,
  `.increment(...)`, or `.decrement(...)` (`buzz_ws_connections_active`,
  `buzz_db_pool_size`, `buzz_community_storage_bytes`). They answer "what is the value
  right now."
- **Histograms** — distributions of observed values, recorded with `.record(...)`
  (`buzz_event_processing_seconds`, `buzz_git_hydrate_seconds`, `buzz_fanout_recipients`).
  They answer "what does the spread of this look like."

This node is the **general/umbrella concept**: what a metric is in Buzz, the three kinds and
what each is for, where each surface installs its own recorder, and the cost/cardinality
concerns that shape how metrics are emitted. It does not describe the Prometheus wire
format or scrape-endpoint mechanics themselves (that is #1142's territory) or enumerate
every metric name in the workspace (see *Boundaries and non-goals*).

## How metrics are installed, per surface

**`buzz-relay`.** The most fully-built surface, and the only one exposing metrics on a
public port. `crates/buzz-relay/src/metrics.rs`'s `install(port, gauge_idle_timeout_secs)`
builds a `PrometheusBuilder`, attaches an HTTP listener on the given port (default `9102`,
overridable via `BUZZ_METRICS_PORT`), configures per-metric-name-or-suffix histogram bucket
boundaries (millisecond buckets for HTTP latency, second-scale buckets for git and other
internal processing, byte and pack-count buckets for git operations, a dedicated bucket set
for fan-out recipient counts), sets an idle timeout that applies **only to gauges**
(`MetricKindMask::GAUGE`) so stale gauge series are dropped from the exporter after they
stop being emitted while counters and histograms are not subject to that eviction, and
installs the result as the process-global recorder — `metrics::set_global_recorder` panics
if called a second time, so `install()` must run exactly once. `main()` calls it
immediately at startup, before the database, Redis, or WebSocket listener are initialized,
and follows it directly with two config-derived gauges (`buzz_audit_enabled`,
`buzz_push_enabled`). A dedicated Axum middleware, `track_metrics`, records the CAKE
framework's own HTTP metrics (`http_requests_total` counter, `http_request_latency_ms`
histogram) labeled by status code, an Istio-header-derived caller identity, and the
*matched route pattern* rather than the raw URI — deliberately, to avoid an unbounded
cardinality blowup from scanner traffic hitting nonexistent paths. Everywhere else in
`buzz-relay`'s handlers and subsystems, Buzz-specific counters, gauges, and histograms are
recorded inline at their call sites (authentication, git hydration and pack caching, push
delivery, storage sweeps, WebSocket connection lifecycle, and more) rather than centralized
in one module.

**Per-community emission cost control.** A block of periodic usage gauges
(`buzz_community_*`, `buzz_total_*`) is gated by `EmissionScope`, read from
`BUZZ_USAGE_METRICS_PER_COMMUNITY` (`"all"` or `"off"`, defaulting to `"all"` including on
an unrecognized value). The source comment states the reason directly: Datadog's cost is
proportional to the number of unique time-series, roughly 25 gauge label combinations per
community, so a relay hosting thousands of communities could incur five-figure monthly
costs emitting a full per-community series set unconditionally. Fleet-wide `buzz_total_*`
gauges always emit regardless of this setting — only the per-community breakdown is
gated.

**`buzz-push-gateway`.** A second, independent installation of the same `metrics`/
Prometheus machinery, shaped differently on purpose: `install()` calls
`PrometheusBuilder::new()...install_recorder()` with **no** HTTP listener attached at all.
Its module doc states metrics are instead rendered from the gateway's private health
router (port 8081), so metrics never share the public port — a different exposure model
from the relay's public `:9102` listener, even though both use the same underlying crates.
Its module doc also states a cardinality guarantee directly: every label value is a
compile-time `&'static str` drawn from a closed set (delivery-outcome variants, fixed
error codes, handler stages), and explicitly that no endpoint, device token, relay pubkey,
request id, or other request-scoped identifier is ever used as a label.

**`buzz-db`.** Does not install its own recorder or exporter — it emits into whichever
recorder the hosting binary (`buzz-relay`) has already installed. `runtime/observability.rs`
states the same bounded-cardinality discipline as the push gateway, but as an explicit rule
for its own label enums (`PoolRole`, `LockType`, `Outcome`): label values come only from
those closed enums, and callers must never derive a label from tenant data, events, SQL
text, or query identifiers. `store/usage.rs` supplies plain-data usage rollups that the
relay's usage poller maps to `metrics::gauge!(...).set(...)` calls — the query layer itself
never touches the `metrics` facade.

**Local scrape side.** `ARCHITECTURE.md` documents a docker-compose Prometheus service
bound to port `9090` for local development, described as the "Metrics collection"
component — the scrape-side counterpart to the relay's exposition port. This node does not
trace whether that local Prometheus is actually configured to scrape `:9102`, versus
documented as the intended pairing; see *Scope and omissions*.

## Use cases

A reader reaches for this node to understand, before touching any one surface's specifics:
what a metric is in Buzz and which of the three kinds (counter, gauge, histogram) a given
name implies from its suffix and call site; why some metrics are gated behind an
environment variable (`EmissionScope`) while others always emit; why two binaries
(`buzz-relay`, `buzz-push-gateway`) both use the `metrics` crate but expose their data
completely differently (public port vs. private health-router route); and why label values
throughout the codebase are deliberately drawn from closed, bounded sets rather than
request-scoped identifiers — a cost and cardinality discipline that recurs across every
surface this node inspected.

## Boundaries and non-goals

This node does **not** cover:

- **Prometheus exposition format and scrape-endpoint mechanics** — the wire format
  `PrometheusBuilder`'s HTTP listener actually serves, `GET /metrics` response shape, or
  scrape-configuration details. That is issue #1142's (prometheus) territory; this node
  states only that such an exporter exists per surface and where it listens, not how the
  wire protocol works.
- **A catalogue of every metric name in the workspace.** Dozens of `metrics::counter!`/
  `gauge!`/`histogram!` call sites exist across `buzz-relay`, `buzz-push-gateway`, and
  `buzz-db`. This node names representative examples of each kind rather than enumerating
  all of them — an exhaustive list would be a generated-view candidate (derived from the
  source, not hand-authored) and would drift out of date the moment a new metric is added,
  which is exactly the kind of content `AGENTS.md` says does not belong in a hand-authored
  node.
- **Structured logging** (#1139, `layers-observability-logging`) and **datastore tracing
  policy** (#1136, datastore-tracing) — separate observability concerns with their own
  sibling tasks, not described here.
- **Operational dashboarding, alerting, or Datadog-side configuration** — this node
  describes what Buzz emits and why, not what a downstream observability platform does
  with it afterward.

## Scope and omissions

**This document covers** what a metric is in Buzz (the `metrics`-crate facade, the three
kinds and their naming/call conventions), how each surface this node inspected (`buzz-relay`
public exporter and inline call sites, the `EmissionScope` cost-control gate,
`buzz-push-gateway`'s private-router-only exporter, `buzz-db`'s bounded-cardinality label
convention) actually installs and emits metrics, at the recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Prometheus exposition format / scrape-endpoint mechanics | #1142 (prometheus), not yet a merged corpus node |
| Structured logging conventions | #1139 (logging), not yet a merged corpus node |
| Datastore tracing policy macros | #1136 (datastore-tracing), open task |
| Exhaustive per-metric name/label catalogue | Not attempted here — see *Boundaries and non-goals* |
| Whether the local docker-compose Prometheus (`:9090`) is actually configured to scrape the relay's `:9102` endpoint | Not investigated for this node |

**Expected but not verified when this node was written:**

- **Whether the local docker-compose Prometheus service is wired to scrape the relay's
  metrics port.** `ARCHITECTURE.md` documents both components, but this node did not open a
  `docker-compose.yml` scrape-config block to confirm the pairing is actually configured
  rather than merely intended — recorded as an INFERENCE with `confidence: 0.6`, not a
  FACT, in the evidence ledger.
- **No `relationships` are declared.** At this node's recorded revision, `origin/launchpad`
  carries no `layers/` corpus path at all — the sibling nodes for logging (#1139),
  liveness (#1138), and Prometheus (#1142) exist only as unmerged commits on other
  worktree branches. Declaring a `relationships[].target` against any of them would be a
  hard validation error once this node lands ahead of them. This is a fact about this
  moment, checked directly via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`, not a general policy.
