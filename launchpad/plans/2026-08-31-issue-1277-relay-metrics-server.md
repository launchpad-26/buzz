# Plan: issue #1277 — document platforms/relay/metrics-server

## ALREADY TRUE

- Repository revision for this task: `131b02f989684117d9ab1dd426f1673fa638e523`
  (worktree `__worktrees/task-1277-relay-metrics-server`, branch
  `task/1277-relay-metrics-server`, based on `origin/launchpad`).
- `launchpad/docs/corpus/platforms/relay/metrics-server.md` does not exist yet;
  neither does the `launchpad/docs/corpus/platforms/` directory on
  `origin/launchpad` at all (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus` returns no `platforms/**` entries).
- `launchpad/docs/corpus/templates/component.md` is merged on `origin/launchpad`
  and is the closest fitting template, but its own text recommends
  `type: implementation`. The unmerged sibling node
  `platforms-relay-health-server` (issue #1272, branch
  `task/1272-relay-health-server`) instead uses `type: platforms`, matching
  every other already-authored `platforms/**` sibling at the time of writing.
  This task follows the same `type: platforms` convention per the batch's
  established practice, stating the deviation from the template's own
  suggestion in the node body, same as `#1272` did.
- `crates/buzz-relay/src/metrics.rs` is the metrics server: a module doc
  (lines 1-14) describing `metrics-rs facade → PrometheusBuilder → HTTP
  listener on :9102 → GET /metrics`; `install()` (lines 58-147) builds a
  `PrometheusBuilder`, registers per-metric histogram bucket boundaries for
  HTTP latency and several Buzz-specific git/fanout histograms, calls
  `.build()`, sets the global recorder, and spawns the exporter future
  (which itself owns the `:9102` HTTP listener — no axum route is involved);
  `track_metrics()` (lines 149-207) is separate axum middleware recording
  `http_requests_total`/`http_request_latency_ms`, explicitly skipping
  `/_*`, `/health`, and `/metrics` paths.
- `crates/buzz-relay/src/config.rs` defines `metrics_port` (lines 197-198,
  `BUZZ_METRICS_PORT` env var parsed at lines 823-826, default `9102`).
- `crates/buzz-relay/src/main.rs` calls `relay_metrics::install(config
  .metrics_port, usage_idle_timeout_secs)` once (line 170, aliased import at
  line 21), immediately after computing `usage_idle_timeout_secs` from two
  small env-driven helper functions (`usage_metrics_interval_secs` lines
  1479-1485, `usage_metrics_idle_timeout_secs`/`idle_timeout_secs` lines
  1488-1500); `serve()`'s own doc comment (lines 1244-1256) names the metrics
  listener as "Listener 4", already bound by the time `serve()` runs.
- `crates/buzz-relay/src/router.rs` layers `track_metrics` onto the main API
  router only (`use` at line 25, `.layer(middleware::from_fn(track_metrics))`
  at line 203), never onto the separate health-only router — corroborating
  the sibling `platforms-relay-health-server` node's own finding.
- No automated test exercises `install()` or `track_metrics()` directly
  (searched `crates/buzz-relay/tests/`, `crates/buzz-test-client/tests/`);
  the one hit for `BUZZ_METRICS_PORT` outside `metrics.rs`/`config.rs`/
  `main.rs` is a doc-comment example in
  `crates/buzz-test-client/tests/nip42_host_binding_live.rs:14` showing how to
  run a second relay binary on a non-colliding port, not a test of metrics
  behavior. `idle_timeout_secs` (one of `install()`'s two arguments) does have
  direct unit coverage: `main.rs:2189-2192`
  (`test_idle_timeout_is_at_least_three_usage_intervals`).
- `launchpad/docs/corpus/architecture/containers/relay.md`
  (`id: architecture-containers-relay`) is merged on `origin/launchpad` and
  already names the metrics listener at topology level (lines 34 and 178:
  "a Prometheus metrics listener (default 0.0.0.0:9102, already bound by
  PrometheusBuilder before serve() is called)" / a routing table row) — a
  valid `references` relationship target, since it resolves on
  `origin/launchpad` and this node's content (handler/config/bucket detail)
  does not duplicate that container-level topology mention.
- Baseline `python3 launchpad/project-intelligence/corpus/validate.py`
  produces exactly 21 pre-existing `FAIL` lines at this revision, unrelated to
  this task (known finding #1).

## STEP 1 — Draft front matter and evidence ledger

Author `launchpad/docs/corpus/platforms/relay/metrics-server.md` with
`id: platforms-relay-metrics-server`, `type: platforms`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, and one
evidence entry per substantive claim (revision, metrics.rs/config.rs/main.rs/
router.rs facts above, the containers-relay cross-reference, the test-coverage
gap), each `FACT` citing the real file/line range actually opened. Done when:
front matter validates against `node.schema.json` in isolation.

## STEP 2 — Write the body

Sections: purpose/scope paragraph naming the `type`/template deviation note
(mirroring `#1272`); Responsibility (module doc, `install()`'s role: global
recorder + HTTP exporter + bucket configuration for Buzz-specific
histograms); Public interface (`install`, `track_metrics`, `metrics_port`
config field, as a table); the metrics-exclusion behavior shared with the
health surface; Dependencies (depends on: `metrics`/`metrics-exporter-
prometheus`/`metrics-util` crates, `Config.metrics_port`; depended on by:
`main.rs` as sole caller of `install`, `router.rs` layering `track_metrics`);
Boundary (does not cover: bucket-boundary rationale for any one Buzz-specific
histogram, the health-only router, deployment/scrape topology); Relationships
(`references: architecture-containers-relay`); Scope and omissions (including
the `type: platforms` vs `type: implementation` open question and the "no
direct test found" gap). Done when: every Definition-of-Done bullet in issue
#1277 is addressed by a named section.

## STEP 3 — Validate in isolation

Temporarily move the new file aside, run
`python3 launchpad/project-intelligence/corpus/validate.py`, confirm the
pre-existing FAIL set (baseline: 21 `FAIL` lines at this revision, matching
known finding #1), restore the file, re-run, confirm the same 21 `FAIL` lines
plus zero new ones. Done when: FAIL set is byte-identical before/after.

## STEP 4 — Earn the commit gate

Run the corpus unittest suite as the sole content of one Bash call, confirm
`OK`, then in a separate call `git add` both the node and this plan file and
`git commit -s`. Done when: commit exists with a verification stamp.

## STEP 5 — Final verification

Re-read the diff against issue #1277's Definition of Done checklist and
re-open every cited file/line once more.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` introduces zero
  new FAIL lines beyond the pre-existing 21.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`.
- Every evidence entry classified `FACT` cites a file this task actually
  opened at the recorded revision.
- The `references` relationship target (`architecture-containers-relay`)
  resolves against `origin/launchpad`, not merely this worktree.

## OPEN

- Whether `type: platforms` or `type: implementation` is the corpus's
  eventual settled convention for `platforms/**` documents is not resolved by
  any accepted decision found; this task follows the batch's established
  practice (per `#1272`) and states the ambiguity in the node body rather
  than resolving it unilaterally.
- No sibling `platforms/relay/*` node (e.g. `platforms-relay-app-state`,
  `platforms-relay-health-server`) is merged onto `origin/launchpad` at this
  revision, so no `depends-on`/`references` edge can be declared toward any of
  them yet, even though they are real content on their own unmerged branches.

## LEFT OUT

- The bucket-boundary rationale for any individual Buzz-specific histogram
  (git hydration, fanout, etc.) is named as belonging to that subsystem's own
  future component node, not restated here — this node documents that
  `install()` is the single place those boundaries are configured, not why
  each boundary set was chosen.
- Testing coverage gaps for `install()`/`track_metrics()` are named as a scope
  gap, not fixed — this task documents existing behavior, it does not add
  tests.
- Kubernetes/deployment scrape configuration for the metrics port is out of
  scope per the issue's "creating or materially editing a second canonical
  document" boundary; deployment topology belongs to
  `architecture/deployment/*` nodes, not this one.
