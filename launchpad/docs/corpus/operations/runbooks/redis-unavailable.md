---
id: operations-runbooks-redis-unavailable
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
  - statement: "buzz-relay's readiness_handler at the `/_readiness` route checks Postgres (`state.db.ping()`), Redis (`state.redis_pool.get().await.is_ok()`), and the deletion-serving catalog concurrently under a 2-second timeout, returning HTTP 503 with a per-check JSON body (`{status, postgres, redis, deletion_catalog}`) if any one check fails or the whole check times out, and HTTP 200 `{status: ready}` only when all three succeed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "readiness_handler's Redis check only confirms that a pooled connection can be acquired (`redis_pool.get().is_ok()`); it does not verify that the three long-running Redis subscriber loops are connected, that the NIP-98 replay guard or rate limiter can execute a command, or that PUBLISH/SUBSCRIBE traffic is flowing."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.85
  - statement: "router.rs's build_health_router mounts /_liveness, /_readiness, /_status and /_mesh on a separate, unauthenticated, unmetered router than the main API router, with a comment stating this is \"the health-only router for K8s probes (port 8080 in CAKE)\", distinct from the main app port."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The Helm chart wires relay.readinessProbe and relay.livenessProbe to HTTP GET /_readiness and /_liveness respectively on the container port named `health`, and the deployment template exposes three named container ports: `app` (3000), `health` (service.healthPort, default 8080) and `metrics` (service.metricsPort, default 9102)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "buzz-relay's admission-control rate limiter (RedisRateLimiter, backed by an atomic Lua INCR+EXPIRE script) and the request-side check_principal wrapper map a Redis error from check_and_increment to a distinct AdmissionError::Unavailable variant, separate from AdmissionError::Exceeded (quota hit); the WebSocket send_admission_result handler treats Unavailable the same as Exceeded for the purpose of the connection -- it rejects the request/message and sends the client a \"rate-limited: shared admission unavailable\" notice, incrementing buzz_admission_rejections_total{reason=\"unavailable\"}."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/rate_limiter.rs"
      - "crates/buzz-relay/src/admission.rs"
      - "crates/buzz-relay/src/connection.rs"
  - statement: "The same AdmissionError::Unavailable -> rejection mapping is used by the HTTP bridge and GIF-proxy admission checks in api/bridge.rs and api/gifs.rs, so a Redis outage rejects rate-limit-gated HTTP requests the same way it rejects WebSocket traffic: closed, not open."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/api/gifs.rs"
  - statement: "RedisNip98ReplayGuard::try_mark_in_scope's own doc comments state twice that a Redis pool-acquire failure or a failed SET NX EX means \"caller MUST fail closed\", and buzz-relay's check_nip98_replay_with_guard implements that: on Err from the guard it returns HTTP 401 with a NIP-98 replay-check-unavailable message rather than admitting the request, which check_nip98_replay gates every one of the git smart-HTTP bridge, the GIF proxy, invites, workflow webhooks, and admin auth endpoints on."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/nip98_replay.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "bridge.rs carries a test, nip98_replay_check_fails_closed_when_guard_errors, that injects a replay guard whose try_mark always returns Err and asserts check_nip98_replay_with_guard returns HTTP 401 rather than admitting the request, with an inline comment naming this \"Attack 3\" and stating that \"a stateless worker that loses Redis MUST reject the request, never admit it\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "buzz-pubsub's presence writes (set_presence, clear_presence) return a proper Result and propagate a Redis error with `?`, but both call sites in buzz-relay -- the on-disconnect clear in connection.rs and the client-driven presence update in handlers/event.rs -- discard that Result with `let _ = ...`, so a Redis outage silently drops a presence write: the client that set or cleared its status receives no error and is never told the update did not take effect."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-relay/src/connection.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "By contrast, presence.rs's get_presence_bulk propagates a Redis connection failure as Err rather than an empty map, and buzz-pubsub carries its own test (get_presence_bulk_surfaces_connection_failure_as_error) asserting exactly that with an inline comment that a fake-empty \"all offline\" snapshot must not be returned; api/bridge.rs's synthesize_presence (the NIP-01 presence-query path) matches that Err and returns an error response, with its own test (synthesize_presence_surfaces_redis_failure_as_error_response) confirming a Redis outage surfaces as an error to the querying client rather than a false negative."
    entry_class: FACT
    evidence:
      - "crates/buzz-pubsub/src/presence.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "For persisted channel/global events, the durable Postgres insert is the completion boundary and the subsequent Redis publish_event call for cross-pod fan-out is best-effort: handlers/side_effects.rs's send_system_message comments \"Durable insert is the completion boundary -- propagate failure\" for the DB write and \"Fan out to subscribers: best-effort, clients can retrieve the persisted event\" for the Redis publish, only logging a warning (`warn!(\"... fan-out failed: {e}\")`) on a publish error rather than failing the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "handlers/event.rs's ephemeral-event path (channel-scoped and global/channel-less ephemeral events, e.g. presence deltas and NIP-AB pairing signaling) follows the same best-effort pattern on publish_event failure: it invalidates the locally-marked event id, logs a warning (\"Ephemeral publish failed\" / \"Ephemeral global publish failed\"), and still performs direct local fan-out to same-pod WebSocket subscribers -- so same-pod delivery survives a Redis outage while cross-pod delivery is silently lost for that event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-relay spawns three long-running Redis subscriber loops at startup (run_subscriber for channel/global event fan-out, run_cache_invalidation_subscriber, run_conn_control_subscriber for cross-pod ban enforcement); buzz-pubsub's conn_control.rs implements this loop with an explicit exponential-backoff reconnect (BACKOFF_INITIAL_SECS=1, BACKOFF_MAX_SECS=30, doubling on each failed attempt) that logs and retries forever rather than terminating the task, and buzz-pubsub/src/lib.rs documents the same backoff shape for the other two loops."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-pubsub/src/conn_control.rs"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "mesh_boot.rs's boot_mesh returns Ok(None) and touches Redis not at all when BUZZ_MESH is not 'on' (the default, per its own log line \"mesh disabled ... single-instance behavior\"); when the mesh is enabled, its first act is to publish an attested ReadyRecord to the Redis-backed ready registry, and a failure there is propagated as an Err with the comment \"if Redis can't take the attested record, peers can never find us -- fail loudly now, not quietly forever\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "buzz-relay's main() calls boot_mesh(...).await? directly in the startup sequence of `async fn main() -> anyhow::Result<()>` under #[tokio::main], so an Err from boot_mesh -- including the ready-registry publish failure above -- propagates out of main and aborts relay startup entirely; this is fatal only when BUZZ_MESH=on, per boot_mesh's own doc comment: \"a misconfigured mesh fails loudly (bind failure, Redis unreachable at publish)\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/mesh_boot.rs"
  - statement: "Once the mesh has booted successfully, a later Redis outage is not fatal to the running process: spawn_registry_heartbeat's loop only logs a warning (\"mesh: registry heartbeat tick failed\") on a failed heartbeat.tick and continues on the next refresh_interval, with no process abort and no propagation past the spawned task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay-mesh/src/runtime.rs"
  - statement: "buzz-relay's config.rs defaults REDIS_URL to \"redis://localhost:6379\" when the environment variable is unset (`std::env::var(\"REDIS_URL\").unwrap_or_else(...)`), the same default .env.example documents for local development."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - ".env.example"
  - statement: "The Helm chart's deployment template makes the REDIS_URL secret key `optional` only when the resolved minimum replica count is 1 and neither redis.enabled nor externalRedis.url is set (`optional: {{ and (eq (include \"buzz.minimumReplicas\" . | int) 1) (not .Values.redis.enabled) (not .Values.externalRedis.url) }}`); in every other configuration REDIS_URL is a required secret key at deploy time."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "A separate chart-side template guard (_validate.tpl) hard-fails `helm install`/`helm upgrade` at render time -- before any pod is created -- when the resolved minimum replica count exceeds 1 and none of redis.enabled, externalRedis.url or secrets.existingSecret is set, with the message \"minimum replica count %d requires Redis for buzz-pubsub\"; this is a render-time configuration guard, not a runtime reachability check, and does not by itself prove Redis is reachable once the chart does install."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
  - statement: "readiness_handler's Redis check is unconditional -- it runs and can fail the readiness probe regardless of replicaCount -- so a single-replica deployment that has REDIS_URL unset or pointing nowhere reachable still reports not_ready (and, behind a load balancer or a Kubernetes Service, stops receiving traffic) even though buzz-pubsub's multi-pod fan-out has no second pod to serve in that topology; only the Helm chart's REDIS_URL-optionality and _validate.tpl's install-time guard are conditioned on replica count, not the readiness check itself."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "deploy/charts/buzz/templates/deployment.yaml"
      - "deploy/charts/buzz/templates/_validate.tpl"
    confidence: 0.85
  - statement: "The repository's dev docker-compose.yml runs Redis as service `redis` (container_name buzz-redis, image redis:7-alpine) published on 127.0.0.1:6379 with a healthcheck of `redis-cli ping`; no `relay` service is defined in docker-compose.yml, so under this compose stack the relay process runs on the host (per Justfile's `just relay`), not as a compose service, and reaches Redis via the published loopback port."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "Justfile"
  - statement: "The Justfile's dev-services readiness wait polls `docker inspect --format '{{.State.Health.Status}}' buzz-redis` (alongside buzz-postgres) before reporting the local stack ready, using the same container-level health status the redis-cli-ping healthcheck produces."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "docker-compose.yml's own keycloak service healthcheck demonstrates, in this repository, a TCP-connectivity probe written without a dedicated client binary: `exec 3<>/dev/tcp/localhost/8080 && echo -e '...' >&3 && cat <&3 | grep -q '200 OK'`, using bash's /dev/tcp pseudo-device rather than curl or a service-specific CLI."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "The relay's runtime container image (built from the repository's root Dockerfile, runtime-base stage) installs ca-certificates, curl, git and openssl but does not install redis-cli or any redis-tools package, and its base is debian-slim (not a distroless image), so a shell (bash) and curl are available for connectivity checks from inside a relay pod, but a native Redis client is not."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "buzz-relay periodically polls the Redis pool's status() and emits it as four Prometheus-style gauges -- buzz_redis_pool_available, buzz_redis_pool_size, buzz_redis_pool_max, buzz_redis_pool_waiting -- on the metrics port, and the repository's local-dev prometheus.yml scrapes exactly that port (9102, documented as the relay's default metrics port) from the host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "prometheus.yml"
  - statement: "No PrometheusRule, alerting rule or Grafana dashboard exists anywhere under deploy/charts/buzz/ (the main relay chart) mentioning Redis; the only prometheusrule.yaml in the repository belongs to the unrelated deploy/charts/buzz-push-gateway chart and does not mention Redis, and no markdown or YAML file elsewhere in the repository defines a Redis-availability alert for buzz-relay."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml"
  - statement: "This repository's atomicity standard classifies \"a concept and the procedure that uses it\" as two nodes on the grounds that a concept changes when the design changes while a procedure changes when the tooling or operational practice around it changes -- different maintenance clocks in the ordinary case -- which is the same boundary this document draws against issue #1219's planned failure-mode reference for Redis."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/atomicity.md"
  - statement: "Issue #1226's Definition of Done requires this node to state trigger/symptom, severity/impact and prerequisites; provide diagnosis then mitigation/recovery steps in executable order; include verification of recovery, rollback/escalation and evidence to preserve; and avoid secret values, linking authoritative automation/dashboards rather than copying credentials."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1226 definition of done"
  - statement: "Issue #1219 (operations/reliability/redis-failure.md, a reference-type node cataloguing Redis failure modes) is a sibling task under the same parent Feature #618, dispatched in parallel with #1226 and unmerged at the recorded revision, so its path must not be linked from this document."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1219, read via gh issue view, dispatch brief for the operations corpus batch under #618"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook node to carry, in order, a Trigger, Severity and impact, Diagnosis, Mitigation and resolution, Escalation, and Scope and omissions section, each traceable to the Google SRE Workbook's playbook definition the template adapts."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: architecture-containers-redis
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-deployment-multi-relay
---

# Runbook: Redis unavailable

What an operator does when `buzz-relay` cannot reach Redis: what actually breaks,
what only looks broken, how to tell them apart, and how to bring the relay back to a
clean state once Redis returns. This is the response playbook, not the failure-mode
catalogue -- see *Scope and omissions* for that boundary.

## Trigger and symptom

There is no dedicated alerting rule for this condition in this repository (see
*Scope and omissions*), so the trigger is one or more of the following observed
signals rather than a named page:

1. **The readiness probe fails.** `GET /_readiness` (health port, default `8080`)
   returns HTTP 503 with a JSON body whose `redis` field is `false` -- distinguishing
   this from a Postgres or deletion-catalog failure, which would show `postgres` or
   `deletion_catalog` as `false` instead in the same response. In Kubernetes this
   shows up as the pod losing `Ready` status and being pulled out of Service
   endpoints; `kubectl get pods` shows `0/1` or similar in the `READY` column while
   `kubectl describe pod` shows `Readiness probe failed`.
2. **Clients see admission rejections that were not there before.** WebSocket
   clients receive a `"rate-limited: shared admission unavailable"` notice (not the
   ordinary quota-exceeded message) on connect or on sending events, and
   `buzz_admission_rejections_total{reason="unavailable"}` increases.
3. **NIP-98-authenticated HTTP requests start failing with 401.** The git smart-HTTP
   bridge, the GIF proxy, invites, workflow webhooks and admin auth all gate on the
   NIP-98 replay guard; a Redis outage turns every one of them into a 401 rather than
   admitting the request.
4. **Presence looks wrong but nothing else does.** Users' online/away status stops
   updating or briefly shows everyone offline, with no errors visible to the affected
   client, while messages still send and receive normally.
5. **The `buzz_redis_pool_*` gauges go to zero or the pool metrics stop updating.**
   `buzz_redis_pool_available` dropping to 0 while `buzz_redis_pool_waiting` climbs is
   the earliest machine-readable signal, ahead of the readiness probe actually
   flipping.

**What is not, by itself, this trigger.** A single slow Redis command is not the
same as Redis being unreachable; the diagnosis step below is how to tell the
difference. A relay pod that fails to *start* with a Redis-related error in its logs
and `BUZZ_MESH=on` is a related but distinct condition -- see *Severity and impact*,
mesh case.

## Prerequisites

- Read access to relay logs (structured `tracing` output) and, in Kubernetes, `kubectl`
  access to the relay's namespace (`get pods`, `describe pod`, `logs`, `exec`).
- Under Docker Compose: shell access to the host running `just relay` and to the
  `buzz-redis` container (`docker inspect`, `docker exec`).
- Knowledge of which environment is affected (local Compose dev, a Kubernetes
  deployment via `deploy/charts/buzz`, or another topology) and whether
  `BUZZ_MESH=on` is set for that deployment -- the mitigation path and the
  startup-fatality of a Redis outage both depend on this.
- The relay's own metrics endpoint (`service.metricsPort`, default `9102`) and, where
  configured, whatever scrapes it (this repository's own local dev setup is a plain
  `prometheus.yml` scrape target; no bundled dashboard exists -- see *Evidence to
  preserve*).
- No credential value is needed to diagnose this condition beyond what an operator
  already holds to reach the relay's own health endpoint and its Redis host; do not
  print `REDIS_URL` or any secret in full when working through this runbook (see
  *Evidence to preserve*).

## Severity and impact

Redis in this repository is coordination and rate-limiting state, never the system
of record -- Postgres holds durable data, and no Redis write path in `buzz-pubsub`
persists anything without a TTL. That shapes the impact: nothing already stored is
at risk, but several live-path behaviors degrade differently, and the split between
"fails closed" and "fails silently open" is the single most important fact for
triage.

**Fails closed (requests get rejected, visibly, as a security decision):**

- **Shared rate limiting** (`RedisRateLimiter`, used for both WebSocket message/event
  admission and HTTP bridge/GIF-proxy admission): a Redis error is mapped to
  `AdmissionError::Unavailable` and rejected exactly like a quota breach, with a
  distinguishing message and its own rejection-reason metric.
- **NIP-98 HTTP auth replay protection**: every endpoint gated by
  `check_nip98_replay` -- the git bridge, GIF proxy, invites, workflow webhooks, and
  admin auth -- returns HTTP 401 rather than admitting a request whose freshness it
  cannot verify. This is deliberate: the code's own comments state the caller "MUST
  fail closed," and a dedicated test exercises exactly this path.
- **Presence *reads*** (the NIP-01 presence-query path, `synthesize_presence`):
  surfaces the Redis failure as an error response rather than a fabricated "everyone
  offline" snapshot.

**Fails silently open (nothing errors, something just does not happen):**

- **Presence *writes*** (a client setting or clearing its own online/away status):
  both call sites discard the write's `Result`, so the update is silently lost. The
  client believes its status changed; it did not.
- **Cross-pod realtime fan-out** for already-persisted events (regular channel
  messages, system messages, thread-summary overlays): the durable Postgres insert
  already succeeded, so the message is not lost, but the Redis publish that pushes it
  to *other* relay pods in real time is best-effort and only logs a warning on
  failure. Same-pod WebSocket subscribers still receive it directly; a client
  connected to a different pod sees it only once it next re-syncs from history.
- **Ephemeral events** (presence deltas, NIP-AB pairing signaling) follow the same
  pattern: same-pod delivery survives, cross-pod delivery is silently dropped.
- **Cross-pod cache invalidation and live ban enforcement** are also fire-and-forget
  publishes; this document does not re-derive their fallback behavior in detail --
  see *Scope and omissions*.

**Topology-dependent severity:**

- **Single relay pod, mesh off (the default).** The most common case: no cross-pod
  fan-out exists to lose in the first place, so the "fails silently open" list above
  is mostly moot, but the readiness probe still treats Redis as mandatory
  unconditionally -- a single-replica deployment with no Redis configured or
  reachable still reports `not_ready` and can be pulled from a load balancer even
  though nothing in that topology structurally needs Redis for message delivery.
  Rate limiting and NIP-98 replay protection still fail closed regardless of replica
  count.
- **Multiple relay pods, mesh off.** The chart's own install-time guard already
  requires a Redis source to be *configured* before a multi-replica install is even
  accepted; an outage after that point degrades exactly as described above --
  cross-pod delivery lost, admission and NIP-98 checks failing closed on every pod
  independently.
- **Mesh enabled (`BUZZ_MESH=on`), Redis unreachable at relay startup.** Fatal to
  that pod: the mesh's first act is to publish an attested ready-record to Redis, a
  failure there is propagated out of the relay's `main()`, and the process exits
  before serving any traffic. This is the one case in this document where "restart
  the pod" alone does not recover anything -- Redis must be reachable *before* the
  next start attempt.
  If `BUZZ_MESH` is unset or not `"on"`, none of this applies: mesh boot touches no
  Redis at all and this whole case does not arise.
- **Mesh enabled, Redis becomes unreachable after a successful boot.** Not fatal:
  the mesh's registry heartbeat only logs a warning on a failed tick and keeps
  retrying on its normal interval. No restart is needed for the mesh specifically in
  this case; see *Mitigation and resolution*.

## Diagnosis

Work through these in order; stop at the first one that confirms the condition.

1. **Check the readiness endpoint directly**, since it is the single authoritative
   signal and distinguishes this from a Postgres or deletion-catalog failure:
   - Kubernetes: `kubectl exec <relay-pod> -c relay -- curl -sS
     http://localhost:8080/_readiness` (the health port is separate from the app
     port; see *Prerequisites*). A `redis: false` field in the JSON body confirms
     this condition specifically.
   - Compose/local dev: `curl -sS http://localhost:8080/_readiness` from the host
     running `just relay` (the relay is a host process here, not a compose service).
2. **Check the relay's own logs** for the specific warning strings this document's
   evidence ledger names verbatim: `"rate limit key has no TTL"` (a different,
   milder condition -- see below), `"nip98 replay: redis pool acquire failed"`,
   `"Ephemeral publish failed"`, `"... fan-out failed"`, or (mesh only) `"mesh:
   registry heartbeat tick failed"`. Their presence and frequency distinguish a
   total outage from an intermittent one.
3. **Check Redis's own reachability from the relay's actual network position** --
   not from your workstation, which may have different routing:
   - **Docker Compose (local dev).** The relay is a host process, and Redis is
     published on `127.0.0.1:6379`. From the same host: `docker exec buzz-redis
     redis-cli ping` (exercises the same healthcheck the compose file itself already
     uses) or `docker inspect --format '{{.State.Health.Status}}' buzz-redis` (the
     same command `just`'s dev-services readiness wait already polls). Either
     confirms whether the *container* is healthy from outside the relay's own
     process; the relay's own `/_readiness` output remains the authority on whether
     the relay process itself can reach it.
   - **Kubernetes.** The relay's runtime image has `curl` and a shell but no
     `redis-cli` (see the evidence ledger). Exec into the pod and use a plain TCP
     probe rather than assuming a Redis client exists:
     `kubectl exec <relay-pod> -c relay -- bash -c 'exec 3<>/dev/tcp/<redis-host>/6379
     && echo redis-port-open'` -- the same `/dev/tcp` technique this repository's
     own `docker-compose.yml` already uses for a different service's healthcheck, not
     an invented one. `<redis-host>` is whatever `REDIS_URL` resolves to for this
     deployment (the in-cluster `redis` subchart's Service name when
     `redis.enabled=true`, or the host in `externalRedis.url`) -- read it from the
     chart's values or the deployment's environment, and do not print the full
     `REDIS_URL` if it carries embedded credentials (see *Evidence to preserve*).
     A connection refusal or timeout here, together with `redis: false` on
     `/_readiness`, confirms the relay cannot reach Redis at all; a connection that
     opens but a slow or erroring command inside the relay's own logs points to a
     degraded-but-reachable Redis instead of a full outage, which changes the
     mitigation path below.
4. **Check the pool gauges** on the metrics port (`buzz_redis_pool_available`,
   `_size`, `_max`, `_waiting`) if a scraper is already in place; a pool at zero
   available connections with a growing waiting count corroborates an outage rather
   than a one-off blip.
5. **Distinguish "no TTL" log noise from a real outage.** `RedisRateLimiter`'s Lua
   script self-repairs a rate-limit key that exists without an expiry (logged as a
   warning, not an error) -- this is expected self-healing from a past crash between
   `INCR` and `EXPIRE`, not evidence Redis is currently unreachable, and should not be
   confused with the `AdmissionError::Unavailable` rejections this runbook is about.

## Mitigation and resolution

Redis itself is out of this document's scope to operate (see *Scope and
omissions*) -- these steps assume Redis's own recovery is being handled separately
(restarting the service, fixing network/security-group access, restoring an
ElastiCache instance, etc.) and describe what to do on the `buzz-relay` side while
that happens and once it is done.

1. **Confirm no data loss is in progress.** Per *Severity and impact*, persisted
   events are already durable in Postgres before Redis is ever touched, and nothing
   in `buzz-pubsub` writes a key without a TTL. There is no persisted state to
   rescue on the relay side; this step is about ruling out panic, not performing a
   rescue.
2. **If `BUZZ_MESH=on` and an affected pod failed to *start*** (as opposed to a
   running pod losing Redis after boot): do not repeatedly restart that pod hoping
   it recovers on its own -- it will keep failing the same way until Redis is
   reachable at boot time. Restore Redis reachability first, then let the
   orchestrator's normal restart policy (or a manual restart) bring the pod up; no
   other relay-side action is needed once Redis answers, because `boot_mesh` runs
   its ready-registry publish fresh on every start attempt.
3. **If a pod is already running and Redis drops out underneath it** (mesh on or
   off): no relay-side action is required to keep the pod alive. The three Redis
   subscriber loops and (if mesh is on) the registry heartbeat all retry on their
   own schedules (exponential backoff up to 30s for the subscriber loops; the
   configured refresh interval for the heartbeat) rather than crashing the process.
   Do not restart the pod as a first response -- it will not reconnect any faster
   than the built-in backoff already does, and a restart of a mesh-enabled pod
   while Redis is still down re-triggers the startup-fatal path in step 2.
4. **If the outage is prolonged and the deployment can tolerate it**, communicate
   the degraded-mode impact from *Severity and impact* to affected users/operators
   rather than attempting a workaround this repository does not support: there is no
   configuration flag in this codebase to run the relay with Redis disabled once
   `replicaCount > 1` or `BUZZ_MESH=on` are set, and disabling Redis is not something
   this runbook recommends inventing ad hoc.
5. **Once Redis is confirmed reachable again** (re-run the *Diagnosis* connectivity
   check above until it succeeds), move to *Verification of recovery* below. No
   relay restart is required in the general case -- the pool and the subscriber
   loops reconnect on their own -- except for the one case named in step 2.

## Verification of recovery

1. **Re-check `/_readiness`** the same way as in *Diagnosis*, on every affected pod
   if there is more than one: `redis: true` (and `postgres`/`deletion_catalog` still
   `true`) with an overall HTTP 200 confirms the relay itself considers Redis
   healthy again.
2. **Confirm admission and NIP-98 rejections have stopped.** Watch
   `buzz_admission_rejections_total{reason="unavailable"}` flatten out, and confirm a
   fresh NIP-98-authenticated request against one of the gated endpoints (git
   bridge, GIF proxy, invites, workflows, admin auth) succeeds rather than returning
   401.
3. **Confirm the pool gauges recovered.** `buzz_redis_pool_available` back above
   zero and `buzz_redis_pool_waiting` back near zero, where a scraper is in place.
4. **Spot-check presence and cross-pod delivery** if the deployment has more than
   one relay pod: have a client on one pod update its presence status or send a
   message, and confirm a client connected to a *different* pod observes it in real
   time rather than only after a manual refresh -- this is the signal that
   cross-pod fan-out, not just the readiness check, is flowing again.
5. **If step 2 of *Mitigation and resolution* applied** (a mesh-enabled pod that
   failed to start), confirm the pod actually reached `Running`/`Ready` and check
   its logs for `"mesh ready record published"` rather than only checking that the
   process is up -- a pod can be running while still failing the mesh boot sequence
   if `BUZZ_MESH=on` reachability was only partially restored.

## Rollback and escalation

There is no relay-side configuration change to roll back as part of this runbook --
nothing in *Mitigation and resolution* above changes relay configuration, restarts
services other than the affected pod in the one named case, or modifies the Helm
chart's Redis wiring. If an operator finds themselves editing `REDIS_URL`,
`redis.enabled`, `externalRedis.url`, or `_validate.tpl` while working this runbook,
that is scope creep past what this document covers -- stop and treat it as a
separate, deliberate change with its own review, not part of restoring service.

**Escalate when:**

- Redis itself has been unreachable for longer than the deployment's agreed
  tolerance for degraded admission/NIP-98 behavior (this document does not set that
  threshold -- it is an operational decision outside this runbook's scope).
- A mesh-enabled pod remains stuck failing to start after Redis reachability has
  been confirmed restored by the *Diagnosis* connectivity check -- that is no longer
  this condition and needs its own investigation.
- The *Diagnosis* steps show Redis is reachable (TCP connects, `redis-cli ping`
  succeeds against the container) but `/_readiness` still reports `redis: false` --
  that combination is outside what this document explains and should not be
  worked around by restarting pods repeatedly.
- Escalate to whoever owns the Redis instance for this deployment (an in-cluster
  subchart, an external ElastiCache instance, or another managed service) for the
  Redis-side recovery itself; this document does not own that procedure (see *Scope
  and omissions*).

## Evidence to preserve

- The `/_readiness` JSON body (all three check fields) from at least one affected
  pod, with a timestamp, before it recovers.
- Relay log lines matching the warning strings named in *Diagnosis*, with
  timestamps spanning the outage.
- The `buzz_redis_pool_*` gauge values (or a screenshot/export of whatever consumes
  them) across the incident window, if a scraper was in place.
- The result of the *Diagnosis* connectivity check (TCP probe or `redis-cli ping`
  output), timestamped, from both during and after the outage.
- **Never** capture, log, or paste the full `REDIS_URL` value or any Redis
  `AUTH`/password in evidence -- it may embed credentials
  (`redis://:pass@host:6379`). Capture the host and port only, or reference the
  Kubernetes Secret/environment-file key name (`REDIS_URL`, `redis-password`) rather
  than its value. This repository ships no dashboard or alerting rule for this
  condition (see *Scope and omissions*); where a deployment has since added one
  externally, link it here as evidence rather than re-typing its contents.

## Scope and omissions

**This document covers** how an operator recognizes, diagnoses, mitigates and
verifies recovery from `buzz-relay` losing Redis connectivity, and the specific
places in the codebase where that failure is handled -- consistently or
inconsistently -- across rate limiting, NIP-98 replay protection, presence,
cross-pod event fan-out, the readiness probe, and the inter-relay mesh.

**What this document does not cover, and who owns it:**

- **The taxonomy of Redis failure modes themselves** -- network partition vs. OOM
  eviction vs. ElastiCache failover vs. TLS/auth misconfiguration, and which of
  those look identical from the relay's side versus which are distinguishable --
  is issue #1219's planned `operations/reliability/redis-failure.md` reference node,
  not this one. This repository's own atomicity standard treats "a concept and the
  procedure that uses it" as two nodes precisely because they sit on different
  maintenance clocks; the failure-mode catalogue changes when Redis's own operating
  characteristics are better understood, this runbook changes when the relay's own
  code changes. #1219 is unmerged at the time this document was written, so its
  path is deliberately not linked here.
- **Operating Redis itself** -- provisioning, failover, backup, patching an
  ElastiCache instance or the `redis:7-alpine` container -- belongs to whoever owns
  that infrastructure for a given deployment, not to this relay-focused corpus.
- **Cross-pod cache invalidation and live ban enforcement's exact fallback
  behavior** during a Redis outage is not traced to the same depth as presence and
  event fan-out above; both are fire-and-forget publishes per
  `architecture-containers-redis`, but this document did not independently verify
  their specific downstream consequences (e.g. how long a stale cache entry or an
  unenforced ban persists) claim by claim, and that is named here as a gap rather
  than asserted.
- **What counts as an acceptable outage duration before escalating** is an
  operational SLO decision this document does not set.
- **Whether this repository should add a PrometheusRule or dashboard for this
  condition** is out of scope for this task -- confirmed absent today (see the
  evidence ledger), named as a gap, not filled in.

**Expected but not verified when this node was written:**

- **No live Redis outage was reproduced against a running relay to observe these
  behaviors end to end.** Every claim above is read from source (including two
  tests -- `nip98_replay_check_fails_closed_when_guard_errors` and
  `synthesize_presence_surfaces_redis_failure_as_error_response` -- that exercise
  the failure path directly) rather than from operating a real incident, so the
  exact wall-clock timing of reconnect backoff, probe flap, and load-balancer
  eviction under a genuine outage was not observed.
- **The in-cluster Redis subchart's exact Service DNS name** (when
  `redis.enabled=true`) was not resolved to a literal hostname here, because it
  depends on the release name at install time; an operator following the
  *Diagnosis* Kubernetes connectivity step needs to read it from the deployed
  chart's values or the pod's own `REDIS_URL` environment variable rather than
  assuming a fixed name.
- **Whether a runbook may itself trigger `buzz-workflow` automation**, as opposed
  to only describing manual operator steps, is left open by the template this node
  implements and is not resolved here either -- every step above is manual.
