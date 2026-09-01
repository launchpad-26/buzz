---
id: layers-lifecycle-startup
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-relay's process entry point, async fn main(), begins by installing the rustls ring crypto provider (required before any TLS connection: rediss:// to a managed Redis, wss://, or S3-over-TLS media storage), then initializes a JSON-structured tracing subscriber with an optional OpenTelemetry layer attached only when OTEL_EXPORTER_OTLP_ENDPOINT-driven tracer construction succeeds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:86-138"
  - statement: "Config::from_env() is the first fallible step after logging is up; a config error is logged and returned as an Err, which ends the process before any connection is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:142-154"
      - "crates/buzz-relay/src/config.rs:461-465"
  - statement: "The Prometheus metrics exporter is installed (relay_metrics::install) immediately after config load, before any database or Redis connection is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:156-164"
  - statement: "Db::new(&db_config) opens the Postgres writer pool (and, if configured, a lazy read-replica pool with min_connections=0 that dials nothing until first use) and is the first hard external dependency in the sequence; failure returns an Err before startup proceeds further."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:166-186"
      - "crates/buzz-db/src/runtime/mod.rs:488-517"
  - statement: "Database migrations only run when the BUZZ_AUTO_MIGRATE environment variable parses as a truthy value (true/1/yes/on, case-insensitive); otherwise startup logs that migrations were skipped and proceeds without applying schema changes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:29-36"
      - "crates/buzz-relay/src/main.rs:188-198"
  - statement: "When migrations do run, db.migrate() calls buzz-db's run_migrations, whose static MIGRATOR is sqlx::migrate!(\"../../migrations\") relative to crates/buzz-db -- i.e. the repository-root migrations/ directory this repository's own top-level CLAUDE.md describes as 'auto-applied on relay startup' -- and migration additionally re-verifies the replica-fence floor-guard trigger catalog on every run, failing closed if any partition is missing it."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs:15"
      - "crates/buzz-db/src/runtime/migration.rs:27-34"
      - "CLAUDE.md"
  - statement: "After the migration decision, startup ensures future table partitions exist, validates the deletion-serving-fence catalog (fatal on failure), and only then spawns the replica freshness-fence probe -- deliberately after the migration decision, per the function's own comment, so a relay running with BUZZ_AUTO_MIGRATE off can never open the fence over an unenforced floor guard; probe failure is loud but non-fatal, leaving all cursor reads on the writer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:200-228"
  - statement: "NIP-43 membership enforcement (BUZZ_REQUIRE_RELAY_MEMBERSHIP=true) requires both a valid RELAY_OWNER_PUBKEY and a configured BUZZ_RELAY_PRIVATE_KEY; either missing is a fatal, fail-fast error returned before any database mutation is attempted, specifically so a relay never starts in an unadministerable or ephemeral-identity state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:230-252"
  - statement: "The deployment's own community is seeded (ensure_configured_community, derived from the same host-normalization the request path uses) before any membership backfill or owner bootstrap, so those subsequent writes are scoped to a real community rather than a global pubkey; an unresolvable host is fatal only when membership enforcement is on."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:254-297"
  - statement: "Existing pubkey_allowlist entries are backfilled into relay_members before bootstrap_owner runs, specifically ordered (per the function's own comment) so that enabling membership enforcement does not lock out users who were already allowlisted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:299-320"
  - statement: "bootstrap_owner ensures the configured RELAY_OWNER_PUBKEY holds the owner role in the deployment community; failure is fatal only when membership enforcement is on, since an unadministerable relay is otherwise a silent operational risk rather than a hard invariant violation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:322-345"
  - statement: "A Redis connection pool and PubSubManager are constructed, and three background subscriber tasks are spawned immediately after (multi-node fan-out relay, cross-pod cache-key invalidation, cross-pod connection-control commands); Redis pool creation or PubSubManager::new failure is fatal."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:369-399"
  - statement: "The relay's own signing keypair is resolved by strict precedence: a configured BUZZ_RELAY_PRIVATE_KEY is used if present; otherwise, if BUZZ_REQUIRE_AUTH_TOKEN is false, a hardcoded deterministic dev keypair is used with a warning (so addressable events replace correctly across dev restarts); otherwise the process panics, because BUZZ_RELAY_PRIVATE_KEY is required whenever BUZZ_REQUIRE_AUTH_TOKEN is true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:425-446"
  - statement: "AppState::new is constructed from the config clone plus every service built so far (db, redis_health_pool, audit, pubsub, auth, search, workflow_engine, relay_keypair, media_storage), and is the point after which every subsequent startup step and every request handler shares one Arc<AppState>."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:456-468"
  - statement: "The inter-relay mesh is optional and gated by a kill switch inside boot_mesh: when off, nothing is bound, published, or spawned and the relay behaves identically to a build without the mesh; when the switch is on, a misconfigured mesh (bind or Redis failure) is fatal, per the function's own comment ('an operator who asked for the mesh gets it or gets told why not')."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:470-497"
  - statement: "An optional git object-storage conformance probe (default-on, disabled only by BUZZ_GIT_CONFORMANCE_PROBE=false) admits the configured S3/MinIO backend against a linearizable conditional-write axiom before any git traffic is served; probe failure is fatal, per the function's own comment describing it as 'a deployment gate, not a proof.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:499-535"
  - statement: "When membership enforcement is on, NIP-43 membership snapshots are reconciled once synchronously before the listener opens, then again periodically every BUZZ_NIP43_RECONCILE_INTERVAL_SECS (default 60s) in a spawned background loop; both the one-shot and periodic reconciliation log a warning rather than aborting startup on failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:537-577"
  - statement: "Roughly a dozen background tasks are spawned via tokio::spawn between AppState construction and the call to serve(): the workflow cron loop (wired to its action sink first), the ephemeral-channel reaper, the optional NIP-PL push matcher and delivery worker (gated on push_gateway_delivery_url being configured), the NIP-ER reminder scheduler, the multi-node pub/sub fan-out consumer, the cross-pod cache-invalidation consumer, the community-lifecycle revalidator, the cross-pod connection-control consumer, a periodic pool-metrics poller, and a jittered periodic usage-metrics poller; none of these spawns is awaited, so main() proceeds to build the router and call serve() without waiting for any of them to complete a first tick."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:626-633"
      - "crates/buzz-relay/src/main.rs:635-726"
      - "crates/buzz-relay/src/main.rs:728-927"
      - "crates/buzz-relay/src/main.rs:929-1048"
      - "crates/buzz-relay/src/main.rs:1050-1099"
  - statement: "serve() binds the health-probe TCP listener (0.0.0.0:health_port) and spawns its axum::serve task first, then spawns the shutdown-signal watcher (SIGTERM on Unix, or Ctrl+C otherwise, via shutdown_signal()), then binds the primary application TCP listener at config.bind_addr, and, on Unix only, an optional Unix domain socket listener if BUZZ_UDS_PATH is set -- each bind failure returns an Err and ends the process."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1248-1362"
      - "crates/buzz-relay/src/main.rs:1407-1422"
  - statement: "The primary router (and, on Unix, the UDS router) is served via axum::serve(...).with_graceful_shutdown(...), subscribed to a tokio::sync::watch channel the shutdown-signal task sends true on; this is the seam where startup's serving state hands off to the shutdown sequence a sibling node (#1118) covers, and is not re-narrated past that handoff here."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1263-1267"
      - "crates/buzz-relay/src/main.rs:1295-1328"
      - "crates/buzz-relay/src/main.rs:1364-1398"
  - statement: "The liveness probe (/_liveness or equivalent route) always returns 200 unconditionally once its handler is reachable; the readiness probe (/_readiness) returns 503 immediately if the shutting_down flag is set, and otherwise returns 200 only when Postgres (db.ping()), Redis (a pool checkout), and the deletion-serving catalog validation all succeed within a 2-second timeout -- a timeout or any single failed check reports 503 with a per-check breakdown."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:370-372"
      - "crates/buzz-relay/src/router.rs:374-414"
  - statement: "desktop/src-tauri/src/main.rs is Buzz Desktop's own process entry point (Tauri 2 application boot: an agent-access probe short-circuit, a Linux-only WebKitGTK rendering-environment fix applied while the process is still single-threaded, then buzz_lib::run()) -- a different trigger (a human launching the desktop app) and different actors (WebKitGTK/Tauri, not Postgres/Redis/the relay's own background tasks) from the buzz-relay process startup this node narrates, with no shared code path between the two mains."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/main.rs:1-20"
  - statement: "No test in this repository directly drives buzz-relay's async fn main() end-to-end and asserts on its startup ordering; the function is exercised only indirectly, by every integration and e2e test that connects to an already-running relay process started out-of-band (e.g. via `just relay` or a test harness that shells out to the built binary)."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs:1121-1165"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
    confidence: 0.6
  - statement: "This node carries type: layers rather than the flow.md template's own worked-skeleton default of type: architecture, because that default is precedent specifically from the architecture/flows/* family (12 nodes narrating flows across the C4 static model this repository's architecture/ corpus subtree already documents), while this task's target path is layers/lifecycle/startup.md and parent Feature #611's own stated Outcome names cross-cutting compute, telemetry, configuration and runtime-lifecycle behavior -- the layers surface, not a C4 diagram family. Per standards/taxonomy.md's Choosing a value step 2 (pick the enum member whose plain-English name most concretely names the node's primary subject, not where the node currently happens to live), layers is that concrete name here, mirroring the same reasoning sibling task #1043 (layers/compute/lifecycle.md) already applied and disclosed in its own body."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
      - "git_show(ref='origin/task/611-batch-1a-compute', path='launchpad/docs/corpus/layers/compute/lifecycle.md') -> 'A note on `type`' section"
    confidence: 0.7
  - statement: "Issue #1120's Definition of Done requires this node to state trigger, preconditions and termination/outcome; list ordered interactions and data/state movement; identify authentication/authorization/trust-boundary crossings; and document failure/abort/rollback behavior linked to representative verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1120 definition of done"
relationships:
  - type: references
    target: architecture-containers-relay
---

# buzz-relay startup: flow

## A note on `type`

This node carries `type: layers`, not `type: architecture` — a deliberate,
disclosed choice, not the `flow.md` template's own worked-skeleton default.
That default (`type: architecture`) is precedent specifically from the
`architecture/flows/*` family (12 nodes narrating flows across the C4 static
model this repository's `architecture/` corpus subtree already documents).
This task's target path is `layers/lifecycle/startup.md`, and parent Feature
`#611`'s own stated Outcome is "cross-cutting compute, telemetry,
configuration and runtime-lifecycle behavior" — the `layers` surface, not a
C4 diagram family. Per `standards/taxonomy.md`'s *Choosing a value* step 2
("pick the enum member whose plain-English name most concretely names the
node's primary subject... not where the node currently happens to live"),
`layers` is that concrete name here. This mirrors the same reasoning sibling
task #1043 (`layers/compute/lifecycle.md`) already applied and disclosed in
its own body. Per `standards/taxonomy.md` step 5, `type` may be revised later
without touching this node's permanent `id`.

## Flow statement

This node narrates one scenario: the `buzz-relay` process's own startup, from
process entry (`async fn main()`) to the point its readiness probe can first
report `ready`. The trigger is process launch — a container start, a local
`just relay`, or a process manager restart. Preconditions: a reachable
Postgres instance at `DATABASE_URL`, a reachable Redis instance at
`REDIS_URL` (or `rediss://` with TLS), and, if `BUZZ_REQUIRE_RELAY_MEMBERSHIP`
is set, a configured `RELAY_OWNER_PUBKEY` and `BUZZ_RELAY_PRIVATE_KEY`. The
actors are the `buzz-relay` process itself, Postgres, Redis, and — only when
optional features are enabled — an S3/MinIO-compatible object store (git
conformance probe) and peer relay processes (inter-relay mesh). Termination
of this flow is either a fully bound, request-serving process whose
readiness probe reflects live Postgres/Redis/deletion-catalog health, or a
fatal early exit on one of several fail-fast checks named in *Outcome* below.

## Sequence

1. Install the `rustls` `ring` crypto provider — required before any TLS
   connection (`rediss://`, `wss://`, or TLS media storage) is attempted
   later in startup (`crates/buzz-relay/src/main.rs:92-94`).
2. Initialize a JSON-structured `tracing` subscriber; attach an OpenTelemetry
   layer only if OTLP tracer construction succeeds (`crates/buzz-relay/src/main.rs:103-133`).
3. Load configuration (`Config::from_env()`). An invalid config is logged and
   returned as an `Err`, ending the process before any connection is
   attempted (`crates/buzz-relay/src/main.rs:142-154`).
4. Install the Prometheus metrics exporter (`crates/buzz-relay/src/main.rs:156-164`).
5. Connect to Postgres (`Db::new`) — the writer pool synchronously, and, if
   `read_database_url` is configured, a lazy read-replica pool that dials
   nothing until first use (`crates/buzz-relay/src/main.rs:166-186`).
6. If `BUZZ_AUTO_MIGRATE` is truthy, run database migrations
   (`db.migrate()` → `sqlx::migrate!("../../migrations")`, the repository-root
   `migrations/` directory) and re-verify the replica-fence floor-guard
   trigger catalog; otherwise skip migrations and log that they were skipped
   (`crates/buzz-relay/src/main.rs:188-198`, `crates/buzz-db/src/runtime/migration.rs:15,27-34`).
7. Ensure future table partitions exist, validate the deletion-serving-fence
   catalog (fatal on failure), then spawn the replica freshness-fence probe
   — deliberately after the migration decision, so an un-migrated relay can
   never open the fence over an unenforced floor guard
   (`crates/buzz-relay/src/main.rs:200-228`).
8. If `BUZZ_REQUIRE_RELAY_MEMBERSHIP` is set, fail fast unless both
   `RELAY_OWNER_PUBKEY` and `BUZZ_RELAY_PRIVATE_KEY` are configured — before
   any database mutation is attempted (`crates/buzz-relay/src/main.rs:230-252`).
9. Seed the deployment's own community (`ensure_configured_community`, host
   derived the same way request routing resolves a host), then backfill
   `pubkey_allowlist` entries into `relay_members`, then bootstrap the
   configured owner into the owner role — in that order, so enabling
   membership enforcement never locks out an already-allowlisted user
   (`crates/buzz-relay/src/main.rs:254-345`).
10. Backfill `d_tag` for any pre-existing NIP-33 parameterized-replaceable
    events (idempotent no-op once fully populated)
    (`crates/buzz-relay/src/main.rs:347-353`).
11. Optionally connect a dedicated audit-log Postgres pool if
    `BUZZ_AUDIT_ENABLED` (`crates/buzz-relay/src/main.rs:355-367`).
12. Create the Redis connection pool and `PubSubManager`, then spawn three
    background subscriber tasks (multi-node event fan-out, cross-pod cache
    invalidation, cross-pod connection control)
    (`crates/buzz-relay/src/main.rs:369-399`).
13. Construct `AuthService`, the search service (Postgres FTS, preferring
    the read replica when configured), and the `WorkflowEngine`
    (`crates/buzz-relay/src/main.rs:401-423`).
14. Resolve the relay's own signing keypair by strict precedence: configured
    private key, else a hardcoded dev keypair only if
    `BUZZ_REQUIRE_AUTH_TOKEN=false`, else panic
    (`crates/buzz-relay/src/main.rs:425-446`).
15. Validate and connect media storage (`crates/buzz-relay/src/main.rs:448-454`).
16. Construct `AppState::new` from every service built so far. From this
    point on, one shared `Arc<AppState>` backs every remaining startup step
    and every request handler (`crates/buzz-relay/src/main.rs:456-468`).
17. Optionally boot the inter-relay mesh (no-op if its kill switch is off;
    fatal on misconfiguration if the switch is on)
    (`crates/buzz-relay/src/main.rs:470-497`).
18. Optionally run the git object-storage conformance probe against the
    configured S3/MinIO backend (default-on; fatal on failure unless
    explicitly disabled) (`crates/buzz-relay/src/main.rs:499-535`).
19. If membership enforcement is on, reconcile NIP-43 membership snapshots
    once synchronously (warning-only on failure), then spawn a periodic
    reconciliation loop (`crates/buzz-relay/src/main.rs:537-577`).
20. Spawn roughly a dozen background tasks without awaiting any of them: the
    workflow cron loop, the ephemeral-channel reaper, the optional NIP-PL
    push matcher/worker, the NIP-ER reminder scheduler, the multi-node
    fan-out consumer, the cache-invalidation consumer, the community
    revalidator, the connection-control consumer, a pool-metrics poller, and
    a jittered usage-metrics poller (`crates/buzz-relay/src/main.rs:626-1099`).
21. Build the application router and health router
    (`crates/buzz-relay/src/main.rs:973-974`), then enter `serve()`: bind the
    health-probe TCP listener and spawn its `axum::serve` task first
    (`crates/buzz-relay/src/main.rs:1255-1261`).
22. Spawn the shutdown-signal watcher (SIGTERM on Unix, Ctrl+C otherwise) —
    it now runs concurrently with the remaining binds, waiting on the
    signal (`crates/buzz-relay/src/main.rs:1295-1328`, `main.rs:1407-1422`).
23. Bind the primary application TCP listener at `config.bind_addr`, and, on
    Unix, an optional Unix-domain-socket listener if `BUZZ_UDS_PATH` is set
    (`crates/buzz-relay/src/main.rs:1330-1362`).
24. Serve the primary router (and UDS router, if bound) via
    `axum::serve(...).with_graceful_shutdown(...)`, each subscribed to the
    same `watch` channel the shutdown-signal task will later send `true` on
    — this call blocks `main()` until that shutdown signal arrives, and is
    the handoff point to the graceful-shutdown sequence a sibling node
    (`#1118`) covers (`crates/buzz-relay/src/main.rs:1263-1267,1364-1398`).

## Diagram

```mermaid
sequenceDiagram
    participant Proc as buzz-relay process
    participant PG as Postgres
    participant R as Redis
    participant S3 as Object storage (optional)
    participant OS as OS / signal source

    Proc->>Proc: install crypto provider, init tracing
    Proc->>Proc: Config::from_env()
    Proc->>PG: connect writer pool (Db::new)
    alt BUZZ_AUTO_MIGRATE=true
        Proc->>PG: run migrations + verify floor-guard catalog
    end
    Proc->>PG: ensure partitions, validate deletion-serving catalog
    alt BUZZ_REQUIRE_RELAY_MEMBERSHIP=true
        Proc->>Proc: require owner pubkey + relay private key (fatal if missing)
        Proc->>PG: ensure community, backfill allowlist, bootstrap owner
    end
    Proc->>R: connect pool + PubSubManager
    Proc->>Proc: spawn 3 pub/sub subscriber tasks
    Proc->>Proc: resolve relay signing keypair
    Proc->>Proc: construct AppState (shared Arc)
    opt mesh enabled
        Proc->>R: boot inter-relay mesh
    end
    opt git conformance probe enabled
        Proc->>S3: run conformance probe (fatal on failure)
    end
    Proc->>Proc: spawn ~12 background tasks (cron, reaper, pollers, consumers)
    Proc->>Proc: build router + health router
    Proc->>OS: bind health TCP listener, serve
    Proc->>OS: spawn shutdown-signal watcher (SIGTERM/Ctrl+C)
    Proc->>OS: bind primary TCP listener (+ optional UDS)
    Proc->>OS: axum::serve primary router (blocks until shutdown signal)
    Note over Proc,R: readiness now reports "ready" once<br/>Postgres + Redis + deletion-catalog checks all pass
```

## Outcome

**Success.** `main()`'s call to `serve()`'s `axum::serve(...)` blocks,
meaning the process is now accepting connections on its health listener, its
primary TCP listener, and (on Unix, if configured) its UDS listener. The
process is not fully "up" in the operational sense the moment a socket
binds, though: the readiness handler independently re-checks Postgres,
Redis, and the deletion-serving catalog on every request with a 2-second
timeout, and only returns `200 {"status":"ready"}` when all three currently
succeed (`crates/buzz-relay/src/router.rs:374-414`). The liveness handler,
by contrast, returns `200` unconditionally once reachable
(`crates/buzz-relay/src/router.rs:370-372`) — the two probes answer different
questions ("is the process alive" vs. "can it currently serve").

**Failure paths, each an early, fatal exit before the listener opens
(fail-fast, no partial-listening state):**
- **Invalid configuration** (`Config::from_env()` returns `Err`) — exits
  before any connection is attempted (`main.rs:142-154`).
- **Postgres connection failure** (`Db::new` `Err`) — exits before
  migrations or any further step (`main.rs:174-177`).
- **Migration failure** (only reachable when `BUZZ_AUTO_MIGRATE=true`) —
  exits with the migration error (`main.rs:188-198`).
- **Deletion-serving-fence catalog validation failure** — exits
  (`main.rs:204-207`).
- **Membership enforcement misconfigured**: `BUZZ_REQUIRE_RELAY_MEMBERSHIP=true`
  with a missing/invalid `RELAY_OWNER_PUBKEY` or missing
  `BUZZ_RELAY_PRIVATE_KEY` — exits before any DB mutation, by explicit
  design (`main.rs:230-252`).
- **Deployment-community host unresolvable, with membership required** —
  exits (`main.rs:268-273`); the same failure with membership *not*
  required is logged and treated as non-fatal, skipping backfill/bootstrap
  (`main.rs:274-278`).
- **Allowlist backfill or owner-bootstrap failure, with membership
  required** — exits; the same failures with membership not required are
  logged and non-fatal (`main.rs:307-319`, `329-344`).
- **Redis pool creation or `PubSubManager::new` failure** — exits
  (`main.rs:373,379`).
- **No configured relay private key with `BUZZ_REQUIRE_AUTH_TOKEN=true`** —
  panics (`main.rs:442-445`).
- **Invalid media configuration, or media storage init failure** — exits
  (`main.rs:450-453`).
- **Inter-relay mesh misconfigured, only if the mesh's own kill switch is
  on** — exits (`main.rs:475-482`); with the switch off, this step is a
  complete no-op.
- **Git object-storage conformance probe failure, only if the probe is
  enabled (its own default)** — exits (`main.rs:524-528`).
- **TCP or UDS listener bind failure** — exits, in `serve()`
  (`main.rs:1255-1257,1330-1332,1349-1350`).

None of these failure paths perform partial cleanup of already-opened
resources (pools, spawned background tasks) — the process simply exits, and
the OS reclaims sockets and connections. This is consistent with a
fail-fast, restart-oriented process model rather than an in-process rollback
model.

## Boundary

This node does not describe:
- **The compute-provider lifecycle** that creates, starts, and destroys the
  *substrate* (a Kubernetes Pod, today) a remote managed agent's compute
  runs on — a different flow entirely, already claimed by sibling task
  `#1043` (`layers/compute/lifecycle.md`, not yet merged at the checked
  revision).
- **The graceful-shutdown sequence** this node's *Sequence* step 24 hands
  off to (the `shutdown_tx` watch channel, the 5-second grace, the 30-second
  hard-drain timeout, jittered connection close) — sibling task `#1118`'s
  subject, not re-narrated here beyond naming the handoff point.
- **Buzz Desktop's own process boot** (`desktop/src-tauri/src/main.rs`) — a
  genuinely different flow: different trigger (a human launching the
  desktop app, not a deployment starting a server process), different
  actors (WebKitGTK/Tauri, not Postgres/Redis/the relay's background
  tasks), no shared code path with `buzz-relay`'s `main()`.
- **The per-connection WebSocket authentication handshake** (NIP-42) a
  client performs against an already-running relay — already covered by
  the existing `architecture/flows/websocket-authentication.md` node (not
  linked here as a `relationships` edge, since this node's own evidence
  ledger did not re-verify that node's content at this revision).
- **The inter-relay mesh's own internal wire protocol**, and **the git
  object-storage conformance probe's own algorithm** — both are optional
  steps this node names as steps 17-18, but neither's internal mechanics
  are documented here; no corpus node yet exists for either.
- **The standing container structure of `buzz-relay` itself** (what crates
  it composes, what it orchestrates) — that is
  `architecture-containers-relay`'s subject (see *Relationships*); this
  node covers only how that container comes to be running and serving.

## Relationships

- `references`: `architecture-containers-relay` — the container this
  flow's steps run inside; supporting context, no ownership or currency
  dependency implied.

No other merged node on `origin/launchpad` at the checked revision was
found to be a valid `relationships` target for this scenario (`git ls-tree
-r --name-only origin/launchpad -- launchpad/docs/corpus`, re-checked before
drafting): no `layers/*` sibling exists yet on `origin/launchpad` (this is
the first node in that surface there — `layers/compute/lifecycle.md`
exists only on the unmerged `origin/task/611-batch-1a-compute` branch), and
no `interfaces-events` node documents the NIP-43/NIP-33 wire behavior this
node's sequence touches.

## Scope and omissions

**This node covers** `buzz-relay`'s own process startup sequence, from
`async fn main()`'s first line through the point its primary listener is
serving and its readiness probe's contract is defined: configuration
loading, Postgres and Redis connection, the conditional migration decision
and its ordering relative to the replica-fence probe, the NIP-43
membership fail-fast checks and community/allowlist/owner bootstrap
ordering, the relay signing-keypair resolution precedence, the optional
mesh and git-conformance-probe gates, the roughly dozen background tasks
spawned before the listener opens, the listener-bind order (health, then
shutdown-signal watcher, then primary/UDS), and the liveness/readiness
probe contract that defines when startup is functionally "done."

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The compute-provider deploy/start/stop/destroy lifecycle | `#1043` (`layers/compute/lifecycle.md`, not yet merged) |
| The graceful-shutdown sequence this node's Sequence hands off to | `#1118` (sibling `layers/lifecycle/*` task) |
| Buzz Desktop's own process boot sequence | Not yet a corpus node |
| The per-connection WebSocket authentication handshake | `architecture/flows/websocket-authentication.md` (not linked as a `relationships` edge — see *Boundary*) |
| The inter-relay mesh's own internal wire protocol | Not yet a corpus node |
| The git object-storage conformance probe's own algorithm | Not yet a corpus node |
| The standing container structure `buzz-relay` composes | `architecture-containers-relay` |
| Background-worker startup ordering/dependencies in general (beyond the specific ordering facts cited above) | `#1115` (sibling `layers/lifecycle/*` task, `background-workers`) |

**Expected but not verified when this node was written:**
- **No test in this repository was found that directly drives `buzz-relay`'s
  `async fn main()` end-to-end and asserts on its startup ordering.** The
  function is exercised only indirectly, by integration and e2e tests that
  connect to an already-running relay process started out-of-band (for
  example via `just relay`). A targeted search of
  `crates/buzz-test-client/tests/` found no test that starts the relay
  binary itself and asserts on readiness transitions.
- **Whether the relative spawn order of the roughly dozen background tasks
  in step 20 is load-bearing beyond the two dependencies this node does
  cite** (the workflow cron loop must be spawned after its action sink is
  wired; the deployment-community bootstrap must precede allowlist backfill
  and owner bootstrap) **was not exhaustively checked.** Each task was read
  individually; whether any other pair has an undocumented ordering
  dependency is an open question this node does not resolve.
- **Whether `BUZZ_RECONCILE_CHANNELS`'s dev/CI-only reconciliation path
  (`main.rs:579-624`) is ever enabled in a real deployment** was not
  independently verified beyond the surrounding code comment stating it is
  a dev/CI pattern; this node omits it from the numbered *Sequence* on that
  basis rather than asserting it never runs in production.
