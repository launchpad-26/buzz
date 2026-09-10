Issue #1224 — task: document operations/runbooks/postgres-unavailable.md
Stated size: none stated  →  cap: 5 steps (set by the feature #618 task brief: a single
  hand-authored document against conventions already settled by the schema, AGENTS.md,
  and the merged runbook template, not the first corpus node overall)

Target file: `launchpad/docs/corpus/operations/runbooks/postgres-unavailable.md`
Node id: `operations-runbooks-postgres-unavailable` (assigned by the issue brief; permanent)
Base branch: `origin/launchpad`

ALREADY TRUE  (verified against git at 473205a7457b208455f188847bfb27b01aa83cac, not notes)
  `git status --short` in this worktree reports a clean tree; no corpus content is
    part-built.
  `launchpad/docs/corpus/operations/` does not exist yet — this task creates it and the
    `runbooks/` subdirectory. The sibling reliability reference (issue #1215, path
    `operations/reliability/database-failure.md`) is a separate, unmerged task; it is not
    on `origin/launchpad` and this node must not link its path.
  `launchpad/docs/corpus/templates/runbook.md` (`corpus-template-runbook`) is merged and
    active; its Required sections are Trigger, Severity and impact, Diagnosis, Mitigation
    and resolution, Escalation, Scope and omissions — the issue's DoD tail bullets map
    onto exactly these.
  `node.schema.json` requires id, type, status, origin, audiences, evidence; permits
    `relationships`; `additionalProperties: false` rejects everything else.
  Six already-merged nodes are legitimate `relationships[].target`s per
    `<SCRATCH>/existing-node-ids.txt`: `layers-observability-readiness`,
    `layers-observability-liveness`, `layers-observability-health-checks`,
    `layers-observability-prometheus`, `architecture-containers-postgres`,
    `architecture-deployment-kubernetes`.
  Code read directly (not inferred) establishes the runbook's factual spine:
    `crates/buzz-relay/src/router.rs` — `liveness_handler` is an unconditional
    `(StatusCode::OK, "ok")`; `readiness_handler` checks `shutting_down`, then
    `state.db.ping()` + Redis + `validate_deletion_serving_catalog()` under a 2s
    `tokio::time::timeout`, returning 503 with a JSON body distinguishing
    `shutting_down` from `not_ready`.
    `crates/buzz-db/src/runtime/mod.rs` — the writer pool connects eagerly
    (`PgPoolOptions::connect`, not lazy) with `acquire_timeout_secs: 3` default;
    `ping()` runs `SELECT 1`; pool exhaustion surfaces as `sqlx::Error::PoolTimedOut`.
    `crates/buzz-relay/src/main.rs` — `Db::new(&db_config).await?` at startup returns
    early (before the HTTP listeners bind) on failure; a background task emits
    `buzz_db_pool_size/idle/active/max` gauges every `BUZZ_POOL_METRICS_INTERVAL_SECS`
    (default 10s).
    `deploy/charts/buzz/values.yaml` + `templates/deployment.yaml` — livenessProbe and
    startupProbe both hit `/_liveness`; only readinessProbe hits `/_readiness`;
    `postgresql.enabled: false` by default (production points at `externalPostgresql`,
    no in-cluster DB pod to exec into).
    `Dockerfile` — runtime image installs `curl`; `deploy/compose/compose.yml`'s relay
    healthcheck comment asserts the opposite ("no curl/wget/socat") and instead probes
    `/_readiness` over raw `/dev/tcp` — a genuine unresolved discrepancy between two
    in-repo sources, to be surfaced honestly rather than picked a side on.
    `deploy/compose/run.sh`'s `backup_hint` prints a static checklist and performs no
    backup or restore action; `crates/buzz-admin/src/main.rs`'s `Command` enum has no
    backup/restore/db-check subcommand — confirms no in-repo restore tooling exists.

STEP 1  Front matter, Trigger, and Severity and impact              [independent]
        Create `launchpad/docs/corpus/operations/runbooks/postgres-unavailable.md` with
        schema-valid front matter (`id: operations-runbooks-postgres-unavailable`,
        `type: operations`, `status: draft`, `origin: launchpad`,
        `audiences: [operator, developer, agent, reviewer]`), the single permitted
        commit-only FACT for revision 473205a7457b208455f188847bfb27b01aa83cac, and a body
        opening with one level-1 heading followed by Trigger (readiness 503 / probe
        failures / CrashLoopBackOff, cited to `router.rs`'s `readiness_handler` and the
        Helm chart's probe wiring) and Severity and impact (writes and reads fail,
        distinguishing a running-but-not-ready pod from a boot-time crash loop).
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
                   exits 0 with the new file on disk, and
                   `git cat-file -e 473205a7457b208455f188847bfb27b01aa83cac` exits 0.

STEP 2  Diagnosis                                          [needs 1]  ← RUNS HERE
        Write Diagnosis: how to tell startup-abort from runtime-ping-failure from
        pool-exhaustion, using `/_readiness`'s JSON body, the `buzz_db_pool_*` gauges, and
        the eager-writer-pool-vs-lazy-read-pool distinction in `runtime/mod.rs`. Include
        the reasoned (INFERENCE, confidence 0.6) point that the readiness handler's fixed
        2s timeout is shorter than the writer pool's own 3s default `acquire_timeout`, so
        a saturated-but-reachable pool can present identically to a fully unreachable one
        at this endpoint. One `evidence` entry per substantive claim, classified honestly.
        done when: validator exits 0; every claim in the Diagnosis section has a matching
                   `evidence` entry, checked by reading the section against the ledger.

STEP 3  Mitigation/resolution and verification of recovery          [needs 2]
        Write Mitigation and resolution in executable order — check DB reachability from
        the relay's own network position (the compose healthcheck's `/dev/tcp` one-liner,
        which works without depending on the disputed curl availability; `kubectl exec` /
        `kubectl describe pod` for probe-failure events under Kubernetes; `docker inspect
        --format '{{json .State.Health}}'` to read Docker's own cached healthcheck result
        under compose) — then verification of recovery (`/_readiness` returns 200,
        `buzz_db_pool_active` stabilizes, pod `Ready` condition flips true / compose health
        turns `healthy`).
        done when: validator exits 0; the section's steps are numbered/ordered rather than
                   an unordered list, and each step that asserts *why* it works (not merely
                   *what* to run) carries an `evidence` entry.

STEP 4  Escalation, evidence to preserve, relationships, scope-and-omissions   [needs 3]
        Write Escalation (no in-repo restore tooling — `backup_hint` and `buzz-admin`
        checked directly and cited — so unrecoverable data loss escalates to whoever owns
        the external Postgres instance/managed-DB console, outside this repository) and
        evidence-to-preserve (pool-metrics snapshot, `/_readiness` body, pod
        events/compose health-check log, relay logs around the failure). Add
        `relationships` entries (`references`) to the six already-merged sibling nodes
        listed in ALREADY TRUE. Write Scope and omissions carrying two distinct things:
        what this node does not cover (the deeper failure-mode analysis is the sibling
        reliability reference under separate, unmerged issue #1215 — named without linking
        its path; backup/restore procedure design; capacity planning) and what was expected
        but could not be verified (the curl/no-curl discrepancy above; whether the eval-only
        Postgres subchart pod is ever reachable via `kubectl exec` in practice). Add the
        template-citation evidence entry.
        done when: validator exits 0; `grep -n 'operations/reliability/database-failure'
                   launchpad/docs/corpus/operations/runbooks/postgres-unavailable.md`
                   prints nothing (no link to the unmerged sibling path); every
                   `relationships[].target` resolves per the validator.

STEP 5  Audit against the DoD, run the test suite, commit            [needs 4]
        Re-read the finished node against issue #1224's Definition of Done bullet by
        bullet, and against the runbook template's Required sections list. Fix any gap.
        Run the corpus test suite as a lone command, confirm `OK`, then commit.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
                   exits 0; `cd <worktree> && python3 -m unittest discover -s
                   launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK
                   as the sole command in its own tool call; `git log -1 --format=%H` shows
                   a new commit with a DCO `Signed-off-by` trailer (`git log -1 -s`).

PARALLEL  None. All five steps edit the same single file, and two steps touching one file
          are sequential regardless of how unrelated they look. There is no second
          artefact to fan out to — the issue's Definition of Done caps this task at
          exactly one hand-authored document.

GATES     `review-plan` on this plan before STEP 1 — self-run, therefore not independent,
          and the report says so. `review-code` on the finished diff after STEP 5.
          `review-tests` does not apply: the diff adds one Markdown corpus node and this
          plan file, and touches no test file (STEP 5 runs the existing corpus suite but
          does not modify it). `review-adjudicate` over any findings both reviewers
          report. `qa` explore mode does not apply: this change adds no runtime interface.

BUDGET    STEP 2 and STEP 3. Diagnosis and mitigation are where the runbook has to be
          honest about a genuinely tricky distinction (startup-abort vs. runtime-503 vs.
          pool-exhaustion-that-looks-like-an-outage) without inventing operational
          procedure the repository does not support — e.g. there is no in-repo Prometheus
          alerting rule or dashboard to cite for the trigger, only the raw probe/metric
          surface.

OPEN      Whether `agent` belongs in `audiences`. Resolved here as yes: buzz's own
          architecture principle treats humans and agents as peers for on-call-style
          response, and the sibling `layers-observability-readiness`/`health-checks`
          nodes already carry `agent` in their audiences for the same underlying
          machinery this runbook responds to.

          Whether the curl/no-curl discrepancy between `Dockerfile` and
          `deploy/compose/compose.yml`'s healthcheck comment should route to
          `status: flagged` under ADR-0029. Resolved here as no: ADR-0029's flagged state
          is for two *authoritative* sources of the same claim type making a real claim
          this node depends on; here the safer, repo-proven `/dev/tcp` check sidesteps
          needing to resolve which source is stale, so the node states the discrepancy
          as an "expected but not verified" gap rather than blocking on it.

LEFT OUT  Any relationship or link to `operations/reliability/database-failure.md` /
          `operations-reliability-database-failure` — issue #1215's node is unmerged; the
          brief explicitly forbids linking unmerged sibling paths. The boundary is named
          in prose only.

          A second hand-authored corpus document, of any kind. The issue's out-of-scope
          list forbids it explicitly.

          Designing or implementing actual backup/restore tooling, an alerting rule, or a
          Prometheus dashboard. This runbook documents the response given what exists
          today; building the tooling it finds missing is separate implementation work,
          not a corpus-authoring task.
