# Issue #1097 — corpus node: layers/data/redis/role.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/templates/datastore.md`, and
`launchpad/docs/corpus/architecture/containers/redis.md` (id
`architecture-containers-redis`, `type: architecture`, `status: draft`) are merged on
`origin/launchpad`. The target file `launchpad/docs/corpus/layers/data/redis/role.md`
does not exist yet, and no `layers/` subtree exists in the corpus at all yet — this is
the first `type: layers` node. `layers/data/object-storage/role.md` (#1073) and
`layers/data/postgres/role.md` (#1087) are siblings drafted in the same Feature #610,
on unmerged PR branches — not present on `origin/launchpad`, so not valid
`relationships` targets per `AGENTS.md` step 9.

STEP 1 — Confirm distinctness from `architecture-containers-redis` and gather
datastore-level evidence not already covered by that container document. Read
`crates/buzz-pubsub/src/{lib.rs,topic.rs,presence.rs,rate_limiter.rs,nip98_replay.rs,
cache_invalidation.rs,conn_control.rs,publisher.rs,subscriber.rs}` for the current key
namespace, TTL/lifecycle, atomicity (Lua scripts, `NX`), tenancy scoping, and
fire-and-forget/fail-closed behavior at HEAD (the crate has been refactored since the
container doc's revision — `publisher.rs`/`subscriber.rs` now exist as separate
modules; `PubSubManager::publish_cache_invalidation`/`publish_conn_control` doc
comments explicitly state fire-and-forget + DB backstop). Read `crates/buzz-relay/src/
{main.rs,state.rs,router.rs}` for pool construction/sizing, readiness-probe behavior,
and metrics. Read `.env.example` and `docker-compose.yml` for the attachment profile
(no schema/namespace *migration* mechanism exists for Redis — key conventions are
enforced in code, not in a versioned migration file, which is itself a datastore fact
worth stating explicitly per the template's required section 4). RUNS HERE.

STEP 2 — Write front matter (id `layers-data-redis-role`, type `layers` — override
disclosed per `standards/taxonomy.md`, since `templates/datastore.md` itself directs a
real instance node to `type: architecture`; this Feature's own precedent from #1073 and
#1087 uses `layers` instead) and the body per `templates/datastore.md`'s seven required
sections: purpose/scope naming `architecture-containers-redis` as the container this
zooms into; technology & attachment profile; key-namespace inventory (Redis's structural
analogue to a schema/table inventory — one row per key-family/channel-family); the
explicit "no migration mechanism" fact for section 4; access-pattern summary (which
crate/module reads/writes, under what atomicity guarantee); operational characteristics
(TTL/retention, no persistence in local dev, reconnect backoff); and scope/omissions.
Also state explicitly, per the issue DoD's non-template-shaped bullets: authoritative
vs. derived vs. cache vs. transport (cache + transport, never system of record — INFERENCE,
mirroring the container doc's own INFERENCE but re-derived from this session's own
evidence, not copied); tenancy/security boundaries (community-prefixed keys, one
deliberate operator-global exception for IP rate-limiting); and failure behavior
(fail-closed on pool-acquire failure for admission paths; fire-and-forget + DB backstop
for cache-invalidation/conn-control). One `relationships` entry: `part-of` →
`architecture-containers-redis` (merged, confirmed present in `origin/launchpad`'s
corpus tree). No edges to the two unmerged `layers/data/*/role.md` siblings. RUNS HERE.

STEP 3 — Run `python3 launchpad/project-intelligence/corpus/validate.py` against the
full tree; fix and re-run until exit 0. RUNS HERE.

STEP 4 — Run the corpus unittest suite as the sole prior command
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`, bare and unpiped), confirm OK, then commit (plan + node) in a separate
call. Do not push and do not open a PR — a later orchestration step bundles this branch
with its batch siblings. RUNS HERE.

PARALLEL: none — single file, single worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK before commit, run as a bare standalone command (a piped
command's exit code belongs to the pipe, not the suite). `review-adjudicate` and any
cross-model final-review pass are explicitly deferred to the batch owner's later
bundling/review step — not run in this session.

BUDGET: single document, one sitting — no multi-hour scope expected.

OPEN: the issue's DoD bullets ("authoritative/derived/cache/transport",
"owned data, key access patterns, lifecycle/retention and consistency semantics",
"tenancy/security boundaries and failure behavior", "link schema/migrations/code/tests
rather than copying DDL") read as `templates/datastore.md`'s own required-sections
list under different wording, plus the container/datastore distinction the template
itself defines. This plan treats them as satisfied by the template's shape rather than
as a second, independently-invented section list — flagged here per the batch's own
"disclose deviation from template's worked example" pattern, in case a reviewer expects
a literal one-bullet-per-heading mapping instead.

LEFT OUT: no `relationships` to the two sibling `layers/data/*/role.md` documents
(#1073, #1087) — both are on unmerged PR branches, and `AGENTS.md` step 9 requires a
target to exist on the branch being merged into, not the author's own branch. No attempt
to resolve the `.env.example` Typesense-vs-Postgres-FTS discrepancy or the
`#[datastore_span]` Postgres-only instrumentation gap the datastore template's own
worked illustration already names — those are pre-existing, general corpus gaps, not
specific to Redis, and are out of this task's scope per the issue's own "Broad 'while
here' documentation cleanup" exclusion.
