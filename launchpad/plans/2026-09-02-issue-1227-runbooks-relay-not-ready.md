Plan: issue #1227 -- corpus doc for operations/runbooks/relay-not-ready.md

ALREADY TRUE: the worktree's HEAD is 473205a7457b208455f188847bfb27b01aa83cac. The
target file launchpad/docs/corpus/operations/runbooks/relay-not-ready.md does not exist
(confirmed by `ls`). `launchpad/docs/corpus/templates/runbook.md` (id
`corpus-template-runbook`) is merged on `origin/launchpad` and appears in
`existing-node-ids.txt`, so it is a legal `relationships` target. No
`operations/runbooks/*` node exists anywhere in this worktree's corpus tree yet --
`postgres-unavailable` (#1224), `redis-unavailable` (#1226), and
`object-storage-unavailable` (#1223) are sibling tasks in this same batch, not merged
nodes to link to.

Stated size: issue #1227's body has no explicit Size line; the batch dispatch brief caps every task at "Max 5 steps; this is one document" -> cap: 5 steps.

STEP 1 (RUNS HERE) [independent]: gather evidence directly from the code that decides relay
readiness -- `crates/buzz-relay/src/router.rs` (`health_handler`, `liveness_handler`,
`readiness_handler`, `build_health_router`, `status_handler`, `mesh_status_handler`);
the eager startup gates in `crates/buzz-relay/src/main.rs` (Postgres connect, auto-
migrate, `validate_deletion_serving_catalog`, `verify_channel_roster_fence`/migration
0032, the git object-store A3 conformance probe, NIP-43 owner/key config checks, Redis
pool construction vs. `PubSubManager::new`, search/audit DB pools, the health-port
listener bind); `crates/buzz-db/src/store/deletion.rs`'s
`validate_serving_catalog`/`validate_catalog` bodies and `crates/buzz-db/src/runtime/mod.rs`'s
`ping`; the Helm probe defaults in `deploy/charts/buzz/values.yaml` and their wiring in
`deploy/charts/buzz/templates/deployment.yaml`; the Compose healthcheck and
`depends_on` ordering in `deploy/compose/compose.yml`'s `relay` service (confirming
root `docker-compose.yml` carries no relay service to check); and
`launchpad/docs/Observability/current-state/relay.md` plus `ARCHITECTURE.md`'s route
table as independent, already-written cross-checks of the same behavior.
done when: each fatal-vs-non-fatal startup path and each readiness-check branch is
read and its line range noted.

STEP 2 [needs 1]: write the front matter (id `operations-runbooks-relay-not-ready`, type
`operations`, status `draft`, origin `launchpad`, audiences `[operator, developer,
agent]`, one `relationships` entry `{type: implements, target:
corpus-template-runbook}`) and the body against `templates/runbook.md`'s required
sections -- Trigger, Severity and impact, Diagnosis, Mitigation and resolution,
Escalation, Scope and omissions -- built around the real decision tree the code
produces: crash-looping (an eager `?`-propagated startup failure exits the process
before or shortly after the health port binds) versus running-but-not-ready (the
readiness handler's JSON body names which of Postgres/Redis/the deletion serving
catalog failed, or reports `shutting_down`). Hand off Postgres- and Redis-specific
recovery to the sibling runbooks by name (not by link, since neither is merged); state
plainly that object storage is not part of the readiness check at all.
done when: every DoD tail bullet (trigger/symptom, severity/impact, prerequisites;
diagnosis then mitigation in executable order; verification, rollback/escalation,
evidence to preserve) has a concrete section backing it.

STEP 3 [needs 2]: run `python3 launchpad/project-intelligence/corpus/validate.py`
from the worktree root and fix whatever it reports until it exits 0.
done when: the command prints a pass and exit status 0.

STEP 4 [needs 3]: re-read the finished node against `launchpad/docs/corpus/AGENTS.md`'s
evidence rules and `templates/runbook.md`'s evidence-class guidance one more time --
every `FACT` traces to a source actually opened in Step 1, every commit-only `FACT`
count stays at exactly one, and the scope-and-omissions section separates "not
covered, owned elsewhere" from "expected to verify and could not."
done when: a re-read of the diff finds no citation rebuilt from memory rather than
from Step 1's notes.

STEP 5 [needs 4]: run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own tool call to earn the commit
verification stamp (confirm `OK`), then, in a separate tool call, `git add -A && git
commit -s -m "docs(corpus): add relay-not-ready operations runbook (#1227)"`.
done when: the commit exists locally and `git status` is clean.

PARALLEL: none -- one file, one worktree, no dependency on a sibling task's output
(the sibling runbooks are named in prose only, never linked as `relationships` or as
paths, since none is merged).

GATES: `validate.py` must exit 0 locally before commit, and the unittest suite must
print `OK` immediately before the commit (no piped output, no chained `cd`, per this
task's process notes). review-adjudicate and any cross-model final review are deferred
to the batch owner's integration pass across Feature #618, not run here.

BUDGET: single document, one sitting.

OPEN: the readiness handler's JSON error body (`postgres`, `redis`,
`deletion_catalog` booleans) is the load-bearing diagnostic signal this runbook is
built around, and it was read directly from `router.rs` rather than from a test that
exercises a real dependency outage -- no test in this repository was found driving a
downed Postgres/Redis/catalog through `readiness_handler` end-to-end. This is recorded
as a scope-and-omissions gap in the node itself rather than treated as a blocker,
since the code path is unambiguous on its own.

LEFT OUT: no `relationships` entry toward `postgres-unavailable`, `redis-unavailable`,
or `object-storage-unavailable` -- none of the three is merged on `origin/launchpad`
at this worktree's base, so none is a legal target yet (per AGENTS.md step 9 and this
batch's own dispatch note); they are named in body prose only, per the linking
standard's rule for a real connection that does not yet resolve on the merge branch.
No change to `launchpad/docs/Observability/current-state/relay.md` or `ARCHITECTURE.md`
even though both already describe this behavior accurately -- editing them is out of
this task's scope and neither has drifted from the code.
