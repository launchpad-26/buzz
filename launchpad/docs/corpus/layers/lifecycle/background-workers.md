---
id: layers-lifecycle-background-workers
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
  - statement: "node.schema.json's type enum is a closed set of thirteen values including layers, described only as 'the corpus surface a node documents' -- schema/README.md's own field table repeats that same one-line description with no further per-value elaboration."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "standards/taxonomy.md's 'Choosing a value' step 2 instructs picking the enum member whose plain-English name most concretely names the node's primary subject, not where the node currently lives; step 3 instructs following how the corpus has actually used the enum when more than one value plausibly fits, rather than what a label could technically stretch to cover."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/taxonomy.md"
  - statement: "This node uses type: layers rather than templates/concept.md's own worked-skeleton default of type: governance-for-meta-documents-only (concept.md's own instance guidance says a real concept instance 'may take a type value other than governance, decided by that instance's own subject'), because this task's target path is layers/lifecycle/background-workers.md and parent Feature #611's task set is organized under that same layers/lifecycle/ directory taxonomy for cross-cutting runtime-lifecycle behavior. Sibling nodes layers/lifecycle/graceful-shutdown.md and layers/lifecycle/startup.md (both unmerged task branches, read directly from their own worktrees rather than from origin/launchpad) independently reached type: layers for the identical reason, applying standards/taxonomy.md's step 2/3 guidance to the same parent Feature."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/concept.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
      - "git_show(worktree='__worktrees/task-1118-graceful-shutdown', path='launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md') -> 'A note on `type`' section"
      - "git_show(worktree='__worktrees/task-1120-startup', path='launchpad/docs/corpus/layers/lifecycle/startup.md') -> line 123, 'A note on `type`' section"
    confidence: 0.75
  - statement: "buzz-relay spawns a NIP-43 membership-snapshot reconciler: after an immediate startup pass, a loop reconciles NIP-43 membership snapshots on a fixed interval (BUZZ_NIP43_RECONCILE_INTERVAL_SECS, default 60s, floor 1s), logging a repaired count when reconciliation finds and fixes drift."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:541-577"
  - statement: "buzz-relay spawns an ephemeral-channel reaper: every BUZZ_REAPER_INTERVAL_SECS (default 60s) it archives channels whose TTL deadline has passed, then emits a system message, updates NIP-29 discovery events, and evicts live subscriptions for each archived channel -- guarded by an `archived_at IS NULL` SQL condition so concurrent runs from multiple pods are harmless (at worst, duplicate system messages), a trade-off the code comment states explicitly and calls out for a future pg_advisory_lock upgrade."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:635-715"
  - statement: "buzz-relay spawns a NIP-ER reminder scheduler polling for due reminders every SPROUT_REMINDER_SCHEDULER_INTERVAL_SECS (default 10s, batch limit SPROUT_REMINDER_SCHEDULER_BATCH_LIMIT default 100), publishing each to Redis pub/sub for cross-pod fan-out; cross-pod dedup is a claim-before-publish pattern (claim_due_reminder_with_stamp, an opaque per-attempt stamp) with an explicit release_due_reminder rollback if the publish itself fails, rather than a lock held for the tick's duration."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:728-850"
  - statement: "buzz-relay spawns a durable-lifecycle-backstop community revalidator on BUZZ_COMMUNITY_REVALIDATE_INTERVAL_SECS (default 30s, clamped to [1, 300]) specifically because Redis pub/sub cannot deliver an archive command to a pod that was offline; it periodically revalidates only communities with local live sockets so a missed command still converges without a global DB scan."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:911-927"
  - statement: "The community revalidator is the one background worker in buzz-relay built on a shared, reusable helper (run_periodic_until_cancelled) rather than a hand-rolled loop: the helper ticks on an interval with MissedTickBehavior::Skip and races each tick against a CancellationToken via tokio::select!(biased), breaking the loop the moment the token fires -- cooperative self-termination observed from inside the task, not an external JoinHandle abort. main() fires that token (state.community_revalidator_cancel.cancel()) exactly once, immediately after serve() returns."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1167-1201"
      - "crates/buzz-relay/src/main.rs:1101-1102"
  - statement: "buzz-relay spawns a pool-metrics poller on BUZZ_POOL_METRICS_INTERVAL_SECS (default 10s) that, alongside emitting DB/Redis pool-utilization and replica-fence-lag gauges, also reaps expired deletion-serving write leases every tick (deletion_store.reap_expired_serving_write_leases(1000)) -- a GC sweep riding inside a metrics-poller's own tick rather than its own dedicated task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:976-1048"
  - statement: "buzz-relay's usage-metrics tick (BUZZ_USAGE_METRICS_INTERVAL_SECS, default 300s floor 5s) is leader-elected via a Postgres advisory lock (try_lock_usage_metrics(USAGE_METRICS_LOCK_KEY)) so only one pod in a multi-pod deployment performs the DB-derived collection, the expired-relay-invite reap, and the storage sweep on each tick, while every pod (leader or not) still emits its own in-memory gauges; the first tick is delayed by a random per-process jitter in [0, interval) to avoid every pod hammering the DB simultaneously at boot, and the interval uses MissedTickBehavior::Skip so a slow tick is skipped rather than triggering a catch-up burst."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1060-1099"
      - "crates/buzz-relay/src/main.rs:84"
      - "crates/buzz-relay/src/main.rs:1439-1445"
  - statement: "Nested inside the leader-only branch of the usage-metrics tick, buzz-relay reaps expired relay invites older than a rolling 30-day retention cutoff (chrono::Duration::days(30) subtracted from the current instant) on every tick, logging the deleted count when nonzero."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1606-1626"
  - statement: "Also nested in the leader-only branch, run_storage_sweep_tick drives storage_sweep::maybe_spawn_sweep, an hourly (BUZZ_STORAGE_SWEEP_INTERVAL_SECS default 3600s, floored to 60s), single-flight S3-bucket listing sweep: at most one sweep attempt runs at a time (guarded by an in-flight JoinHandle check under a Mutex), a sweep_fut built fresh every tick is only ever polled if the single-flight+cadence rule decides to spawn, a bounded tokio::time::timeout (BUZZ_STORAGE_SWEEP_TIMEOUT_SECS default 120s) wraps each attempt, and a hard BUZZ_STORAGE_SWEEP_MAX_OBJECTS cap (default 1,000,000) fails an attempt that lists too much rather than growing memory unbounded; the whole feature has a kill switch (BUZZ_STORAGE_METRICS=off) that stops every storage-family gauge, including the health gauges, from ever being emitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs:1-18"
      - "crates/buzz-relay/src/storage_sweep.rs:30-80"
      - "crates/buzz-relay/src/storage_sweep.rs:149-259"
      - "crates/buzz-relay/src/main.rs:1638-1674"
  - statement: "A cold storage-sweep cache (no sweep has ever succeeded) publishes health gauges only (sweep_ok=0); a warm cache re-publishes the last good snapshot even while the newest attempt is failing, so a transient S3 blip never blanks the storage dashboards -- and a permanently failing sweep (e.g. missing s3:ListBucket) retries on every leader-only usage tick rather than waiting a full sweep interval, because should_spawn returns true unconditionally after any failed attempt."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/storage_sweep.rs:1-18"
      - "crates/buzz-relay/src/storage_sweep.rs:149-179"
  - statement: "buzz-db runs a replica freshness-fence probe (replica_fence::run_probe) on a fixed 500ms PROBE_INTERVAL, independent of any env var, committing a heartbeat token every tick; a probe failure closes the fence (fence.close()) rather than leaving stale routing decisions in place, and the loop uses MissedTickBehavior::Delay rather than the Skip behavior other buzz-relay workers use. It is spawned only after Db::spawn_fence_probe verifies the replica floor-guard end-to-end, itself called from buzz-relay's startup sequence after the migration decision and future-partition/deletion-fence setup, deliberately so a relay running with auto-migrate off can never open the fence over an unenforced floor guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/replica_fence.rs:91"
      - "crates/buzz-db/src/runtime/replica_fence.rs:774-789"
      - "crates/buzz-db/src/runtime/replica_fence.rs:774-788"
      - "crates/buzz-relay/src/main.rs:200-228"
  - statement: "buzz-workflow's WorkflowEngine::run is a 60-second, fixed (not env-configurable) tick loop, spawned once from buzz-relay's boot sequence, that evaluates every enabled Schedule-triggered (cron or interval) workflow definition on every relay pod; architecture-flows-workflow-execution already narrates this cron/interval trigger path -- including its deterministic per-pod scheduled_for computation, its durable per-fire claim row, and its documented non-replay of fires missed during downtime -- in full, so this node names it as one instance of the background-worker shape rather than re-describing that behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:489-493"
      - "crates/buzz-relay/src/main.rs:632-633"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "None of the tokio::spawn call sites for the workers cited above bind the returned JoinHandle to anything main() retains -- confirmed by reading every spawn expression individually (crates/buzz-relay/src/main.rs:556, 585, 633, 647, 721-722, 743, 857, 887, 922, 938, 984, 1066; crates/buzz-relay/src/storage_sweep.rs:248; crates/buzz-db/src/lib.rs:874). Of all of them, only the community revalidator observes any externally-triggered stop signal at all (via its own CancellationToken, not via the discarded JoinHandle); every other worker listed runs until the tokio runtime itself shuts down when main() returns, with no code path that awaits, aborts, or drains it first."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:541-1099"
      - "crates/buzz-relay/src/storage_sweep.rs:248"
      - "crates/buzz-db/src/runtime/mod.rs:679-688"
  - statement: "crates/buzz-backend-kubernetes's gc.rs and reconcile.rs are not background workers despite their names: gc.rs's own module doc states 'GC runs on every deploy, after identity derivation and before the state transition,' and reconcile.rs's own module doc describes 'the deploy loop: executes classify's actions against a substrate and re-enters' -- both execute synchronously inside one deploy() call, bounded by a 600-second OPERATION_DEADLINE_SECS, not on a standing process-lifetime timer independent of any caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-backend-kubernetes/src/gc.rs:1-18"
      - "crates/buzz-backend-kubernetes/src/reconcile.rs:1-9"
  - statement: "buzz-relay's BUZZ_RECONCILE_CHANNELS-gated dev/CI task is also not a background worker in this node's sense: it retries reconcile_channel_events at most 24 times with a 5-second sleep between attempts (about two minutes total) and then stops permanently, rather than running for the process lifetime -- the surrounding comment states plainly that 'production relays create channels through the event pipeline and don't need this.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:579-624"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-flows-workflow-execution
---

# Background workers

A **background worker** is a task spawned once at process start, independent of any
inbound connection or request/response cycle, that runs for the life of the process on
its own timer to keep durable state converged, reclaim expired or orphaned resources, or
fire time-based triggers. Reconciliation loops, GC/reap sweepers, and scheduled/cron jobs
are all instances of this one shape: no caller is waiting on their result, and their
correctness is judged by what state looks like *eventually*, not by any single
invocation's return value.

**What this is not.** A function whose name contains "reconcile" or "gc" is not
automatically an instance of this concept. `crates/buzz-backend-kubernetes/src/gc.rs` and
`reconcile.rs` run entirely inside one `deploy()` call, bounded by a 600-second operation
deadline — they reconcile *one* deploy attempt against cluster state and return, the same
shape as a retry loop inside a single request, not a standing timer. Similarly,
`buzz-relay`'s `BUZZ_RECONCILE_CHANNELS` dev/CI task retries at most 24 times over about
two minutes and then stops for good — a bounded startup fixup, not a worker that runs for
the process's life. Both are real code, both use reconciliation-shaped language, and
neither is what this node describes.

## Visual aid

```mermaid
flowchart TB
    Boot["buzz-relay main(): boot sequence"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W1["NIP-43 membership reconciler (60s)"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W2["Ephemeral channel reaper (60s)"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W3["NIP-ER reminder scheduler (10s)"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W4["Pool-metrics poller + lease reaper (10s)"]
    Boot -->|"tokio::spawn, CancellationToken"| W5["Community revalidator (30s)"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W6["Usage-metrics tick, leader-elected (300s)"]
    W6 -->|"leader only, nested"| W6a["Storage sweep (3600s, single-flight)"]
    W6 -->|"leader only, nested"| W6b["Expired relay-invite reap (30d retention)"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W7["Replica freshness-fence probe (500ms)"]
    Boot -->|"tokio::spawn, no retained JoinHandle"| W8["Workflow cron/interval loop (60s)"]
    Serve["serve(): axum::serve + graceful shutdown"]
    Boot --> Serve
    Serve -.->|"on return, cancel() fires once"| W5
```

## Use cases

**A developer adding a new periodic task** needs this shape before reaching for their
own: pick an interval and env var following the existing naming convention
(`BUZZ_*_INTERVAL_SECS`), decide honestly whether the task needs cross-pod coordination
(none, a Postgres advisory-lock leader as the usage-metrics tick uses, or a
claim-column compare-and-swap as the reminder scheduler uses), and decide whether the
task must observe a stop signal — `run_periodic_until_cancelled` is the one reusable
helper for that, and every other worker cited here shows what happens by default when a
task does not use it: nothing stops it early, and it is simply dropped when the runtime
shuts down.

**An operator tuning relay behavior** needs to know which interval env vars exist and
what a worker actually does on each tick before changing its cadence — for example,
lowering `BUZZ_STORAGE_SWEEP_INTERVAL_SECS` costs S3 `ListBucket` calls at the sweep's
own bounded rate, while lowering `BUZZ_POOL_METRICS_INTERVAL_SECS` also changes how
often expired deletion-serving leases are reaped, since that reap rides inside the same
tick.

**A reviewer of a new background task** needs to check, deliberately, whether the task
should be cancellable at shutdown and whether it needs cross-pod dedup — both are easy
to omit silently, as most of the workers cited here in fact do, and neither omission
fails any test on its own.

## Comparison

| Worker | Cadence | Cross-pod coordination | Cancellation-aware |
|---|---|---|---|
| NIP-43 membership reconciler | 60s (`BUZZ_NIP43_RECONCILE_INTERVAL_SECS`) | None — every pod reconciles independently | No |
| Ephemeral channel reaper | 60s (`BUZZ_REAPER_INTERVAL_SECS`) | `archived_at IS NULL` SQL guard (idempotent, not locked) | No |
| NIP-ER reminder scheduler | 10s (`SPROUT_REMINDER_SCHEDULER_INTERVAL_SECS`) | Claim-before-publish stamp, per-reminder | No |
| Community revalidator | 30s (`BUZZ_COMMUNITY_REVALIDATE_INTERVAL_SECS`) | None — each pod revalidates its own local sockets | Yes — `CancellationToken` via `run_periodic_until_cancelled` |
| Pool-metrics poller + lease reaper | 10s (`BUZZ_POOL_METRICS_INTERVAL_SECS`) | None | No |
| Usage-metrics tick | 300s (`BUZZ_USAGE_METRICS_INTERVAL_SECS`), jittered first tick | Postgres advisory lock (one leader pod) | No |
| Storage sweep (nested in usage tick) | 3600s (`BUZZ_STORAGE_SWEEP_INTERVAL_SECS`), single-flight | Runs only on the usage-metrics leader | No |
| Relay-invite reap (nested in usage tick) | Every leader tick, 30-day retention cutoff | Runs only on the usage-metrics leader | No |
| Replica freshness-fence probe | 500ms fixed (`PROBE_INTERVAL`, not env-configurable) | None — every pod probes its own writer connection | No |
| Workflow cron/interval loop | 60s fixed, not env-configurable | Durable per-fire claim row (all pods compute the same `scheduled_for`) | No |

## Background

Fire-and-forget `tokio::spawn` with no retained `JoinHandle` is the dominant shape in
this codebase, not an oversight isolated to one task — nine of the ten workers compared
above share it. The one exception, the community revalidator, does not achieve its
cancellation by holding the handle either: it uses a shared `CancellationToken` the task
checks against itself inside its own loop. This is a genuine architectural asymmetry —
most background workers here have no way to be told to stop, and are simply dropped
along with the rest of the process when the tokio runtime shuts down — rather than a
documented, decided trade-off; nothing in the cited code states this is intentional.
Whether it should stay that way is exactly the kind of question `layers/lifecycle/`'s
sibling nodes on graceful shutdown and cancellation exist to answer, not this one.

## Relationships

- **references**: `architecture-containers-relay` — the container almost every worker
  cited above is spawned from and runs inside.
- **references**: `architecture-flows-workflow-execution` — the canonical, detailed
  narration of the workflow cron/interval trigger path this node cites only briefly, to
  avoid duplicating its content.

## Scope and omissions

**This node covers** what makes a spawned task a background worker in this codebase (an
independent, process-lifetime timer loop with no caller awaiting its result), ten
concrete instances of that shape across `buzz-relay`, `buzz-db`, and `buzz-workflow`,
their cadence and cross-pod coordination strategy, and the two code shapes that use
reconciliation-shaped naming but are not instances of this concept.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How any of these workers is stopped or drained at process shutdown, and the buzz-relay/buzz-acp graceful-shutdown sequence in general | `layers/lifecycle/graceful-shutdown.md` (#1118, unmerged as of this writing) |
| `CancellationToken` mechanics and cooperative-cancellation patterns in general, beyond naming that the community revalidator uses one | `layers/lifecycle/cancellation.md` (#1116, unmerged as of this writing) |
| The general concurrent-execution model (task scheduling, synchronization primitives) beyond what these specific workers happen to use | `layers/lifecycle/concurrency.md` (#1117, unmerged as of this writing) |
| Resource-cleanup semantics in general, beyond the specific GC/reap behavior narrated per-worker above | `layers/lifecycle/resource-cleanup.md` (#1119, unmerged as of this writing) |
| Process boot ordering and what must succeed before these workers are even spawned | `layers/lifecycle/startup.md` (#1120, unmerged as of this writing) |
| `buzz-acp`'s presence-heartbeat and agent-pool-wake background tasks | Not yet owned by any corpus node at the recorded revision |
| The workflow cron/interval trigger path's own detailed behavior (per-pod deterministic scheduling, durable claim rows, missed-fire non-replay) | `architecture-flows-workflow-execution` |
| Whether the fire-and-forget/no-cancellation pattern found across nine of the ten cited workers is an accepted trade-off or an unaddressed gap | Not decided by any source found while authoring this node — named as an open architectural asymmetry above, not resolved |

**Expected but not verified when this node was written:**

- **Whether any automated test exercises a full tick of each cited worker end-to-end**
  was not established. Names and line ranges were confirmed by reading the source
  directly; the corresponding test suites (if any) for the NIP-43 reconciler, ephemeral
  reaper, and reminder scheduler were not opened.
- **Whether `buzz-workflow`'s cron loop or any of the `buzz-relay` workers is ever
  aborted early in a test harness (e.g. via `JoinHandle::abort` in an integration test)**
  was not checked — this node's claim that no *production* code path retains a
  `JoinHandle` does not rule out a test-only one.
- **The sibling nodes this table names as "unmerged as of this writing" may have merged
  by the time this node is read.** Their content was read directly from their own task
  worktrees to confirm the `type: layers` precedent and to avoid duplicating their
  scope, but their `relationships` targets could not be added here because `AGENTS.md`
  requires a target to exist on the branch being merged into, and none of them did at
  authoring time.
