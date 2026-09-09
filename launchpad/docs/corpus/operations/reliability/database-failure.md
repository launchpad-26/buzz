---
id: operations-reliability-database-failure
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-relay's writer pool is sized by Config::from_env's BUZZ_DB_POOL_SIZE (default 50 when unset, zero, or unparseable) and connected through DbConfig, whose own struct-literal default (used only where a caller builds DbConfig directly, e.g. in tests) is 20 max / 2 min connections with a 3-second acquire_timeout_secs, a 1800-second max_lifetime_secs, and a 600-second idle_timeout_secs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "The writer pool is connected eagerly (PgPoolOptions::connect, not connect_lazy) with an after_connect hook that sets the buzz.created_at_floor GUC and asserts the session's transaction_isolation is exactly read committed, failing the connection attempt otherwise; a failure at this call propagates out of Db::new as a DbError."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "DbError::Sqlx(#[from] sqlx::Error) is the variant that carries a driver-level failure such as a timed-out pool acquire (sqlx::Error::PoolTimedOut) or a lost/refused connection; DbError has no variant of its own for a degraded-but-serving Postgres state, only variants for specific rejected operations and this passthrough for everything the driver reports."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/error.rs"
  - statement: "An optional read-replica pool is connected lazily (connect_lazy) with min_connections pinned to 0 so no connection is dialed at construction, and a much shorter 150-millisecond acquire timeout (Db::READER_ACQUIRE_TIMEOUT) than the writer's; the doc comment states this is deliberate so a reader that is down at boot cannot crash the relay and so a saturated or absent reader fails closed to the writer quickly rather than adding writer-level latency to a routed read."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "Db::proved_reader treats a reader-pool acquire timeout, a reader transaction-begin failure, and several replica-freshness-proof failures as fail-open-to-the-writer conditions: every one of them returns an Err reason string and the caller routes the read to the writer pool instead of failing the request, so a struggling or unreachable read replica degrades routed reads to writer latency rather than rejecting them, in contrast to a writer-pool failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "Db::ping executes SELECT 1 against the writer pool and returns a bare bool (true on success, false on any error), with no distinction between a slow response, a timed-out acquire, and a fully unreachable server; this is the sole function the relay's readiness probe uses to represent Postgres health."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "At startup, buzz-relay calls Db::new(&db_config).await and maps any error to an anyhow error that propagates out of async fn main() -> anyhow::Result<()>, before the HTTP/WebSocket listener (the serve(...) call) is ever invoked; a Postgres connection failure at this point means the process exits without having bound its listening port at all, rather than starting in a degraded or partially-serving state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "buzz-relay opens two further Postgres connections at startup outside of buzz_db::Db, both also eager and both also gating startup on failure via the same map_err(...).await? pattern: a 5-connection audit pool (only when BUZZ_AUDIT_ENABLED is set) backing buzz-audit's hash-chain log, and a search pool (always constructed, preferring READ_DATABASE_URL when set, otherwise DATABASE_URL) backing buzz-search's Postgres full-text search; a failure connecting either one aborts startup exactly as a writer-pool failure does."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Database migrations only run at startup when the BUZZ_AUTO_MIGRATE environment variable parses as truthy (true/1/yes/on, case-insensitive and trimmed); an absent or any other value skips migrations and only logs a notice, so a schema mismatch from a skipped migration is a separate startup risk from Postgres being unreachable at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The readiness handler at GET /_readiness first checks a shutting_down flag and returns 503 with {\"status\":\"shutting_down\"} if set; otherwise it runs Db::ping, a Redis pool checkout, and validate_deletion_serving_catalog concurrently under a 2-second timeout, collapsing the whole check to (false, false, false) if the timeout elapses, and returns HTTP 200 {\"status\":\"ready\"} only if all three succeeded, else HTTP 503 naming which of postgres/redis/deletion_catalog failed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "GET /health and GET /_liveness both return an unconditional HTTP 200 with no dependency check of any kind, so neither reflects a Postgres outage; only /_readiness does."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The Helm chart's default probes point livenessProbe and startupProbe at /_liveness and readinessProbe at /_readiness, with the readiness probe's periodSeconds: 5 and failureThreshold: 3, meaning a continuous Postgres outage is reflected as not-ready roughly 15-20 seconds after it begins, while liveness and startup checks never observe it because they hit the unconditional-200 endpoint."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "The relay's Deployment template declares no restartPolicy override, so the workload runs under whatever restartPolicy a Kubernetes Deployment applies by default (documented externally as Always); combined with the startup-time behavior above, a Postgres outage present when a pod is created would repeatedly fail the container's process at (or near) boot, which Kubernetes surfaces as a crash-looping pod rather than a pod that starts and reports not-ready."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/templates/deployment.yaml"
      - "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy"
    confidence: 0.8
  - statement: "docker-compose.yml defines no relay service at all — only the bundled adminer service declares depends_on: postgres: condition: service_healthy — so in the repository's local-development compose file nothing gates relay startup on a Postgres health check besides the relay process's own eager connection attempt described above; the relay is run separately (e.g. via just relay or cargo run), not as a compose service."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "On the event-write path, a Postgres failure while checking a community's write fence (an ordinary DbError, exercised in tests with DbError::Sqlx(sqlx::Error::PoolTimedOut)) is mapped by map_serving_fence_state to IngestError::Internal with a message prefixed error:, deliberately distinct from the restricted: prefix used when the fence check succeeds and reports the community inactive — the code comment states a lookup outage can neither admit a write past the fence nor be reported to the client as an ordinary bad request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Further down the same write path, any DbError from insert_event_with_thread_metadata other than AuthEventRejected is mapped to IngestError::Internal(format!(\"error: database error: {other}\")), so an ordinary Postgres outage during the insert itself produces the same error:-prefixed rejection as the fence-check outage above; a pre-created channel row (kind:9007) is compensated with a soft-delete on this path so no orphaned channel remains from a write that ultimately failed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "On the WebSocket read paths (REQ and COUNT), a database failure while resolving accessible channels or confirming channel membership causes the handler to send RelayMessage::closed(&sub_id, \"error: database error\") (or a formatted equivalent) and return immediately; no partial, cached, or degraded subscription or count result is ever produced from a failed lookup on these paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "crates/buzz-relay/src/handlers/count.rs"
  - statement: "On the HTTP Nostr bridge (POST /events, reached without a WebSocket), an IngestError::Internal is turned into a response via internal_error, which logs the detailed message and returns HTTP 500 with a generic {\"error\":\"internal server error\"} body — the same ingest-error taxonomy that drives the WebSocket error: prefix drives the HTTP bridge's 500 for the same class of failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/mod.rs"
  - statement: "A unit test named serving_fence_lookup_outage_fails_closed_as_internal constructs a DbError::Sqlx(sqlx::Error::PoolTimedOut) directly (no live Postgres needed) and asserts map_serving_fence_state maps it to IngestError::Internal with a message starting error: , distinguishing this outage path in the same test file from serving_fence_inactive_community_maps_to_restricted, which asserts the different restricted: wire text used for an authorization decision rather than an outage."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Ephemeral events (kinds 20000-29999) are never persisted to Postgres at all — buzz-db's own crate-level design invariants state they are Redis pub/sub only — so live, ephemeral traffic that does not require durability (e.g. typing indicators, presence-shaped kinds in that range) is unaffected by a Postgres outage in a way that ordinary durable events are not; this document does not further characterize which product features rely on which kind ranges."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/lib.rs"
  - statement: "A repository-wide search for retry or backoff logic touching buzz-db's pools or Db methods finds no retry path on the ordinary read or write route: the only matches are a dev/CI-only channel-reconciliation loop gated on the BUZZ_RECONCILE_CHANNELS environment variable (retries every 5 seconds for up to 2 minutes) and a debug-logged Aurora-identity capability re-probe that only affects replica-routing metadata, neither of which retries a failed insert, event lookup, or fence check on behalf of a client request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "Pool utilization is exported as Prometheus gauges (buzz_db_pool_size, buzz_db_pool_idle, buzz_db_pool_active, buzz_db_pool_max, and the equivalent read-pool gauges when a reader is configured), giving an operator a way to observe pool exhaustion approaching before Db::ping or a request-path acquire actually times out; this document does not describe alerting thresholds or dashboards built on these gauges."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "This node was written using launchpad/docs/corpus/templates/reference.md, which was already merged on origin/launchpad at the recorded revision and directs a reference-shaped node to a Reference-description paragraph, structured entries, an explicit boundary statement, relationships, and a scope-and-omissions section carrying both what the node excludes and what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
relationships:
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: layers-observability-readiness
  - type: references
    target: layers-observability-health-checks
  - type: references
    target: layers-lifecycle-startup
---

# Database failure: reference

This node catalogues how buzz-relay behaves when Postgres is degraded or
unreachable — connection-pool exhaustion and timeouts in `crates/buzz-db`, how
the relay's write, read and readiness paths respond to a failed query, the
difference between a database outage at startup and one during normal
operation, what (if anything) retries, and what data is and is not at risk. It
is a reference for the failure *behavior* the code already implements, not a
procedure for responding to an outage — see *Boundary* below for that split.
It is linked from, and assumes the reader has, the general container and
lifecycle picture in `architecture-containers-postgres.md`,
`layers/observability/readiness.md`, `layers/observability/health-checks.md`
and `layers/lifecycle/startup.md`.

## Failure surfaces and observed behavior

buzz-relay holds up to three independent Postgres connections, all
constructed at startup, all eager (not lazy) except the optional read
replica:

| Connection | Sizing | Connect mode | On connect failure |
|---|---|---|---|
| Writer pool (`buzz_db::Db`) | `BUZZ_DB_POOL_SIZE`, default 50 max / 2 min, 3s acquire timeout, 600s idle timeout, 1800s max lifetime | Eager (`connect`) | Startup aborts before the listener binds |
| Read-replica pool (`buzz_db::Db`, optional) | `BUZZ_DB_READ_POOL_SIZE` or inherits the writer's size, 0 min, 150ms acquire timeout | Lazy (`connect_lazy`) | Never blocks startup; a boot-time reachability probe only warns |
| Audit pool (only if `BUZZ_AUDIT_ENABLED`) | 5 max / 1 min | Eager (`connect`) | Startup aborts |
| Search pool (always) | unconfigured pool defaults; prefers `READ_DATABASE_URL` | Eager (`connect`) | Startup aborts |

The reader pool is the one deliberate exception to "a failed Postgres
connection stops the relay": it is dialed lazily so a replica that is down at
boot cannot crash the relay, and a routed read that cannot reach it within
its 150ms acquire budget falls back to the writer pool rather than failing —
a **degrade**, not a fail-closed rejection. Every other connection above
fails the whole process at startup if it cannot connect, and every ordinary
operation against the writer pool at runtime fails the specific request
closed rather than degrading.

### Startup versus runtime

**At startup**, `Db::new` (and, separately, the audit and search pool
connects) run *before* the HTTP/WebSocket listener binds. A Postgres outage
at this point means the process exits with a logged error and never starts
serving any traffic at all — not even the always-200 liveness endpoint,
because nothing is listening yet. Recovery is external to the process: the
container orchestrator restarts it, and each restart repeats the same
connect attempt. There is no internal startup retry loop for these connects.
An `#[ignore]`-free schema mismatch from a skipped migration
(`BUZZ_AUTO_MIGRATE` unset) is a related but distinct startup risk, not a
Postgres-availability one.

**At runtime**, once the listener is up, a Postgres failure never crashes the
process or drops the listener. Instead:

- The writer pool's 3-second acquire timeout bounds how long any single
  operation waits for a free connection before returning
  `DbError::Sqlx(sqlx::Error::PoolTimedOut)` (or a similar driver error for an
  outright unreachable server).
- Every code path this node found that handles such an error handles it by
  **rejecting the specific request**, not by entering some relay-wide
  degraded mode. There is no circuit breaker or global fail-fast switch that
  buzz-relay flips when Postgres first fails; each request independently
  discovers the failure against the same pool.
- No retry-with-backoff exists on the ordinary read or write route. A failed
  acquire or query surfaces to the caller once, immediately.

### Write path (EVENT over WebSocket, and the HTTP bridge)

A Postgres failure while checking a community's write fence, or while
inserting the event itself, is mapped to `IngestError::Internal` and carries
an `error: ` (NIP-01) wire prefix — the same taxonomy arm used for any other
server fault, and deliberately distinct from the `restricted: ` prefix used
when the fence check *succeeds* and reports the community genuinely fenced.
Over the WebSocket this becomes an `OK false` with that message; over the
HTTP bridge (`POST /events`) the same `IngestError::Internal` is turned into
HTTP 500 with a generic body, while the detailed message is logged
server-side only.

### Read paths (REQ / COUNT over WebSocket, and `POST /query` / `POST /count`)

A Postgres failure while resolving accessible channels or confirming channel
membership on a `REQ` or `COUNT` subscription causes the handler to close the
subscription immediately with `CLOSED <sub_id> "error: database error"` (or a
formatted variant carrying the underlying error). No partial or stale result
set is served from a failed lookup.

### Readiness, liveness, and the Kubernetes probe wiring

`GET /_readiness` is the only probe endpoint that reflects Postgres health:
it runs `Db::ping` (`SELECT 1` against the writer pool), a Redis pool
checkout, and a deletion-serving-catalog check concurrently, under a 2-second
timeout that collapses every check to failure if it elapses, and returns
HTTP 503 unless all three succeed. `GET /health` and `GET /_liveness` return
an unconditional 200 and never observe Postgres at all. The chart's default
`livenessProbe` and `startupProbe` point at `/_liveness`; only
`readinessProbe` points at `/_readiness`, with `periodSeconds: 5` and
`failureThreshold: 3` — so a continuous outage is reflected as "not ready"
roughly 15-20 seconds after it begins, the pod is pulled from service
endpoints, and the container process itself is left running rather than
restarted, because liveness never sees the failure.

### What is at risk

An outage does not put already-committed data at risk by itself — Postgres
is the durable store and this document found no code path that writes
committed data anywhere else as a fallback. What is at risk, or lost, during
an outage is **admission**: writes that a client attempted while the writer
pool or an ordinary insert was failing are rejected (`error:` / HTTP 500),
not queued or buffered for later replay, so a client that does not retry on
its own loses that write. Ephemeral events (kinds 20000-29999) are the one
category of live traffic never persisted to Postgres in the first place —
Redis pub/sub only, by design — so that traffic is unaffected by a Postgres
outage regardless of the above. Pool-utilization metrics
(`buzz_db_pool_size`/`_idle`/`_active`/`_max`, and the reader equivalents) are
exported continuously and are the operator-visible signal that exhaustion is
approaching before `Db::ping` or a request-path acquire actually times out.

## Boundary

This node does not describe:
- **How an operator should detect, escalate, or remediate a live Postgres
  outage.** That is a separate operational runbook for this exact subject,
  not yet written at the time this node was authored; this node describes
  only the behavior the runbook would be responding to.
- **General service availability or SLO treatment** for buzz-relay as a
  whole, of which a Postgres outage is one cause among several. That is a
  separate, broader reliability document, also not yet written at the time
  this node was authored.
- **Redis failure**, beyond noting that the readiness probe checks Postgres
  and Redis together and either one failing produces the same `not_ready`
  response shape. Redis has its own connection, pooling, and failure
  behavior that this node does not characterize.
- **An API-Reference-depth enumeration of every individual Postgres-touching
  endpoint's exact failure response.** The tables and sections above describe
  the pattern each transport surface follows (WebSocket write, WebSocket
  read, HTTP bridge, startup); they are not a per-endpoint catalogue.
- **The audit pool and search pool's failure behavior in the same depth as
  the writer/reader pools.** Their existence, sizing intent, and eager
  connection at startup are described above only insofar as they share the
  startup-abort behavior; `architecture-containers-postgres.md` is the
  canonical description of these pools' configuration.

## Relationships

- `references`: `architecture-containers-postgres` — the general Postgres
  container, pool configuration, and migration description this node adds
  failure-mode behavior on top of, without re-enumerating its configuration
  tables.
- `references`: `layers-observability-readiness` — the general
  readiness-probe contract; this node states only the Postgres-specific
  contribution to that contract's pass/fail decision.
- `references`: `layers-observability-health-checks` — the general
  health-check surface (`/health`, `/_liveness`, `/_readiness`) this node's
  readiness section is a specific instance of.
- `references`: `layers-lifecycle-startup` — general startup-ordering
  behavior; this node's startup-versus-runtime section is the Postgres
  special case of that ordering.

No `depends-on`, `implements`, `part-of` or `supersedes` edge is declared:
this node adds failure-behavior content alongside the four referenced nodes
rather than being a constituent part of, an implementation of, or a
replacement for any of them.

## Scope and omissions

**This node covers** connection-pool configuration and timeouts for the
writer and (optional) read-replica pools in `crates/buzz-db`; what
`DbError` looks like and how it propagates; the difference between a
Postgres failure at startup (process exits before serving) and one at
runtime (individual requests fail; the process keeps running); how the
WebSocket write path (EVENT), the WebSocket read paths (REQ/COUNT), and the
HTTP Nostr bridge each respond to a failed query; the `/_readiness` probe's
Postgres check and its relationship to the Kubernetes probe configuration
that consumes it; that no retry-with-backoff exists on the ordinary
read/write route; and what data is and is not at risk during an outage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The operator detection/escalation/remediation procedure for a live Postgres outage | a sibling runbook for this exact subject, not yet written at the time of authoring |
| General service availability / SLO treatment | a sibling reliability document, not yet written at the time of authoring |
| Redis's own failure behavior | a Redis-specific node, not yet written at the time of authoring |
| Full Postgres container/pool configuration detail | `architecture-containers-postgres` |
| The general readiness/health-check contract beyond Postgres's contribution to it | `layers-observability-readiness`, `layers-observability-health-checks` |
| General startup-ordering behavior beyond the Postgres-specific case | `layers-lifecycle-startup` |
| Audit-pool and search-pool failure behavior in the same depth as the writer/reader pools | `architecture-containers-postgres` |

**Expected but not verified when this node was written:**

- **No live Postgres outage was actually induced against a running relay.**
  Every behavior above is read from source and, where one exists, from a
  unit test that constructs the failure condition directly
  (`DbError::Sqlx(sqlx::Error::PoolTimedOut)`) without a live database. Actual
  wall-clock timing under a real outage — how long an in-flight request
  actually waits before the 3-second writer acquire timeout fires under
  concurrent load, and how the pool behaves as it recovers once Postgres
  returns — was not observed running.
- **The Kubernetes crash-loop consequence of a startup-time outage is stated
  as an inference from the chart's unset `restartPolicy` plus Kubernetes'
  own documented default, not from observing a real pod fail to start.** No
  cluster was exercised to confirm the observed `CrashLoopBackOff` behavior
  or its exact backoff schedule.
- **Whether any client (desktop, mobile, CLI, or another relay in a mesh)
  retries a rejected write or a closed subscription on its own** was not
  checked; this node describes only what buzz-relay itself does, not client
  behavior after receiving an `error:` response.
- **Whether the search pool's own query failures (as opposed to its
  connection failing at startup) are handled the same way as the paths
  described above** was not traced — this node followed `buzz_db::Db`'s
  error path in depth and only confirmed the search pool's startup-time
  connect behavior, not its steady-state query error handling.
