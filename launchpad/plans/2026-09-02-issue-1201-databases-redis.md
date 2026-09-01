# Plan — issue #1201: document operations/databases/redis.md

Issue #1201, `launchpad-26/buzz`. No `Size:` label or field is present on the
issue (labels: `type:task`, `area:docs`, `by:agent`); the dispatch brief for
this batch run states the cap directly instead: "Max 5 steps; this is one
document."

Stated size: no Size line on the issue; dispatch brief states the cap directly -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/operations/databases/redis.md` does not exist yet
  (confirmed: `ls launchpad/docs/corpus/operations/` fails — the `operations/`
  subtree has no nodes at all on this branch).
- `launchpad/docs/corpus/architecture/containers/redis.md` (id
  `architecture-containers-redis`) is already merged on `origin/launchpad`
  (confirmed present in the batch's `existing-node-ids.txt`) and documents
  Redis's architectural role, ownership boundary and interfaces in depth. This
  task must link it, not restate it.
- The template is `launchpad/docs/corpus/templates/reference.md`
  (id `corpus-template-reference`), already merged.
- `crates/buzz-pubsub` is the crate the issue's subject matter names as
  primary (pub/sub fan-out, presence, typing indicators per its own
  `Cargo.toml` description), but direct `redis::`/`deadpool_redis::` usage
  also exists in `crates/buzz-deletion` (community-offboarding Redis-namespace
  purge), `crates/buzz-relay-mesh` (a `mesh:ready:*` readiness registry, not
  `buzz:`-prefixed) and `crates/buzz-admin` — none of which the merged
  architecture container node discusses.
- `deploy/charts/buzz/` exists in this repository as a first-party Helm chart
  with real Redis provisioning logic (`redis.enabled`, `externalRedis.url`, a
  hard-fail validation rule at `replicaCount > 1`), distinct from the
  `squareup/block-coder-tf-stacks` deployment repo this repo's own AGENTS.md
  names for staging.
- Repository revision at plan time: `git rev-parse HEAD` =
  `473205a7457b208455f188847bfb27b01aa83cac`.

STEP 1 [independent] — Gather and verify evidence

Open and read every source the reference will cite: all of
`crates/buzz-pubsub/src/{lib,presence,topic,cache_invalidation,conn_control,
nip98_replay,rate_limiter,publisher}.rs` and `Cargo.toml`; the Redis call
sites in `crates/buzz-deletion/src/lib.rs` and
`crates/buzz-relay-mesh/src/registry.rs`; `crates/buzz-relay/src/{admission,
router,state}.rs` and `handlers/event.rs` and `api/bridge.rs` for fail-open-
vs-fail-closed behaviour on a Redis outage; `crates/buzz-auth/src/{rate_limit,
nip98_replay}.rs` for the exact key-suffix and TTL constants; `.env.example`,
`docker-compose.yml`, `docker-compose.harness.yml`, `Justfile`, `TESTING.md`;
and `deploy/charts/buzz/{Chart.yaml,Chart.lock,README.md,values.schema.json,
templates/_validate.tpl,templates/secret-chart.yaml}`.

done when: every fact the node will assert has been read at its source, not
inferred from the architecture container node's prior write-up, and the exact
key formats, TTL constants and HTTP status/message strings are transcribed
from the code rather than paraphrased from memory.

STEP 2 [needs 1] — Draft the node   <- RUNS HERE

Write `launchpad/docs/corpus/operations/databases/redis.md`, `id:
operations-databases-redis`, `type: operations`, `status: draft`, following
`templates/reference.md`'s required sections: a reference description; one or
more structured-entry tables (key namespaces/TTLs, connection configuration,
provisioning by environment, behaviour on a Redis outage); an explicit
boundary paragraph; a `references` relationship to
`architecture-containers-redis`; and a scope-and-omissions section separating
"not covered, owned by X" from "expected but not verified."

done when: the file exists with schema-legal front matter and a body matching
the template's required sections, and every substantive claim has a matching
`evidence` entry citing a file opened in STEP 1.

STEP 3 [needs 2] — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and fix anything it reports until it exits 0.

done when: the validator exits 0.

STEP 4 [needs 2] — Self-review against the issue's DoD

Re-read `gh issue view 1201`'s Definition of Done bullet by bullet against
the drafted body: exactly one hand-authored node; schema-valid front matter
with typed relationships; one independently maintainable idea; every claim
traceable and classed; links rather than duplicates neighbours; checked
against the recorded revision; validation passes; structured for lookup;
labels generated vs. authored values; defines scope/omissions; links
authoritative source/schema/config.

done when: each bullet is matched to a specific section of the body, and any
bullet that cannot be satisfied honestly is named in the final report rather
than silently dropped.

STEP 5 [needs 3, 4] — Earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call, confirm `OK`, then in a separate
call `git add -A && git commit -s -m "docs(corpus): document Redis operations
reference (#1201)"`.

done when: the test suite reports `OK` and the commit exists with a
`Signed-off-by` trailer.

PARALLEL

None. This is a single document written by one agent, so no two steps here
execute concurrently in practice. The first step is tagged `[independent]`
only because it has no upstream step, not because it overlaps with another
step in time.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK` before commit, run alone in its own tool call.
- `git commit -s` (DCO) is mandatory; no `--no-verify`.

BUDGET

One document, one plan file, one commit. Target under 400 lines for the node
body plus front matter (precedent: the merged `architecture-containers-redis`
reference-adjacent node runs to ~255 lines; a similar order of magnitude is
appropriate here given the extra crates this node covers that the container
node does not).

OPEN

- Whether `squareup/block-coder-tf-stacks` (the staging deployment repo) uses
  this repository's own `deploy/charts/buzz` chart or a different one is not
  established from this repository and is named as a gap, not resolved.
- Exact numeric values for any per-tier rate-limit thresholds beyond the
  `.env.example` defaults are `buzz-auth`'s `RateLimitConfig`, out of this
  node's scope per the architecture container node's own precedent.

LEFT OUT

- Restating `architecture-containers-redis`'s ownership-boundary and
  interfaces content — linked, not duplicated.
- The redis-failure concept (#1219) and redis-unavailable runbook (#1226):
  both open, unmerged siblings under the same Feature. Named in the body's
  scope section as planned companions, not linked as paths, and no
  `relationships` edge is declared to either (neither has a node id yet).
