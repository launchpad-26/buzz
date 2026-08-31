---
id: platforms-relay-startup
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum has thirteen members, including platforms; at the recorded revision, launchpad/docs/corpus/templates/ contains no platforms-specific template, so per AGENTS.md's documented no-template path this node is written against node.schema.json directly rather than against an authoritative platforms template."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "templates/component.md's own front matter, section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions) and stated subject -- one software component documented as a standalone knowledge artifact -- is a structurally close analog for this node's subject; this node borrows that shape but not that template's type: implementation, following the same type: platforms convention the sibling platforms/relay/graceful-shutdown.md node (issue #1271, unmerged branch task/1271-relay-graceful-shutdown) already established for this batch."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.7
  - statement: "Issue #1283 ('startup') and sibling issue #1281 ('process') carry byte-identical Definition of Done checklists with no textual distinction beyond the target filename; #1281 has a local worktree and branch (task/1281-relay-process) but no content has ever been committed or drafted there (git diff origin/launchpad task/1281-relay-process is empty, and the worktree's git status is clean). This node therefore takes the narrowest defensible reading of its own filename and its own issue's evidence-gathering hint ('config load, DB migration check, pool creation, etc.'): the ordered sequence of initialization steps main() executes, in the order it executes them, ending at the call to serve(). What #1281 ('process') will eventually cover is not verified here and may overlap; that risk is named explicitly in Boundary below rather than silently assumed away."
    entry_class: INFERENCE
    evidence:
      - "git_diff(base='origin/launchpad', head='task/1281-relay-process', paths=['launchpad/docs/corpus/platforms/relay/process.md']) -> empty"
      - "git_status(worktree='__worktrees/task-1281-relay-process') -> clean, nothing to commit"
    confidence: 0.55
  - statement: "crates/buzz-relay/src/main.rs's #[tokio::main] async fn main() runs a single strictly sequential chain of fallible initialization steps from line 97 through the call to serve() at line 1142; no branch of this sequence runs concurrently with another before serve() is reached, and the two #[cfg(test)] modules in this file (main.rs:1162-1206, main.rs:2045-2194) test individual startup-adjacent functions (buzz_auto_migrate_enabled, relay_keypair_from_config, log/otel filter construction) but exercise no part of main() itself, which is untestable directly as a #[tokio::main] entry point."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:97-1160"
  - statement: "main() installs the rustls ring CryptoProvider as the first statement in the function, via rustls::crypto::ring::default_provider().install_default().expect(...); the preceding comment states this is required before any rustls TLS connection (rediss:// to ElastiCache, wss://, S3 over TLS) because both aws-lc-rs and ring are compiled in transitively, so rustls cannot auto-select a provider and would panic at first use without this call -- making this step a process-crash (via .expect()), not a returned-error, failure mode if it were ever to fail."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:98-104"
  - statement: "Structured logging and OpenTelemetry tracing are initialized next (main.rs:106-150): telemetry::service_resource() builds a shared Resource, telemetry::try_init_tracer(resource) conditionally enables an OTLP layer if OTEL_EXPORTER_OTLP_ENDPOINT is set, and tracing_subscriber::registry()...init() installs the combined subscriber; only after .init() does the function log its first message, info!(\"Starting buzz-relay\") at line 150 -- meaning no structured log line from this process exists before the subscriber is fully wired."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:106-150"
  - statement: "Config::from_env() (crates/buzz-relay/src/config.rs:541) is the single fail-fast configuration-parsing entry point main() calls at line 152, returning Result<Self, ConfigError>; individual fields either fall back to a hardcoded default when their env var is absent (e.g. BUZZ_BIND_ADDR -> \"0.0.0.0:3000\", DATABASE_URL -> a local dev Postgres URL) or return ConfigError::InvalidValue for a present-but-unparseable value (e.g. non-integer BUZZ_REPLICA_READ_MAX_AGE_MS), and one legacy variable name (BUZZ_REPLICA_HEAD_MAX_AGE_SECS) is rejected outright as a hard startup error rather than silently reinterpreted, per an inline comment warning that honouring it silently would apply a 1000x-wrong budget."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:541-592"
  - statement: "relay_keypair_from_config (main.rs:38-46), called immediately after Config::from_env() at main.rs:156, requires BUZZ_RELAY_PRIVATE_KEY to be set and parses it as a Nostr secret key via nostr::Keys::parse, returning an anyhow error (which main()'s Result<()> return type propagates as a non-zero process exit, not a panic) if the value is absent or invalid; two unit tests exercise this function directly outside of main() itself: configured_relay_identity_is_preserved and missing_relay_identity_is_rejected."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:38-46"
      - "crates/buzz-relay/src/main.rs:156"
      - "crates/buzz-relay/src/main.rs:2105-2120"
  - statement: "relay_metrics::install(config.metrics_port, usage_idle_timeout_secs) (main.rs:170) starts the Prometheus metrics exporter immediately after config is loaded and logged, before any datastore connection is attempted; this ordering means the metrics port becomes available (per its own log line at main.rs:173-177) well before the process can serve any Nostr/HTTP traffic."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:168-177"
  - statement: "Db::new(&db_config) (crates/buzz-db/src/runtime/mod.rs:488-507), awaited at main.rs:187, eagerly connects a writer PgPool via Self::connect_pool (mod.rs:514-543) -- whose after_connect hook sets the buzz.created_at_floor session config and asserts the connection's transaction_isolation is exactly \"read committed\", returning a connection error otherwise -- and, only if config.read_database_url is Some, constructs a second, lazily-connected (min_connections(0)) read-replica pool via Self::connect_read_pool (mod.rs:569-577) whose own doc comment states a down replica at boot must not crash or block the relay, matching the observed fact that connect_read_pool never dials the replica at construction time."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/mod.rs:488-507"
      - "crates/buzz-db/src/runtime/mod.rs:514-543"
      - "crates/buzz-db/src/runtime/mod.rs:569-577"
      - "crates/buzz-relay/src/main.rs:179-190"
  - statement: "If Db::new succeeds and db.has_read_pool() is true, main() calls db.spawn_read_pool_boot_ping() (runtime/mod.rs:594), whose own doc comment states this one-shot probe only WARNs and must never gate startup or Db::spawn_fence_probe -- it exists solely so a misconfigured READ_DATABASE_URL is visible in logs at boot rather than silently invisible until the first routed read."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:191-199"
      - "crates/buzz-db/src/runtime/mod.rs:579-594"
  - statement: "Database migration is conditional and opt-in: main() checks buzz_auto_migrate_enabled(std::env::var(\"BUZZ_AUTO_MIGRATE\").ok().as_deref()) (main.rs:29-36, matching only \"true\"/\"1\"/\"yes\"/\"on\" case-insensitively after trimming) at main.rs:201-211 and only then awaits db.migrate() (runtime/mod.rs:859-861, which delegates to migration::run_migrations at migration.rs:28); a migration failure here is fail-fast (propagated as an anyhow error, ending main() before any further step runs), while BUZZ_AUTO_MIGRATE unset or falsy skips migration entirely and only logs that it was skipped. buzz_auto_migrate_is_opt_in is a dedicated unit test asserting every one of these truthy/falsy string cases."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:29-36"
      - "crates/buzz-relay/src/main.rs:201-211"
      - "crates/buzz-db/src/runtime/mod.rs:859-861"
      - "crates/buzz-db/src/runtime/migration.rs:28"
      - "crates/buzz-relay/src/main.rs:2090-2103"
  - statement: "Immediately after the migration decision, main() runs three more DB-dependent verification/repair steps in this fixed order, with different fatality: db.ensure_future_partitions(3) (main.rs:213-215, delegating to store/partition.rs:63) only logs an error on failure and does not stop startup; db.validate_deletion_serving_catalog() (main.rs:217-221, delegating to store/deletion.rs:633) is fail-fast, returning an anyhow error if community-deletion serving fences are unsafe; db.spawn_fence_probe() (main.rs:223-241, delegating to runtime/mod.rs:679) is non-fatal on failure but the surrounding comment states its ordering after the migration decision is deliberate, so a relay running with BUZZ_AUTO_MIGRATE off and a required migration unapplied can never open the replica-read freshness fence over an unenforced floor."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:213-241"
      - "crates/buzz-db/src/store/partition.rs:63"
      - "crates/buzz-db/src/store/deletion.rs:633"
      - "crates/buzz-db/src/runtime/mod.rs:679"
  - statement: "NIP-43 relay-membership bootstrapping runs as a fixed five-step sub-sequence (main.rs:243-366), each step's comment stating why it must precede the next: (1) if config.require_relay_membership is true, config.relay_owner_pubkey must be Some, else main() returns an error before any DB mutation; (2) if membership is required, config.relay_private_key must also be Some (checked before any DB mutation, per the comment, so an unusable ephemeral-key config is rejected before bootstrapping or backfilling); (3) db.ensure_configured_community(&host) (store/community.rs:278) seeds the deployment's own community from the host derived from relay_url, fatal only when membership is required; (4) db.backfill_from_allowlist(community) (store/relay_members.rs:773) migrates legacy pubkey_allowlist rows into relay_members before any owner promotion, so existing allowlisted users are not locked out when membership enforcement is enabled; (5) db.bootstrap_owner(community, owner_pubkey) (store/relay_members.rs:737) ensures the configured owner holds the owner role. Steps 3-5 are each individually fatal only when config.require_relay_membership is true; with membership not required, the same failures are logged and startup continues."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:243-358"
      - "crates/buzz-db/src/store/community.rs:278"
      - "crates/buzz-db/src/store/relay_members.rs:773"
      - "crates/buzz-db/src/store/relay_members.rs:737"
  - statement: "db.backfill_d_tags() (main.rs:360-366, delegating to store/event.rs:1705) backfills the d_tag column for NIP-33 parameterized-replaceable events that predate the column's addition; it runs unconditionally (not gated on require_relay_membership) and is non-fatal -- a failure only logs an error and startup continues."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:360-366"
      - "crates/buzz-db/src/store/event.rs:1705"
  - statement: "Audit service construction (main.rs:368-380) is conditional on config.audit_enabled: when true, a dedicated 1-5 connection PgPoolOptions pool is connected to config.database_url and wrapped in AuditService::new, fatal on connection failure; when false, no pool is created and audit stays None for the rest of startup and for AppState::new's audit parameter."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:368-380"
  - statement: "Redis pool creation and PubSubManager::new (main.rs:382-393) are both fail-fast: deadpool_redis::Config::create_pool and PubSubManager::new each map their error into an anyhow error that ends main() early. Once pubsub is constructed (as an Arc), main() immediately spawns three long-running background subscriber tasks via tokio::spawn (main.rs:399-412) -- run_subscriber (multi-node event fan-out), run_cache_invalidation_subscriber (cross-pod moka cache drops), run_conn_control_subscriber (cross-pod ban/disconnect commands) -- none of which is awaited; their own loop bodies are out of scope for this node (see Boundary)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:382-412"
  - statement: "AuthService::new(config.auth.clone()) (main.rs:414) is infallible construction with no I/O. SearchService::new(search_pool) (main.rs:416-433) is fail-fast on its own dedicated PgPoolOptions connection (to config.read_database_url if set, else config.database_url) -- a connection failure here ends main() with an anyhow error -- and its accompanying comment states search prefers the read replica because it is lag-tolerant, unlike the fence-gated cursor-read path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:414-433"
  - statement: "config.media.validate() (main.rs:438-441) and buzz_media::MediaStorage::new(&config.media) (main.rs:442-444) are both fail-fast: an invalid media configuration or a construction failure each end main() with an anyhow error before AppState::new is reached."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:438-444"
  - statement: "AppState::new (crates/buzz-relay/src/state.rs:782-793) is the single point where every previously constructed service (config, db, redis_health_pool, audit, pubsub, auth, search, workflow_engine, relay_keypair, media_storage) is assembled into one Arc<AppState> (main.rs:446-458); its own doc comment states it returns (state, audit_shutdown) so the caller can drain the audit worker during graceful shutdown, tying this node's construction step directly to platforms-relay-graceful-shutdown's post-serve() cleanup step."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:775-793"
      - "crates/buzz-relay/src/main.rs:446-458"
  - statement: "Inter-relay mesh boot (buzz_relay::mesh_boot::boot_mesh, main.rs:465-487) is gated by the BUZZ_MESH kill switch: the surrounding comment states boot_mesh returns None when the switch is off, in which case nothing is bound, published, or spawned and the relay behaves byte-identically to a build without the mesh; when the switch is on, a misconfigured mesh (bind or Redis failure) is fatal here, per the same comment's stated rationale that an operator who asked for the mesh should get it or be told why not."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:460-487"
  - statement: "The git object-storage conformance probe (main.rs:493-525) runs by default (opt-out via BUZZ_GIT_CONFORMANCE_PROBE=false) and is fail-fast: state.git_store.run_conformance_probe(cfg) admits the configured S3/MinIO backend against a linearizable conditional-write axiom (A3) before any git traffic is served, and the preceding comment states failure here is fatal because a backend that cannot satisfy pointer CAS invalidates the manifest-pointer protocol -- explicitly calling this 'a deployment gate, not a proof.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:489-525"
  - statement: "state.db.verify_channel_roster_fence() (main.rs:527-537, delegating to store/channel_members.rs:1198) is fail-fast: its failure returns an anyhow error naming migration 0032 as the required fix, ending main() before the router is ever built. Two best-effort repairs follow, both non-fatal on error (only logged): reconcile_large_channel_member_snapshots (main.rs:539-550) and, only when config.require_relay_membership is true, reconcile_nip43_membership_snapshots (main.rs:552-592), which also spawns a periodic (default 60s) background re-reconciliation task that is never awaited."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:527-592"
      - "crates/buzz-db/src/store/channel_members.rs:1198"
  - statement: "From main.rs:594 through main.rs:1140, main() spawns roughly ten additional tokio::spawn background tasks in sequence -- a dev/CI-only channel-discovery reconciler (BUZZ_RECONCILE_CHANNELS-gated), the workflow engine's cron loop (after wiring its action sink), an ephemeral-channel reaper, the NIP-PL push matcher and delivery worker (when config.push_enabled), an admin-outbox delivery worker, an admin-action recovery worker, a NIP-ER reminder scheduler, a multi-node pub/sub fan-out consumer, a cross-pod cache-invalidation consumer, a community-lifecycle revalidator, a cross-pod connection-control consumer, a DB/Redis pool-metrics poller, and a per-community usage-metrics poller -- none of which main() awaits; each keeps running independently for the rest of the process's life. build_router(Arc::clone(&state)) and build_health_router(Arc::clone(&state)) (main.rs:1014-1015) are constructed after the earlier consumer spawns but before the pool-metrics and usage-metrics tasks."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:594-1140"
      - "crates/buzz-relay/src/main.rs:1014-1015"
  - statement: "Only after every step above completes does main() call serve(router, health_router, Arc::clone(&state)).await? at main.rs:1142; serve() itself (main.rs:1289-1446, documented by platforms-relay-graceful-shutdown) binds the health listener at main.rs:1296-1298 -- meaning no HTTP endpoint on this process, including the /_liveness route build_health_router registers (crates/buzz-relay/src/router.rs:296), is reachable at any point during the sequence this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1142"
      - "crates/buzz-relay/src/main.rs:1289-1302"
      - "crates/buzz-relay/src/router.rs:294-296"
  - statement: "deploy/charts/buzz/values.yaml configures a startupProbe against the /_liveness path with failureThreshold: 60 and periodSeconds: 2 -- a 120-second budget -- separately from the readinessProbe and livenessProbe (both initialDelaySeconds: 5); because /_liveness cannot answer until serve() binds the health listener (see the FACT above), this 120-second startupProbe budget is the deployment-level bound the entire sequence this node documents (crypto init through the last background-worker spawn) must fit inside before Kubernetes considers the pod to have failed to start."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml:143-164"
  - statement: "No corpus node for platforms-relay-connection-manager (#1267), platforms-relay-app-state (#1263), platforms-relay-mesh-bootstrap (#1276), or platforms-relay-admission (#1262) exists on origin/launchpad at the recorded revision -- each is drafted only on its own unmerged sibling branch -- so no relationships.depends-on or .references edge toward any of them is declared in this node's front matter, per this batch's own established convention that a declared target must resolve against the merge-target branch."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/platforms') -> path does not exist at commit 131b02f989684117d9ab1dd426f1673fa638e523"
---

# Startup sequence (buzz-relay)

`crates/buzz-relay/src/main.rs`'s `main()` function, from its first statement
through the call to `serve()`, is the relay process's single, strictly
sequential chain of initialization steps: install a crypto provider, stand
up structured logging, load configuration, connect to Postgres and Redis,
conditionally migrate and verify the schema, bootstrap NIP-43 relay
membership, construct every long-lived service, build `AppState`, run two
opt-in/opt-out admission gates (inter-relay mesh, git-backend conformance),
verify data invariants, spawn roughly a dozen background workers, and only
then hand control to `serve()`. This node answers: what order these steps
run in, which ones are fail-fast versus best-effort, and what a deployment
observes (or cannot yet observe) while this sequence is in progress.

No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`
at the recorded revision. Per `AGENTS.md`'s documented no-template path, this
node is written directly against `node.schema.json`; its body borrows
`templates/component.md`'s section shape as a structurally close analog,
using `type: platforms` rather than that template's `type: implementation`,
following the convention the sibling `platforms/relay/graceful-shutdown.md`
node (issue #1271) already established for this batch.

**On the #1281/#1283 boundary.** Sibling issue #1281 targets
`platforms/relay/process.md` with a Definition of Done identical to this
issue's own, and neither issue's text distinguishes "process" from
"startup." At the recorded revision #1281 has no drafted content anywhere to
check against (see the `INFERENCE` entry above). This node takes the
narrowest defensible reading available -- the ordered sequence of
initialization steps in `main()`, ending at `serve()` -- and names that
choice explicitly here rather than silently assuming a boundary that was
never confirmed. If #1281 is later drafted to cover the identical ground,
reconciling the two is a decision for whoever authors it, not something this
node resolves in advance.

## Responsibility

`main()` owns *deciding whether the process is fit to start serving traffic
at all*, and in what order to find out. It is the only place that decides
"fail fast and exit" versus "log and continue" for each of Postgres
connectivity, schema migration, replica-fence safety, NIP-43 membership
bootstrapping, Redis connectivity, media-storage configuration, the
inter-relay mesh, and the git-object-storage backend. It does not itself
serve any request: no listener is bound and no traffic is accepted until
every step in this sequence completes and `serve()` is called (see
*Boundary*).

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `main` | `#[tokio::main] async fn` | The process entry point; runs the full sequence below and calls `serve()` at its end. Returns `anyhow::Result<()>`, so any propagated error becomes a non-zero process exit rather than a panic. | `crates/buzz-relay/src/main.rs:97-1160` |
| `Config::from_env` | `fn` | Fail-fast configuration parsing; env-var defaults or `ConfigError::InvalidValue`. | `crates/buzz-relay/src/config.rs:541-592` |
| `buzz_auto_migrate_enabled` | `fn` | Gates `db.migrate()` on `BUZZ_AUTO_MIGRATE` (`true`/`1`/`yes`/`on`, case-insensitive, trimmed); everything else is treated as off. | `crates/buzz-relay/src/main.rs:29-36` |
| `relay_keypair_from_config` | `fn` | Requires and parses `BUZZ_RELAY_PRIVATE_KEY`; returns an error (not a panic) if absent or invalid. | `crates/buzz-relay/src/main.rs:38-46` |
| `Db::new` | `async fn` | Connects the writer pool eagerly (fail-fast) and the read-replica pool lazily (never fails on a down replica). | `crates/buzz-db/src/runtime/mod.rs:488-507` |
| `Db::migrate` | `async fn` | Runs all pending SQL migrations; fail-fast when called. | `crates/buzz-db/src/runtime/mod.rs:859-861` |
| `AppState::new` | `fn` | Assembles every constructed service into one `Arc<AppState>`; returns `(state, audit_shutdown)`. | `crates/buzz-relay/src/state.rs:782-793` |
| `serve` | `async fn` (boundary only) | The function this sequence hands off to once every step below succeeds; its own internals are out of scope here. | `crates/buzz-relay/src/main.rs:1142`, `:1289-1446` |

## Dependencies

**Depends on** (this sequence requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `rustls` (`ring` crypto provider) | Must be installed before any TLS connection this sequence or any later code path makes. | `Cargo.toml` (buzz-relay) declares `rustls`; installed at `crates/buzz-relay/src/main.rs:98-104` |
| `buzz-db` (`Db`, `migration`, `partition`, `deletion`, `community`, `relay_members`, `event`, `channel_members`) | Pool creation, migration, and every fence/backfill/bootstrap step. | `crates/buzz-relay/Cargo.toml` declares `buzz-db`; called throughout `crates/buzz-relay/src/main.rs:179-592` |
| `buzz-auth`, `buzz-search`, `buzz-media`, `buzz-workflow` | Constructed during this sequence and handed to `AppState::new`. | `crates/buzz-relay/src/main.rs:414-444` |
| `buzz-pubsub` (`PubSubManager`) | Redis pub/sub connection and the three subscriber tasks spawned immediately after it. | `crates/buzz-relay/src/main.rs:382-412` |
| `buzz-audit` (`AuditService`) | Constructed conditionally on `config.audit_enabled`. | `crates/buzz-relay/src/main.rs:368-380` |
| `deadpool_redis` | Redis connection pool creation, fail-fast. | `crates/buzz-relay/src/main.rs:382-393` |

**Depended on by** (these require this sequence to have completed, or observe its effects):

| Component | Why | Evidence |
|---|---|---|
| `serve()`'s listener binding | The health, TCP, and (optional) UDS listeners are not bound until this entire sequence returns and `serve()` is called; no request of any kind is reachable before then. | `crates/buzz-relay/src/main.rs:1142`, `:1296-1298` |
| Kubernetes `startupProbe` (`/_liveness`) | Cannot observe any signal from the process until the health listener binds, so its 120-second (`failureThreshold: 60` x `periodSeconds: 2`) budget is the deployment-level bound this whole sequence must fit inside. | `deploy/charts/buzz/values.yaml:143-164` |
| `platforms-relay-graceful-shutdown`'s post-`serve()` cleanup | Awaits the same `AuditShutdownHandle` this sequence's `AppState::new` call returns. | `crates/buzz-relay/src/state.rs:778-793` |

## Boundary

This node does not describe:
- **`serve()`'s own internals** -- listener binding order, the shutdown
  watch channel, the connection drain, and the hard-shutdown timer are
  `platforms-relay-graceful-shutdown`'s subject (#1271, unmerged). This node
  documents only that `serve()` is the sequence's final call.
- **What issue #1281 ("process") will eventually cover.** No content exists
  for #1281 at the recorded revision (see the `INFERENCE` entry above); this
  node's scope is inferred from its own filename and issue text, not from
  reading a sibling document, and the two nodes may need reconciling once
  #1281 is drafted.
- **The individual internal behavior of every background worker spawned
  during startup** (ephemeral-channel reaper, NIP-ER reminder scheduler,
  admin outbox/action workers, pool- and usage-metrics pollers, the three
  pub/sub consumers, the community-lifecycle revalidator). This node
  documents only that each is spawned, in what order, and that none of them
  is awaited before `serve()` is called -- not their own loop logic.
- **The inter-relay mesh's own internals** beyond its boot-time
  fail-fast/no-op gating (`BUZZ_MESH`). `platforms-relay-mesh-bootstrap`
  (#1276) is the natural home for that detail, once drafted.
- **The git object-storage conformance probe's own protocol** (the A3
  conditional-write axiom, its race-width/rounds knobs). This node documents
  only that it runs, by default, as a fail-fast admission gate at a fixed
  point in the sequence.
- **Kubernetes deployment topology** beyond the one `startupProbe` fact this
  sequence's timing is measured against.

## Relationships

None declared. `platforms-relay-graceful-shutdown` (#1271) is the closest
conceptual neighbor -- this node's sequence hands off directly to the
function that node documents -- but it exists only on the unmerged branch
`task/1271-relay-graceful-shutdown`, not on `origin/launchpad`, so per this
batch's convention (and `AGENTS.md`'s rule that a declared relationship
target must resolve against the merge-target branch) no edge to it is
declared here. The same applies to `platforms-relay-connection-manager`
(#1267), `platforms-relay-app-state` (#1263), and
`platforms-relay-mesh-bootstrap` (#1276), each named in prose above but
unmerged. Edges to all four should be added once their respective PRs merge.

## Scope and omissions

**This node covers** the ordered, strictly sequential chain of
initialization steps `crates/buzz-relay/src/main.rs`'s `main()` runs before
calling `serve()`: crypto provider install, logging/OTEL setup, config
loading, metrics install, Postgres pool creation, conditional migration,
partition/fence/roster verification, NIP-43 membership bootstrapping, Redis
pool and pub/sub setup, auth/search/media service construction, `AppState`
assembly, the inter-relay mesh and git-conformance admission gates, and the
point at which roughly a dozen background workers are spawned -- along with
which of these steps are fail-fast versus best-effort/non-fatal.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `serve()`'s listener binding, shutdown watch channel, and connection drain | `platforms-relay-graceful-shutdown` (#1271), unmerged at time of writing |
| Whatever `process.md` (#1281) will eventually claim | Not yet drafted anywhere at the recorded revision |
| Each spawned background worker's own internal logic | Not yet a corpus node for most of them at this revision |
| `ConnectionManager` / `AppState` field-level internals | `platforms-relay-connection-manager` (#1267) / `platforms-relay-app-state` (#1263), both unmerged |
| The inter-relay mesh's own wire protocol and consumer wiring | `platforms-relay-mesh-bootstrap` (#1276), unmerged |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Real-world timing of the full sequence against the 120-second
  `startupProbe` budget.** The 120-second figure is read from the Helm
  chart, and the sequence's step order is read from source; how long the
  sequence actually takes to run in staging/production (especially the
  fail-fast git-conformance probe and any slow migration) was not measured
  from a live boot.
- **Whether #1281 ("process"), once drafted, will describe the same
  sequence this node does under a different name**, in which case one of
  the two nodes will need to be narrowed, merged, or have its scope
  renegotiated. This node states its own inferred boundary explicitly (see
  above) precisely so that collision is visible and decidable later, rather
  than silently duplicated.
- **Whether any of the roughly ten background workers spawned during this
  sequence can itself fail in a way that should have been fail-fast but
  currently is not** -- this node records the observed fact (each is
  spawned via `tokio::spawn` and never awaited) without independently
  judging whether that non-blocking treatment is correct for every worker.
