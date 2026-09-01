---
id: operations-runbooks-postgres-unavailable
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "liveness_handler is an async fn whose entire body returns (StatusCode::OK, \"ok\") unconditionally -- it performs no Postgres check, no Redis check, and no shutdown-flag check, so a Postgres outage discovered after a pod has already started never fails /_liveness on its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "readiness_handler first returns 503 with a {\"status\": \"shutting_down\"} body if the shutdown flag is set; otherwise it runs state.db.ping(), a Redis pool acquisition, and validate_deletion_serving_catalog() concurrently under one 2-second tokio::time::timeout, treats a timeout as if all three checks had failed, and on any failure returns 503 with a JSON body naming which of postgres/redis/deletion_catalog is not ok."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "Db::ping() reports Postgres reachability by executing `SELECT 1` against the writer pool and returning whether that query succeeded."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "The writer pool is established with PgPoolOptions::new().connect(), an eager connection attempt made once inside Db::new(), with defaults of min_connections 2, acquire_timeout_secs 3, max_lifetime_secs 1800 and idle_timeout_secs 600 -- unlike the read-replica pool, which is deliberately connected with connect_lazy() and min_connections 0 specifically so that a down reader cannot fail boot."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "buzz-relay's main() calls Db::new(&db_config).await and propagates any error with `?` before constructing the API router, the health router, or binding any TCP listener -- so a Postgres connection failure at startup prevents the process from ever serving /_liveness or /_readiness at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Because buzz-relay's main is declared #[tokio::main] async fn main() -> anyhow::Result<()>, an Err returned during startup (including a Postgres connection failure) causes the process to terminate with a non-zero exit status under Rust's process::Termination behaviour for a Result-returning main, rather than logging and continuing to serve traffic."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "https://doc.rust-lang.org/std/process/trait.Termination.html"
    confidence: 0.8
  - statement: "The Helm chart's default livenessProbe and startupProbe both target /_liveness (periodSeconds 10 / 2, failureThreshold 3 / 60), while only readinessProbe targets /_readiness (periodSeconds 5, failureThreshold 3) -- so Kubernetes' decision to restart an already-running pod is never gated on Postgres reachability; only its traffic-routing decision is."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/deployment.yaml"
  - statement: "Because startupProbe and livenessProbe both target /_liveness rather than /_readiness, a Postgres outage that begins only after the pod has already started cannot, by itself, cause Kubernetes to restart the container; a Postgres outage present at pod start instead causes the process itself to exit before any probe can succeed (per the eager-connect and main()-abort entries above), which the kubelet observes as a container crash and restarts under a Deployment's restartPolicy: Always, repeating and backing off into CrashLoopBackOff for as long as Postgres stays unreachable."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "deploy/charts/buzz/templates/deployment.yaml"
      - "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy"
    confidence: 0.8
  - statement: "The Helm chart's own Postgres subchart dependency is disabled by default (postgresql.enabled: false) and is documented as an eval-only convenience; a production deployment instead points externalPostgresql.url at a managed database the chart neither runs nor manages, so there is typically no in-cluster Postgres pod for an operator to kubectl exec into."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/Chart.yaml"
  - statement: "The published relay runtime image installs only ca-certificates, curl, git and openssl beyond the base debian-slim image, and exposes port 3000 for the app, 8080 for /_liveness and /_readiness, and 9102 for Prometheus metrics; it installs no PostgreSQL client -- no psql, no pg_isready."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "deploy/compose/compose.yml's own production relay healthcheck avoids curl, wget and socat entirely, probing /_readiness with a raw /dev/tcp bash redirection under an inline comment stating the runtime image has bash but none of those three tools -- which is in tension with the Dockerfile's curl install recorded in the previous entry, and is recorded here as an unresolved discrepancy between two in-repo sources rather than resolved in either direction."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "/_liveness and /_readiness are registered both on the main application router and on a separate build_health_router carrying no auth, CORS, or metrics middleware; main() binds that second router on a dedicated port (BUZZ_HEALTH_PORT, default 8080) that the code comments describe explicitly as existing 'for K8s probes'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "buzz-relay's own configuration doc comment states that its default writer/reader pool ceiling of 50 connections, originally sized for a handful of pods against a fixed Postgres max_connections=100, becomes the binding constraint against a large connection budget such as Aurora's roughly 5,000: a burst of concurrent handlers exhausts the per-pod pool and requests fail on acquire timeout while the database itself sits idle -- a distinct symptom from Postgres being unreachable."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "An exhausted pool surfaces to a caller as sqlx::Error::PoolTimedOut once the pool's acquire_timeout elapses (3 seconds by default for the writer pool); buzz-db's own read-routing fallback explicitly matches this variant to detect and log reader-pool exhaustion under the reason reader_acquire_timeout, the same error class a saturated writer pool returns to any handler trying to acquire a connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "A background task polls Db::pool_stats() every BUZZ_POOL_METRICS_INTERVAL_SECS (default 10 seconds) and publishes buzz_db_pool_size, buzz_db_pool_idle, buzz_db_pool_active and buzz_db_pool_max -- plus the equivalent buzz_db_read_pool_* gauges when a read replica is configured -- as Prometheus gauges."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "Because readiness_handler wraps all three dependency checks in one fixed 2-second timeout while the writer pool's own default acquire_timeout is 3 seconds, a Postgres that is reachable but saturated enough that SELECT 1 cannot acquire a connection within 2 seconds can present at /_readiness identically to Postgres being fully unreachable -- the endpoint alone cannot distinguish 'down' from 'so exhausted the ping itself starves'."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-db/src/runtime/mod.rs"
    confidence: 0.6
  - statement: "The repository's local-development docker-compose.yml runs Postgres 17 with a healthcheck of `pg_isready -U buzz` every 5 seconds, and the Justfile's _ensure-services target polls `docker inspect --format '{{.State.Health.Status}}' buzz-postgres` to wait for that healthcheck to report healthy before running migrations."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
      - "Justfile"
  - statement: "deploy/compose/compose.yml's production single-relay stack runs its own postgres service with a pg_isready healthcheck and a `depends_on: postgres: condition: service_healthy` clause on the relay service, and composes the relay's DATABASE_URL against the hostname `postgres` on the compose network rather than `localhost`."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "deploy/compose/run.sh's backup-hint command runs a backup_hint shell function that only prints a static checklist naming deploy/compose/.env secrets, the owner private key, 'Postgres data (prefer pg_dump or a quiesced volume snapshot)', object/git storage, and the Caddy volumes; it performs no backup or restore action itself."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh"
  - statement: "buzz-admin's entire CLI surface (its Command enum) offers AddMember, RemoveMember, ListMembers, GenerateKey, Migrate, ProductFeedback, Deletions and ReconcileChannels; none of these is a backup, restore, or database-connectivity-check subcommand."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
  - statement: "deploy/charts/buzz/README.md's own 'Backups' section likewise only enumerates five things an operator must save (including 'PostgreSQL database -- the canonical event store') without providing any chart-driven backup or restore automation for any of them."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "Issue #1215 (unmerged at the time this node was written) is the separate reliability reference node scoped to deeper database-failure-mode analysis; this runbook does not restate that analysis and does not link its path because the corresponding node is not yet merged to origin/launchpad."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "batch dispatch brief for issue #1224, naming sibling issue #1215 as the failure-mode reference"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook's body to carry Trigger, Severity and impact, Diagnosis, Mitigation and resolution, Escalation, and Scope and omissions, each traceable to the Google SRE Workbook's playbook definition."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: references
    target: layers-observability-readiness
  - type: references
    target: layers-observability-liveness
  - type: references
    target: layers-observability-health-checks
  - type: references
    target: layers-observability-prometheus
  - type: references
    target: architecture-containers-postgres
  - type: references
    target: architecture-deployment-kubernetes
---

# Runbook: Postgres unavailable

How to recognize, diagnose, mitigate, and escalate a Postgres outage affecting
`buzz-relay`, and how to tell that condition apart from a saturated-but-reachable
connection pool that presents almost identically. This node is the operational
playbook for the moment of the incident. It is not the failure-mode analysis --
that is a separate, narrower reference node (see *Scope and omissions*) -- and it
is not a description of Postgres's own architecture in this system, which
`architecture-containers-postgres` already covers.

## Trigger

Two distinct triggers exist, and they look different from the first moment:

1. **Boot-time trigger.** A relay pod or container fails to become healthy at
   all: no `/_liveness` or `/_readiness` response, and the process log shows
   `Failed to connect to Postgres: ...` followed by process exit. This happens
   because `buzz-relay`'s writer pool is connected eagerly, not lazily -- `main()`
   awaits `Db::new(&db_config)` and propagates any connection error with `?`
   before the API router, the health router, or any TCP listener is constructed.
   Under Kubernetes this reads as `CrashLoopBackOff`, or as a `startupProbe`
   that never succeeds during the initial rollout window.
2. **Runtime trigger.** A previously healthy relay starts returning `503` from
   `/_readiness` (both on the main app port and on the dedicated health port,
   `BUZZ_HEALTH_PORT`, default `8080`, which the code comments describe as
   existing specifically "for K8s probes"), with a JSON body naming `postgres`
   as not-ok, while `/_liveness` keeps returning `200`. This is Postgres
   becoming unreachable (or too slow to reach) *after* the writer pool already
   exists, not at boot.

Under Kubernetes, the chart's `livenessProbe` and `startupProbe` both target
`/_liveness`; only `readinessProbe` targets `/_readiness`. A runtime-trigger
outage therefore never makes Kubernetes restart an already-running pod by
itself -- it only removes the pod from Service endpoints. Do not expect a
restart to fix a runtime-trigger outage; there is nothing for a restart to
clear that the readiness check itself has not already reported.

## Prerequisites

- Read or exec access to the relay's runtime environment: `docker compose exec`
  under the compose stacks, or `kubectl exec` / `kubectl describe pod` /
  `kubectl logs` under Kubernetes.
- Access to whatever collects the `buzz_db_pool_*` Prometheus gauges this
  deployment scrapes (this repository defines the metrics; it does not ship a
  dashboard or alerting rule for them -- see *Scope and omissions*).
- Under Kubernetes with an externally managed Postgres (the default: the
  chart's own Postgres subchart dependency is `postgresql.enabled: false`),
  access to that external database's own operator console or monitoring, since
  there is typically no in-cluster Postgres pod to inspect directly.
- Knowledge of which deployment shape is running: the local-development
  `docker-compose.yml` (relay runs on the host, Postgres in a container reached
  at `localhost`), the self-hosted production `deploy/compose/compose.yml`
  (relay *and* Postgres both containerized, reached at the compose-network
  hostname `postgres`), or the Helm chart under Kubernetes. The checks below
  differ by shape.

## Severity and impact

A **boot-time** outage means the affected pod or container never starts
serving. Under a multi-replica Kubernetes deployment, existing healthy pods
keep serving while the new one crash-loops; under a single-instance compose
deployment, the service is fully down. A **runtime** outage means every
handler that needs the writer pool -- event writes, most reads, membership and
moderation actions -- starts failing for connections still routed to the
affected instance, and, once `readinessProbe`'s `failureThreshold` (3 checks at
`periodSeconds: 5`, so roughly 15 seconds by the chart's own defaults) is
reached, Kubernetes stops sending new traffic to that pod at all. Either way,
this is user-facing and urgent: no code path in this relay serves Nostr events
without the writer pool.

## Diagnosis

1. **Read the `/_readiness` body, not just the status code.** A `503` with
   `{"status": "shutting_down"}` is a graceful drain, not a Postgres outage --
   `readiness_handler` returns that distinct body when the shutdown flag is
   already set, before it ever checks Postgres. A `503` with
   `{"status": "not_ready", "postgres": false, ...}` is the outage this runbook
   covers.
2. **Distinguish boot-time from runtime by whether the process is running at
   all.** If the container/pod is not up (`docker compose ps` shows the relay
   exited, or `kubectl get pods` shows `CrashLoopBackOff`/`Error`), this is the
   boot-time trigger: check relay logs for `Failed to connect to Postgres`. If
   the process is up and only `/_readiness` is unhealthy, this is the runtime
   trigger.
3. **Distinguish "Postgres is down" from "the pool is exhausted."** Both
   present as `/_readiness` reporting `postgres: false`, because the readiness
   check's own 2-second timeout is shorter than the writer pool's default
   3-second `acquire_timeout` -- a pool so saturated that `SELECT 1` cannot get
   a connection within 2 seconds looks identical, at this endpoint, to Postgres
   being fully unreachable. Check `buzz_db_pool_active` against
   `buzz_db_pool_max`: pool exhaustion shows `active` pinned at `max` with
   `idle` at zero while the database itself may otherwise be reachable (`docker
   compose exec postgres pg_isready`, or the equivalent for an externally
   managed instance, still succeeds). A genuine outage shows the pool unable to
   open *any* connection, active or idle.
4. **Check reachability from the relay's own network position**, without
   depending on a Postgres client being present in the relay image (the
   Dockerfile installs `curl`, but `deploy/compose/compose.yml`'s own relay
   healthcheck avoids `curl`/`wget`/`socat` and instead probes over a raw
   `/dev/tcp` redirection -- see *Scope and omissions* for why this document
   does not resolve that discrepancy). The same technique works from either
   compose or Kubernetes, since it depends only on `bash`, which both
   environments' healthchecks already assume is present:

   ```
   bash -c 'exec 3<>/dev/tcp/127.0.0.1/8080; \
     printf "GET /_readiness HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n" >&3; \
     cat <&3'
   ```

   Under compose: `docker compose exec relay <that command>`, or simply read
   Docker's own cached result with `docker inspect --format '{{json .State.Health}}' <relay-container>`
   -- the production compose stack already runs an equivalent check on a timer,
   so the answer may already be sitting there. Under Kubernetes:
   `kubectl exec <pod> -- <that command>`, or `kubectl describe pod <pod>` to
   read the probe-failure events Kubernetes already recorded.
5. **Check Postgres itself, not just the relay's view of it**, when the shape
   permits: under either compose stack, `docker compose exec postgres pg_isready -U buzz`
   talks to Postgres directly (the `postgres:17-alpine` image ships
   `pg_isready`); the compose files' own healthchecks already run this on a
   timer, so `docker compose ps` or `docker inspect ... buzz-postgres` may
   answer this without a fresh command. Under Kubernetes with a managed
   external database (the common case -- see *Prerequisites*), there is
   usually no pod to exec into at all; use that provider's own status surface
   instead.

## Mitigation and resolution

Ordered from least to most disruptive; try mitigation before resolution steps
that require someone else's action.

1. **If this is the runtime trigger and the diagnosis points at pool
   exhaustion, not a real outage:** this is a capacity problem, not a Postgres
   failure. Reducing concurrent load (backing off a bulk job, a misbehaving
   client, or a traffic spike) can relieve it without touching Postgres at
   all. Raising `BUZZ_DB_POOL_SIZE` is a configuration change for a future
   rollout, not something to attempt live against an already-struggling
   instance.
2. **If Postgres itself is unreachable, escalate to whoever operates it**
   (see *Escalation*) -- nothing in this repository can restart or repair
   Postgres from the relay's side. The relay's own writer pool has no failover
   or reconnection strategy beyond `sqlx`'s normal per-acquire reconnect
   attempts on the same configured URL: it does not fail over to a different
   host, and it does not retry the URL that is currently unreachable on any
   schedule the relay controls.
3. **If this is the boot-time trigger**, the pod itself is not the fault --
   redeploying or restarting it changes nothing while Postgres stays
   unreachable, and under Kubernetes it will simply keep crash-looping.
   Confirm Postgres is reachable first (*Diagnosis*, step 5), then let the
   existing restart mechanism (Kubernetes' own backoff, or `docker compose up`
   under compose) bring the process back up once it is; do not intervene
   beyond confirming the underlying cause is cleared.
4. **Once Postgres is confirmed reachable again**, no manual reconnect step
   exists or is needed for a runtime-trigger pod: the writer pool's own
   `acquire`-time behavior against a healthy Postgres recovers on its own, and
   `/_readiness`'s next check cycle reflects that. A boot-time-trigger pod
   that is still crash-looping needs Kubernetes' own backoff to bring it back,
   or a manual restart under compose (`docker compose exec relay` is not
   available on a crashed container; use `docker compose restart relay` /
   `docker compose up -d`).

## Verification of recovery

- `/_readiness` returns `200` with `{"status": "ready"}` from both the main
  app port and the dedicated health port.
- `buzz_db_pool_active` stops being pinned at `buzz_db_pool_max`, and
  `buzz_db_pool_idle` is nonzero again.
- Under Kubernetes, the pod's `Ready` condition is `True` and it has rejoined
  the Service's endpoint list; under compose, `docker compose ps` / `docker
  inspect ... <relay-container>` reports the relay healthy again.
- For a boot-time-trigger incident, confirm the process actually stayed up
  past one full `startupProbe` window (or, under compose, past one full
  restart) rather than only checking that it started once.

## Escalation

There is no in-repo backup or restore tooling to reach for. `deploy/compose/run.sh`'s
`backup-hint` command prints a static checklist -- naming "Postgres data (prefer
`pg_dump` or a quiesced volume snapshot)" among the things to have saved -- and
performs no backup or restore action itself; `buzz-admin`'s entire CLI surface
(`AddMember`, `RemoveMember`, `ListMembers`, `GenerateKey`, `Migrate`,
`ProductFeedback`, `Deletions`, `ReconcileChannels`) contains nothing for
database connectivity, backup, or restore either. This runbook's mitigation
steps are therefore the full extent of what this repository gives an operator;
beyond them:

- **Postgres itself is unreachable and stays that way past a few minutes of
  the checks in *Diagnosis*:** escalate to whoever operates the database --
  under Kubernetes with an external/managed Postgres (the default deployment
  shape), that is the managed-database provider or its on-call, not this
  relay's own on-call; under either compose stack, that is whoever has access
  to the `buzz-postgres` / `postgres` container and its volume.
- **Data appears lost, not merely unreachable** (a corrupted volume, a
  Postgres instance that comes back up empty): this is beyond mitigation --
  restoring from whatever backup the operator's own process produced (this
  repository only tells them what to have saved, per `backup-hint` and the
  Helm chart's own "Backups" section; it does not produce or apply a backup
  itself) is the only path, and that decision belongs to whoever owns data
  recovery for the deployment, not to this runbook.
- **The pool-exhaustion diagnosis in step 3 does not resolve after reducing
  load:** this points at undersized pool configuration for the deployment's
  actual concurrency, which is a capacity-planning and rollout decision, not
  an incident-response action -- escalate to whoever owns `buzz-relay`'s
  configuration for this deployment.

## Evidence to preserve

Before mitigating, capture (a screenshot or copy is enough -- nothing here
needs to be pristine, only legible afterward):

- The `/_readiness` response body at the time of the incident, including which
  of `postgres` / `redis` / `deletion_catalog` it named as failing.
- A snapshot of `buzz_db_pool_size` / `_idle` / `_active` / `_max` (and the
  read-pool equivalents, if a replica is configured) from whatever scrapes
  those Prometheus gauges, spanning from before the incident started through
  recovery.
- Relay logs from the affected instance covering the failure window --
  particularly the exact `Failed to connect to Postgres: ...` line for a
  boot-time trigger.
- Under Kubernetes: `kubectl describe pod` output (probe-failure events) and
  `kubectl get events` for the affected pod/namespace; under compose:
  `docker compose logs postgres relay` and `docker inspect ... <container>`
  health history.

## Scope and omissions

**This node covers** recognizing a Postgres-unavailable condition against
`buzz-relay`, telling a boot-time crash-loop apart from a runtime readiness
failure, telling a real outage apart from pool exhaustion that presents the
same way, mitigation and resolution steps in executable order, verifying
recovery, and escalation given what this repository does and does not provide.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Deeper analysis of database failure modes and their causes | A separate reliability reference node, tracked under issue #1215 at the time this node was written. That node is unmerged, so this runbook names the boundary without linking its path -- see `launchpad/docs/corpus/AGENTS.md`'s rule that a `relationships[].target` may only name an id already merged to the branch being validated against. |
| Postgres's role and configuration in this system's architecture in general | `architecture-containers-postgres` |
| Kubernetes deployment topology in general | `architecture-deployment-kubernetes` |
| What `/_liveness`, `/_readiness`, and health-check design mean in general (not specific to a Postgres incident) | `layers-observability-liveness`, `layers-observability-readiness`, `layers-observability-health-checks` |
| Designing or standing up a Prometheus alerting rule or dashboard for `buzz_db_pool_*` | Not implemented in this repository today -- `layers-observability-prometheus` documents the exposition pipeline the gauges ride, not an alert on them |
| Designing or implementing backup/restore tooling for Postgres | Not implemented in this repository today; `deploy/compose/run.sh`'s `backup-hint` and `deploy/charts/buzz/README.md`'s "Backups" section only enumerate what to save |
| Capacity planning for pool sizing under a given deployment's real concurrency | Not settled here; *Escalation* names it as a rollout decision |

**Expected but not verified when this node was written:**

- **The curl/no-curl discrepancy** between the Dockerfile (which installs
  `curl` into the runtime image) and `deploy/compose/compose.yml`'s own relay
  healthcheck comment (which asserts the runtime image has "bash but no
  curl/wget/socat" and probes over raw `/dev/tcp` instead) was not resolved.
  Both are real, current files in this repository; which one accurately
  describes the image actually published under a given tag was not checked
  against a running container. *Diagnosis* step 4 sidesteps the question by
  using the `/dev/tcp` technique either way, since it is proven by being the
  exact check the shipped compose healthcheck already runs.
- **Whether the eval-only Postgres subchart pod (`postgresql.enabled: true`)
  is ever reachable via `kubectl exec` in a real deployment** was not
  exercised -- this node relied on the chart's own values file and dependency
  declaration, not on installing the chart with that flag set and inspecting
  the result.
- **No live incident was reproduced against a running relay** to observe the
  boot-time and runtime triggers directly; every claim above is grounded in
  reading the source that implements the behavior, not in triggering it and
  watching the outcome.
