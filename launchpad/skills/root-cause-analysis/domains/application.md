---
name: application
summary: Evidence map for the code and its runtime — deploys, flags, pools, GC, retries, and dependency drift.
layer: Application
---

# Application

## First five checks
1. **What deployed or changed in the runtime window around onset** — a build, a config push, a feature-flag flip, an autoscale event, or a dependency upgrade. Most application incidents start here, and it is the fastest check to rule in or out.
2. **Error and status-code rates by endpoint or transaction, before and after onset** — a spike confined to one route or one downstream call narrows the search space immediately; a broad spike across all routes points at a shared resource (pool, GC, thread starvation) rather than a code path.
3. **Thread pool, connection pool, and queue saturation** — exhausted worker threads, a maxed-out DB connection pool, or a backed-up request queue produces symptoms that look identical to "the app is slow" or "the app is down" but the fix is capacity or a leak, not the business logic.
4. **Garbage collection pauses and memory trend** — a rising heap or lengthening GC pause correlates with creeping latency and eventual unresponsiveness; check this before assuming the slowdown is load-driven.
5. **Retry and timeout configuration on outbound calls** — an aggressive retry policy with no backoff turns one slow downstream dependency into a self-inflicted retry storm that saturates the very pools checked in #3. This is the check most often skipped because it looks like someone else's problem until the multiplier is visible.

## Evidence sources
Application logs (structured/JSON preferred) and stack traces; APM/tracing (span latency, error rate, throughput by endpoint); deployment and release history (CI/CD pipeline, change record system); feature-flag platform's change/audit log; runtime metrics (heap, GC pause time, thread pool and connection pool utilization, queue depth); dependency manifest and lockfile diffs; upstream/downstream service health dashboards; container or process restart and OOM-kill events from the orchestrator.

## Common root causes in this layer
Bad deploy or unvalidated config change; a feature flag enabled for a cohort it was never tested against; connection or thread pool exhaustion from a slow downstream dependency; a memory leak surfacing as GC pressure and eventual OOM; a retry storm amplifying a minor downstream blip into a full outage; a dependency version bump that silently changed behavior (serialization, default timeouts, TLS ciphers); a stale or expired credential/certificate used by the app; a code path that only executes under a rare input combination or load pattern; cache stampede after a mass cache invalidation or cold restart.

## Diagnostic commands and queries
- Deployment/release history: `git log --oneline -20` on the release branch, or the CI/CD pipeline's run history view, to list what shipped in the incident window.
- Feature-flag audit log: the flag platform's read-only change history (who flipped what, when) — do not toggle flags to "test" during triage.
- Process and resource state: `ps aux | grep <process>`, `top -b -n 1`, `free -m` (or container-runtime equivalents like `docker stats --no-stream`) to read CPU/memory without altering anything.
- Thread and connection pool state: an app's `/metrics` or `/actuator`-style read-only endpoint, or a JVM thread dump. Confirm the pid is actually a JVM first (`jps` or `jcmd -l`), then prefer `jstack <pid>` — it fails harmlessly against a non-JVM target instead of touching it. `kill -QUIT <pid>` only prints a dump and does not terminate the process **for a JVM, which installs a SIGQUIT handler**; against any other process, SIGQUIT's default disposition is to terminate it (with a core dump), so never send it to a pid you have not confirmed is a JVM.
- GC behavior: read existing GC logs, or a live read-only GC stats sample (`jstat -gcutil <pid> 1000 5`); do not enable verbose GC logging mid-incident if it requires a restart.
- Log search: `grep`/`zgrep` or the log platform's query UI for error signatures, exception stack traces, and timeout messages in the incident window — read-only by construction.
- Dependency drift: `git diff <last-known-good-tag> HEAD -- package-lock.json` (or `Gemfile.lock`, `poetry.lock`, `go.sum`) to see what versions moved; diffing a lockfile never mutates the running system.
- Network/DNS from the app host, read-only: `curl -sv --max-time 5 <downstream-url>`, `dig <hostname>` — safe probes with a short timeout so a hung probe cannot itself add load.
- **Avoid:** any command with a destructive sibling — `kill -9`, `kill -QUIT` against a pid not confirmed to be a JVM (it terminates the process instead of dumping it), restarting the process or pod to "clear it," toggling a feature flag to test a theory, or running a load test against production. Each of these changes state and can destroy the evidence the incident needs.

## Escalation signals
- Error and latency symptoms appear identically across every application on hosts that share the same node, cluster, or availability zone — points at compute, network, or cloud-platform layer, not this application's code.
- The application's outbound calls are timing out or refused, but its own CPU, memory, threads, and GC are all healthy — the fault is in the downstream dependency, database, or network path, not here.
- Authentication or token-issuance failures precede the application errors, and the app is correctly rejecting or erroring on invalid credentials — hand off to identity/auth.
- The application logs show clean, fast queries but user-facing latency is still high — check network or load-balancer layer for the added latency before continuing to dig here.
- Symptoms track a storage-layer signal (disk I/O wait, volume latency, replication lag) rather than any application-level metric — hand off to the storage or database domain.
