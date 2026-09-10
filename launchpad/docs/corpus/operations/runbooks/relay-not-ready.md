---
id: operations-runbooks-relay-not-ready
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
  - statement: "`/health` and `/_liveness` each return an unconditional `200 ok` with no dependency check of any kind -- neither handler references the database, Redis, or media storage."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`/_readiness` returns 503 with body `{\"status\": \"shutting_down\"}` immediately once the process's shutdown flag is set, before any dependency check runs; otherwise it runs a Postgres ping, a Redis pool acquisition, and the community-deletion serving-catalog validation concurrently under a 2-second timeout (a timed-out check counts as failed), and returns 200 `{\"status\": \"ready\"}` only when all three succeed, else 503 with a JSON body naming which of `postgres`, `redis`, and `deletion_catalog` is false."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`Db::ping` (the `postgres` check behind `/_readiness`) executes `SELECT 1` and returns `false` on any error rather than propagating the underlying error, so the readiness JSON body cannot distinguish 'Postgres unreachable' from 'Postgres reachable but the query itself failed' -- both read as `postgres: false`."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs"
  - statement: "The `deletion_catalog` check (`validate_deletion_serving_catalog` -> `DeletionStore::validate_serving_catalog`) compares the live `communities` table's `deletion_state`, `deletion_fence_generation`, and `deleted_at` columns against expected types and nullability, and confirms that `communities`, `community_serving_write_leases`, and `community_deletion_requests` exist -- a narrow schema-shape check on three tables and three columns, not a general migration-freshness check and not a connectivity check. A `deletion_catalog: false` reading means one of those tables or columns is missing or mistyped, which is a migration/schema-drift condition distinct from what the `postgres` field measures."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs"
  - statement: "The health-only router serving `/_liveness`, `/_readiness`, `/_status`, and `/_mesh` is bound to a separate TCP listener on `config.health_port` (default 8080), distinct from the main application router's WebSocket/REST listener on `config.bind_addr` -- so the health port and the main port can each be reachable or unreachable independently of the other."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "At startup, connecting the writer Postgres pool, running pending migrations when `BUZZ_AUTO_MIGRATE` is enabled, validating the community-deletion serving catalog, and verifying the channel-roster fence (whose own error message names migration `0032_channel_roster_snapshot_fence.sql` as the fix) are each propagated with `?`/`return Err` out of `main`, so a failure in any one of them ends the process before it ever binds the health-port listener -- no `/_liveness` or `/_readiness` response is possible during this window."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "migrations/0032_channel_roster_snapshot_fence.sql"
  - statement: "`relay_keypair_from_config` turns an absent `BUZZ_RELAY_PRIVATE_KEY` into the error \"BUZZ_RELAY_PRIVATE_KEY must be set. Run `just bootstrap` for local development or configure a stable 32-byte hex private key.\", and `main` calls it at line 156 -- immediately after `Config::from_env()` and before the Postgres pool is built -- so a relay with no signing key exits before it reaches any dependency check, unconditionally and regardless of `BUZZ_REQUIRE_RELAY_MEMBERSHIP`. The membership-conditional message at line 260 is therefore unreachable when the key is absent."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:38-45"
      - "crates/buzz-relay/src/main.rs:156"
      - "crates/buzz-relay/src/main.rs:260-265"
  - statement: "The git object-store A3 conformance probe runs at startup whenever `BUZZ_GIT_CONFORMANCE_PROBE` is unset or not the literal string `\"false\"`, and its error is likewise propagated with `?`, ending the process before the health-port listener binds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The Redis pool handle is constructed synchronously by `deadpool_redis::Config::create_pool`, which performs no network I/O and fails only on an unparseable URL, and `PubSubManager::new`/`with_config` -- awaited immediately afterward -- only allocate in-process broadcast channels and state, issuing no Redis command. So, unlike an unreachable Postgres, an unreachable Redis at boot does not stop the relay process from starting or from binding the health-port listener."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-pubsub/src/lib.rs"
  - statement: "Once a SIGTERM is observed, the relay sets the shutdown flag before beginning its drain, so `/_readiness` starts returning 503 `{\"status\": \"shutting_down\"}` immediately, while `/_liveness` and `/health` keep reporting `200 ok` until the process actually exits -- a `shutting_down` readiness body during a rolling deploy or restart is expected, not a fault."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/router.rs"
  - statement: "`deploy/charts/buzz/values.yaml`'s default `livenessProbe` and `startupProbe` both target `/_liveness` (the unconditional endpoint); only `readinessProbe` targets `/_readiness`. `startupProbe.failureThreshold: 60` at `periodSeconds: 2` allows up to 120 seconds after container start before Kubernetes gives up on startup and restarts the container."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
  - statement: "Because both `livenessProbe` and `startupProbe` check the unconditional `/_liveness` endpoint rather than the dependency-aware `/_readiness` endpoint, a relay process that is running (health port bound, main loop alive) but permanently failing its dependency checks does not fail liveness on that basis alone, so this probe configuration gives kubelet no mechanism to restart such a pod -- it is removed from Service endpoints and left running until the dependency recovers or an operator intervenes."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "crates/buzz-relay/src/router.rs"
    confidence: 0.85
  - statement: "`deploy/compose/compose.yml`'s `relay` service declares `depends_on` on `postgres`, `redis`, and `minio` reaching `service_healthy` and `minio-init` reaching `service_completed_successfully`, so Compose will not even start the relay container until those dependencies already report healthy -- narrowing a relay-not-ready symptom seen immediately after `docker compose up` on this stack toward migration state, the git-object-store conformance probe, or configuration, rather than raw dependency unreachability at first boot. `architecture-deployment-docker-compose` is the canonical node for this stack's full topology and healthcheck mechanism and is not restated here."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.yml"
  - statement: "The repository root `docker-compose.yml` (dev-support stack: postgres, redis, adminer, keycloak, minio, prometheus) declares no relay or buzz-relay service at all, so none of its healthchecks gate a local-development relay process -- that process is run separately (for example via `just relay`), outside this compose file."
    entry_class: FACT
    evidence:
      - "docker-compose.yml"
  - statement: "`/_status` reports the service name, package version, process uptime in seconds, and build identity (source SHA, build id, build URL) -- useful for telling a process that has just (re)started, or that is cycling through a crash loop, from one that has been running for a long time while still failing readiness."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`readiness_handler`'s dependency check calls only `state.db.ping()`, `state.redis_pool.get()`, and `state.db.validate_deletion_serving_catalog()` -- it makes no call into `buzz_media`, S3, or any object-storage client. An object-storage outage therefore does not surface as 'relay not ready': `/_readiness` continues to report ready while media upload/download requests fail."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "`launchpad/docs/Observability/current-state/relay.md`, written independently of this node, describes the same three application-router health endpoints and states that the readiness failure response 'names which check failed,' corroborating this node's reading of `readiness_handler` from a separately authored source."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/relay.md"
  - statement: "`architecture-deployment-kubernetes` records that Buzz's canonical Kubernetes deployment automation is the Helm chart at `deploy/charts/buzz`, that schema migrations run automatically at relay startup by default, and that 'the readiness probe checks DB connectivity only, not schema freshness: a pod can report ready against an unmigrated schema and only fail once real traffic hits it' -- a broader caveat this node's own, narrower reading of the `deletion_catalog` check (three tables, three columns) does not contradict: that one specific schema-shape gate is now part of `/_readiness`, but the rest of the schema is still unchecked by it, consistent with the wider point already recorded there."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "`architecture-deployment-kubernetes` also records that the launchpad-26 fork's own operated deployment targets a single VPS via Docker Compose (documented in `launchpad/deploy/`), not Kubernetes, and that `squareup/block-coder-tf-stacks` -- a separate, private repository not present in this checkout -- is what deploys the OSS Helm chart to Block's own staging Kubernetes cluster."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
      - "AGENTS.md"
  - statement: "`launchpad/deploy/README.md` states that `launchpad/deploy/run.sh` is the guarded entry point for this fork's VPS operations, delegating to `deploy/compose/run.sh`, and that it rejects a non-`ghcr.io/launchpad-26/buzz` or floating relay image outside an explicit development override -- confirming a single-VPS, single-Compose-stack deployment with no built-in relay redundancy for this fork's own operated environment."
    entry_class: FACT
    evidence:
      - "launchpad/deploy/README.md"
  - statement: "AGENTS.md (repository root) states that this checkout is a fork that operates Buzz rather than develops it, and that a genuine product bug in Buzz still belongs at `block/buzz/issues` rather than this fork's own issue tracker."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "Neither `launchpad/AGENTS.md` nor `launchpad/README.md` documents an on-call rotation, a paging tool, or a formal incident-escalation contact for this fork's operated deployment; the only escalation path evidenced anywhere in this repository is filing a GitHub issue."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "launchpad/README.md"
  - statement: "Issue #1227's definition of done requires this node to state trigger/symptom, severity/impact, and prerequisites; to give diagnosis then mitigation/recovery in executable order; and to include verification of recovery, rollback/escalation, and evidence to preserve -- the structure this node's sections are organized around."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1227 definition of done"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook instance to state its trigger, severity and impact, diagnosis, mitigation and resolution, and escalation, each traceable to the Google SRE Workbook's playbook definition, plus a scope-and-omissions section, and to declare an `implements` relationship back to the template."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-deployment-docker-compose
---

# Runbook: relay reports not ready / never becomes ready

How to tell why `buzz-relay` is failing its readiness probe, or never becoming
ready at all, and what to do about each real cause the code produces. Built
against the trigger, diagnosis, mitigation, and escalation shape
`corpus-template-runbook` requires.

## Prerequisites

- Ability to read the target relay instance's logs (stdout, JSON-structured)
  and, for a Kubernetes deployment, `kubectl` access to the relay `Deployment`,
  its `Pod`s, and events in its namespace; for this fork's own VPS deployment,
  shell access to the host running `deploy/compose/` (see `launchpad/deploy/README.md`).
- Ability to reach the relay's health port directly (`curl` or an equivalent)
  -- the health-only router is a separate listener from the main application
  port, so the two must be checked independently.
- Familiarity with which deployment target is in play: the OSS Helm chart
  under Kubernetes (Block's own staging cluster, provisioned by the private
  `squareup/block-coder-tf-stacks` repository this checkout does not contain),
  or this fork's own single-VPS Docker Compose stack. The two differ in probe
  wiring, restart behavior, and topology; conflating them misdirects
  diagnosis. `architecture-deployment-kubernetes` and
  `architecture-deployment-docker-compose` cover each in full and are not
  restated here.

## Trigger

Either of two distinct symptoms, which this runbook treats as two different
problems sharing one name:

1. **The relay `Pod`/container never reaches a running, healthy state** --
   Kubernetes reports `CrashLoopBackOff` or repeated restarts, or Compose
   shows the `relay` container exiting and restarting under `restart:
   unless-stopped`.
2. **The relay process is up and staying up, but traffic is not being routed
   to it** -- a Kubernetes `Service` has zero or fewer-than-expected ready
   endpoints for the relay `Deployment`, or a Compose healthcheck reports the
   container `unhealthy` while `docker ps` still shows it running.

These look similar from the outside ("the relay isn't serving") and have
non-overlapping causes. *Diagnosis*, below, is built to tell them apart first.

## Severity and impact

**If every relay replica is affected**, this is a full outage: no new
WebSocket connections, no new HTTP bridge requests (`/events`, `/query`,
`/count`), and no git smart-HTTP traffic can be served, because the readiness
gate (or the process being down at all) removes every replica from serving.
Already-open long-lived connections on a replica that flips from ready to
not-ready are not dropped by readiness alone -- only new connections and
reconnects stop being routed there -- but a replica that is crash-looping has
no open connections to begin with.

**This fork's own operated deployment has no relay redundancy to fall back
on**: `launchpad/deploy/README.md` describes a single VPS running one Compose
stack, so a not-ready or crash-looping relay there is a total outage for
every community this deployment serves, not a partial-capacity event. The
upstream OSS Helm chart supports multiple replicas and a `PodDisruptionBudget`
(`architecture-deployment-kubernetes`), which changes this calculus only for a
deployment that actually runs more than one replica.

**Urgency**: treat as high-severity immediately if every replica is affected
(equivalent to a full service outage); treat as degraded/investigate-soon if
only some replicas of a multi-replica deployment are affected, since the
`Service` is still routing traffic to the healthy ones.

## Diagnosis

Work through these in order; each step is designed to route to the right
half of *Mitigation and resolution* rather than to guess.

### 1. Is the process crash-looping, or running?

- **Kubernetes**: `kubectl get pods -l <relay-selector>` and `kubectl describe
  pod <pod>`. A `RESTARTS` count that keeps climbing, or a status of
  `CrashLoopBackOff`, means the process is exiting -- go to *2a*.
  `kubectl logs <pod> --previous` shows the last exited attempt's output.
- **Compose**: `docker compose ps` (from `deploy/compose/`). A `relay`
  container flapping between `Restarting` and `Exited` means the process is
  exiting -- go to *2a*. `docker compose logs relay --tail=200` shows recent
  output across restarts.
- If the process is `Running`/`Up` and staying up, go to *2b*.

### 2a. Crash-looping: read the last log line before exit

Every eager startup gate in `main` logs a specific `error!` message and
returns `Err` before the process exits, so the log line immediately before
the process restarts names the cause directly. In order of where they run:

1. **`Invalid configuration: ...`** -- `Config::from_env()` rejected an
   environment variable. No health port was ever bound; probes see connection
   refused, not a slow or failing HTTP response.
2. **`BUZZ_RELAY_PRIVATE_KEY must be set. Run `just bootstrap` for local
   development or configure a stable 32-byte hex private key.`** -- the relay
   requires its signing key unconditionally, and checks for it immediately
   after configuration parsing and before it dials Postgres. A deployment
   that has never set the variable never reaches any dependency check at all,
   so this cause looks identical to case 3 from the outside and is
   distinguished only by this log line.
3. **`DB connection failed: ...`** or **`Failed to connect to Postgres:
   ...`** -- the writer Postgres pool could not be established. Hand off to
   the postgres-unavailable runbook (issue #1224 in this same corpus batch)
   for Postgres-side diagnosis and recovery; this node does not duplicate it.
4. **`Failed to run database migrations: ...`** -- only possible when
   `BUZZ_AUTO_MIGRATE` is enabled; a pending migration failed to apply.
5. **`Community deletion serving fence is unsafe: ...`** -- the same
   schema-shape check `/_readiness` runs (`deletion_catalog`) also runs at
   startup and is fatal there. If this is the line, the fix is a schema
   migration, not a Postgres-reachability fix, even though the symptom
   (relay down) looks the same as case 2.
6. **`Channel roster fence is unsafe; apply or repair migration 0032 before
   starting this relay: ...`** -- names the exact migration file
   (`migrations/0032_channel_roster_snapshot_fence.sql`) to check.
7. **`git conformance probe failed: ...`** -- the A3 object-store
   conformance probe rejected the configured git backend. Check
   `BUZZ_GIT_CONFORMANCE_PROBE`/`BUZZ_GIT_PROBE_WRITERS`/`BUZZ_GIT_PROBE_ROUNDS`
   and the backing object-store's support for conditional writes.
8. **`BUZZ_REQUIRE_RELAY_MEMBERSHIP=true but RELAY_OWNER_PUBKEY is not set or
   invalid`** -- a configuration inconsistency between two flags, not a
   dependency outage. Its sibling message `BUZZ_RELAY_PRIVATE_KEY is required
   when BUZZ_REQUIRE_RELAY_MEMBERSHIP=true` exists in the source but is
   unreachable: `relay_keypair_from_config` rejects a missing key
   unconditionally and much earlier, with **`BUZZ_RELAY_PRIVATE_KEY must be
   set`**. That is the message a keyless relay actually prints, whatever the
   membership flag says.
9. **`Redis pool creation failed: ...`** or **`PubSub init failed: ...`** --
   rare in practice: pool construction and `PubSubManager` initialization do
   no real Redis I/O (see the evidence ledger), so this almost always means a
   malformed `REDIS_URL`, not an unreachable Redis host. An unreachable Redis
   host at boot does **not** stop the process from starting; if the process
   is crash-looping, this is not why.
10. **`Search DB connection failed: ...`** or **`Audit DB connection failed:
   ...`** -- a second, separate Postgres connection (search replica or audit
   database) failed, distinct from the writer pool in case 2.
11. **`invalid media config: ...`** or **`failed to initialize media
    storage: ...`** -- a configuration/construction failure for object
    storage, distinct from the object-storage-unavailable runbook's subject
    (issue #1223), which covers a reachable-but-failing store after startup.

If none of these lines appear and the process is exiting anyway (for
example, `Drain timeout exceeded — forcing exit`), that is the graceful-shutdown
hard-stop firing after a SIGTERM -- expected during a deploy or manual
restart, not a fault; confirm a deploy or `docker compose restart relay` was
in flight around the same timestamp.

### 2b. Running but not routed: read `/_readiness`'s body

```
curl -s http://<health-host>:<health-port>/_readiness
```

(Default health port `8080` unless `BUZZ_HEALTH_PORT`/`service.healthPort`
overrides it.) Three shapes, three different next steps:

- **`{"status": "shutting_down"}`, HTTP 503** -- a SIGTERM has been received
  and the relay is draining. Expected during a deploy or restart; wait for
  the rollout to finish. If this persists far longer than the configured
  termination grace period, the drain itself may be stuck -- check for the
  `Drain timeout exceeded — forcing exit` log line, which forces the process
  to exit and should end this state.
- **`{"status": "not_ready", "postgres": false, ...}`, HTTP 503** -- Postgres
  is unreachable or the `SELECT 1` ping is failing. Hand off to the
  postgres-unavailable runbook (#1224); this node does not duplicate its
  recovery steps.
- **`{"status": "not_ready", "redis": false, ...}`, HTTP 503** -- the Redis
  pool cannot acquire a connection. Hand off to the redis-unavailable runbook
  (#1226); this node does not duplicate its recovery steps.
- **`{"status": "not_ready", "deletion_catalog": false, ...}`, HTTP 503** --
  the `communities`/`community_serving_write_leases`/
  `community_deletion_requests` schema-shape contract is not satisfied on the
  live database. This is a migration/schema problem, not a raw connectivity
  problem, even when `postgres` reads `true` in the same body. Check pending
  migrations against the live schema and confirm they have actually been
  applied (`BUZZ_AUTO_MIGRATE` may be disabled in this environment, requiring
  a manual `buzz-admin migrate` per `architecture-deployment-kubernetes`).
- **More than one of the three is `false`** -- diagnose in the order above;
  a downed Postgres commonly also drags down `deletion_catalog` (the query
  behind it needs the same database), so `postgres: false` is very likely the
  root cause when both are false together, while `redis: false` failing
  alongside a healthy `postgres` is unrelated to it.
- **No response at all / connection refused on the health port** -- the
  process has not bound the health-port listener yet (early in an eager
  startup gate, see *2a*) or the health port is unreachable for a network/
  firewall/`NetworkPolicy` reason unrelated to application state. Distinguish
  by checking whether the main application port is reachable: if neither
  port responds, suspect the process itself (case *2a*); if only the health
  port is unreachable while the main port answers, suspect port-specific
  network configuration, a `NetworkPolicy`, or a Compose port-mapping change.
- **Confirm this is not an object-storage problem wearing this runbook's
  symptom**: `/_readiness` never checks object storage at all, so a media/S3
  outage cannot produce a `not_ready` reading here. If uploads or downloads
  are failing while `/_readiness` reports `ready`, that is the
  object-storage-unavailable runbook's subject (#1223), not this one.

### 3. Cross-check with `/_status` and `/_liveness`

`/_liveness` returning `200 ok` while `/_readiness` returns 503 confirms the
process is alive and the health port is bound -- this is case *2b*, not *2a*.
`/_status`'s `uptime_seconds` tells you whether this is a long-lived pod
stuck not-ready (large uptime, dependency has been down a while) or a pod
that just restarted and has not yet passed its checks (small uptime, may
still be within `startupProbe`'s grace window). Because `livenessProbe` also
targets `/_liveness` rather than `/_readiness`
(*Kubernetes-specific behavior*, below), a long-uptime, permanently-not-ready
pod will **not** be restarted by kubelet on that basis alone -- it stays
`Running` and unready until the dependency recovers or an operator acts.

## Mitigation and resolution

**Mitigation (reduce impact now), by cause:**

- **Dependency-specific `not_ready` (`postgres`/`redis`/`deletion_catalog`
  false)**: if a multi-replica deployment has at least one healthy replica,
  the `Service` is already routing only to it -- no immediate action needed
  beyond fixing the dependency per the relevant sibling runbook. On this
  fork's single-VPS deployment there is no other replica to fall back to.
- **Crash-looping on a config or schema-gate error (cases 1, 3, 4, 5, 7, 10
  in *2a*)**: do not restart-loop the deployment hoping it self-heals -- none
  of these resolve without an operator fixing the underlying configuration,
  migration, or key material. Repeated restarts only extend the outage
  window and add log noise.
- **Crash-looping on a genuine Postgres outage (case 2)**: follow the
  postgres-unavailable runbook (#1224).

**Resolution (fix the underlying condition), by cause:**

- **Missing/invalid config** (`Invalid configuration`, the NIP-43
  owner/key checks, `invalid media config`): correct the named environment
  variable and redeploy/restart.
- **Unapplied or failed migration** (`Failed to run database migrations`,
  `Community deletion serving fence is unsafe`, the migration-0032 channel
  roster fence error, or a `deletion_catalog: false` `/_readiness` body):
  apply the pending migration(s) against the live database (`buzz-admin
  migrate`, or ensure `BUZZ_AUTO_MIGRATE` is enabled for environments that
  rely on it), then restart the relay so the startup gates re-check cleanly.
- **Git conformance probe failure**: fix the backing object-store's
  conditional-write support, or, only as a temporary, explicitly-accepted
  risk, set `BUZZ_GIT_CONFORMANCE_PROBE=false` to skip the gate -- this
  removes a correctness guarantee for the git manifest-pointer protocol and
  should not be left set long-term.
- **Malformed `REDIS_URL`** (`Redis pool creation failed`/`PubSub init
  failed`): correct the URL; these two errors are not evidence of a reachable
  -but-down Redis host, which instead surfaces only via `/_readiness`'s
  `redis: false` (see the redis-unavailable runbook, #1226).
- **Postgres or Redis genuinely unreachable**: follow the postgres-unavailable
  (#1224) or redis-unavailable (#1226) runbook; not duplicated here.
- **Stuck in `shutting_down` past the expected drain window**: check whether
  the graceful-drain hard-stop (`Drain timeout exceeded — forcing exit`) has
  fired; if the process has not exited and no such deploy/restart was
  intended, treat it as a hung process and escalate per *Escalation*.

## Verification of recovery

1. **`/_readiness` returns HTTP 200 `{"status": "ready"}`** from the affected
   instance(s) directly (not only via a load balancer, which may already be
   routing around the bad instance).
2. **For a crash-loop fix**: the process stays `Running`/`Up` past one full
   `startupProbe` window (up to 120 seconds under the chart's defaults) and
   `/_status`'s `uptime_seconds` keeps climbing across at least two checks a
   few seconds apart, rather than resetting to a small number.
3. **For a Kubernetes `Service`**: `kubectl get endpoints <service>` lists
   the expected number of ready addresses again.
4. **For the Compose stack**: `docker compose ps` shows the `relay` service
   as `healthy`, not merely `Up`.
5. **Confirm the specific dependency check that was failing now reads
   `true`** in the `/_readiness` JSON body, not just that the overall status
   flipped to `ready` -- a flapping dependency can briefly read `ready` mid-
   recovery before failing again.

## Rollback

If the trigger was a deployment (a new image, a config change, or a
migration bundled with a release) rather than an external dependency outage,
rolling back the deployment to the last known-good image/config is a valid
mitigation while the underlying defect is fixed properly -- standard for
this Helm chart's `RollingUpdate` strategy and this fork's Compose `upgrade`/
`restart` commands (`architecture-deployment-kubernetes`,
`architecture-deployment-docker-compose`). A schema migration that already
ran against the live database is not automatically undone by rolling back
the relay image; do not assume a code rollback also reverts a migration.

## Escalation

No on-call rotation, paging tool, or formal incident contact for this
fork's operated deployment was found anywhere in this repository or its
`launchpad/` governance documents -- escalation here means opening a GitHub
issue and getting a human's attention on it directly.

- **A genuine defect in Buzz itself** (the relay code, not this fork's
  configuration or infrastructure) belongs at
  [block/buzz/issues](https://github.com/block/buzz/issues), per this
  repository's own fork-boundary statement in `AGENTS.md`.
- **This fork's own VPS deployment** is operated via `launchpad/deploy/
  run.sh`; consult `launchpad/deploy/README.md` before changing how it is
  invoked, and escalate to whoever holds deploy access for that host if the
  fix requires host-level intervention this runbook does not cover.
- **Block's own staging Kubernetes cluster**, provisioned via the private
  `squareup/block-coder-tf-stacks` repository, is outside this checkout
  entirely -- a responder without access to that repository cannot inspect
  or change its cluster-level configuration and needs to escalate to
  whoever operates it.
- **Stop trying alone** once the diagnosis in this runbook cannot identify
  which of the documented causes applies, or once a fix has been applied and
  *Verification of recovery* still fails after one full retry -- at that
  point the cause is likely outside what this runbook and its evidence
  cover, and continuing to guess costs more than asking.

## Evidence to preserve

Before restarting a crash-looping process or otherwise clearing the
condition, capture:

- The exact log line(s) matched in *Diagnosis, step 2a* (the `error!`
  message immediately preceding process exit), with timestamps.
- The full `/_readiness` JSON body (not just the HTTP status code) from
  every affected instance, and the `/_status` body from the same instances.
- `kubectl describe pod`/`kubectl get events` output (Kubernetes) or
  `docker compose logs relay --tail=500` (Compose) spanning the incident
  window.
- Whether a deployment, configuration change, or migration was in flight
  around the time the symptom started, and its identifying reference (image
  tag/digest, PR, or migration filename).

## Scope and omissions

**This node covers** distinguishing a crash-looping relay from a
running-but-not-ready one, reading the specific cause out of the startup
log or the `/_readiness` JSON body, and the mitigation, verification, and
escalation steps that follow from each cause -- for both the OSS Kubernetes
Helm chart and this fork's own Docker Compose deployment.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Postgres-side diagnosis and recovery once `postgres` or `deletion_catalog` reads false | The postgres-unavailable runbook, issue #1224 (not merged at this node's recorded revision; named here, not linked) |
| Redis-side diagnosis and recovery once `redis` reads false | The redis-unavailable runbook, issue #1226 (not merged at this node's recorded revision; named here, not linked) |
| Object-storage/media diagnosis and recovery -- explicitly **not** part of what `/_readiness` checks at all | The object-storage-unavailable runbook, issue #1223 (not merged at this node's recorded revision; named here, not linked) |
| The Kubernetes Helm chart's full deployment topology, rolling-update behavior, and probe wiring in detail | `architecture-deployment-kubernetes` |
| This fork's Docker Compose stack's full topology and healthcheck mechanism in detail | `architecture-deployment-docker-compose` |
| The relay container's general responsibility boundary (as opposed to its failure modes) | `architecture-containers-relay` (not read in depth for this node; not cited above) |

**Expected but not verified when this node was written:**

- **No test in this repository was found exercising `readiness_handler`
  against a real downed Postgres, Redis, or deletion-serving catalog.** The
  behavior described above was read directly from `router.rs` and
  `deletion.rs`, not observed from a test driving a real outage through the
  handler end-to-end.
- **Whether `kubectl describe pod`/`kubectl get events` actually surface the
  specific `error!` log lines named in *Diagnosis, step 2a* as distinct
  container-termination reasons, as opposed to only in the container's own
  stdout log, was not verified against a running cluster** -- this node
  assumes the operator reads application logs directly (`kubectl logs
  --previous`), which is confirmed, rather than relying on `kubectl
  describe`'s own event summary for the exact error text.
- **The interaction between a flapping dependency and the 2-second
  readiness timeout under real network conditions (as opposed to reading the
  timeout value in code) was not measured.**
- **Whether `docker compose ps`'s `healthy`/`unhealthy` status alone triggers
  any external action** (an alerting rule, a reverse proxy's own health
  check, or similar) **on this fork's VPS was not established** -- `restart:
  unless-stopped` in `deploy/compose/compose.yml` restarts the container only
  if the process itself exits, not merely because its healthcheck reports
  unhealthy, but what (if anything) watches that Docker-level health status
  from outside the container was not investigated for this node.
