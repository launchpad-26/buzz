---
id: operations-runbooks-high-error-rate
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The relay's `track_metrics` Axum middleware records `http_requests_total` and `http_request_latency_ms`, both labeled `code` (the exact HTTP status code as a string), `caller` (from the `x-envoy-downstream-service-cluster` header, falling back to the literal string `unknown`), and `action` (the matched route pattern, e.g. `/api/channels/{channel_id}`), and it explicitly returns early — recording nothing — for any path starting with `/_`, for `/health`, and for `/metrics` itself, plus any request with no matched route at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
  - statement: "The Prometheus exposition endpoint is `GET /metrics` on a dedicated embedded HTTP listener that `relay_metrics::install` binds separately from the main relay listener and the health listener, on the port `BUZZ_METRICS_PORT` names, defaulting to `9102` when that variable is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/metrics.rs"
      - "crates/buzz-relay/src/config.rs:823-826"
  - statement: "`GET /_readiness` runs three dependency checks concurrently under a 2-second timeout — `Db::ping` against Postgres, obtaining a connection from the Redis pool, and validating the deletion-serving catalog — and returns HTTP 200 with `{\"status\":\"ready\"}` only if all three succeed; otherwise it returns HTTP 503, either `{\"status\":\"shutting_down\"}` while the process is draining, or a body naming exactly which of `postgres`, `redis`, and `deletion_catalog` came back false."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-449"
  - statement: "`readiness_handler` contains no `metrics::counter!`, `histogram!`, or `gauge!` call on any of its branches, so neither a readiness failure nor a successful readiness check increments or sets any Prometheus series; the endpoint's own JSON response, polled directly, is the only signal it produces."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:409-449"
  - statement: "`GET /_liveness` is unconditional: its handler always returns HTTP 200 with the body `ok`, independent of any dependency state, and is registered on both the main API router and the separate health-only router that `build_health_router` assembles."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:405-407"
      - "crates/buzz-relay/src/router.rs:291-301"
  - statement: "The health-only router — `/_liveness`, `/_readiness`, `/_status`, `/_mesh` — is bound on its own TCP listener at `BUZZ_HEALTH_PORT`, defaulting to `8080` when unset, distinct from the main relay listener (`BUZZ_BIND_ADDR`, defaulting to `0.0.0.0:3000`) and from the metrics listener."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:818-821"
      - "crates/buzz-relay/src/main.rs:1296-1299"
  - statement: "At startup the relay emits one structured log event naming `bind_addr`, `relay_url`, `health_port`, and `metrics_port` under the message \"Config loaded\", and a second naming `port` and `idle_timeout_secs` under \"Prometheus metrics exporter started\" — reading these two lines is the fastest way to learn which ports a given running instance actually bound before assuming this document's defaults apply."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:157-177"
  - statement: "All relay logs are emitted as JSON via `tracing_subscriber`'s `fmt::layer().json()`, filtered by the `RUST_LOG` environment variable which defaults to `buzz_relay=info` when unset, and handler code attaches structured fields — for example `event_id` and `error` — to individual log events rather than relying on free-text messages alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:8-10"
      - "crates/buzz-relay/src/main.rs:130-136"
      - "crates/buzz-relay/src/handlers/event.rs:724"
  - statement: "When `OTEL_EXPORTER_OTLP_ENDPOINT` is set, the JSON log formatter additionally injects lowercase-hexadecimal `trace_id` and `span_id` fields into any log event whose span resolves to a valid OpenTelemetry context; when that variable is unset, tracing initialization is a no-op and log lines carry no such fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/telemetry.rs:79-115"
      - "crates/buzz-relay/src/telemetry.rs:1-19"
  - statement: "Over the WebSocket protocol the relay sends machine-parseable reason strings prefixed `error:`, `invalid:`, `restricted:`, `rate-limited:`, `blocked:`, or `auth-required:` inside NOTICE, OK, and CLOSED frames; the equivalent HTTP surfaces (the NIP-98 bridge and the git-over-HTTP transport) return the same prefixes as response bodies alongside a 4xx or 5xx status."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/connection.rs:575"
      - "crates/buzz-relay/src/handlers/auth.rs:164"
      - "crates/buzz-relay/src/handlers/report.rs:59"
      - "crates/buzz-relay/src/api/git/transport.rs:224"
      - "crates/buzz-relay/src/handlers/count.rs:91"
  - statement: "Several rejection classes are broken out into their own Prometheus counters, independent of `http_requests_total`: `buzz_auth_failures_total{reason}`, `buzz_admission_rejections_total{transport,reason}` (`reason` is `quota` or `unavailable`), `buzz_ws_backpressure_disconnects_total`, `buzz_ws_auth_timeouts_total`, and `buzz_audit_send_errors_total` among them — so a spike confined to one of these is diagnosable without first correlating raw log lines."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs:84"
      - "crates/buzz-relay/src/connection.rs:721"
      - "crates/buzz-relay/src/connection.rs:106"
      - "crates/buzz-relay/src/connection.rs:266"
      - "crates/buzz-relay/src/handlers/event.rs:599"
  - statement: "This repository defines no Prometheus alerting rule file and no Alertmanager configuration anywhere in the tree. The only Prometheus instance wired up anywhere in the repository is the `prometheus` service in the root `docker-compose.yml`, exposed to the host at `http://127.0.0.1:9090` and configured by the root `prometheus.yml`, which scrapes only the relay's `/metrics` and declares no `rule_files:` section."
    entry_class: FACT
    evidence:
      - "prometheus.yml"
      - "docker-compose.yml"
  - statement: "The only environment in this fork with a public, internet-facing relay — the \"Cohort VPS\" row — is marked status `OPEN`, not `IMPLEMENTED`, as of this node's recorded revision, and the same document states no hostname has been decided for it."
    entry_class: FACT
    evidence:
      - "launchpad/ENVIRONMENTS.md"
  - statement: "An ADR-shaped issue proposing an observability strategy for this cohort recorded, among its decision drivers, that nobody is on call and there is no rota, and listed 'alerting as part of the first answer' under expected rejections for exactly that reason; the issue itself was closed not-planned rather than accepted, so this is a documented consideration on record, not a settled decision this node can rely on as current policy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#83 (closed, not planned), Decision drivers and Considered options sections"
  - statement: "An open PRD scopes a fleet-wide observability strategy for Buzz, 'queryable by humans and agents', that would be the natural place a future alerting or paging pipeline for an elevated relay error rate gets decided, if the cohort ever builds one."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#289"
  - statement: "The established idiom elsewhere in this repository for a scripted readiness check is `curl --silent --fail --max-time 1 \"http://127.0.0.1:${health_port}/_readiness\"`, used identically by the pre-push relay launcher and the desktop release-smoke script."
    entry_class: FACT
    evidence:
      - "Justfile:572"
      - "scripts/run-desktop-release-smoke.sh:125"
  - statement: "28 call sites across `crates/buzz-relay/src/api/` and `crates/buzz-relay/src/handlers/` return `StatusCode::INTERNAL_SERVER_ERROR`; since `/_readiness` already fails closed (returns 503) the moment Postgres, Redis, or the deletion-serving catalog is unreachable, an elevated `http_requests_total{code=\"500\"}` ratio while `/_readiness` keeps reporting `ready` more plausibly traces to a handler-level failure — a `?`-propagated error surfaced generically — than to a dependency outage, which readiness would already be surfacing on its own."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:2555"
      - "crates/buzz-relay/src/router.rs:409-449"
    confidence: 0.6
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook's body to carry Trigger, Severity and impact, Diagnosis, Mitigation and resolution, Escalation, and Scope-and-omissions sections, each traceable to the Google SRE Workbook's playbook definition."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: layers-observability-metrics
  - type: references
    target: layers-observability-readiness
  - type: references
    target: layers-observability-liveness
  - type: references
    target: layers-observability-health-checks
  - type: references
    target: layers-observability-logging
  - type: references
    target: layers-observability-structured-logging
  - type: references
    target: layers-observability-prometheus
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-containers-redis
  - type: references
    target: capabilities-moderation-moderation
---

# High error rate (relay)

## Trigger

There is no configured alert for this condition anywhere in this repository — see
*Scope and omissions* — so "trigger" here means the observable condition a responder
notices, checks for deliberately, or is told about, rather than a paging system firing.

The condition is: the relay's request-outcome counter, `http_requests_total`, shows an
elevated share of non-2xx `code` values over a recent window, for one or more `action`
route patterns, sustained rather than a single blip. Concretely, with the local Prometheus
this repository ships (`http://127.0.0.1:9090`, scraping the relay's `/metrics`), the
query is:

```
sum(rate(http_requests_total{code=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m]))
```

There is no dashboard or saved query for this in the repository — the query above is
written out here because nothing runs it automatically. A responder may also arrive here
because of a symptom on the client side (repeated `error:`-prefixed CLOSED/NOTICE frames
over WebSocket, or 5xx bodies from `/events`, `/query`, or `/count`) before ever looking
at a metric.

**What this metric does not include.** `track_metrics` skips `/_liveness`, `/_readiness`,
`/_status`, `/_mesh`, `/health`, and `/metrics` itself. A responder who queries
`http_requests_total` and sees nothing wrong has *not* ruled out a readiness failure —
only ruled out elevated error responses on ordinary API traffic. Check `/_readiness`
directly (see *Diagnosis*, step 1) regardless of what the counter shows.

## Severity and impact

- **Elevated 5xx on `/events`, `/query`, `/count`, or the WebSocket path** — clients
  cannot submit or read events. This is the direct-impact case: real user- or
  agent-initiated work is failing.
- **Elevated `rate-limited:`, `restricted:`, or `auth-required:` responses** — these are
  the relay's admission control and authorization working as designed (see *Diagnosis*,
  step 4), not necessarily a defect. Note where they do and do not surface: on the HTTP
  bridge they carry an HTTP status and so land in `http_requests_total`, but on the
  WebSocket path they are `NOTICE`/`CLOSED`/`OK`-with-`false` frames sent *after* the
  101 upgrade, and `track_metrics` records only the status Axum itself produced — so a
  WebSocket flood of rejections moves the logs and the admission counters but **not**
  the HTTP error rate. Separate them from genuine failures before calling this an
  incident, and do not read a flat `http_requests_total` as proof the WebSocket surface
  is healthy.
- **`/_readiness` reporting `not_ready`** — new connections and HTTP requests may still be
  accepted by the process (readiness gates orchestration, not admission), but the
  dependency it named (`postgres`, `redis`, or `deletion_catalog`) is degraded, which is
  usually the more urgent problem even if `http_requests_total` has not moved yet.

Urgency scales with how much of the traffic is affected (a spike on one `action` route
versus a broad rise across all of them) and how long it persists — a five-minute window is
a diagnostic starting point, not a severity threshold this repository defines anywhere.

## Prerequisites

- Shell or exec access to the running relay process or its container, sufficient to run
  `curl` against the health and metrics ports.
- If running the local development stack: `docker compose ps` / `docker compose logs`
  access (per the root `docker-compose.yml`), and a browser or `curl` reachable to
  `http://127.0.0.1:9090` for the local Prometheus UI.
- Knowledge of which ports this instance actually bound — read its "Config loaded"
  startup log line (see the front-matter evidence entry citing
  `crates/buzz-relay/src/main.rs:157-177`) rather than assuming the `8080` / `9102` / `3000`
  defaults, since `BUZZ_HEALTH_PORT`, `BUZZ_METRICS_PORT`, and `BUZZ_BIND_ADDR` can all
  override them.
- No credential is required to read `/_liveness`, `/_readiness`, `/_status`, or
  `/metrics` — none of the four health-router routes carry auth in this codebase. Do not
  paste any secret value into a ticket or chat message while gathering evidence below;
  link to the configuration that holds it (for example, the relay's own environment
  configuration) instead of copying it out.

## Diagnosis

Work top-down: is the process alive, is it ready, is the error concentrated somewhere,
then read logs for the specific failure.

1. **Confirm the process is alive and not draining.**
   ```
   curl --silent --fail --max-time 1 "http://127.0.0.1:${health_port:-8080}/_liveness"
   curl --silent --fail --max-time 1 "http://127.0.0.1:${health_port:-8080}/_readiness"
   ```
   (This is the same idiom the repository's own pre-push relay launcher and release-smoke
   script use.) `/_liveness` failing to respond at all means the process is down or
   unreachable — that is a different runbook than an elevated error *rate*. `/_readiness`
   returning `{"status":"shutting_down"}` means the instance is mid-drain, which will
   self-resolve; returning `{"status":"not_ready", ...}` names exactly which dependency
   (`postgres`, `redis`, `deletion_catalog`) is failing.

2. **Query the request-outcome breakdown.** Against the local Prometheus UI (or
   `curl http://127.0.0.1:${metrics_port:-9102}/metrics` and read the raw exposition if no
   Prometheus is running), break `http_requests_total` down by `code` and `action` to find
   whether the elevated rate is one route or the whole surface, and whether it is 5xx
   (server-side) or 4xx (often client-side: malformed input, auth, or rate limiting).

3. **Cross-reference against readiness.** An elevated 5xx ratio while `/_readiness` keeps
   reporting `ready` points toward a handler-level failure rather than a dependency
   outage — readiness already fails closed the moment Postgres, Redis, or the
   deletion-serving catalog is unreachable. An elevated ratio *coinciding* with
   `/_readiness` reporting `not_ready` points at the named dependency instead; diagnosing
   that dependency in depth is out of scope here (see *Scope and omissions*).

4. **Separate deliberate rejections from failures.** Query the narrower counters —
   `buzz_auth_failures_total{reason}`, `buzz_admission_rejections_total{transport,reason}`,
   `buzz_ws_backpressure_disconnects_total`, `buzz_ws_auth_timeouts_total`,
   `buzz_audit_send_errors_total` — before assuming every non-2xx response is a bug. A
   `rate-limited:` or `restricted:` reason string is the relay's admission control or
   authorization behaving as designed; only a genuine spike in one of these (versus its
   normal baseline) or a sustained rise with no known cause is actionable the same way an
   unexplained 500 is.

5. **Read the structured JSON logs for the affected window.** Filter by `level` and, if
   the failure is scoped to one request, by whatever `event_id` or similar field the
   affected handler attaches. If `OTEL_EXPORTER_OTLP_ENDPOINT` was set when the instance
   started, log lines from the same request or connection share a `trace_id` — use it to
   pull every log line for one failing request rather than guessing from timestamps alone.
   `RUST_LOG` (default `buzz_relay=info`) controls how much is emitted; a responder who
   needs more detail than `info` restarts the process with a higher level, which is itself
   a disruptive mitigation-adjacent step — weigh it against the impact in *Severity and
   impact* before doing it on a process serving live traffic.

6. **If the failure is entirely inside one `action` route,** check the code path that
   route's handler runs. `StatusCode::INTERNAL_SERVER_ERROR` is returned from many
   distinct call sites in this codebase, so the specific log line at the failure's
   timestamp — not the fact that it is a 500 — is what identifies the actual defect.

## Mitigation and resolution

- **`/_readiness` names a failing dependency.** Restarting the relay process does not fix
  a down Postgres or Redis — it only restarts a process that will immediately report
  `not_ready` again. Resolving the dependency itself is out of scope for this node (see
  *Scope and omissions*); this runbook's job stops at correctly identifying which
  dependency it is.
- **A specific `action` route is failing and a recent deploy changed it.** `GET /_status`
  reports the running build's `source_sha` and `build.id`. If the elevated rate began at
  or shortly after a deploy, rolling back to the previous build is a faster mitigation
  than debugging forward, and confirming the rollback landed is exactly what `/_status`
  is for.
- **`buzz_admission_rejections_total{reason="quota"}` or `rate-limited:` frames dominate
  the count.** This is the relay's load-shedding working as intended, not a defect by
  itself. Decide whether traffic has legitimately grown (a capacity question, out of
  scope here) or one client is misbehaving; a misbehaving client is a moderation action
  (banning), which this node does not itself specify — see *Scope and omissions*.
- **`buzz_ws_backpressure_disconnects_total` is elevated.** This means the relay is
  disconnecting WebSocket clients that cannot keep up with their own outbound message
  queue. It is evidence about the client population (many slow consumers) more than
  about the relay itself; investigate what changed for those clients before treating the
  relay as broken.
- **The failure is a genuine handler bug reproducible independent of any dependency
  state.** Restarting the process is a valid mitigation of last resort — it clears any
  bad in-process state — but it drops every open WebSocket connection and in-flight
  request on that instance, so treat it as a real cost, not a free first step, and prefer
  a build rollback (above) when the timing points at a specific deploy.
- **No step above is a deterministic command sequence to run unconditionally on every
  occurrence of this condition** — each branches on what diagnosis actually found, which
  is the template this node is built against calling out explicitly: a runbook that has
  degenerated into one fixed command sequence with no decision point is a sign the step
  should be automation instead of documentation.

## Escalation

**There is no on-call rotation, PagerDuty, or Alertmanager route configured anywhere in
this fork as of the recorded revision**, and the one environment where "escalation" would
mean paging a rotation — a public, internet-facing relay — does not exist yet (see the
`ENVIRONMENTS.md` evidence entry above). An ADR-shaped issue that considered building
alerting for this cohort was closed not-planned, on the recorded grounds that "nobody is
on call, and there is no rota" and "an alert with no recipient produces noise, not
detection" — cited above as `TEAM_KNOWLEDGE`, not as settled policy, since that issue was
never accepted.

Given that, escalation today means:

1. If diagnosis (above) does not resolve the condition, open a GitHub issue on
   `launchpad-26/buzz` describing the `http_requests_total` breakdown observed, the
   `/_readiness` response at the time, and relevant JSON log excerpts — with any
   configuration value that could be a credential linked to its source rather than pasted
   in.
2. Directly notify whoever is operating the affected relay instance. There is no formal
   rotation to page; naming a name here would go stale the moment cohort membership
   changes, so this node does not attempt it.
3. If diagnosis points to a genuine defect in the relay itself — not an environmental or
   dependency problem specific to how this instance is run — file it as a product bug at
   `block/buzz` per this repository's own routing convention for upstream defects, separate
   from any operational issue opened in step 1.

## Verification of recovery

- `/_readiness` returns `{"status":"ready"}` on repeated polling, not just once.
- The `http_requests_total{code=~"5.."}` ratio (see *Trigger*) has returned to its
  pre-incident baseline over a subsequent window, not merely stopped climbing.
- The specific narrower counter that was elevated in *Diagnosis* step 4 (if any) has
  returned to its own baseline.
- Representative WebSocket clients are no longer receiving `error:`-prefixed CLOSED or
  NOTICE frames for the operation that was failing.

## Evidence to preserve

- The JSON log lines spanning the incident window, before container restart or log
  rotation discards them — including the `trace_id`/`span_id` pair for at least one
  representative failing request if OpenTelemetry export was enabled.
- The `/_status` response (build `source_sha` and `build.id`) active during the incident,
  to know exactly which build was running.
- The `http_requests_total` query and result (an exported range or a screenshot of the
  Prometheus UI) showing the elevated ratio and, separately, its return to baseline —
  nothing in this repository persists that automatically.
- Never preserve a raw credential or secret value as "evidence." Link to the
  configuration source it came from instead.

## Scope and omissions

**This node does not cover, and names who does:**

| Not covered here | Owned by |
|---|---|
| Diagnosing a specific Postgres outage in depth | `architecture-containers-postgres` |
| Diagnosing a specific Redis outage in depth | `architecture-containers-redis` |
| The mechanics of `/_readiness`, `/_liveness`, and the health-only router beyond what this node cites for triage | `layers-observability-readiness`, `layers-observability-liveness`, `layers-observability-health-checks` |
| The relay's metric catalog and JSON logging conventions in general, beyond the specific series and fields this node names | `layers-observability-metrics`, `layers-observability-logging`, `layers-observability-structured-logging`, `layers-observability-prometheus` |
| Banning or otherwise acting on a client identified as abusive in *Mitigation and resolution* | `capabilities-moderation-moderation` |
| Building an actual alerting, paging, or dashboard pipeline for this condition | Not owned by any accepted decision as of this node's recorded revision — `launchpad-26/buzz#83` considered and did not adopt one; `launchpad-26/buzz#289` is the open PRD where a future answer would be decided |

**Expected but not verified when this node was written:**

- **No live relay instance was exercised to reproduce an actual elevated error rate.**
  Every endpoint, metric name, and log field cited above was verified by reading the
  source that produces it, not by observing it under real failure traffic.
- **Whether a future Cohort VPS deployment will keep today's default ports and today's
  entirely-manual diagnosis, or gain a real alerting/paging mechanism, is not decided.**
  `ENVIRONMENTS.md` marks that environment `OPEN`; this node documents the mechanism that
  exists today and does not guess at what replaces the manual steps above once that
  environment exists.
- **Whether any monitoring or alerting is layered on top of this relay outside this
  repository** — for example by whichever infrastructure ultimately hosts it — was not
  checked and is outside what a source in this repository could establish either way.
