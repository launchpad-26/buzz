# Plan: issue #1272 — document platforms/relay/health-server

## ALREADY TRUE

- Repository revision for this task: `131b02f989684117d9ab1dd426f1673fa638e523`
  (worktree `__worktrees/task-1272-relay-health-server`, branch
  `task/1272-relay-health-server`, based on `origin/launchpad`).
- `launchpad/docs/corpus/platforms/relay/health-server.md` does not exist yet.
- `launchpad/docs/corpus/templates/component.md` is merged on `origin/launchpad`
  and is the closest fitting template (single-component documentation), but its
  own text recommends `type: implementation`. Every already-authored sibling
  node under `platforms/**` (e.g. `platforms-relay-app-state`,
  `platforms-relay-admission`, `platforms-relay-admin-api`, ~40 others across
  desktop/mobile/cli/agents/relay) instead uses `type: platforms`, matching the
  corpus surface implied by the `platforms/` path. None of those sibling nodes
  are merged onto `origin/launchpad` yet (`git ls-tree -r --name-only
  origin/launchpad -- launchpad/docs/corpus/platforms` returns nothing), so
  they cannot be cited as merged precedent for validation purposes, but they
  are real committed content on real task branches and this task follows the
  same `type: platforms` convention per the batch orchestrator's explicit
  instruction, stating the deviation from the template's own suggestion in the
  node body.
- `crates/buzz-relay/src/router.rs` defines the relay's health-probe HTTP
  surface: a `build_health_router` (health-only, no auth/CORS/metrics
  middleware, routes `/_liveness`, `/_readiness`, `/_status`, `/_mesh`) plus
  `/health`, `/_liveness`, `/_readiness` also mounted directly on the main API
  router (pre-tenant-binding, host-agnostic).
- `crates/buzz-relay/src/config.rs` defines `health_port` (`BUZZ_HEALTH_PORT`,
  default `8080`), documented as separate from the app router so K8s probes
  bypass Istio and auth middleware.
- `crates/buzz-relay/src/main.rs`'s `serve()` binds the health router on its
  own TCP listener (`config.health_port`) via a separate `tokio::spawn`, and
  the SIGTERM handler (`shutdown_signal` + `shutting_down: Arc<AtomicBool>`)
  flips readiness to 503 immediately, while liveness stays 200 throughout —
  the standard K8s liveness/readiness split.
- `crates/buzz-relay/src/metrics.rs`'s `track_metrics` middleware explicitly
  skips `/_*` and `/health` paths; that middleware is layered only onto the
  main app router, not onto the health-only router, which has no such layer
  at all.
- No automated test file exercises `build_health_router`, `liveness_handler`,
  `readiness_handler`, `status_handler`, or `mesh_status_handler` directly
  (searched `crates/buzz-relay/tests/`, `crates/buzz-test-client/tests/`); one
  conformance test (`conformance_multitenant.rs:578-581`) cites the main
  router's route list including `/health`, `/_liveness`, `/_readiness` as
  incidental evidence for an unrelated (token-minting-surface) obligation.

## STEP 1 — Draft front matter and evidence ledger

Author `launchpad/docs/corpus/platforms/relay/health-server.md` with
`id: platforms-relay-health-server`, `type: platforms`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, and one
evidence entry per substantive claim (revision, router/config/main.rs/metrics
facts above), each `FACT` citing the real file/line range actually opened.
Done when: front matter validates against `node.schema.json` in isolation.

## STEP 2 — Write the body

Sections: purpose/scope paragraph; Responsibility; the two-router split
(health-only router vs. routes on the main API router) with the reason
(K8s probes bypass Istio/auth); each handler (`health_handler`,
`liveness_handler`, `readiness_handler`, `status_handler`,
`mesh_status_handler`) with what it checks and returns; configuration
(`health_port`); shutdown integration (`shutting_down` flag, SIGTERM
sequencing); metrics-middleware exclusion; Dependencies (depends on /
depended on by); Boundary; Relationships (none — no `platforms/**` node is
merged onto `origin/launchpad` yet); Scope and omissions (including the "no
template merged as `type: implementation`" deviation and "no automated test
found" gap). Done when: every Definition-of-Done bullet in issue #1272 is
addressed by a named section.

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

Re-read the diff against issue #1272's Definition of Done checklist and
re-open every cited file/line once more.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` introduces zero
  new FAIL lines beyond the pre-existing 21.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`.
- Every evidence entry classified `FACT` cites a file this task actually
  opened at the recorded revision.

## OPEN

- Whether `type: platforms` or `type: implementation` is the corpus's
  eventual settled convention for `platforms/**` documents is not resolved by
  any accepted decision found; this task follows the batch's established
  practice and states the ambiguity in the node body rather than resolving it
  unilaterally.
- No `platforms/**` sibling node is merged onto `origin/launchpad` at this
  revision, so no `relationships` edge can be declared from this node yet.

## LEFT OUT

- Testing coverage gaps for the health/readiness/liveness/status/mesh
  handlers are named as a scope gap, not fixed — this task documents existing
  behavior, it does not add tests.
- Kubernetes deployment manifests (`deploy/charts/buzz/values.yaml`) that
  configure `health_port`/probes are out of scope per the issue's "creating or
  materially editing a second canonical document" boundary; deployment
  topology belongs to `architecture/deployment/*` nodes, not this one.
