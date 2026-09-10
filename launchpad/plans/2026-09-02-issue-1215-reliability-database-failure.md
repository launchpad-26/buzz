# Issue #1215 — task: document operations/reliability/database-failure.md

Stated size: no Size line in the issue body  ->  cap: 5 steps
(Set by the batch dispatch brief for Feature #618, not asked about: this is one
hand-authored corpus document plus its plan, not the first node in the corpus.)

Target file: `launchpad/docs/corpus/operations/reliability/database-failure.md`
Node id: `operations-reliability-database-failure` (assigned in the task prompt; permanent)
Branch: `task/1215-reliability-database-failure`, based on `origin/launchpad`
Worktree: `/home/serina/Launchpad/buzz/__worktrees/task-1215-reliability-database-failure`

---

ALREADY TRUE  (verified against git and by running the tools, not against notes)
-------------------------------------------------------------------------------

- `git rev-parse HEAD` is `473205a7457b208455f188847bfb27b01aa83cac`. `git status`
  reports a clean tree tracking `origin/launchpad` before this plan file is added.
- `launchpad/docs/corpus/operations/reliability/database-failure.md` does not exist:
  `ls launchpad/docs/corpus/operations/reliability/` fails with "No such file or
  directory" in this worktree.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` contains
  **no** path under `operations/` at all — this is the first `type: operations` node
  in the corpus. It does contain `architecture/containers/postgres.md`
  (`architecture-containers-postgres`), `layers/observability/readiness.md`
  (`layers-observability-readiness`), `layers/observability/health-checks.md`
  (`layers-observability-health-checks`) and `layers/lifecycle/startup.md`
  (`layers-lifecycle-startup`), all confirmed present in
  `<SCRATCH>/existing-node-ids.txt` and therefore legal `relationships` targets.
- Neither sibling issue's node exists on `origin/launchpad` or in this tree: no
  `operations/reliability/availability.md` (#1214) and no
  `operations/reliability/postgres-unavailable.md` (#1224, the sibling runbook).
  Both are named only in prose, never linked as paths or relationship targets.
- Evidence gathered by opening source directly (paths, not memory), all under this
  worktree at the recorded revision:
  - `crates/buzz-db/src/runtime/mod.rs` — `DbConfig::default()` (max_connections 20,
    min 2, `acquire_timeout_secs` 3, `idle_timeout_secs` 600, `max_lifetime_secs`
    1800), `Db::connect_pool` (eager writer connect, `after_connect` floor-guard +
    isolation check), `Db::connect_read_pool` (lazy, `min_connections(0)`,
    `READER_ACQUIRE_TIMEOUT` = 150ms), `Db::ping` (`SELECT 1`), `Db::pool_stats`.
  - `crates/buzz-db/src/error.rs` — `DbError` enum, `Sqlx(#[from] sqlx::Error)` variant.
  - `crates/buzz-relay/src/config.rs` — `BUZZ_DB_POOL_SIZE` default 50,
    `BUZZ_DB_READ_POOL_SIZE` optional, `BUZZ_HEALTH_PORT`.
  - `crates/buzz-relay/src/main.rs` — startup sequence: `Db::new(&db_config).await`
    at line 187 wrapped in `.map_err` that turns a connection failure into
    `anyhow::anyhow!` propagated out of `async fn main() -> anyhow::Result<()>`
    (line 97) **before** the HTTP listener (`serve(...)`, line 1142) ever binds;
    `BUZZ_AUTO_MIGRATE` gate; pool-stats gauges (`buzz_db_pool_size/idle/active/max`).
  - `crates/buzz-relay/src/router.rs` — `readiness_handler` (`/_readiness`): checks
    `shutting_down` flag, then `tokio::join!(db.ping(), redis_pool.get(), \
    validate_deletion_serving_catalog())` under a 2s `tokio::time::timeout`, any
    timeout/failure collapsing to `(false, false, false)` and HTTP 503; `health_handler`
    (`/health`) and `liveness_handler` (`/_liveness`) both return unconditional 200.
  - `crates/buzz-relay/src/handlers/ingest.rs` — `map_serving_fence_state` (DB lookup
    failure on the write path fails closed as `IngestError::Internal("error: ...")`,
    doc comment states this explicitly), the `insert_event_with_thread_metadata`
    error arm (any non-`AuthEventRejected` `DbError` becomes
    `IngestError::Internal(format!("error: database error: {other}"))`), and the unit
    tests `serving_fence_lookup_outage_fails_closed_as_internal` (constructs
    `DbError::Sqlx(sqlx::Error::PoolTimedOut)` directly, no live Postgres needed) and
    `serving_fence_inactive_community_maps_to_restricted` (contrasts the `restricted:`
    authorization path with the `error:` outage path).
  - `crates/buzz-relay/src/handlers/req.rs` and `crates/buzz-relay/src/handlers/count.rs`
    — every DB-lookup failure on the REQ/COUNT read paths sends
    `RelayMessage::closed(&sub_id, "error: database error")` (or `"error: {e}"`) and
    returns; no partial or degraded subscription is ever created.
  - `crates/buzz-relay/src/api/mod.rs` — `internal_error()` logs and returns
    `StatusCode::INTERNAL_SERVER_ERROR` with a generic body; `crates/buzz-relay/src/api/bridge.rs`
    — `IngestError::Internal` on the HTTP bridge (`POST /events`) maps through
    `internal_error`, i.e. HTTP 500.
  - `docker-compose.yml` — no `relay` service exists in local compose; only
    `adminer` declares `depends_on: postgres: condition: service_healthy`, so nothing
    in local dev gates relay startup on a Postgres health check besides the relay's
    own eager connect.
  - `deploy/charts/buzz/values.yaml` — `livenessProbe`/`startupProbe` both target
    `/_liveness` (unconditional 200, never fails on a DB outage);
    `readinessProbe` targets `/_readiness` with `periodSeconds: 5`,
    `failureThreshold: 3`; `deploy/charts/buzz/templates/deployment.yaml` is a
    `kind: Deployment` with no `restartPolicy` override.
  - `crates/buzz-db/src/lib.rs` — ephemeral events (kinds 20000–29999) are never
    persisted to Postgres at all (Redis pub/sub only, by design), stated in the
    crate's own doc comment.
  - No retry-with-backoff exists for an ordinary failed acquire/query: grep for
    `retry`/`backoff` across `crates/buzz-db/src` and `crates/buzz-relay/src/main.rs`
    turns up only a dev/CI-gated (`BUZZ_RECONCILE_CHANNELS`) channel-reconciliation
    loop and an Aurora-identity probe re-check, neither on the ordinary read/write path.
- `python3 launchpad/project-intelligence/corpus/validate.py` run against the current
  (pre-draft) tree exits 0, confirming the harness itself is not the obstacle.

---

STEP 1  Front matter, evidence ledger, and reference-description section  [independent]  <- RUNS HERE
        Create `launchpad/docs/corpus/operations/reliability/database-failure.md` with
        the complete `evidence` ledger (one entry per claim enumerated in ALREADY TRUE,
        classified FACT with the source path that was actually opened; the one
        commit-only FACT records `473205a7457b208455f188847bfb27b01aa83cac`), the
        section skeleton per `launchpad/docs/corpus/templates/reference.md`'s required
        sections, and the Reference-description paragraph written.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
        against the tree including the new file; AND
        `grep -c '^## ' launchpad/docs/corpus/operations/reliability/database-failure.md`
        returns at least 6.

STEP 2  Structured entries — connection pool, startup vs runtime, HTTP/WS surface  [needs 1]
        Write the reference table(s): pool configuration and timeouts (writer vs.
        lazy reader), what happens on pool exhaustion / acquire timeout, the
        startup-failure path (process exits before serving) versus the runtime-failure
        path (individual requests fail, process keeps running), and how each of the
        WebSocket (EVENT/REQ/COUNT) and HTTP (`/events`, `/query`, `/count`) surfaces
        responds to a failed query — all fail-closed, cited to the specific handler
        and, where one exists, the specific unit test.
        done when: validator still exits 0; and the body contains a table with a row
        for each of: writer pool exhaustion, reader pool exhaustion/absence, WS write
        (EVENT) failure, WS read (REQ/COUNT) failure, HTTP bridge failure, startup
        connect failure.

STEP 3  Readiness-probe behaviour and the boundary with the sibling runbook  [needs 2]
        Write the readiness-probe section (what `/_readiness` checks, the 2s timeout,
        the fail-collapse to `(false, false, false)`, the coupling with Redis and the
        deletion-catalog check, and the Kubernetes probe wiring —
        `periodSeconds`/`failureThreshold` and that liveness/startup probes hit
        `/_liveness` and never observe a DB outage on their own). Write the required
        Boundary section naming: not the operator response procedure (that is a
        sibling runbook, described in words only, never linked as a path), not the
        general availability/observability treatment, not an API-Reference-depth
        catalogue of every DB-touching endpoint.
        done when: validator exits 0; AND
        `grep -c 'postgres-unavailable\|reliability/postgres-unavailable' \
        launchpad/docs/corpus/operations/reliability/database-failure.md` returns 0
        (no path reference to the unmerged sibling runbook) while a plain-word mention
        of it existing is still permitted and checked by reading the section.

STEP 4  Relationships and Scope-and-omissions  [needs 3]
        Declare `references` toward `architecture-containers-postgres` (pool/config
        detail this node does not re-enumerate), `layers-observability-readiness` and
        `layers-observability-health-checks` (the general readiness/health-check
        contract this node instantiates for the Postgres case only), and
        `layers-lifecycle-startup` (general startup-ordering this node's
        startup-vs-runtime section is a special case of). Write Scope and omissions
        with the two required, distinct parts: what the node does not cover / who owns
        it (the runbook, availability, Redis/audit/search pool failure in detail), and
        separately what was expected but could not be verified (see OPEN below).
        Add the final evidence entry naming the reference template.
        done when: validator exits 0 with every `relationships[].target` resolving; and
        `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus | grep -c \
        -E 'architecture-containers-postgres|layers-observability-readiness|layers-observability-health-checks|layers-lifecycle-startup'`
        is not needed as a literal grep (those are ids, not paths) — instead re-run
        the id existence check directly against `<SCRATCH>/existing-node-ids.txt` for
        all four targets and confirm all four are present.

STEP 5  Self-review, test suite, and commit  [needs 4]
        Re-read the diff against issue #1215's Definition of Done bullet by bullet.
        Re-open every FACT's cited source adversarially (does it say the statement, not
        merely concern it). Confirm exactly one commit-only FACT. Run the corpus test
        suite as the sole command in its own Bash call, confirm `OK`, then commit with
        `-s` in a separate call.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests \
        -p "test_*.py"` reports `OK`; `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0; `git log -1 --format=%s` matches `docs(corpus): .* (#1215)`; and
        `git show -s --format=%B HEAD | grep -c '^Signed-off-by:'` returns at least 1.

---

PARALLEL  **Nothing here may run in parallel.** All five steps edit the same single
          file. The ledger written in STEP 1 is the contract STEPs 2-4 fill in; running
          them out of order risks body prose with no matching ledger entry, which is
          exactly the drift STEP 5 checks for.

GATES     `review-plan` on this plan before STEP 1. `review-code` after STEP 5 on the
          whole diff (the file is Markdown, but the evidence-honesty and
          citation-accuracy checks that matter for a corpus node are the same kind of
          adversarial read `review-code` already performs). `review-tests` does not
          apply — no test file is added or edited; confirmed by `git diff --stat`
          naming only the node and this plan. `qa` explore mode does not apply — no
          runtime interface is added.

BUDGET    **STEP 2 is the step most likely to overrun.** It is the section with the
          most distinct code paths to cite accurately (writer pool, reader pool,
          three transport surfaces, startup vs runtime), and getting the citation
          granularity right — bare path vs. path:line, per the code-references
          standard's preference for bare paths — takes longer than writing the prose.

OPEN      - **Whether `BUZZ_DB_POOL_SIZE`'s default (50, in `config.rs`) or
            `DbConfig::default()`'s literal default (20, in `runtime/mod.rs`) is the
            one worth stating** — the relay always constructs `DbConfig` through
            `Config::from_env`, so 50 is what a real deployment sees; 20 only applies
            to a `DbConfig` built by hand (mainly tests). This plan states 50 as the
            operative default and cites `config.rs`, noting the literal-struct default
            only where the distinction matters.
          - **Whether the Kubernetes chart's unstated `restartPolicy` defaulting to
            `Always`, and the resulting crash-loop-on-repeated-startup-failure, is
            fairly described as a repository fact or as external Kubernetes-platform
            behaviour this repository does not itself assert.** Resolved by stating
            the chart fact (no override) as FACT and the Kubernetes default-behaviour
            consequence as a plainly-labelled INFERENCE, not folded into one FACT.
          - **The audit pool and search pool** (`architecture-containers-postgres.md`
            records both exist, connected independently of `buzz_db::Db`) are a real
            second failure surface this node's Definition of Done does not require
            covering in equal depth; named in Scope and omissions as out of this
            node's depth rather than silently absent.

LEFT OUT  - **The operator response procedure** — detection, escalation, remediation
            steps. That is sibling runbook #1224
            (`operations/reliability/postgres-unavailable.md`), not yet written; named
            in words, never linked as a path or relationship target per the batch
            brief's merge-order rule.
          - **General service availability / SLO treatment** — sibling #1214
            (`operations/reliability/availability.md`), same rule.
          - **Redis failure and its interaction with the readiness probe**, beyond
            noting the probe checks both together. Redis is a different subsystem
            with its own failure modes; owned elsewhere.
          - **Audit-log and search-index Postgres connections in the same depth as the
            core `buzz_db::Db` pool.** Already described at the level this node needs
            by `architecture-containers-postgres.md`, referenced rather than
            duplicated.
          - **API-Reference-depth enumeration of every DB-touching endpoint's exact
            failure response.** The reference template's own boundary excludes that
            depth for a general reference; the structured entries cover the
            transport-level pattern (WS write, WS read, HTTP bridge, startup), not
            every individual handler.
