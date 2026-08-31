---
id: platforms-relay-process
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum includes platforms as one of PRD #602's own enumerated corpus surfaces, and no platforms-specific template is merged under launchpad/docs/corpus/templates/ at this revision, so this node borrows templates/component.md's section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) by convention, per AGENTS.md's documented no-template path, rather than inventing a new shape."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "buzz-relay's main() is a #[tokio::main] async fn that, in order, installs the ring rustls CryptoProvider, builds a tracing_subscriber registry (JSON stdout logs plus an optional OpenTelemetry layer gated on OTEL_EXPORTER_OTLP_ENDPOINT), loads Config::from_env, and derives the relay's Nostr keypair from BUZZ_RELAY_PRIVATE_KEY, failing fast if any of these error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:96-166"
  - statement: "Immediately after config load, main() installs the Prometheus metrics exporter (relay_metrics::install) and sets two boot-time gauges (buzz_audit_enabled, buzz_push_enabled) before any datastore connection is attempted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:168-177"
  - statement: "Postgres connection (Db::new) is followed by an opt-in migration gate (buzz_auto_migrate_enabled, reading BUZZ_AUTO_MIGRATE), then ensure_future_partitions, then two fatal fence checks -- validate_deletion_serving_catalog and, later in the sequence, verify_channel_roster_fence -- either of which returns Err from main() and aborts startup before the router is ever built."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:179-221"
      - "crates/buzz-relay/src/main.rs:527-537"
  - statement: "A replica freshness fence probe (db.spawn_fence_probe) runs after the migration decision but before any multi-tenant bootstrap, and its own inline comment states this ordering is deliberate: a relay running with BUZZ_AUTO_MIGRATE off and a required migration unapplied must never open the fence over an unenforced floor. Probe failure is logged as an error but is non-fatal -- the fence stays closed and cursor reads stay on the writer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:223-241"
  - statement: "Two NIP-43 membership-enforcement preconditions (a valid RELAY_OWNER_PUBKEY, and a configured BUZZ_RELAY_PRIVATE_KEY) are checked and, if BUZZ_REQUIRE_RELAY_MEMBERSHIP is true and either is missing, main() returns Err before any database mutation runs -- the code comments state this ordering exists so the process fails fast rather than backfilling or bootstrapping data for a configuration it will reject anyway."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:243-265"
  - statement: "The deployment's own multi-tenant community is derived from BUZZ_RELAY_URL's authority (relay_url_authority) and ensured (ensure_configured_community) before allowlist backfill (backfill_from_allowlist) and owner bootstrap (bootstrap_owner) run; the inline comments state this order is required so that membership backfill and owner promotion are scoped to a real (community_id, pubkey) pair rather than a global pubkey, and so existing allowlist users become members before the owner is promoted (avoiding a lockout). All three steps are stated as idempotent, safe to re-run on every startup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:267-358"
  - statement: "A NIP-33 d_tag backfill (db.backfill_d_tags) for parameterized-replaceable events runs after community/membership bootstrap and is stated as idempotent (no-ops when fully populated); its own error path only logs, it does not abort startup."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:360-366"
  - statement: "After the datastore-bootstrap phase, main() constructs one collaborator service per subsystem crate in sequence: an optional AuditService (gated on config.audit_enabled, its own dedicated Postgres pool), a deadpool_redis pool plus a PubSubManager (buzz-pubsub) with three tokio::spawn'd subscriber loops (multi-node fan-out, cache invalidation, connection control), an AuthService (buzz-auth), a SearchService (buzz-search, over its own Postgres pool preferring the read replica when configured), a WorkflowEngine (buzz-workflow), and a MediaStorage client (buzz-media, after config.media.validate())."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:368-444"
  - statement: "AppState::new takes ten parameters -- config, db, redis_pool, an impl Into<Option<AuditService>> audit, the PubSubManager, auth, search, the workflow engine, the relay keypair, and media_storage -- and returns (Self, AuditShutdownHandle); this call is the single point in main() where every previously constructed collaborator service is assembled into one shared, Arc-wrapped state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:446-458"
      - "crates/buzz-relay/src/state.rs:782-792"
  - statement: "After AppState is assembled, two optional subsystem seams are wired conditionally: buzz_relay::mesh_boot::boot_mesh (the BUZZ_MESH inter-relay peer transport, a no-op returning None when the kill switch is off, fatal on bind/Redis failure when enabled), and a git object-store conformance probe (gated on BUZZ_GIT_CONFORMANCE_PROBE, defaulting to on) that is fatal if the configured S3/MinIO backend fails its conditional-write (A3) check, per the inline comment describing it as a deployment gate rather than a proof."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:460-525"
  - statement: "Two more fatal-or-warning consistency checks run before background workers are spawned: verify_channel_roster_fence (fatal -- returns Err naming migration 0032 if unsafe) and reconcile_large_channel_member_snapshots (non-fatal, only warns on failure); when BUZZ_REQUIRE_RELAY_MEMBERSHIP is set, reconcile_nip43_membership_snapshots also runs once at startup and then again on a periodic tokio::spawn'd loop (default 60s, BUZZ_NIP43_RECONCILE_INTERVAL_SECS)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:527-592"
  - statement: "main() contains 23 tokio::spawn call sites in total, covering: three pubsub subscriber loops, an optional dev-only channel-discovery reconciler (BUZZ_RECONCILE_CHANNELS), the workflow engine's cron loop, an ephemeral-channel reaper, an optional pair of NIP-PL push workers (matcher and delivery, gated on config.push_enabled), an admin outbox delivery worker, an admin action recovery worker, a NIP-ER reminder scheduler, a multi-node fan-out consumer, a cache-invalidation consumer, a community lifecycle revalidator, a connection-control consumer, a DB/Redis pool-metrics poller, and a per-community usage-metrics poller -- each spawned as an independent, long-running background task before serve() is called."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='tokio::spawn', scope='crates/buzz-relay/src/main.rs') -> 23 matches, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
      - "crates/buzz-relay/src/main.rs:396-1140"
  - statement: "The action sink (RelayActionSink) is wired to the already-constructed WorkflowEngine, and the code's own inline comment states this must happen after AppState (which creates sub_registry and conn_manager) and before the workflow cron loop starts -- an explicit ordering dependency between two already-documented construction steps."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:641-648"
  - statement: "build_router and build_health_router are called once each, after every background worker above has already been spawned, and each takes only Arc<AppState> as its input, confirming the previously assembled AppState is the router layer's sole dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1014-1015"
      - "crates/buzz-relay/src/router.rs:33-39"
      - "crates/buzz-relay/src/router.rs:294-299"
  - statement: "main()'s final composition step is a single call, serve(router, health_router, Arc::clone(&state)).await?, whose own doc comment states it binds all listeners and runs with graceful shutdown; the SIGTERM/drain/exit sequence inside serve() is a separate concern from this node's composition-and-wiring scope."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1142"
      - "crates/buzz-relay/src/main.rs:1244-1296"
  - statement: "After serve() returns (i.e. after the process has begun exiting), main() cancels the community revalidator's CancellationToken, drains the audit worker with a 5s timeout via audit_shutdown.drain, and, if the OpenTelemetry tracer was enabled, shuts it down to flush pending spans -- this teardown sequence runs strictly after the listener-level shutdown serve() itself performs, and is therefore part of the same shutdown continuum #1271 scopes, not part of the startup composition this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1142-1159"
  - statement: "architecture-containers-relay is an existing, merged corpus node (status: draft) that already documents buzz-relay's listener addresses/ports, route table, outbound connected systems, deployment/image facts, the graceful-shutdown time budget, and the BUZZ_AUTO_MIGRATE gate at the container level; this node deliberately does not restate any of those facts and instead references that node for them."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "Issue #1271 (graceful shutdown) is committed to a local, unmerged branch at the time this node was written and therefore cannot be a relationships[].target, per AGENTS.md's rule that a target must exist on the branch being merged into, not merely in some worktree."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1281 task brief (batch dispatch context: #1271 committed locally, not on origin/launchpad)"
relationships:
  - type: references
    target: architecture-containers-relay
---

# Process: `buzz-relay` startup composition

What `crates/buzz-relay/src/main.rs`'s `async fn main()` actually does, in
order, to go from process start to a serving relay: which collaborator
services it constructs, in what sequence, which steps are fatal versus
best-effort, and where it hands off to the router and to graceful shutdown.
This node answers "how does the relay wire itself together at boot", not
"what does the relay expose" (that is `architecture-containers-relay`) and
not "how does it shut down" (that is `#1271`'s scope, unmerged at this
revision).

## Responsibility

`main()` is the single composition root for the `buzz-relay` binary. It owns
the order in which every subsystem collaborator (datastore connections,
Redis/pub-sub, auth, search, workflow engine, media storage, the optional
mesh and push seams) is constructed, assembled into one shared `AppState`,
validated against a handful of fatal consistency fences, and handed to the
HTTP/WebSocket router and finally to `serve()`. No other function in the
crate performs this composition; a caller who wants to know "in what order
does the relay become ready" has exactly one place to look.

## Composition phases

In the order `main()` executes them:

| # | Phase | Fatal on failure? | Evidence |
|---|---|---|---|
| 1 | Install rustls `ring` crypto provider | yes (`.expect`) | `crates/buzz-relay/src/main.rs:96-104` |
| 2 | Init tracing/logging (JSON + optional OTEL layer) | no | `crates/buzz-relay/src/main.rs:106-148` |
| 3 | Load `Config::from_env`, derive relay keypair | yes | `crates/buzz-relay/src/main.rs:152-166` |
| 4 | Install Prometheus metrics exporter | no | `crates/buzz-relay/src/main.rs:168-177` |
| 5 | Connect Postgres (`Db::new`) | yes | `crates/buzz-relay/src/main.rs:179-190` |
| 6 | Migration gate (`BUZZ_AUTO_MIGRATE`, opt-in) | yes, only if enabled and it fails | `crates/buzz-relay/src/main.rs:201-211` |
| 7 | Ensure future partitions | no (logs only) | `crates/buzz-relay/src/main.rs:213-215` |
| 8 | Deletion serving-fence validation | yes | `crates/buzz-relay/src/main.rs:217-221` |
| 9 | Replica freshness-fence probe | no | `crates/buzz-relay/src/main.rs:223-241` |
| 10 | NIP-43 membership preconditions (owner pubkey, private key) | yes, only if membership required | `crates/buzz-relay/src/main.rs:243-265` |
| 11 | Deployment community ensure → allowlist backfill → owner bootstrap | yes, only if membership required | `crates/buzz-relay/src/main.rs:267-358` |
| 12 | NIP-33 `d_tag` backfill | no | `crates/buzz-relay/src/main.rs:360-366` |
| 13 | Construct audit, Redis pool + pub/sub (+3 subscriber tasks), auth, search, workflow engine, media storage | yes for each connection/init call | `crates/buzz-relay/src/main.rs:368-444` |
| 14 | `AppState::new` — assemble every collaborator into one shared state | n/a (infallible) | `crates/buzz-relay/src/main.rs:446-458`, `crates/buzz-relay/src/state.rs:782-792` |
| 15 | Optional seams: mesh boot, git conformance probe | yes if enabled and it fails | `crates/buzz-relay/src/main.rs:460-525` |
| 16 | Channel roster fence + snapshot/NIP-43 reconciliation | fence check yes; reconciliation no | `crates/buzz-relay/src/main.rs:527-592` |
| 17 | Spawn 23 background workers (cron, reapers, push, admin, reminders, pub/sub consumers, revalidator, metrics pollers) | no (each runs detached) | `crates/buzz-relay/src/main.rs:396-1140` |
| 18 | `build_router` / `build_health_router` | n/a (infallible) | `crates/buzz-relay/src/main.rs:1014-1015` |
| 19 | `serve(...)` — binds listeners, runs with graceful shutdown | hands off to `#1271`'s scope | `crates/buzz-relay/src/main.rs:1142` |
| 20 | Post-`serve` teardown (audit drain, OTEL flush) | part of shutdown continuum, not startup | `crates/buzz-relay/src/main.rs:1142-1159` |

Ordering within this table is not incidental: several inline comments in
`main.rs` state *why* a given step must come before or after another (the
replica-fence probe after the migration decision; community ensure before
allowlist backfill and owner bootstrap; the action sink after `AppState`
and before the workflow cron loop) — see the evidence entries above for the
exact statements.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `main` | `async fn` (binary entry point, `#[tokio::main]`) | Runs the full composition above; returns `anyhow::Result<()>`, `Err` on any fatal step | `crates/buzz-relay/src/main.rs:96-97` |
| `serve` | `async fn` | Binds all listeners and runs with graceful shutdown; called once, last, from `main` | `crates/buzz-relay/src/main.rs:1289-1296` |
| `build_router` | `pub fn` (in `router.rs`) | Builds the app router from `Arc<AppState>` alone | `crates/buzz-relay/src/router.rs:33` |
| `build_health_router` | `pub fn` (in `router.rs`) | Builds the health-only router from `Arc<AppState>` alone | `crates/buzz-relay/src/router.rs:294` |
| `AppState::new` | `pub fn` (in `state.rs`) | Assembles ten already-constructed collaborators into `(Self, AuditShutdownHandle)` | `crates/buzz-relay/src/state.rs:782-792` |

## Dependencies

**Depends on** (constructed and consumed during composition, in the order
named in *Composition phases* above):

| Component | Why | Evidence |
|---|---|---|
| `buzz-db` (`Db`, `DbConfig`) | Postgres connection, migrations, partitions, fences, membership bootstrap | `crates/buzz-relay/src/main.rs:179-366` |
| `buzz-audit` (`AuditService`) | Optional hash-chain audit sink | `crates/buzz-relay/src/main.rs:368-380` |
| `buzz-pubsub` (`PubSubManager`) | Redis-backed fan-out, cache invalidation, connection control | `crates/buzz-relay/src/main.rs:382-412` |
| `buzz-auth` (`AuthService`) | Authentication/authorization service | `crates/buzz-relay/src/main.rs:414` |
| `buzz-search` (`SearchService`) | Postgres FTS search service | `crates/buzz-relay/src/main.rs:416-433` |
| `buzz-workflow` (`WorkflowEngine`) | Workflow evaluation engine, cron-driven | `crates/buzz-relay/src/main.rs:435-436, 641-648` |
| `buzz-media` (`MediaStorage`) | Blossom media storage client | `crates/buzz-relay/src/main.rs:438-444` |
| `buzz-relay-mesh` (via `mesh_boot::boot_mesh`) | Optional inter-relay peer transport | `crates/buzz-relay/src/main.rs:460-487` |

**Depended on by:** the `serve` function and the router-building functions
in the same crate, each of which requires the fully assembled `AppState`
this composition produces; no other crate calls into `main()` itself.

## Boundary

This node does not describe:
- The relay's externally observable listener addresses, route table,
  outbound connected systems, deployment/chart facts, or the
  graceful-shutdown time budget -- those are `architecture-containers-relay`'s
  subject; see *Relationships* below.
- The internals of `serve()`'s SIGTERM/drain/force-exit sequence -- that is
  issue `#1271`'s scope, unmerged at the time this node was written, so this
  node states only that `main()` hands off to it.
- The individual behavior of each of the 23 spawned background workers --
  named as a class with a citation to the exact count, not itemized one by
  one; any single worker becoming its own maintainable idea is a future,
  separate task per `AGENTS.md`'s "second concept" rule.
- The internal logic of each constructed collaborator service
  (`buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit`,
  `buzz-workflow`, `buzz-media`) -- each is its own component/container
  subject, not restated here.

## Relationships

- `references`: `architecture-containers-relay` -- the container-level node
  this process node deliberately does not duplicate.

## Scope and omissions

**This node covers** the ordered composition inside `buzz-relay`'s `main()`:
process bootstrap, config load, metrics install, datastore connection and
fence checks, multi-tenant bootstrap, subsystem service construction,
`AppState` assembly, optional seams, background-worker spawn, router
construction, and the handoff to `serve()`.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Listener addresses, route table, deployment facts, shutdown time budget | `architecture-containers-relay` |
| `serve()`'s SIGTERM/drain/force-exit sequence | `#1271` (graceful shutdown), unmerged at time of writing |
| Individual behavior of each of the 23 spawned background workers | Not yet owned by any corpus node; a gap |
| Internal logic of each constructed collaborator crate | Each crate's own future component node |

**Expected but not verified when this node was written:**
- Whether the exact 23-`tokio::spawn` count stays stable is not something
  this node's `FACT` claims can guarantee going forward -- it is accurate at
  the recorded revision, verified by `grep`, not asserted as permanent.
- Whether a `platforms` template will later prescribe a different section
  shape than the borrowed `component.md` structure was not checked; if
  one lands, this node is a candidate for reshaping, per `AGENTS.md`'s own
  statement that documents written before a template exists "expect a
  later task to reshape it."
