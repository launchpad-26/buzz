---
id: layers-lifecycle-resource-cleanup
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type enum includes layers as one of thirteen closed values (alongside architecture, capabilities, platforms, ...), described only as \"the corpus surface a node documents\" with no further per-value elaboration in either node.schema.json or schema/README.md's own prose table for the type field."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "This node uses type: layers rather than flow.md's own worked-skeleton default of type: architecture, for the same reason siblings layers/lifecycle/graceful-shutdown.md (#1118) and layers/lifecycle/startup.md (#1120) each give in their own 'A note on type' sections: Feature #611 (this node's parent) organizes its whole task set under a layers/lifecycle/ directory naming convention -- a cross-cutting technical-behavior grouping distinct from the architecture/ subtree's C4 static-diagram family -- and layers is node.schema.json's own dedicated enum member for that surface. Both sibling files were opened directly rather than assumed from memory; at authoring time they existed only on their own unpushed worktree branches, and both have since merged to origin/launchpad, so they are cited here by path."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md"
      - "launchpad/docs/corpus/layers/lifecycle/startup.md"
    confidence: 0.75
  - statement: "hydrate.rs's own module doc comment states: 'The returned HydratedRepo owns a tempfile::TempDir; dropping it cleans up. Cached pack/index pairs are immutable performance state; object storage remains authoritative.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hydrate.rs:21-23"
  - statement: "HydratedRepo's own struct doc comment states: 'The tempdir is removed when this value is dropped -- callers must keep the handle alive for the duration of the subprocess that reads from path().' The struct's only owning field is _tempdir: TempDir; path, hydrated_bytes and hydrated_packs are plain derived data with no cleanup responsibility of their own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hydrate.rs:47-60"
  - statement: "materialize_manifest creates the TempDir (TempDir::new_in(options.scratch_dir)) as its first fallible step, before any pack is fetched or any ref is written; every subsequent step in the function uses the `?` operator to propagate a failure, so an error partway through Phase 1 (pack fetch/index) or Phase 2 (ref/HEAD write) returns early and drops the local tempdir binding before it is ever wrapped into a HydratedRepo -- deleting the half-built workspace via ownership, not via an explicit catch-and-clean branch written for each failure site."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hydrate.rs:289-379"
  - statement: "GitPackCache owns a session-scoped tempfile::TempDir (field _session_dir) created once per process via Builder::new().prefix(\"session-\").tempdir_in(cache_parent), plus a `.heartbeat` file inside it that a periodic background task rewrites every HEARTBEAT_INTERVAL (60 seconds) for as long as the process is alive."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/pack_cache.rs:66-74"
      - "crates/buzz-relay/src/api/git/pack_cache.rs:105-155"
      - "crates/buzz-relay/src/api/git/pack_cache.rs:20"
  - statement: "impl Drop for GitPackCache aborts the heartbeat background task; the session tempdir itself is cleaned up by tempfile::TempDir's own Drop as an ordinary field of GitPackCache, requiring no explicit removal call in this impl. This Drop only runs on a normal Rust unwind (process exit, panic unwind, or the value going out of scope) -- it does not run if the process is killed with SIGKILL or otherwise aborts without unwinding."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/pack_cache.rs:420-425"
  - statement: "cleanup_stale_sessions (called once from GitPackCache::new before the new session directory is created) sweeps every sibling session-* directory under the same cache parent whose .heartbeat file's mtime is older than STALE_SESSION_AGE (10 minutes) and removes it via std::fs::remove_dir_all -- the fallback that exists specifically for the case Drop cannot cover: a prior process that crashed or was force-killed before its own Drop could run, leaving an orphaned session directory with a heartbeat that stopped ticking."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/pack_cache.rs:126"
      - "crates/buzz-relay/src/api/git/pack_cache.rs:482-509"
      - "crates/buzz-relay/src/api/git/pack_cache.rs:21"
  - statement: "The test abandoned_sessions_are_removed_after_grace_period creates a session-abandoned directory with a fresh .heartbeat file, sleeps past a zero-duration max_age, calls cleanup_sessions_older_than directly, and asserts the directory no longer exists -- exercising the crash-fallback sweep path independent of any real crash or GitPackCache instance."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/pack_cache.rs:561-572"
  - statement: "PopulationPermit and FlightParticipant are both short-lived RAII guards constructed inside materialize_pack (at lines 203 and 269) around a cache miss's population work: PopulationPermit's Drop decrements a gauge metric when the population's tokio::sync::Semaphore permit is released; FlightParticipant's Drop decrements an AtomicUsize participant count and, only when it reaches zero, removes the shared PopulationFlight entry from the cache's DashMap -- releasing both a concurrency-limiting resource and a shared coordination-map entry on every exit path from materialize_pack, success or error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/pack_cache.rs:81-103"
      - "crates/buzz-relay/src/api/git/pack_cache.rs:203"
      - "crates/buzz-relay/src/api/git/pack_cache.rs:269"
  - statement: "StreamingGit's own field doc comments state its child field is 'held purely to extend lifetime' -- the child process is spawned with .kill_on_drop(true), so dropping StreamingGit after its stream completes reaps any lingering subprocess, and on the happy path the child has already exited by the time the drop runs -- and its _repo field (a HydratedRepo) is commented 'must not be removed from disk until the subprocess is done -- i.e. until the stream ends,' making the ephemeral bare-repo tempdir's lifetime and the child git process's lifetime co-owned by the same struct."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:1509-1522"
      - "crates/buzz-relay/src/api/git/transport.rs:1679"
  - statement: "impl Drop for StreamingGit aborts the detached stdin-pump task (stdin_task.abort()); the child's own kill_on_drop(true) and the _repo field's own Drop (tempdir removal) each fire as StreamingGit's remaining fields drop in turn, so one struct's Drop ends up releasing a background task, a subprocess (and its stdin/stdout pipes), and a temp directory together, in field-declaration order."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:1639-1642"
      - "crates/buzz-relay/src/api/git/transport.rs:1690"
      - "crates/buzz-relay/src/api/git/transport.rs:1717-1722"
  - statement: "CommunityConnectionGuard's own doc comment states it 'removes a socket lifecycle registration on every handler exit path'; its Drop implementation is a single call, self.connections.remove(&self.connection_id), removing the WebSocket connection's entry from the registry DashMap regardless of whether the handler returned normally, returned early, or panicked."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:173-177"
      - "crates/buzz-relay/src/state.rs:179-182"
  - statement: "UploadPermit is held for the lifetime of one Blossom upload request via the AuthenticatedUpload extractor's own _upload_permit field; its Drop implementation releases a global upload OwnedSemaphorePermit (by simply dropping the field, which needs no explicit code in this impl) and separately decrements (or removes, if it was the last one) a per-pubkey in-flight-upload counter held in a DashMap, so one failed or completed upload never leaves a stale counter entry for that pubkey."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/media.rs:33-40"
      - "crates/buzz-relay/src/api/media.rs:68-72"
      - "crates/buzz-relay/src/api/media.rs:74-85"
  - statement: "Production call sites in buzz-db (for example, Db::execute_in_transaction acquiring a connection at crates/buzz-db/src/store/event.rs:276-278) obtain a Postgres connection via self.pool.acquire(), which returns an sqlx::pool::PoolConnection<Postgres> -- sqlx's own RAII guard type around one pooled connection, which is not itself defined in this repository but whose acquisition and use this repository's own code depends on for returning connections to the pool without an explicit release call at each call site."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:276-278"
      - "crates/buzz-db/src/runtime/observability.rs:137-140"
  - statement: "A single PgPool connection's return to the pool when its PoolConnection guard drops is sqlx's own documented RAII behavior, not code this repository defines or could re-verify by reading sqlx's source from within this repository; this node treats that specific mechanic as INFERENCE rather than FACT for that reason, while treating buzz-db's own call sites that rely on it (acquire() without a matching explicit release) as directly observed FACT above."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/event.rs:276-278"
    confidence: 0.75
  - statement: "buzz-db's own test suite calls pool.close().await explicitly and repeatedly (for example at crates/buzz-db/src/runtime/tests.rs:388-389, 7999, 8324, 8779, 8904, 8920-8921, 8997-8999) -- an eager, whole-pool teardown distinct from a single connection's per-use release, used to tear down scratch/seed databases between tests rather than relied on anywhere in this repository's own production request-handling code paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/tests.rs:388-389"
      - "crates/buzz-db/src/runtime/tests.rs:2220-2221"
      - "crates/buzz-db/src/runtime/tests.rs:2345-2346"
      - "crates/buzz-db/src/runtime/tests.rs:2361-2363"
      - "crates/buzz-db/src/runtime/tests.rs:2438-2443"
      - "crates/buzz-db/src/store/deletion.rs:4788-4789"
      - "crates/buzz-db/src/store/deletion.rs:4913-4914"
  - statement: "architecture-containers-relay and architecture-containers-agent-runtime are both present as node ids on origin/launchpad at the time this node was authored (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, re-run immediately before drafting), but neither is the standing-structure node for the specific crate (buzz-relay's git-hosting subsystem) every example in this node's Sequence lives in; no more specific relationships target exists on origin/launchpad today, so this node declares none rather than pointing at a container-level node whose content this document does not narrate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md:1-2"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:1-2"
  - statement: "origin/launchpad's corpus tree carries no layers/ node at all as of this node's authoring commit (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, re-run immediately before drafting) -- layers-lifecycle-graceful-shutdown (#1118) and layers-lifecycle-startup (#1120) exist only on their own local, unpushed worktree branches, so naming either as a relationships.target would be a hard validate.py error on the branch this commit is actually merged into."
    entry_class: FACT
    evidence:
      - "absent:launchpad/docs/corpus/layers@338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Issue #1119's Definition of Done requires exactly one hand-authored canonical document, schema-valid front matter with typed relationships 'appropriate to the node,' one independently maintainable idea, FACT/INFERENCE/TEAM_KNOWLEDGE not conflated, links to neighboring corpus nodes without duplicating their content, and a passing local validate.py run."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1119 definition of done"
---

# Resource cleanup: flow

## A note on `type`

`node.schema.json`'s `type` enum lists thirteen closed values, and `layers` is one
of them, described (both in the schema and in `schema/README.md`'s prose table)
only as naming "the corpus surface a node documents," with no further elaboration
distinguishing it from its neighbors. `launchpad/docs/corpus/templates/flow.md`'s
own worked skeleton defaults an instance of this template to `type: architecture`,
reasoning that a flow node is a fourth member of the C4 model's diagram family.
This node departs from that default and uses `type: layers` instead, for the same
reason its two merged-precedent siblings in this same batch already give: parent
Feature `#611` organizes its entire task set under a `layers/lifecycle/` directory
taxonomy — a cross-cutting technical-behavior grouping (lifecycle, concurrency,
cancellation, background work, resource cleanup, startup) distinct from the
structural C4 architecture family the `architecture/` subtree already houses.
Both `layers/lifecycle/graceful-shutdown.md` (`#1118`) and `layers/lifecycle/startup.md`
(`#1120`) were opened directly from their own local worktree branches (not
assumed) for this section, so this is a directly-verified restatement of their
shared reasoning rather than an independent re-derivation. Everything else about
this node — required sections, evidence expectations, the Mermaid
`sequenceDiagram` form — follows `flow.md` unchanged; only the `type` value
differs from its worked skeleton.

## Flow statement

This node narrates one recurring pattern rather than a single request: how Buzz
releases short-lived resources — on-disk temp directories, child-process handles,
concurrency permits, and in-memory registry entries — when the scope that acquired
them ends, whether that end is success, an early error return, or a panic. The
trigger is any one of many things that happen continuously while `buzz-relay` is
running: a git smart-HTTP request finishes streaming, a pack-cache population
completes or fails, a Blossom media upload completes or is rejected, or a
WebSocket connection's handler returns. The actors are the Rust value that owns
the resource and its `Drop` implementation; there is no external signal or
timer involved, unlike `layers-lifecycle-graceful-shutdown` (`#1118`), whose
sequence is driven by SIGTERM/SIGINT and whose resources are the process's whole
listener/connection/audit-worker set, not one request's own private state. This
node's scenario terminates the instant the owning value's `Drop::drop` returns;
the *Outcome* section below also covers the one case where `Drop` does not run at
all — a killed process — and what recovers from it.

## Sequence

Buzz relies on Rust's ownership model (RAII: Resource Acquisition Is
Initialization) rather than an explicit `try`/`finally`-style cleanup block
written at each exit point. A guard type is constructed when a resource is
acquired; its `Drop` implementation runs automatically — on the happy path, on an
early `?`-propagated error, or on a panic unwind — wherever the compiler
determines the value's scope has ended, with no call site required to remember
to clean up. The concrete examples below are ordered from the resource with the
widest scope (a whole cache's session directory) to the narrowest (one request's
permit), then close with the one path `Drop` cannot reach.

1. **Temp-directory ownership, happy path.** `hydrate_for_read`/`hydrate_for_write`
   materialize an ephemeral bare git repo into a `tempfile::TempDir` wrapped by
   `HydratedRepo`; the type's own doc comment states plainly that "the tempdir is
   removed when this value is dropped." (`crates/buzz-relay/src/api/git/hydrate.rs:47-60`)
2. **Temp-directory ownership, failure path.** `materialize_manifest` creates that
   `TempDir` before any fallible step and propagates every later error with `?`;
   an error partway through pack hydration (Phase 1) or ref/HEAD writing (Phase 2)
   returns early, dropping the local tempdir binding and deleting the half-built
   workspace — cleanup falls out of ownership, not a written cleanup branch per
   failure site. (`crates/buzz-relay/src/api/git/hydrate.rs:289-379`)
3. **A whole cache's session directory.** `GitPackCache` owns one process-lifetime
   session `TempDir` plus a periodically-rewritten `.heartbeat` file inside it;
   `impl Drop for GitPackCache` aborts the heartbeat background task, and the
   session tempdir's own `Drop`, running as an ordinary struct field, removes the
   directory — no explicit removal call appears in this `impl` at all.
   (`crates/buzz-relay/src/api/git/pack_cache.rs:66-74`, `pack_cache.rs:420-425`)
4. **Concurrency permits and coordination-map entries.** Each cache-miss
   population in `materialize_pack` constructs a `PopulationPermit` (releases a
   `tokio::sync::Semaphore` permit and decrements a gauge metric on drop) and a
   `FlightParticipant` (decrements a shared participant count and, only at zero,
   removes the coordination entry from a `DashMap`) — both released on every exit
   from the function, success or error. (`crates/buzz-relay/src/api/git/pack_cache.rs:81-103,203,269`)
5. **A child process and its pipes, ordered with a temp directory.**
   `StreamingGit` holds the response's `child: tokio::process::Child` (spawned
   with `.kill_on_drop(true)`) and the `HydratedRepo` (`_repo`) alive together;
   its own field comments state the child is "held purely to extend lifetime"
   and the repo "must not be removed from disk until the subprocess is done."
   `impl Drop for StreamingGit` aborts the detached stdin-pump task; the child's
   `kill_on_drop` and the repo's tempdir `Drop` then fire as the struct's
   remaining fields drop in turn — one `Drop` releasing a task, a subprocess and
   its stdio pipes, and a temp directory together.
   (`crates/buzz-relay/src/api/git/transport.rs:1509-1522,1639-1642,1679,1690,1717-1722`)
6. **An in-memory registry entry (no filesystem involved).**
   `CommunityConnectionGuard`'s own doc comment states it "removes a socket
   lifecycle registration on every handler exit path"; its `Drop` is one call,
   removing the connection's entry from a `DashMap` regardless of how the
   handler exited. (`crates/buzz-relay/src/state.rs:173-182`)
7. **A semaphore permit and a per-key counter, scoped to one HTTP request.**
   `UploadPermit`, held by `AuthenticatedUpload` for one Blossom upload request,
   releases a global upload semaphore permit (implicitly, by field drop) and
   decrements/removes a per-pubkey in-flight-upload counter on `Drop`, so a
   failed or completed upload never leaves a stale counter entry.
   (`crates/buzz-relay/src/api/media.rs:33-40,68-85`)
8. **A pooled database connection.** Production code (e.g.
   `crates/buzz-db/src/store/event.rs:276-278`) acquires a Postgres connection via
   `self.pool.acquire()`, returning an `sqlx::pool::PoolConnection` — sqlx's own
   RAII guard around a pooled connection — which this repository's call sites
   rely on to return the connection to the pool without an explicit release call.
   (`crates/buzz-db/src/store/event.rs:276-278,64-65`)
9. **The one path `Drop` cannot reach.** If the process is killed (`SIGKILL`) or
   otherwise aborts without unwinding, no `Drop` in steps 1-8 runs, and any
   session directory step 3 owns is orphaned on disk with a `.heartbeat` file
   that stops being rewritten. `GitPackCache::new` calls `cleanup_stale_sessions`
   before creating its own new session directory, sweeping any sibling
   `session-*` directory whose `.heartbeat` mtime is older than
   `STALE_SESSION_AGE` (10 minutes) via `std::fs::remove_dir_all` — a
   next-process-start fallback that exists specifically because `Drop`-based
   cleanup cannot cover a crash. (`crates/buzz-relay/src/api/git/pack_cache.rs:126,482-509,21`)

## Diagram

```mermaid
sequenceDiagram
    participant Scope as Owning scope (fn body)
    participant Guard as Guard value (RAII)
    participant Resource as Resource (tempdir / child / permit / map entry)
    participant NextStart as Next GitPackCache::new

    Scope->>Guard: construct (acquire resource)
    alt normal return, early `?` error, or panic unwind
        Scope->>Guard: scope ends
        Guard->>Resource: Drop::drop() releases/removes it
    else process killed (SIGKILL) before unwind
        Note over Guard,Resource: Drop never runs; resource orphaned on disk
        NextStart->>Resource: cleanup_stale_sessions sweeps stale .heartbeat dirs
    end
```

## Outcome

**Normal-exit path.** Once the owning value's scope ends — the happy path, an
early `?`-propagated error, or a panicking unwind — its `Drop` implementation
runs synchronously as part of unwinding, and the resource (temp directory, child
process handle, semaphore permit, or registry/coordination-map entry) is released
before control returns to the caller. No two examples above required a shared
top-level `try`/`finally` block; each guard type's own `Drop` is sufficient, and
composing several guards in one struct (`StreamingGit`) composes their releases
automatically in field order.

**Crash/orphan path.** A process killed by `SIGKILL`, or one that aborts without
unwinding, runs no `Drop` at all — any resource step 3's `GitPackCache` owned at
that moment (its session `TempDir`) is left on disk, unremoved. This is not a bug
description; `cleanup_sessions_older_than`'s own test,
`abandoned_sessions_are_removed_after_grace_period`, exercises exactly this by
creating an orphaned `session-*` directory directly (no crash needed to trigger
the test) and asserting the sweep removes it once its `.heartbeat` is stale.
(`crates/buzz-relay/src/api/git/pack_cache.rs:561-572`) No equivalent
crash-fallback sweep was found for `HydratedRepo`'s own per-request `TempDir`
(steps 1-2) or for `StreamingGit`'s child process — see *Scope and omissions*.

## Boundary

This node does not describe:
- **The graceful-shutdown signal/drain sequence** (`layers-lifecycle-graceful-shutdown`,
  `#1118`) — that node narrates a *process-level*, signal-triggered sequence
  (SIGTERM/SIGINT → flag → drain → backstop → exit) that runs once per process
  lifetime. This node narrates *per-request/per-connection* resource release that
  recurs continuously while the process is running, and does not re-narrate
  `#1118`'s sequence, backstop timeout, or exit codes.
- **The startup sequence** (`layers-lifecycle-startup`, `#1120`) — resource
  *acquisition* (connecting pools, spawning background tasks) is that node's
  subject; this node covers only *release*.
- **Background-worker, cancellation and concurrency semantics in general** —
  siblings `#1115`, `#1116`, `#1117` respectively; this node's `PopulationPermit`/
  `FlightParticipant` example touches concurrency limiting only incidentally, as
  one example of a permit released on drop, not as a general treatment of Buzz's
  concurrency model.
- **The standing container structure of `buzz-relay`** — what crates it
  composes, how it is deployed — is `architecture-containers-relay`'s subject;
  this node narrates only specific resource-release mechanics inside it.
- **sqlx's own internal pool implementation** — this node cites that Buzz's own
  code relies on `PoolConnection`'s drop-based release (see evidence ledger,
  marked `INFERENCE` since sqlx's source was not opened from within this
  repository), not how sqlx implements that guard internally.
- **Any other `Drop`-implementing type in this repository** beyond the seven
  worked examples above — a non-exhaustive but representative selection; see
  *Scope and omissions* for the full list of `impl Drop` sites found but not
  narrated here.

## Relationships

None. `origin/launchpad`'s corpus tree carries no `layers/` node at the recorded
revision (re-checked via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` immediately before drafting) — `layers-lifecycle-graceful-shutdown`
and `layers-lifecycle-startup` exist only on their own local, unpushed worktree
branches, so naming either as a `relationships.target` would be a hard
`validate.py` error against the branch this commit is actually merged into.
`architecture-containers-relay` was considered and rejected as a target: it
documents `buzz-relay`'s standing structure in general, not the git-hosting
subsystem (`hydrate.rs`, `pack_cache.rs`, `transport.rs`) every example in this
node's *Sequence* actually lives in, so pointing at it would assert a closer fit
than exists.

## Scope and omissions

**This node covers** the RAII/`Drop`-based resource-release pattern Buzz's own
code uses for short-lived, per-request or per-connection resources: ephemeral
git-hydration temp directories (happy path and early-error path), a process-wide
git pack cache's session directory and heartbeat file, per-population
concurrency permits and coordination-map entries, a streaming git subprocess's
child handle and pipes (co-owned with a temp directory by one struct), a
WebSocket connection's registry entry, a media-upload semaphore permit and
per-pubkey counter, and a pooled database connection — plus the one case none of
this reaches (a killed process) and the specific fallback (`cleanup_stale_sessions`)
Buzz's own code uses to recover from it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The graceful-shutdown signal/drain/backstop sequence | `layers-lifecycle-graceful-shutdown` (`#1118`) |
| The process startup/connection-acquisition sequence | `layers-lifecycle-startup` (`#1120`) |
| Background-worker lifecycle in general | `#1115` (sibling `layers/lifecycle/*` task) |
| Cancellation semantics in general | `#1116` (sibling `layers/lifecycle/*` task) |
| Concurrency limiting in general | `#1117` (sibling `layers/lifecycle/*` task) |
| The standing container structure of `buzz-relay` | `architecture-containers-relay` |
| Every other `impl Drop` site in the repository (e.g. `AcpClient::shutdown`, `HarnessRelay`, `ConnGuard`, `KillGroup`, `PairingSession`, `QrPayload`, `ServingWriteGuard`, `RespawnGuard`, `KeypairGuard`, `EmitGuard`, `AbortOnDrop`, `TmpFileGuard`, `PgidGuard`, `LivenessGuard`, `TurnCompletionGuard`, `TimedByteStream`) | Not yet owned by any corpus node; found by a repo-wide `grep -rn "impl Drop"` search but not individually narrated here — this node's seven worked examples were chosen as representative of the pattern, not as an exhaustive inventory |

**Expected but not verified when this node was written:**
- **Whether an equivalent crash-fallback sweep exists for `HydratedRepo`'s own
  per-request `TempDir` (steps 1-2) or for `StreamingGit`'s child process was not
  found.** A targeted read of `hydrate.rs` and `transport.rs` found no
  stale-directory or orphaned-process sweep comparable to
  `cleanup_stale_sessions`; whether an orphaned per-request tempdir under the
  OS's own temp root is otherwise reclaimed (OS temp-directory cleaner, disk
  quota, manual operator cleanup) was not established either way.
- **Whether any automated test exercises `StreamingGit`'s or `UploadPermit`'s
  `Drop` directly** (as opposed to `pack_cache.rs`'s
  `abandoned_sessions_are_removed_after_grace_period`, which does) was not
  established; a search for a matching test name in `transport.rs` and
  `media.rs` found none, which is a gap in this node's own verification, not a
  claim that no such coverage exists under a different name.
- **sqlx's own `PoolConnection` drop behavior** was treated as `INFERENCE`
  rather than `FACT` because its implementation lives outside this repository
  and was not opened as part of authoring this node; only Buzz's own call sites
  that depend on it were directly verified.
