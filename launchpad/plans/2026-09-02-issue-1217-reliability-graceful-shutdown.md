Issue #1217 — document operations/reliability/graceful-shutdown.md

Stated size: single document (one hand-authored corpus node + its plan file) -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/operations/reliability/graceful-shutdown.md` does not exist
  (confirmed via `ls`, exit non-zero).
- This plan file did not exist before this step.
- A merged sibling, `layers-lifecycle-graceful-shutdown`
  (`launchpad/docs/corpus/layers/lifecycle/graceful-shutdown.md`), already narrates the
  full code-level shutdown sequence for `buzz-relay` and `buzz-acp` as a `flow`-typed
  node, with a detailed evidence ledger citing exact `main.rs`/`state.rs` line ranges.
  It is present on this worktree's branch, which is based on `origin/launchpad`.
- A second merged sibling, `layers-lifecycle-background-workers`
  (`launchpad/docs/corpus/layers/lifecycle/background-workers.md`), documents that nine
  of ten `buzz-relay` background timer loops are fire-and-forget with no
  `CancellationToken` and are simply dropped, uncancelled, when the process exits —
  directly relevant to "what is dropped if the deadline is hit."
- The repository has a real Helm chart (`deploy/charts/buzz/`) with
  `terminationGracePeriodSeconds: 60`, `readinessProbe`/`livenessProbe` timing, and no
  `preStop` hook. `docker-compose.yml` and `docker-compose.harness.yml` both exist but
  run only Postgres/Redis/Minio/Keycloak/Adminer/Prometheus dependencies — neither runs
  `buzz-relay` as a compose service, so `stop_grace_period` does not apply to it in this
  repository today.
- No explicit `.close()`/shutdown call on the Postgres pool (`Db`) or the Redis
  `deadpool_redis::Pool` was found anywhere in `buzz-relay`'s shutdown path (confirmed
  by reading `state.rs`'s `AppState` definition and grepping the crate).
- Node id `operations-reliability-graceful-shutdown`, `type: operations`, template
  `launchpad/docs/corpus/templates/reference.md`, per this task's assignment.

STEP 1 [independent] — Gather and cross-check evidence against current HEAD

Read `crates/buzz-relay/src/main.rs` (shutdown budget doc comment, `shutdown_signal`,
the spawned shutdown task, `GRACEFUL_DRAIN_TIMEOUT`, post-`serve()` teardown),
`crates/buzz-relay/src/router.rs` (`readiness_handler`, WS-upgrade shutdown check),
`crates/buzz-relay/src/state.rs` (`drain_all`/`drain_all_jittered`,
`RESTART_CLOSE_ACK_TIMEOUT`, `AuditShutdownHandle::drain`, audit worker loop),
`crates/buzz-relay/src/config.rs` (`MAX_DRAIN_JITTER_MS`, `BUZZ_DRAIN_JITTER_MS`
parsing), `deploy/charts/buzz/values.yaml` and
`deploy/charts/buzz/templates/deployment.yaml` (`terminationGracePeriodSeconds`,
probes, absence of `preStop`), and both `docker-compose*.yml` files (confirm no relay
service, no `stop_grace_period`).

done when: every fact this node will assert has been read directly at this worktree's
own `git rev-parse HEAD` (not assumed from the sibling node's citations), and exact
line numbers are recorded for each.

STEP 2 [needs 1] — Write the node <- RUNS HERE

Create `launchpad/docs/corpus/operations/reliability/graceful-shutdown.md` using the
`reference` template's required sections (Reference description, structured entries,
Boundary, Relationships, Scope and omissions; no `Commands` section — there is no CLI
surface for shutdown, it is signal-driven). Content is an operator-facing lookup table
of shutdown phases, timeouts/grace periods and their governing constant or config
value, and what is dropped or unbounded if a deadline is exceeded — for `buzz-relay`
only (the brief scopes this node to the relay's main/shutdown path; `buzz-acp`'s
separate shutdown sequence is the sibling flow node's territory, named only as a
boundary). Link `layers-lifecycle-graceful-shutdown` and
`layers-lifecycle-background-workers` via `references` relationships instead of
restating their sequence narration or worker inventory.

done when: the file exists with schema-legal front matter, a body following the
reference template's required sections, and no restated flow narration or worker
comparison table that already lives in the two merged siblings.

STEP 3 [needs 2] — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root. Fix any reported error (broken node id, invalid path citation, schema violation)
and re-run until exit 0.

done when: `validate.py` exits 0.

STEP 4 [needs 3] — Self-review against the issue DoD

Re-read the issue's Definition of Done bullet by bullet against the drafted file,
including the reference-specific tail bullets (structured for lookup, generated vs.
authored values labelled, scope and omissions defined, authoritative source/schema/
config linked). Confirm every `FACT` citation was actually opened in Step 1, and that
only one commit-only `FACT` (the provenance entry) exists in the ledger.

done when: every DoD bullet is checked off against a real section of the body, or named
as unsatisfied in the final report.

STEP 5 [needs 4] — Commit

Run the corpus test suite (`python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole command in its
own Bash call, confirm `OK`, then in a separate call `git add -A && git commit -s -m
"docs(corpus): add operations/reliability graceful-shutdown reference (#1217)"`.

done when: the commit exists locally with `-s` (DCO) and `git log -1` shows it; no
push, no PR.

PARALLEL

None — Steps 1-5 are strictly sequential (evidence, then write, then validate, then
self-review, then commit). No two steps can run concurrently.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
  committing.
- The corpus unit test suite must print `OK` before committing (verify-gate stamp).
- File must stay under 1000 lines (repo-wide file-size gate) — not a realistic risk for
  a single reference node, but checked.

BUDGET

One document, one plan file, no code changes. Expected total: under 500 lines of new
Markdown.

OPEN

- Whether Kubernetes' own Service-endpoint-removal-on-Terminating behavior (as opposed
  to readiness-probe-failure-triggered removal) is faster than the probe's
  `periodSeconds`/`failureThreshold` — this is generic Kubernetes platform behavior, not
  something this repository's own source establishes, and is named as an unverified
  item rather than asserted.

LEFT OUT

- Any restatement of `buzz-acp`'s own shutdown sequence (SIGINT/SIGTERM/`!shutdown`,
  the 30s+30s+per-agent drain) — that is `layers-lifecycle-graceful-shutdown`'s content
  for a different process, out of this node's scope per the brief.
- Any relationship or prose reference to `operations/availability` or other
  `operations/reliability/*` siblings from this batch (#1214 and others) — they are
  unmerged and not valid relationship targets; named as neighboring concerns in prose
  only, per the brief.
